from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Kodra Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "name": "Kodra Agent",
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/project")
def project():
    root = Path(__file__).resolve().parent.parent

    files = []

    ignored = {
        "node_modules",
        ".git",
        ".venv",
        "dist",
        "__pycache__",
    }

    for path in root.rglob("*"):
        if path.is_file() and not any(
            part in ignored for part in path.parts
        ):
            files.append(str(path.relative_to(root)))

    return {
        "project": root.name,
        "files": files[:200],
    }


@app.post("/chat")
def chat(payload: dict):
    message = payload.get("message", "").strip()

    if not message:
        return {
            "reply": "Send me a message and I'll help you work on the project."
        }

    return {
        "reply": (
            f"I received: '{message}'. "
            "Kodra is connected to the Python agent."
        )
    }