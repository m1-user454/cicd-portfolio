# Cloud-Deployed Portfolio with CI/CD

A small FastAPI web app, containerized with Docker, running on an Oracle Cloud
(OCI) instance behind Nginx, and **auto-deployed by GitHub Actions on every push
to `main`**.

```
git push  ->  GitHub Actions  ->  SSH into OCI  ->  git pull + docker compose up --build  ->  live site
```

Build it in the order below. **Get each phase working before moving to the next** —
the golden rule of deployment is to make it work manually first, then automate.

---

## What's in here

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app: serves the site + a `/health` check + an `/api/projects` endpoint |
| `static/index.html` | The portfolio page; it fetches `/api/projects` on load (so it's a real app, not static HTML) |
| `Dockerfile` | Builds the app image (multi-arch: works on ARM and x86 instances) |
| `docker-compose.yml` | Runs the app, bound to localhost so only Nginx can reach it |
| `deploy/nginx.conf` | Sample reverse-proxy config for the host Nginx |
| `.github/workflows/deploy.yml` | The CI/CD pipeline |

---

## Phase 0 — Prerequisites

- A GitHub account and an empty repo (e.g. `cicd-portfolio`).
- Your OCI instance, and the SSH key you already use to log in.
- Docker installed locally is helpful but optional.
- Optional but recommended: a domain name (even a free one) so you can add HTTPS.

Find out your instance's CPU architecture — it's good to know and good to mention
in an interview:

```bash
uname -m   # aarch64 = ARM (Ampere) | x86_64 = AMD/Intel
```

The app image works on both, so this won't block you either way.

---

## Phase 1 — Run it locally

```bash
docker compose up --build
# open http://localhost:8000
# check http://localhost:8000/health  and  http://localhost:8000/api/projects
```

Edit `main.py` / `static/index.html` to make it yours. When it looks right, push:

```bash
git init && git add . && git commit -m "initial portfolio"
git branch -M main
git remote add origin git@github.com:YOUR-USERNAME/cicd-portfolio.git
git push -u origin main
```

---

## Phase 2 — Prepare the server

SSH in, then install Docker:

```bash
# Ubuntu
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER      # log out & back in so this takes effect

# Oracle Linux (if your instance uses it)
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

**Open the ports — this is a two-layer thing on OCI and trips everyone up the first time:**

1. **OCI console:** Networking -> your VCN -> the subnet's Security List (or the
   instance's Network Security Group) -> add Ingress rules for TCP **80** and **443**
   from `0.0.0.0/0`.
2. **The instance's own firewall:**

```bash
# Oracle Linux (firewalld)
sudo firewall-cmd --permanent --add-service=http --add-service=https
sudo firewall-cmd --reload

# Ubuntu sometimes ships iptables rules that block these:
sudo iptables -I INPUT 5 -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save   # if installed
```

---

## Phase 3 — First deploy, by hand

```bash
sudo dnf install -y git    # or: sudo apt install -y git
cd ~
git clone https://github.com/YOUR-USERNAME/cicd-portfolio.git
cd cicd-portfolio
docker compose up -d --build
curl localhost:8000/health     # should print {"status":"ok"}
```

Then put Nginx in front so it's reachable from the internet:

```bash
sudo apt install -y nginx        # or: sudo dnf install -y nginx
# copy deploy/nginx.conf into Nginx's config dir, edit server_name, then:
sudo nginx -t && sudo systemctl reload nginx
```

Visit `http://YOUR-PUBLIC-IP` (or your domain). If you have a domain, add HTTPS:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

Once `http://...` / `https://...` shows your site, the hard part is done.

---

## Phase 4 — Automate it (the CI/CD payoff)

You want GitHub to deploy for you on every push. The workflow in
`.github/workflows/deploy.yml` SSHes into the server, pulls, and rebuilds.

**1. Make a dedicated deploy key** (don't reuse your personal key). On your laptop:

```bash
ssh-keygen -t ed25519 -f deploy_key -N ""
```

**2. Authorize the public key on the server:**

```bash
# paste the contents of deploy_key.pub into the server's ~/.ssh/authorized_keys
cat deploy_key.pub   # copy this, then on the server append it to ~/.ssh/authorized_keys
```

**3. Add three GitHub repo secrets** (repo -> Settings -> Secrets and variables ->
Actions -> New repository secret):

| Secret | Value |
|--------|-------|
| `SERVER_HOST` | your instance's public IP |
| `SERVER_USER` | your SSH username (`ubuntu`, `opc`, etc.) |
| `SERVER_SSH_KEY` | the **entire** contents of the private `deploy_key` file |

**4. Deploy by pushing:**

```bash
git commit -am "change something" && git push
```

Open the repo's **Actions** tab and watch it run. When it goes green, refresh your
site — your change is live. That's continuous deployment.

---

## CV bullet points you can now write (truthfully)

- Built and deployed a containerized Python (FastAPI) web service to a self-managed
  Oracle Cloud (OCI) Linux instance, fronted by Nginx with HTTPS.
- Implemented a CI/CD pipeline with GitHub Actions that automatically rebuilds and
  redeploys the application over SSH on every push to `main`.
- Configured cloud networking and host firewall rules and used Docker Compose to
  run the service in an isolated, reproducible environment.

---

## Level-ups (each one is another interview talking point)

- **Build in CI, not on the server:** have Actions build the image and push it to
  GitHub Container Registry (GHCR); the server just pulls and restarts. This is
  closer to how real teams do it.
- **Add a test step** to the workflow (e.g. hit `/health`) and only deploy if it passes.
- Add a CI **status badge** to this README.
- Add a real feature with a database (Postgres in another compose service) so you
  have persistent data to talk about.
