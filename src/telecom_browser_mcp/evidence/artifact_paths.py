from __future__ import annotations

from pathlib import Path


class ArtifactPaths:
    def __init__(self, base_dir: str) -> None:
        self.base = Path(base_dir)
        self.screenshots = self.base / "screenshots"
        self.logs = self.base / "logs"
        self.runtime = self.base / "runtime"
        self.screenshots.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        self.runtime.mkdir(parents=True, exist_ok=True)

    def screenshot_path(self, name: str) -> Path:
        return self.screenshots / f"{name}.png"

    def log_path(self, name: str) -> Path:
        return self.logs / f"{name}.json"

    def runtime_path(self, name: str) -> Path:
        return self.runtime / f"{name}.json"
