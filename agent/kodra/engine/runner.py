import time
from pathlib import Path
from typing import List, Optional, Set
from kodra.models.plan import (
    ExecutionPlan,
    ExecutionResult,
    OperationType,
    PlanStatus,
    PlanStep,
    StepResult,
    StepStatus,
)
from kodra.security.policy import SecurityPolicy, SecurityViolation
from kodra.engine.filesystem import FileSystemEngine
from kodra.engine.executor import CommandExecutor


class PlanRunner:
    def __init__(
        self,
        workspace_root: Path,
        fs: Optional[FileSystemEngine] = None,
        executor: Optional[CommandExecutor] = None,
        policy: Optional[SecurityPolicy] = None,
    ):
        self.workspace_root = workspace_root.resolve()
        self.policy = policy or SecurityPolicy(self.workspace_root)
        self.fs = fs or FileSystemEngine(self.workspace_root, self.policy)
        self.executor = executor or CommandExecutor(self.workspace_root)

    def execute_step(self, step: PlanStep) -> StepResult:
        start_time = time.perf_counter()
        step.status = StepStatus.RUNNING

        try:
            # Re-validate security policy on the step before running
            violations = self.policy.validate_step(step)
            if violations:
                step.status = StepStatus.FAILED
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                return StepResult(
                    step_id=step.id,
                    status=StepStatus.FAILED,
                    error="; ".join(violations),
                    duration_ms=round(duration_ms, 2),
                )

            if step.operation == OperationType.CREATE_FILE:
                target = self.fs.create_file(step.path or "", step.content or "")
                step.status = StepStatus.SUCCESS
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                return StepResult(
                    step_id=step.id,
                    status=StepStatus.SUCCESS,
                    output=f"Created file: {step.path} ({len(step.content or '')} chars)",
                    duration_ms=round(duration_ms, 2),
                )

            elif step.operation == OperationType.MODIFY_FILE:
                target = self.fs.modify_file(step.path or "", step.content or "")
                step.status = StepStatus.SUCCESS
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                return StepResult(
                    step_id=step.id,
                    status=StepStatus.SUCCESS,
                    output=f"Modified file: {step.path} ({len(step.content or '')} chars)",
                    duration_ms=round(duration_ms, 2),
                )

            elif step.operation == OperationType.CREATE_DIR:
                self.fs.create_directory(step.path or "")
                step.status = StepStatus.SUCCESS
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                return StepResult(
                    step_id=step.id,
                    status=StepStatus.SUCCESS,
                    output=f"Created directory: {step.path}",
                    duration_ms=round(duration_ms, 2),
                )

            elif step.operation == OperationType.DELETE_FILE:
                success = self.fs.delete_file(step.path or "")
                step.status = StepStatus.SUCCESS if success else StepStatus.FAILED
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                return StepResult(
                    step_id=step.id,
                    status=step.status,
                    output=f"Deleted file: {step.path}" if success else f"File not found to delete: {step.path}",
                    duration_ms=round(duration_ms, 2),
                )

            elif step.operation == OperationType.RUN_COMMAND:
                cmd_res = self.executor.execute(step.command or "")
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                if cmd_res.success:
                    step.status = StepStatus.SUCCESS
                    return StepResult(
                        step_id=step.id,
                        status=StepStatus.SUCCESS,
                        output=cmd_res.combined_output or "Command completed with exit code 0.",
                        exit_code=cmd_res.exit_code,
                        duration_ms=round(duration_ms, 2),
                    )
                else:
                    step.status = StepStatus.FAILED
                    err_msg = cmd_res.stderr or cmd_res.stdout or f"Command exited with code {cmd_res.exit_code}"
                    return StepResult(
                        step_id=step.id,
                        status=StepStatus.FAILED,
                        output=cmd_res.stdout,
                        error=err_msg,
                        exit_code=cmd_res.exit_code,
                        duration_ms=round(duration_ms, 2),
                    )

            else:
                step.status = StepStatus.FAILED
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                return StepResult(
                    step_id=step.id,
                    status=StepStatus.FAILED,
                    error=f"Unsupported operation type: {step.operation}",
                    duration_ms=round(duration_ms, 2),
                )

        except Exception as exc:
            step.status = StepStatus.FAILED
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return StepResult(
                step_id=step.id,
                status=StepStatus.FAILED,
                error=str(exc),
                duration_ms=round(duration_ms, 2),
            )

    def execute_plan(
        self,
        plan: ExecutionPlan,
        approved_step_ids: Optional[Set[str]] = None,
        auto_approve: bool = False,
    ) -> ExecutionResult:
        """
        Executes approved steps in the plan in order.
        Stops immediately on the first step failure to facilitate self-healing analysis.
        """
        is_valid, violations = self.policy.validate_plan(plan)
        if not is_valid:
            plan.status = PlanStatus.FAILED
            return ExecutionResult(
                plan_id=plan.id,
                success=False,
                summary="Plan failed validation policy",
                error="; ".join(violations),
            )

        plan.status = PlanStatus.EXECUTING
        results: List[StepResult] = []
        overall_success = True

        for step in plan.steps:
            # Check approval
            is_approved = (
                auto_approve
                or step.approved
                or (approved_step_ids is not None and step.id in approved_step_ids)
                or not step.requires_approval
            )

            if not is_approved:
                step.status = StepStatus.SKIPPED
                results.append(
                    StepResult(
                        step_id=step.id,
                        status=StepStatus.SKIPPED,
                        output="Step skipped: user approval required.",
                    )
                )
                continue

            # Mark step approved and execute
            step.approved = True
            res = self.execute_step(step)
            results.append(res)

            if res.status == StepStatus.FAILED:
                overall_success = False
                plan.status = PlanStatus.FAILED
                return ExecutionResult(
                    plan_id=plan.id,
                    success=False,
                    step_results=results,
                    summary=f"Execution halted: Step '{step.title}' failed.",
                    error=res.error or "Step execution failed",
                )

        plan.status = PlanStatus.COMPLETED if overall_success else PlanStatus.FAILED
        return ExecutionResult(
            plan_id=plan.id,
            success=overall_success,
            step_results=results,
            summary="All approved steps executed successfully.",
        )
