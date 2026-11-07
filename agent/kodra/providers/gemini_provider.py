import json
from typing import Any, Dict, Optional
import httpx
from kodra.models.plan import ExecutionPlan, PlanStep
from kodra.providers.base import BaseLLMProvider
from kodra.providers.parser import PLAN_SYSTEM_PROMPT, parse_plan_json


class GeminiProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
    ):
        self.api_key = api_key or ""
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    @property
    def name(self) -> str:
        return "gemini"

    def _call_api(self, prompt: str, system_prompt: str = PLAN_SYSTEM_PROMPT) -> str:
        if not self.api_key:
            raise ValueError("Gemini API key is missing. Set GEMINI_API_KEY or configure in Kodra settings.")

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
        }

        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

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
