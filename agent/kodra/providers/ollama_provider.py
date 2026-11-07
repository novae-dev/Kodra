import json
from typing import Any, Dict, Optional
import httpx
from kodra.models.plan import ExecutionPlan, PlanStep
from kodra.providers.base import BaseLLMProvider
from kodra.providers.parser import PLAN_SYSTEM_PROMPT, parse_plan_json


class OllamaProvider(BaseLLMProvider):
    def __init__(
        self,
        host: str = "http://localhost:11434",
        model: str = "llama3",
    ):
        self.host = host.rstrip("/")
        self.model = model

    @property
    def name(self) -> str:
        return "ollama"

    def _call_api(self, prompt: str, system_prompt: str = PLAN_SYSTEM_PROMPT) -> str:
        url = f"{self.host}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "format": "json",
        }

        with httpx.Client(timeout=90.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")

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
