from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
from kodra.models.plan import PlanStep


class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher"
    BACKEND = "backend"
    FRONTEND = "frontend"
    TESTER = "tester"
    SECURITY = "security"


class AgentMessage(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    role: AgentRole
    content: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    role: AgentRole
    summary: str
    analysis: Optional[str] = None
    suggested_steps: List[PlanStep] = Field(default_factory=list)
    findings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
