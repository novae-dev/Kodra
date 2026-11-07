import pytest
from kodra.models.plan import (
    ExecutionPlan,
    PlanStep,
    OperationType,
    RiskLevel,
    StepStatus,
    PlanStatus,
)
from kodra.engine.runner import PlanRunner


def test_plan_runner_full_execution(tmp_path):
    runner = PlanRunner(tmp_path)

    plan = ExecutionPlan(
        task="Create and test calculator",
        summary="Create calc.py and run it",
        steps=[
            PlanStep(
                id="s1",
                title="Create calc.py",
                operation=OperationType.CREATE_FILE,
                path="calc.py",
                content="print('Calc ok')",
                risk_level=RiskLevel.LOW,
                requires_approval=True,
            ),
            PlanStep(
                id="s2",
                title="Execute calc.py",
                operation=OperationType.RUN_COMMAND,
                command="python calc.py",
                risk_level=RiskLevel.LOW,
                requires_approval=True,
            ),
        ],
    )

    res = runner.execute_plan(plan, auto_approve=True)
    assert res.success is True
    assert plan.status == PlanStatus.COMPLETED
    assert len(res.step_results) == 2
    assert res.step_results[0].status == StepStatus.SUCCESS
    assert res.step_results[1].status == StepStatus.SUCCESS
    assert "Calc ok" in res.step_results[1].output
    assert (tmp_path / "calc.py").exists()


def test_plan_runner_requires_approval(tmp_path):
    runner = PlanRunner(tmp_path)

    plan = ExecutionPlan(
        task="Unapproved task",
        summary="Plan with unapproved step",
        steps=[
            PlanStep(
                id="step-1",
                title="Delete critical file",
                operation=OperationType.DELETE_FILE,
                path="somefile.txt",
                risk_level=RiskLevel.HIGH,
                requires_approval=True,
                approved=False,
            )
        ],
    )

    res = runner.execute_plan(plan, auto_approve=False)
    # The step should be skipped due to missing approval
    assert res.step_results[0].status == StepStatus.SKIPPED


def test_plan_runner_failure_halting(tmp_path):
    runner = PlanRunner(tmp_path)

    plan = ExecutionPlan(
        task="Failing task",
        summary="Plan with failing command",
        steps=[
            PlanStep(
                id="s1",
                title="Failing script",
                operation=OperationType.RUN_COMMAND,
                command="python -c \"raise ValueError('Crash')\"",
                risk_level=RiskLevel.LOW,
            ),
            PlanStep(
                id="s2",
                title="Should not run",
                operation=OperationType.CREATE_FILE,
                path="never_created.txt",
                content="none",
            ),
        ],
    )

    res = runner.execute_plan(plan, auto_approve=True)
    assert not res.success
    assert plan.status == PlanStatus.FAILED
    assert len(res.step_results) == 1
    assert res.step_results[0].status == StepStatus.FAILED
    assert not (tmp_path / "never_created.txt").exists()
