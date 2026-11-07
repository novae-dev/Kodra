import re
from pathlib import Path
from typing import Optional
from kodra.models.plan import (
    ExecutionPlan,
    OperationType,
    PlanStatus,
    PlanStep,
    RiskLevel,
    StepStatus,
)
from kodra.engine.filesystem import FileSystemEngine


class SelfHealingEngine:
    def __init__(self, workspace_root: Path, fs: Optional[FileSystemEngine] = None):
        self.workspace_root = workspace_root.resolve()
        self.fs = fs or FileSystemEngine(self.workspace_root)

    def analyze_failure_and_create_repair_plan(
        self,
        original_plan: ExecutionPlan,
        failed_step: PlanStep,
        error_output: str,
    ) -> ExecutionPlan:
        """
        Analyzes the failure output from a step and formulates a structured repair plan.
        """
        repair_steps = []
        diagnosis = "Detected step execution failure."

        err = (error_output or "").strip()

        # Check for missing module error
        missing_module_match = re.search(r"ModuleNotFoundError:\s+No module named '([^']+)'", err)
        if missing_module_match:
            mod_name = missing_module_match.group(1)
            diagnosis = f"Missing Python dependency: '{mod_name}'."
            repair_steps.append(
                PlanStep(
                    title=f"Install missing package: {mod_name}",
                    description=f"Automated resolution for ModuleNotFoundError: '{mod_name}'",
                    operation=OperationType.RUN_COMMAND,
                    command=f"python -m pip install {mod_name}",
                    risk_level=RiskLevel.MEDIUM,
                    requires_approval=True,
                )
            )
            # Re-run the original command
            if failed_step.operation == OperationType.RUN_COMMAND and failed_step.command:
                repair_steps.append(
                    PlanStep(
                        title=f"Re-run command: {failed_step.title}",
                        description="Retry failed command after installing missing dependency.",
                        operation=OperationType.RUN_COMMAND,
                        command=failed_step.command,
                        risk_level=failed_step.risk_level,
                        requires_approval=True,
                    )
                )

        # Check for Python SyntaxError
        syntax_error_match = re.search(r'File "([^"]+)", line (\d+)', err)
        if "SyntaxError" in err and syntax_error_match:
            fpath = syntax_error_match.group(1)
            line_no = syntax_error_match.group(2)
            diagnosis = f"Syntax error detected in {fpath} at line {line_no}."
            try:
                # If relative or in workspace, read and attempt auto-fix or patch
                rel_path = str(Path(fpath).relative_to(self.workspace_root)).replace("\\", "/")
            except Exception:
                rel_path = failed_step.path or Path(fpath).name

            repair_steps.append(
                PlanStep(
                    title=f"Fix syntax error in {rel_path}",
                    description=f"Resolve syntax issue at line {line_no}: {err.splitlines()[-1]}",
                    operation=OperationType.MODIFY_FILE,
                    path=rel_path,
                    content=self.fs.read_file(rel_path) if self.fs.file_exists(rel_path) else failed_step.content,
                    risk_level=RiskLevel.MEDIUM,
                    requires_approval=True,
                )
            )

        # Check for Missing File / Directory
        missing_file_match = re.search(r"No such file or directory:\s*'([^']+)'", err)
        if missing_file_match:
            missing_target = missing_file_match.group(1)
            diagnosis = f"Missing file or directory: '{missing_target}'."
            repair_steps.append(
                PlanStep(
                    title=f"Create missing path: {missing_target}",
                    description=f"Create missing file or directory required by {failed_step.title}",
                    operation=OperationType.CREATE_FILE if "." in Path(missing_target).name else OperationType.CREATE_DIR,
                    path=missing_target,
                    content="",
                    risk_level=RiskLevel.LOW,
                    requires_approval=True,
                )
            )

        # Check for Pytest assertion failures
        if "FAILED" in err and "AssertionError" in err:
            diagnosis = "Test assertion failed. Code implementation requires adjustment to satisfy test assertions."
            repair_steps.append(
                PlanStep(
                    title=f"Patch implementation for test failure",
                    description=f"Adjust implementation to resolve: {err.splitlines()[-1]}",
                    operation=failed_step.operation,
                    path=failed_step.path,
                    content=failed_step.content,
                    command=failed_step.command,
                    risk_level=RiskLevel.MEDIUM,
                    requires_approval=True,
                )
            )

        # Generic fallback repair if specific patterns didn't match
        if not repair_steps:
            diagnosis = f"Execution failed on step '{failed_step.title}'."
            repair_steps.append(
                PlanStep(
                    title=f"Retry corrected step: {failed_step.title}",
                    description=f"Corrected execution addressing error: {err[:120]}...",
                    operation=failed_step.operation,
                    path=failed_step.path,
                    content=failed_step.content,
                    command=failed_step.command,
                    risk_level=failed_step.risk_level,
                    requires_approval=True,
                )
            )

        return ExecutionPlan(
            task=f"Repair: {original_plan.task}",
            summary=f"Auto-repair plan addressing failure: {diagnosis}",
            steps=repair_steps,
            status=PlanStatus.DRAFT,
            metadata={
                "is_repair": True,
                "original_plan_id": original_plan.id,
                "failed_step_id": failed_step.id,
                "diagnosis": diagnosis,
                "error_snippet": err[:500],
            },
        )
