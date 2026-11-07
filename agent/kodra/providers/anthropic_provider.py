import json
from typing import Any, Dict, Optional
import httpx
from kodra.models.plan import ExecutionPlan, PlanStep
from kodra.providers.base import BaseLLMProvider
from kodra.providers.parser import PLAN_SYSTEM_PROMPT, parse_plan_json


class AnthropicProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
    ):
        self.api_key = api_key or ""
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"

    @property
    def name(self) -> str:
        return "anthropic"

    def _call_api(self, prompt: str, system_prompt: str = PLAN_SYSTEM_PROMPT) -> str:
        if not self.api_key:
            raise ValueError("Anthropic API key is missing. Set ANTHROPIC_API_KEY or configure in Kodra settings.")

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }

        with httpx.Client(timeout=60.0) as client:
            resp = client.post(f"{self.base_url}/messages", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["content"][0]["text"]

    def generate_plan(self, task: str, context: Dict[str, Any]) -> ExecutionPlan:
        ctx_prompt = f"Workspace files: {context.get('project_files', [])[:50]}\nProject stack: {context.get('tech_stack', [])}"
        content = self._call_api(f"Task: {task}\nContext:\n{ctx_prompt}")
        return parse_plan_json(content, task)

    def analyze_failure(
        self,
        task: str,
        step: PlanStep,
        error_output: str,
        context: Dict[str, Any],
    ) -> ExecutionPlan:
        prompt = (
            f"A step failed in the task '{task}'.\n"
            f"Failed Step: {step.title} (Operation: {step.operation}, Command: {step.command}, Path: {step.path})\n"
            f"Error Output:\n{error_output}\n"
            f"Generate a repair ExecutionPlan containing only the steps to fix and retry."
        )
        content = self._call_api(prompt)
        plan = parse_plan_json(content, f"Repair: {task}")
        plan.metadata["is_repair"] = True
        return plan

    def chat(self, message: str, context: Dict[str, Any]) -> str:
        return self._call_api(
            f"Context: {context}\nUser: {message}",
            system_prompt="You are Kodra, an autonomous AI software engineering pair programmer.",
        )
