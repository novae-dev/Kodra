import re
from pathlib import Path
from typing import Any, Dict, List
from kodra.models.agent import AgentRole, AgentResponse
from kodra.models.plan import PlanStep, OperationType, RiskLevel
from kodra.agents.base import BaseAgent
from kodra.providers.mock_provider import MockProvider


class BackendDeveloperAgent(BaseAgent):
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.mock = MockProvider()

    @property
    def role(self) -> AgentRole:
        return AgentRole.BACKEND

    @property
    def name(self) -> str:
        return "Kodra Backend Specialist"

    @property
    def description(self) -> str:
        return "Specializes in Python/Go architectures, APIs, data structures, and backend logic."

    def process(self, task: str, context: Dict[str, Any]) -> AgentResponse:
        steps: List[PlanStep] = []
        # Target path detection
        file_match = re.search(r'([\w\-./\\]+\.(py|go|json|sql))', task)
        target = file_match.group(1).replace("\\", "/") if file_match else "backend_module.py"

        if "/" in target:
            dir_name = target.rsplit("/", 1)[0]
            steps.append(
                PlanStep(
                    title=f"Scaffold backend directory: {dir_name}",
                    description="Ensure directory structure exists for backend components",
                    operation=OperationType.CREATE_DIR,
                    path=dir_name,
                    risk_level=RiskLevel.LOW,
                    requires_approval=False,
                )
            )

        content = self.mock._generate_code_snippet(target, task)
        steps.append(
            PlanStep(
                title=f"Implement backend logic: {target}",
                description=f"Construct module satisfying: {task}",
                operation=OperationType.CREATE_FILE,
                path=target,
                content=content,
                risk_level=RiskLevel.LOW,
                requires_approval=True,
            )
        )

        return AgentResponse(
            role=self.role,
            summary=f"Formulated backend implementation plan for {target}.",
            suggested_steps=steps,
            findings=[f"Target file: {target}", "Architecture: Modular service component"],
        )


class FrontendDeveloperAgent(BaseAgent):
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.mock = MockProvider()

    @property
    def role(self) -> AgentRole:
        return AgentRole.FRONTEND

    @property
    def name(self) -> str:
        return "Kodra Frontend Specialist"

    @property
    def description(self) -> str:
        return "Specializes in React, TypeScript, UI components, layout design, and styling."

    def process(self, task: str, context: Dict[str, Any]) -> AgentResponse:
        steps: List[PlanStep] = []
        file_match = re.search(r'([\w\-./\\]+\.(tsx|ts|jsx|js|css|html))', task)
        target = file_match.group(1).replace("\\", "/") if file_match else "src/components/FeatureComponent.tsx"

        if "/" in target:
            dir_name = target.rsplit("/", 1)[0]
            steps.append(
                PlanStep(
                    title=f"Scaffold frontend directory: {dir_name}",
                    description="Ensure directory structure exists for UI component",
                    operation=OperationType.CREATE_DIR,
                    path=dir_name,
                    risk_level=RiskLevel.LOW,
                    requires_approval=False,
                )
            )

        content = self.mock._generate_code_snippet(target, task)
        steps.append(
            PlanStep(
                title=f"Implement frontend component: {target}",
                description=f"Create UI component for: {task}",
                operation=OperationType.CREATE_FILE,
                path=target,
                content=content,
                risk_level=RiskLevel.LOW,
                requires_approval=True,
            )
        )

        return AgentResponse(
            role=self.role,
            summary=f"Formulated frontend UI plan for {target}.",
            suggested_steps=steps,
            findings=[f"Target component: {target}", "Framework: React / TypeScript"],
        )
