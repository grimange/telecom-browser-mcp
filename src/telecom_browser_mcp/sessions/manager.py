from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from telecom_browser_mcp.models.enums import BrowserSessionState
from telecom_browser_mcp.sessions.browser_session import BrowserSession


@dataclass
class SessionManager:
    artifact_root: Path
    sessions: dict[str, BrowserSession] = field(default_factory=dict)

    def create_session(self, adapter_name: str, adapter_version: str, headless: bool) -> BrowserSession:
        run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        session_id = f"sess_{uuid4().hex[:10]}"
        artifacts_dir = self.artifact_root / datetime.now(timezone.utc).strftime("%Y-%m-%d") / run_id
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        session = BrowserSession(
            session_id=session_id,
            run_id=run_id,
            adapter_name=adapter_name,
            adapter_version=adapter_version,
            artifacts_dir=str(artifacts_dir),
            headless=headless,
        )
        self.sessions[session_id] = session
        return session

    def list_sessions(self) -> list[BrowserSession]:
        return list(self.sessions.values())

    def get(self, session_id: str) -> BrowserSession | None:
        return self.sessions.get(session_id)

    async def close_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if session is None:
            return False
        session.status = BrowserSessionState.CLOSING
        if session.driver is not None:
            await session.driver.close()
        session.status = BrowserSessionState.CLOSED
        return True

    async def reset_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if session is None:
            return False
        if session.driver is None:
            return True
        await session.driver.reset(session.base_url)
        session.touch()
        return True
