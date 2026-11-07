from kodra.agents.orchestrator import LeadOrchestrator
from kodra.models.plan import PlanStatus


def test_lead_orchestrator_delegation_flow(tmp_path):
    orchestrator = LeadOrchestrator(tmp_path)

    # 1. Verify specialists registration
    specialists = orchestrator.list_specialists()
    roles = [s["role"] for s in specialists]
    assert "orchestrator" in roles
    assert "researcher" in roles
    assert "backend" in roles
    assert "frontend" in roles
    assert "tester" in roles
    assert "security" in roles

    # 2. Test multi-agent backend flow
    task = "Build a FastAPI authentication service in auth.py"
    plan = orchestrator.plan_task_with_delegation(task, {"tech_stack": ["Python", "FastAPI"]})

    assert plan.status == PlanStatus.DRAFT
    assert plan.metadata.get("orchestration") is True
    assert len(plan.steps) >= 2
    assert any("auth.py" in (s.path or "") for s in plan.steps)
    assert any("python" in (s.command or "") for s in plan.steps)
    assert "researcher" in plan.metadata.get("participating_agents", [])
    assert "security" in plan.metadata.get("participating_agents", [])


def test_lead_orchestrator_frontend_delegation(tmp_path):
    orchestrator = LeadOrchestrator(tmp_path)
    task = "Create a modern React user profile card component in ProfileCard.tsx"
    plan = orchestrator.plan_task_with_delegation(task, {"tech_stack": ["React", "TypeScript"]})

    assert plan.metadata.get("orchestration") is True
    assert any("ProfileCard.tsx" in (s.path or "") for s in plan.steps)
    assert "frontend" in plan.metadata.get("participating_agents", [])
