from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field, ConfigDict


class OperationType(str, Enum):
    CREATE_FILE = "create_file"
    MODIFY_FILE = "modify_file"
    DELETE_FILE = "delete_file"
    CREATE_DIR = "create_dir"
    RUN_COMMAND = "run_command"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StepStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class PlanStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REPAIRED = "repaired"


class PlanStep(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(default_factory=lambda: f"step-{uuid.uuid4().hex[:6]}")
    title: str
    description: str = ""
    operation: OperationType
    path: Optional[str] = None
    content: Optional[str] = None
    command: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    requires_approval: bool = True
    approved: bool = False
    status: StepStatus = StepStatus.PENDING


class ExecutionPlan(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(default_factory=lambda: f"plan-{uuid.uuid4().hex[:8]}")
    task: str
    summary: str
    steps: List[PlanStep] = Field(default_factory=list)
    status: PlanStatus = PlanStatus.DRAFT
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StepResult(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    step_id: str
    status: StepStatus
    output: str = ""
    error: Optional[str] = None
    exit_code: Optional[int] = None
    duration_ms: float = 0.0


class ExecutionResult(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    plan_id: str
    success: bool
    step_results: List[StepResult] = Field(default_factory=list)
    summary: str = ""
    error: Optional[str] = None
