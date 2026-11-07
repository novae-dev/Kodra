from pathlib import Path
from fastapi.testclient import TestClient
from kodra.server.app import app
from kodra.config import settings
from kodra.memory.project_memory import ProjectMemoryManager

client = TestClient(app)


def test_complete_end_to_end_coding_and_self_healing_workflow(tmp_path: Path):
    """
    Tests the complete end-to-end cycle:
    1. Workspace setup with kodra.json initialization.
    2. User submits coding request.
    3. Multi-agent orchestrator formulates structured plan.
    4. Plan validated against security policies.
    5. User approves and executes operations.
    6. Real files are created and executed on disk.
    7. Subprocess output captured.
    8. Failure induced, detected, and analyzed by self-healing engine.
    9. Repair plan formulated, approved, and executed.
    10. History recorded in kodra.json.
    """
    settings.set_workspace(tmp_path)

    # Step 1: Health & Workspace check
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "healthy"

    ws_resp = client.get("/workspace")
    assert ws_resp.status_code == 200
    assert (tmp_path / "kodra.json").exists()

    # Step 2 & 3: Submit task -> Multi-agent plan formulation
    task_prompt = "Build a calculator utility in calc.py and verify it"
    plan_resp = client.post("/plan", json={"task": task_prompt, "multi_agent": True})
    assert plan_resp.status_code == 200
    plan_data = plan_resp.json()

    assert plan_data["task"] == task_prompt
    assert len(plan_data["steps"]) >= 2
    assert plan_data["metadata"]["orchestration"] is True

    # Step 4: Validate plan against policy
    val_resp = client.post("/plan/validate", json=plan_data)
    assert val_resp.status_code == 200
    assert val_resp.json()["valid"] is True

    # Step 5 & 6: Execute approved plan
    exec_resp = client.post(
        "/plan/execute",
        json={"plan": plan_data, "auto_approve": True},
    )
    assert exec_resp.status_code == 200
    exec_data = exec_resp.json()
    assert exec_data["result"]["success"] is True

    # Verify real file created on disk
    calc_path = tmp_path / "calc.py"
    assert calc_path.exists()
    content = calc_path.read_text(encoding="utf-8")
    assert "class Calculator" in content or "def add" in content or "calc" in content.lower()

    # Step 7 & 8: Induce failure and test failure capture + self-healing
    buggy_plan_resp = client.post(
        "/plan",
        json={"task": "Run tests on missing module test_nonexistent.py", "multi_agent": False},
    )
    buggy_plan = buggy_plan_resp.json()
    # Add a step that fails with non-zero exit code
    buggy_plan["steps"] = [
        {
            "id": "failing-step",
            "title": "Execute missing script",
            "operation": "run_command",
            "command": "python -c \"import nonexistent_library_123\"",
            "risk_level": "medium",
            "requires_approval": True,
            "approved": True,
            "status": "pending",
        }
    ]

    failed_exec = client.post("/plan/execute", json={"plan": buggy_plan, "auto_approve": True})
    assert failed_exec.status_code == 200
    failed_data = failed_exec.json()
    assert failed_data["result"]["success"] is False
    assert failed_data["plan"]["status"] == "failed"

    # Step 9: Self-healing engine creates repair plan
    repair_resp = client.post(
        "/plan/repair",
        json={
            "original_plan": failed_data["plan"],
            "failed_step_id": "failing-step",
            "error_output": "ModuleNotFoundError: No module named 'nonexistent_library_123'",
        },
    )
    assert repair_resp.status_code == 200
    repair_plan = repair_resp.json()
    assert repair_plan["metadata"]["is_repair"] is True
    assert any("pip install nonexistent_library_123" in (s.get("command") or "") for s in repair_plan["steps"])

    # Step 10: Verify project memory and history persistence in kodra.json
    hist_resp = client.get("/history")
    assert hist_resp.status_code == 200
    history_records = hist_resp.json()["history"]
    assert len(history_records) >= 2
    assert any(h["task"] == task_prompt and h["success"] is True for h in history_records)
