from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class KodraProjectConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    version: str = "1.0.0"
    name: str = "Kodra Workspace"
    description: Optional[str] = "AI-assisted software engineering project"
    workspace_root: str = "."
    tech_stack: List[str] = Field(default_factory=list)
    guidelines: List[str] = Field(default_factory=list)
    memory: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()
