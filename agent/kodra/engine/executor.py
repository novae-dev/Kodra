import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional, Tuple


class CommandExecutionResult:
    def __init__(
        self,
        command: str,
        exit_code: int,
        stdout: str,
        stderr: str,
        duration_ms: float,
        timed_out: bool = False,
    ):
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms
        self.timed_out = timed_out

    @property
    def success(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    @property
    def combined_output(self) -> str:
        out = self.stdout.strip()
        err = self.stderr.strip()
        if out and err:
            return f"{out}\n{err}"
        return out or err or ""


class CommandExecutor:
    def __init__(self, workspace_root: Path, default_timeout: int = 45):
        self.workspace_root = workspace_root.resolve()
        self.default_timeout = default_timeout

    def _sanitize_output(self, text: str) -> str:
        """Strips likely secrets and tokens from output."""
        sensitive_keys = [
            os.environ.get("OPENAI_API_KEY"),
            os.environ.get("ANTHROPIC_API_KEY"),
            os.environ.get("GEMINI_API_KEY"),
            os.environ.get("GROQ_API_KEY"),
        ]
        sanitized = text
        for secret in sensitive_keys:
            if secret and len(secret) > 8:
                sanitized = sanitized.replace(secret, "[REDACTED_SECRET]")
        return sanitized

    def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        env_overrides: Optional[Dict[str, str]] = None,
    ) -> CommandExecutionResult:
        """
        Executes a command inside the workspace_root.
        Captures stdout, stderr, exit code, and execution time.
        """
        timeout = timeout or self.default_timeout
        start_time = time.perf_counter()

        env = os.environ.copy()
        if env_overrides:
            env.update(env_overrides)

        # On Windows, wrap in powershell or cmd if shell=True
        use_shell = True

        try:
            process = subprocess.Popen(
                command,
                cwd=str(self.workspace_root),
                shell=use_shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                return CommandExecutionResult(
                    command=command,
                    exit_code=process.returncode,
                    stdout=self._sanitize_output(stdout),
                    stderr=self._sanitize_output(stderr),
                    duration_ms=round(duration_ms, 2),
                    timed_out=False,
                )
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                duration_ms = (time.perf_counter() - start_time) * 1000.0
                return CommandExecutionResult(
                    command=command,
                    exit_code=-1,
                    stdout=self._sanitize_output(stdout),
                    stderr=f"Command timed out after {timeout} seconds.\n{self._sanitize_output(stderr)}",
                    duration_ms=round(duration_ms, 2),
                    timed_out=True,
                )

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            return CommandExecutionResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=str(exc),
                duration_ms=round(duration_ms, 2),
                timed_out=False,
            )
