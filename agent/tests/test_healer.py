from kodra.models.plan import ExecutionPlan, PlanStep, OperationType, PlanStatus
from kodra.engine.healer import SelfHealingEngine


def test_healer_module_not_found(tmp_path):
    healer = SelfHealingEngine(tmp_path)
    original_plan = ExecutionPlan(
        task="Run server",
        summary="Start server",
        steps=[],
    )
    failed_step = PlanStep(
        id="s1",
        title="Start API",
        operation=OperationType.RUN_COMMAND,
        command="python app.py",
    )
    error_output = "Traceback (most recent call last):\nModuleNotFoundError: No module named 'fastapi'"

    repair_plan = healer.analyze_failure_and_create_repair_plan(
        original_plan=original_plan,
        failed_step=failed_step,
        error_output=error_output,
    )

    assert repair_plan.metadata.get("is_repair") is True
    assert "fastapi" in repair_plan.metadata.get("diagnosis", "").lower()
    assert any("pip install fastapi" in (s.command or "") for s in repair_plan.steps)


def test_healer_syntax_error(tmp_path):
    healer = SelfHealingEngine(tmp_path)
    (tmp_path / "broken.py").write_text("def foo(\n", encoding="utf-8")
    original_plan = ExecutionPlan(task="Run code", summary="Run code", steps=[])
    failed_step = PlanStep(
        id="s1",
        title="Execute broken code",
        operation=OperationType.RUN_COMMAND,
        command="python broken.py",
        path="broken.py",
    )
    error_output = f'File "{tmp_path / "broken.py"}", line 1\nSyntaxError: was never closed'

    repair_plan = healer.analyze_failure_and_create_repair_plan(
        original_plan=original_plan,
        failed_step=failed_step,
        error_output=error_output,
    )

    assert repair_plan.metadata.get("is_repair") is True
    assert any(s.path == "broken.py" for s in repair_plan.steps)
