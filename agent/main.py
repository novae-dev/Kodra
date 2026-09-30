from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Kodra Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parent.parent

IGNORED = {
    "node_modules",
    ".git",
    ".venv",
    "dist",
    "__pycache__",
    ".next",
    "coverage",
}


def is_ignored(path: Path) -> bool:
    return any(part in IGNORED for part in path.parts)


def safe_path(relative_path: str) -> Path:
    target = (ROOT / relative_path).resolve()

    try:
        target.relative_to(ROOT)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid file path")

    if is_ignored(target):
        raise HTTPException(status_code=400, detail="Access to this path is blocked")

    return target


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
    files = []

    for path in ROOT.rglob("*"):
        if path.is_file() and not is_ignored(path):
            files.append(str(path.relative_to(ROOT)).replace("\\", "/"))

    files.sort()

    return {
        "project": ROOT.name,
        "files": files[:500],
    }


@app.get("/file")
def read_file(path: str):
    target = safe_path(path)

    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not target.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="This file cannot be displayed as text",
        )

    return {
        "path": path,
        "content": content,
    }


@app.post("/chat")
def chat(payload: dict):
    message = payload.get("message", "").strip()
    context = payload.get("context", {})

    if not message:
        return {
            "reply": "Send me a message and I'll help you work on the project."
        }

    current_file = context.get("currentFile")

    if current_file:
        return {
            "reply": (
                f"I received your request about {current_file}. "
                "Kodra now has access to the real project context. "
                "The next step is connecting an AI provider so I can "
                "analyze and modify the code."
            )
        }

    return {
        "reply": (
            f"I received: '{message}'. "
            "Kodra is connected to the project-aware Python agent."
        )
    }