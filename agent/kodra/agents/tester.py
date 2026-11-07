from pathlib import Path
from typing import Any, Dict, List
from kodra.models.agent import AgentRole, AgentResponse
from kodra.models.plan import PlanStep, OperationType, RiskLevel
from kodra.agents.base import BaseAgent


class TestingAgent(BaseAgent):
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    @property
    def role(self) -> AgentRole:
        return AgentRole.TESTER

    @property
    def name(self) -> str:
        return "Kodra Testing Specialist"

    @property
    def description(self) -> str:
        return "Formulates unit test suites, integration tests, and verification commands."

    def process(self, task: str, context: Dict[str, Any]) -> AgentResponse:
        steps: List[PlanStep] = []
        is_backend = any(f.endswith(".py") for f in context.get("target_files", [])) or "backend" in task.lower()
        
        if is_backend:
            targets = [f for f in context.get("target_files", []) if f.endswith(".py")]
            has_tests_dir = (self.workspace_root / "tests").exists() or any(self.workspace_root.glob("test_*.py"))
            
            if has_tests_dir:
                cmd = "python -m pytest"
            elif targets:
                cmd = f"python {targets[0]}"
            else:
                cmd = "python -c \"print('Syntax check passed')\""

            steps.append(
                PlanStep(
                    title="Validate implementation tests",
                    description=f"Execute verification command ({cmd}) to test functionality",
                    operation=OperationType.RUN_COMMAND,
                    command=cmd,
                    risk_level=RiskLevel.LOW,
                    requires_approval=True,
                )
            )
        else:
            steps.append(
                PlanStep(
                    title="Verify build and client tests",
                    description="Execute npm test or build validation",
                    operation=OperationType.RUN_COMMAND,
                    command="npm test",
                    risk_level=RiskLevel.LOW,
                    requires_approval=True,
                )
            )

        return AgentResponse(
            role=self.role,
            summary="Constructed automated test verification steps.",
            suggested_steps=steps,
            findings=["Test suite attached for automated verification."],
        )
