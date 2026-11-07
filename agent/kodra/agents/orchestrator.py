from pathlib import Path
from typing import Any, Dict, List
from kodra.models.agent import AgentRole, AgentResponse
from kodra.models.plan import ExecutionPlan, PlanStatus, PlanStep
from kodra.agents.base import BaseAgent
from kodra.agents.researcher import ResearchAgent
from kodra.agents.developer import BackendDeveloperAgent, FrontendDeveloperAgent
from kodra.agents.tester import TestingAgent
from kodra.agents.security_reviewer import SecurityReviewAgent


class LeadOrchestrator(BaseAgent):
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.researcher = ResearchAgent(self.workspace_root)
        self.backend = BackendDeveloperAgent(self.workspace_root)
        self.frontend = FrontendDeveloperAgent(self.workspace_root)
        self.tester = TestingAgent(self.workspace_root)
        self.security = SecurityReviewAgent(self.workspace_root)

    @property
    def role(self) -> AgentRole:
        return AgentRole.ORCHESTRATOR

    @property
    def name(self) -> str:
        return "Kodra Lead Orchestrator"

    @property
    def description(self) -> str:
        return "Directs specialist agents, coordinates task decomposition, and synthesizes the execution plan."

    def list_specialists(self) -> List[Dict[str, str]]:
        return [
            {"role": self.role.value, "name": self.name, "description": self.description},
            {"role": self.researcher.role.value, "name": self.researcher.name, "description": self.researcher.description},
            {"role": self.backend.role.value, "name": self.backend.name, "description": self.backend.description},
            {"role": self.frontend.role.value, "name": self.frontend.name, "description": self.frontend.description},
            {"role": self.tester.role.value, "name": self.tester.name, "description": self.tester.description},
            {"role": self.security.role.value, "name": self.security.name, "description": self.security.description},
        ]

    def plan_task_with_delegation(self, task: str, context: Dict[str, Any]) -> ExecutionPlan:
        """
        Executes multi-agent collaboration:
        1. Researcher gathers workspace context.
        2. Specialist (Backend/Frontend) drafts implementations.
        3. Tester appends test verification.
        4. SecurityReviewer audits steps.
        5. Orchestrator synthesizes the final ExecutionPlan.
        """
        # Step 1: Research
        research_res = self.researcher.process(task, context)

        # Step 2: Determine appropriate developer specialist
        task_lower = task.lower()
        candidate_steps: List[PlanStep] = []
        is_frontend = any(kw in task_lower for kw in ("react", "ui", "frontend", "css", "component", "button", ".tsx", ".jsx"))
        is_backend = any(kw in task_lower for kw in ("api", "endpoint", "backend", "database", "python", "fastapi", "server", ".py", ".go"))

        if is_frontend and not is_backend:
            dev_res = self.frontend.process(task, context)
            candidate_steps.extend(dev_res.suggested_steps)
        elif is_backend and not is_frontend:
            dev_res = self.backend.process(task, context)
            candidate_steps.extend(dev_res.suggested_steps)
        else:
            # Fullstack or general: invoke backend then frontend if appropriate
            backend_res = self.backend.process(task, context)
            candidate_steps.extend(backend_res.suggested_steps)

        # Step 3: Testing specialist
        test_res = self.tester.process(
            task,
            {**context, "target_files": [s.path for s in candidate_steps if s.path]},
        )
        candidate_steps.extend(test_res.suggested_steps)

        # Step 4: Security auditor
        security_res = self.security.process(task, {"candidate_steps": candidate_steps})
        final_steps = security_res.suggested_steps

        # Step 5: Synthesize
        return ExecutionPlan(
            task=task,
            summary=f"Multi-agent collaborative plan orchestrated across {len(final_steps)} coordinated steps.",
            steps=final_steps,
            status=PlanStatus.DRAFT,
            metadata={
                "orchestration": True,
                "research_summary": research_res.summary,
                "security_findings": security_res.findings,
                "participating_agents": [
                    "orchestrator",
                    "researcher",
                    "frontend" if is_frontend else "backend",
                    "tester",
                    "security",
                ],
            },
        )

    def process(self, task: str, context: Dict[str, Any]) -> AgentResponse:
        plan = self.plan_task_with_delegation(task, context)
        return AgentResponse(
            role=self.role,
            summary=plan.summary,
            suggested_steps=plan.steps,
            findings=[f"Coordinated {len(plan.steps)} steps through multi-agent delegation."],
            metadata=plan.metadata,
        )
