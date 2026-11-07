from abc import ABC, abstractmethod
from typing import Any, Dict
from kodra.models.agent import AgentRole, AgentResponse


class BaseAgent(ABC):
    @property
    @abstractmethod
    def role(self) -> AgentRole:
        """Role identifier of the agent."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Display name of the specialist agent."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Agent capability description."""
        pass

    @abstractmethod
    def process(self, task: str, context: Dict[str, Any]) -> AgentResponse:
        """Executes agent-specific domain task and returns an AgentResponse."""
        pass
