from abc import ABC, abstractmethod
from typing import Any, Dict
from kodra.models.plan import ExecutionPlan, PlanStep


class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g. 'mock', 'openai', 'anthropic', 'gemini', 'ollama')."""
        pass

    @abstractmethod
    def generate_plan(self, task: str, context: Dict[str, Any]) -> ExecutionPlan:
        """Formulates a structured ExecutionPlan for the specified task and project context."""
        pass

    @abstractmethod
    def analyze_failure(
        self,
        task: str,
        step: PlanStep,
        error_output: str,
        context: Dict[str, Any],
    ) -> ExecutionPlan:
        """Analyzes step failure and creates a repair plan."""
        pass

    @abstractmethod
    def chat(self, message: str, context: Dict[str, Any]) -> str:
        """Conversational response aware of project context."""
        pass
