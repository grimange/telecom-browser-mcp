from __future__ import annotations

from telecom_browser_mcp.models.artifact import ArtifactRef


class ScreenshotWriter:
    async def capture(self, session, path: str, label: str) -> ArtifactRef | None:
        if session.driver is None:
            return None
        captured = await session.driver.screenshot(path)
        if not captured:
            return None
        return ArtifactRef(type="screenshot", label=label, path=path, redacted=True)
