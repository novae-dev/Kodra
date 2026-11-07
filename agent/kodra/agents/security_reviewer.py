from pathlib import Path
from typing import Any, Dict, List
from kodra.models.agent import AgentRole, AgentResponse
from kodra.models.plan import PlanStep, RiskLevel, OperationType
from kodra.agents.base import BaseAgent
from kodra.security.policy import SecurityPolicy


class SecurityReviewAgent(BaseAgent):
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.policy = SecurityPolicy(self.workspace_root)

    @property
    def role(self) -> AgentRole:
        return AgentRole.SECURITY

    @property
    def name(self) -> str:
        return "Kodra Security Auditor"

    @property
    def description(self) -> str:
        return "Audits proposed execution steps, path containment, command safety, and secret isolation."

    def process(self, task: str, context: Dict[str, Any]) -> AgentResponse:
        steps_to_review: List[PlanStep] = context.get("candidate_steps", [])
        findings: List[str] = []

        for step in steps_to_review:
            violations = self.policy.validate_step(step)
            if violations:
                findings.extend(violations)
            else:
                findings.append(f"Step '{step.title}' verified safe (Risk: {step.risk_level}).")

            if step.operation == OperationType.RUN_COMMAND:
                step.requires_approval = True

        all_safe = len(findings) == 0 or all("verified safe" in f for f in findings)
        return AgentResponse(
            role=self.role,
            summary="Security audit completed successfully." if all_safe else "Security policy flagged potential concerns.",
            analysis="Workspace containment and policy enforcement evaluated.",
            suggested_steps=steps_to_review,
            findings=findings,
            metadata={"all_safe": all_safe},
        )
