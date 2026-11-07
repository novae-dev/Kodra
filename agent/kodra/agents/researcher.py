from pathlib import Path
from typing import Any, Dict, List
from kodra.models.agent import AgentRole, AgentResponse
from kodra.agents.base import BaseAgent
from kodra.engine.filesystem import FileSystemEngine


class ResearchAgent(BaseAgent):
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.fs = FileSystemEngine(self.workspace_root)

    @property
    def role(self) -> AgentRole:
        return AgentRole.RESEARCHER

    @property
    def name(self) -> str:
        return "Kodra Research Agent"

    @property
    def description(self) -> str:
        return "Inspects workspace context, file structure, existing patterns, and dependencies."

    def process(self, task: str, context: Dict[str, Any]) -> AgentResponse:
        files = self.fs.list_files(limit=100)
        findings: List[str] = []

        # Analyze language and structure
        has_python = any(f.endswith(".py") for f in files)
        has_ts = any(f.endswith((".ts", ".tsx")) for f in files)
        has_go = any(f.endswith(".go") for f in files)

        findings.append(f"Workspace contains {len(files)} indexed files.")
        if has_python:
            findings.append("Python environment detected.")
        if has_ts:
            findings.append("TypeScript / React environment detected.")
        if has_go:
            findings.append("Go environment detected.")

        # Check if task mentions specific files
        mentioned_files = [f for f in files if Path(f).name.lower() in task.lower()]
        if mentioned_files:
            findings.append(f"Target files directly relevant: {', '.join(mentioned_files)}")

        return AgentResponse(
            role=self.role,
            summary=f"Contextual research complete. Indexed {len(files)} files; identified relevant patterns.",
            analysis="Workspace analyzed for appropriate delegation and architectural patterns.",
            findings=findings,
            metadata={"indexed_files_count": len(files), "mentioned_files": mentioned_files},
        )
