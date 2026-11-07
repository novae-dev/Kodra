import os
import pytest
from kodra.engine.executor import CommandExecutor


def test_command_execution(tmp_path):
    executor = CommandExecutor(tmp_path)
    res = executor.execute("echo Hello Kodra")
    assert res.success
    assert "Hello Kodra" in res.combined_output
    assert res.exit_code == 0
    assert res.duration_ms > 0


def test_command_timeout(tmp_path):
    executor = CommandExecutor(tmp_path, default_timeout=1)
    # On Windows powershell / python, sleep for 3 seconds
    res = executor.execute('python -c "import time; time.sleep(3)"', timeout=1)
    assert not res.success
    assert res.timed_out
    assert "timed out" in res.stderr.lower()


def test_secret_redaction(tmp_path, monkeypatch):
    test_secret = "sk-super-secret-12345678"
    monkeypatch.setenv("OPENAI_API_KEY", test_secret)
    executor = CommandExecutor(tmp_path)
    res = executor.execute(f"echo {test_secret}")
    assert test_secret not in res.stdout
    assert "[REDACTED_SECRET]" in res.stdout
