from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Khalid Alznaidi - Portfolio")

# --- API routes (declared BEFORE the static mount so they take priority) ---


@app.get("/health")
def health():
    """Simple health check. Handy for uptime monitoring and CI smoke tests."""
    return {"status": "ok"}


@app.get("/api/projects")
def projects():
    """The portfolio page fetches this and renders it on the client side."""
    return [
        {
            "name": "Cloud-Deployed Portfolio (this site)",
            "stack": ["FastAPI", "Docker", "Nginx", "GitHub Actions", "OCI"],
            "blurb": "A containerized web app that auto-deploys to my own cloud "
                     "server on every push to main via a CI/CD pipeline.",
        },
        {
            "name": "Ultrasonic Radar System",
            "stack": ["C++", "ESP32", "Arduino", "Servo control"],
            "blurb": "Embedded firmware for a scanning distance detector: 120 degree "
                     "sweep, 80 cm range, real-time serial visualization.",
        },
        {
            "name": "Hand-Crank Generator",
            "stack": ["Electromagnetic induction", "Coil/magnet design"],
            "blurb": "A generator producing up to 22 V from manual rotation.",
        },
    ]


# --- Static site mounted last; serves static/index.html at "/" ---
app.mount("/", StaticFiles(directory="static", html=True), name="static")
