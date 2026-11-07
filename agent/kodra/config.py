import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Settings(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    workspace_root: Path = Field(
        default_factory=lambda: Path(os.environ.get("KODRA_WORKSPACE", Path(__file__).resolve().parent.parent.parent))
    )
    provider: str = Field(default_factory=lambda: os.environ.get("KODRA_PROVIDER", "mock"))
    model: Optional[str] = Field(default=None)
    
    # API Keys / endpoints
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: os.environ.get("ANTHROPIC_API_KEY"))
    gemini_api_key: Optional[str] = Field(default_factory=lambda: os.environ.get("GEMINI_API_KEY"))
    groq_api_key: Optional[str] = Field(default_factory=lambda: os.environ.get("GROQ_API_KEY"))
    ollama_host: str = Field(default_factory=lambda: os.environ.get("OLLAMA_HOST", "http://localhost:11434"))

    # Security & Policy settings
    command_timeout_sec: int = 45
    max_file_size_bytes: int = 5 * 1024 * 1024  # 5MB
    ignored_patterns: List[str] = Field(
        default_factory=lambda: [
            "node_modules",
            ".git",
            ".venv",
            "venv",
            "dist",
            "build",
            "__pycache__",
            ".next",
            "coverage",
            ".pytest_cache",
            ".mypy_cache",
        ]
    )

    def set_workspace(self, path: str | Path) -> Path:
        resolved = Path(path).resolve()
        if not resolved.exists():
            resolved.mkdir(parents=True, exist_ok=True)
        self.workspace_root = resolved
        return self.workspace_root


settings = Settings()
