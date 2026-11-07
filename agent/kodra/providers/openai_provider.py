import json
from typing import Any, Dict, Optional
import httpx
from kodra.models.plan import ExecutionPlan, PlanStep
from kodra.providers.base import BaseLLMProvider
from kodra.providers.parser import PLAN_SYSTEM_PROMPT, parse_plan_json


class OpenAIProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        base_url: str = "https://api.openai.com/v1",
    ):
        self.api_key = api_key or ""
        self.model = model
        self.base_url = base_url.rstrip("/")

    @property
    def name(self) -> str:
        return "openai"

    def _call_api(self, messages: list) -> str:
        if not self.api_key:
            raise ValueError("OpenAI API key is missing. Set OPENAI_API_KEY or configure in Kodra settings.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }

        with httpx.Client(timeout=60.0) as client:
            resp = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def generate_plan(self, task: str, context: Dict[str, Any]) -> ExecutionPlan:
        ctx_prompt = f"Workspace files: {context.get('project_files', [])[:50]}\nProject stack: {context.get('tech_stack', [])}"
        messages = [
            {"role": "system", "content": PLAN_SYSTEM_PROMPT},
            {"role": "user", "content": f"Task: {task}\nContext:\n{ctx_prompt}"},
        ]
        content = self._call_api(messages)
        return parse_plan_json(content, task)

    def analyze_failure(
        self,
        task: str,
        step: PlanStep,
        error_output: str,
        context: Dict[str, Any],
    ) -> ExecutionPlan:
        messages = [
            {"role": "system", "content": PLAN_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"A step failed in the task '{task}'.\n"
                    f"Failed Step: {step.title} (Operation: {step.operation}, Command: {step.command}, Path: {step.path})\n"
                    f"Error Output:\n{error_output}\n"
                    f"Generate a repair ExecutionPlan containing only the steps to fix and retry."
                ),
            },
        ]
        content = self._call_api(messages)
        plan = parse_plan_json(content, f"Repair: {task}")
        plan.metadata["is_repair"] = True
        return plan

    def chat(self, message: str, context: Dict[str, Any]) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are Kodra, an autonomous AI software engineering pair programmer.",
            },
            {"role": "user", "content": f"Context: {context}\nUser: {message}"},
        ]
        return self._call_api(messages)
