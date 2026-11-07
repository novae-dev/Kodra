import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from kodra.models.project import KodraProjectConfig


class ProjectMemoryManager:
    CONFIG_FILENAME = "kodra.json"

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()
        self.config_file = self.workspace_root / self.CONFIG_FILENAME
        self._config: Optional[KodraProjectConfig] = None
        self.load_or_initialize()

    def detect_tech_stack(self) -> List[str]:
        stack = []
        if (self.workspace_root / "package.json").exists():
            stack.append("Node.js")
            try:
                pkg_data = json.loads((self.workspace_root / "package.json").read_text(encoding="utf-8"))
                deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                if "react" in deps:
                    stack.append("React")
                if "typescript" in deps:
                    stack.append("TypeScript")
                if "vite" in deps:
                    stack.append("Vite")
                if "next" in deps:
                    stack.append("Next.js")
            except Exception:
                pass

        if (self.workspace_root / "requirements.txt").exists() or (self.workspace_root / "pyproject.toml").exists() or any(self.workspace_root.glob("*.py")):
            stack.append("Python")
            if (self.workspace_root / "agent").exists():
                stack.append("FastAPI")

        if (self.workspace_root / "go.mod").exists():
            stack.append("Go")

        return list(dict.fromkeys(stack))

    def load_or_initialize(self) -> KodraProjectConfig:
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text(encoding="utf-8"))
                self._config = KodraProjectConfig(**data)
                return self._config
            except Exception:
                pass

        # Initialize fresh config
        detected_stack = self.detect_tech_stack()
        self._config = KodraProjectConfig(
            name=self.workspace_root.name or "Kodra Project",
            workspace_root=str(self.workspace_root),
            tech_stack=detected_stack,
            guidelines=[
                "Maintain clean modular code architecture",
                "Ensure execution safety within workspace boundary",
                "Write automated unit tests for new features",
            ],
            memory={
                "architecture_style": "modular",
                "execution_engine": "Python/Go",
                "plan_approval_required": True,
            },
            history=[],
        )
        self.save()
        return self._config

    def save(self) -> None:
        if not self._config:
            return
        self._config.touch()
        self.config_file.write_text(
            self._config.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def get_config(self) -> KodraProjectConfig:
        if not self._config:
            return self.load_or_initialize()
        return self._config

    def record_task_history(
        self,
        task: str,
        plan_id: str,
        success: bool,
        summary: str,
        files_modified: List[str],
    ) -> None:
        config = self.get_config()
        record = {
            "task": task,
            "plan_id": plan_id,
            "success": success,
            "summary": summary,
            "files_modified": files_modified,
            "timestamp": config.updated_at,
        }
        config.history.insert(0, record)
        # Keep latest 50 history entries
        config.history = config.history[:50]
        self.save()

    def add_guideline(self, guideline: str) -> None:
        config = self.get_config()
        if guideline not in config.guidelines:
            config.guidelines.append(guideline)
            self.save()

    def set_memory(self, key: str, value: Any) -> None:
        config = self.get_config()
        config.memory[key] = value
        self.save()

    def get_context_for_prompt(self) -> Dict[str, Any]:
        config = self.get_config()
        return {
            "project_name": config.name,
            "tech_stack": config.tech_stack,
            "guidelines": config.guidelines,
            "key_memory": config.memory,
            "recent_tasks": [h["task"] for h in config.history[:3]],
        }
