import difflib
from pathlib import Path
from typing import List, Optional
from kodra.security.policy import SecurityPolicy


class FileSystemEngine:
    def __init__(self, workspace_root: Path, policy: Optional[SecurityPolicy] = None):
        self.workspace_root = workspace_root.resolve()
        self.policy = policy or SecurityPolicy(self.workspace_root)

    def resolve_safe(self, rel_path: str) -> Path:
        return self.policy.sanitize_path(rel_path)

    def create_directory(self, rel_path: str) -> Path:
        target = self.resolve_safe(rel_path)
        target.mkdir(parents=True, exist_ok=True)
        return target

    def create_file(self, rel_path: str, content: str = "") -> Path:
        target = self.resolve_safe(rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def modify_file(self, rel_path: str, content: str) -> Path:
        target = self.resolve_safe(rel_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return target

    def delete_file(self, rel_path: str) -> bool:
        target = self.resolve_safe(rel_path)
        if target.exists() and target.is_file():
            target.unlink()
            return True
        elif target.exists() and target.is_dir():
            # Only remove directory if empty for safety
            target.rmdir()
            return True
        return False

    def read_file(self, rel_path: str) -> str:
        target = self.resolve_safe(rel_path)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {rel_path}")
        return target.read_text(encoding="utf-8")

    def file_exists(self, rel_path: str) -> bool:
        try:
            target = self.resolve_safe(rel_path)
            return target.exists()
        except Exception:
            return False

    def get_diff(self, rel_path: str, new_content: str) -> str:
        old_content = ""
        if self.file_exists(rel_path):
            old_content = self.read_file(rel_path)
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{rel_path}",
            tofile=f"b/{rel_path}",
        )
        return "".join(diff)

    def list_files(self, limit: int = 500) -> List[str]:
        results: List[str] = []
        ignored_names = {
            "node_modules",
            ".git",
            ".venv",
            "venv",
            "dist",
            "build",
            "__pycache__",
            ".pytest_cache",
            ".next",
            "coverage",
        }

        for path in self.workspace_root.rglob("*"):
            if any(part in ignored_names for part in path.parts):
                continue
            if path.is_file():
                rel = str(path.relative_to(self.workspace_root)).replace("\\", "/")
                results.append(rel)
                if len(results) >= limit:
                    break

        results.sort()
        return results
