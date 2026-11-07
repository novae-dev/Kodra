import os
import re
from pathlib import Path
from typing import List, Optional, Tuple
from kodra.models.plan import ExecutionPlan, PlanStep, OperationType, RiskLevel


class SecurityViolation(Exception):
    """Raised when an operation violates workspace or command security policies."""
    pass


BLOCKED_COMMAND_PATTERNS = [
    r"\brm\s+-[rf]{1,2}\s+(/|~|\$HOME)",
    r"\brmdir\s+/[sq]\s+[a-zA-Z]:\\",
    r"\bdel\s+/[sqfa]\s+[a-zA-Z]:\\",
    r"\bformat\s+[a-zA-Z]:",
    r"\bmkfs\b",
    r"\bdd\s+if=",
    r":\(\)\s*\{\s*:\|:&\s*\};:",  # Fork bomb
    r"\bcurl\b.*\|\s*(bash|sh|cmd|powershell)\b",
    r"\bwget\b.*\|\s*(bash|sh|cmd|powershell)\b",
    r"\bshutdown\b",
    r"\breboot\b",
]

SENSITIVE_FILES = {
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
}

BLOCKED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
}


class SecurityPolicy:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    def sanitize_path(self, relative_path: str | Path) -> Path:
        """
        Ensures a path resolves strictly inside workspace_root and does not traverse out.
        Returns the resolved Path object.
        """
        if not relative_path:
            raise SecurityViolation("Empty path provided")

        path_str = str(relative_path).strip()

        # Check for obvious traversal sequences
        if ".." in path_str.replace("\\", "/").split("/"):
            raise SecurityViolation(f"Path traversal detected in '{path_str}'")

        target = (self.workspace_root / path_str).resolve()

        try:
            target.relative_to(self.workspace_root)
        except ValueError:
            raise SecurityViolation(f"Path '{path_str}' escapes workspace boundary '{self.workspace_root}'")

        # Check blocked directory segments
        rel_parts = target.relative_to(self.workspace_root).parts
        for part in rel_parts:
            if part in BLOCKED_DIRECTORIES:
                raise SecurityViolation(f"Access to protected directory '{part}' is blocked")

        return target

    def validate_command(self, command: str) -> Tuple[bool, Optional[str], RiskLevel]:
        """
        Validates command string against dangerous shell patterns.
        Returns (is_allowed, reason, risk_level).
        """
        cmd = command.strip()
        if not cmd:
            return False, "Command cannot be empty", RiskLevel.HIGH

        for pattern in BLOCKED_COMMAND_PATTERNS:
            if re.search(pattern, cmd, re.IGNORECASE):
                return False, f"Command matches blocked dangerous pattern: {pattern}", RiskLevel.HIGH

        # Analyze risk level
        low_risk_prefixes = ("pytest", "npm test", "npm run", "python -m pytest", "git status", "git diff", "dir", "ls", "echo")
        if any(cmd.lower().startswith(prefix) for prefix in low_risk_prefixes):
            return True, None, RiskLevel.LOW

        return True, None, RiskLevel.HIGH

    def validate_step(self, step: PlanStep) -> List[str]:
        """
        Validates a single plan step against policies. Returns list of violation messages.
        """
        violations: List[str] = []

        if step.operation in (
            OperationType.CREATE_FILE,
            OperationType.MODIFY_FILE,
            OperationType.DELETE_FILE,
            OperationType.CREATE_DIR,
        ):
            if not step.path:
                violations.append(f"Step '{step.title}': Path must be provided for {step.operation}")
            else:
                try:
                    self.sanitize_path(step.path)
                except SecurityViolation as exc:
                    violations.append(f"Step '{step.title}': {str(exc)}")

            if step.operation == OperationType.DELETE_FILE:
                step.risk_level = RiskLevel.HIGH
                step.requires_approval = True

            filename = Path(step.path or "").name
            if filename in SENSITIVE_FILES and step.operation in (OperationType.MODIFY_FILE, OperationType.DELETE_FILE):
                step.risk_level = RiskLevel.HIGH
                step.requires_approval = True

        elif step.operation == OperationType.RUN_COMMAND:
            if not step.command:
                violations.append(f"Step '{step.title}': Command cannot be empty for run_command")
            else:
                allowed, reason, risk = self.validate_command(step.command)
                if not allowed:
                    violations.append(f"Step '{step.title}': {reason}")
                step.risk_level = risk
                # All shell commands require approval by default for safety
                step.requires_approval = True

        return violations

    def validate_plan(self, plan: ExecutionPlan) -> Tuple[bool, List[str]]:
        """
        Validates an entire execution plan. Returns (is_valid, violations).
        """
        all_violations: List[str] = []
        if not plan.steps:
            all_violations.append("Plan must contain at least one step")

        for step in plan.steps:
            step_violations = self.validate_step(step)
            all_violations.extend(step_violations)

        is_valid = len(all_violations) == 0
        return is_valid, all_violations
