import json
import re
from typing import Any, Dict
from kodra.models.plan import ExecutionPlan, PlanStep, OperationType, RiskLevel, PlanStatus


PLAN_SYSTEM_PROMPT = """You are Kodra, an autonomous AI coding agent.
Principle: LLM PLANS. PYTHON/GO EXECUTES.

You must decompose the user's software engineering task into a structured ExecutionPlan.
Return ONLY a valid JSON object matching this schema:
{
  "task": "User task description",
  "summary": "Concise 1-2 sentence overview of the plan",
  "steps": [
    {
      "id": "step-1",
      "title": "Short title of this action",
      "description": "Details of what this step does",
      "operation": "create_file" | "modify_file" | "delete_file" | "create_dir" | "run_command",
      "path": "relative/path/to/file.ext" (or null if run_command),
      "content": "Full source code content" (or null if not creating/modifying file),
      "command": "terminal command to run" (or null if not run_command),
      "risk_level": "low" | "medium" | "high",
      "requires_approval": true | false
    }
  ]
}

Security & Architecture Rules:
1. All file paths MUST be relative to project workspace root. No absolute paths or '..' path traversal.
2. Never delete files unless explicitly instructed by the user.
3. Every terminal command requires approval (requires_approval: true).
4. Do not include markdown code block formatting around the JSON output, or output only valid JSON.
"""


def parse_plan_json(response_text: str, fallback_task: str) -> ExecutionPlan:
    """
    Parses LLM response into a validated ExecutionPlan.
    Handles responses wrapped in ```json ... ``` blocks.
    """
    text = response_text.strip()

    # Strip code block fences if present
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    else:
        # Search for first { and last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start : end + 1]

    try:
        data = json.loads(text)
        steps_raw = data.get("steps", [])
        steps = []
        for idx, s in enumerate(steps_raw, 1):
            op = s.get("operation", "create_file")
            try:
                op_enum = OperationType(op)
            except ValueError:
                op_enum = OperationType.CREATE_FILE

            risk = s.get("risk_level", "low")
            try:
                risk_enum = RiskLevel(risk)
            except ValueError:
                risk_enum = RiskLevel.LOW

            steps.append(
                PlanStep(
                    id=s.get("id") or f"step-{idx}",
                    title=s.get("title", f"Step {idx}"),
                    description=s.get("description", ""),
                    operation=op_enum,
                    path=s.get("path"),
                    content=s.get("content"),
                    command=s.get("command"),
                    risk_level=risk_enum,
                    requires_approval=s.get("requires_approval", True),
                )
            )

        return ExecutionPlan(
            task=data.get("task", fallback_task),
            summary=data.get("summary", f"Plan for: {fallback_task}"),
            steps=steps,
            status=PlanStatus.DRAFT,
        )

    except Exception as exc:
        # Fallback to single draft step if parsing fails
        return ExecutionPlan(
            task=fallback_task,
            summary=f"Automated draft plan for: {fallback_task}",
            steps=[
                PlanStep(
                    title="Execute Task",
                    description=f"Raw plan output: {text[:200]}...",
                    operation=OperationType.CREATE_FILE,
                    path="kodra_output.txt",
                    content=response_text,
                    risk_level=RiskLevel.LOW,
                    requires_approval=True,
                )
            ],
            status=PlanStatus.DRAFT,
            metadata={"parse_warning": str(exc)},
        )
