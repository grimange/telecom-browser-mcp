from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from telecom_browser_mcp.adapters.base import AdapterBase
from telecom_browser_mcp.browser.manager import BrowserHandle, BrowserManager
from telecom_browser_mcp.models.session import SessionModel, SessionSummary


@dataclass
class SessionRuntime:
    model: SessionModel
    adapter: AdapterBase
    browser: BrowserHandle
    created_at: datetime
    operation_lock: asyncio.Lock


class SessionManager:
    def __init__(self, artifact_root: str = "artifacts") -> None:
        self._artifact_root = Path(artifact_root)
        self._artifact_root.mkdir(parents=True, exist_ok=True)
        self._browser_manager = BrowserManager()
        self._sessions: dict[str, SessionRuntime] = {}

    async def create(self, target_url: str, adapter: AdapterBase, headless: bool = True) -> SessionRuntime:
        session_id = str(uuid4())
        root = self._artifact_root / session_id
        root.mkdir(parents=True, exist_ok=True)
        browser_handle = await self._browser_manager.open(target_url=target_url, headless=headless)
        model = SessionModel(
            session_id=session_id,
            adapter_id=adapter.adapter_id,
            adapter_version=adapter.adapter_version,
            capabilities=adapter.capabilities,
            target_url=target_url,
            lifecycle_state="ready" if browser_handle.browser_open else "degraded",
            artifact_root=str(root),
            browser_launch_error=browser_handle.launch_error,
            browser_launch_error_classification=browser_handle.launch_error_classification,
        )
        model.telecom.browser_open = browser_handle.browser_open
        model.telecom.adapter_attached = True
        runtime = SessionRuntime(
            model=model,
            adapter=adapter,
            browser=browser_handle,
            created_at=datetime.now(UTC),
            operation_lock=asyncio.Lock(),
        )
        self._sessions[session_id] = runtime
        return runtime

    def list(self) -> list[SessionSummary]:
        out: list[SessionSummary] = []
        for runtime in self._sessions.values():
            s = runtime.model
            out.append(
                SessionSummary(
                    session_id=s.session_id,
                    adapter_id=s.adapter_id,
                    lifecycle_state=s.lifecycle_state,
                    target_url=s.target_url,
                    registration_state=s.telecom.registration_state,
                    incoming_call_state=s.telecom.incoming_call_state,
                    active_call_state=s.telecom.active_call_state,
                )
            )
        return out

    def get(self, session_id: str) -> SessionRuntime | None:
        return self._sessions.get(session_id)

    def mark_broken(self, session_id: str) -> None:
        runtime = self._sessions.get(session_id)
        if runtime is None:
            return
        if runtime.model.lifecycle_state in {"closed", "closing"}:
            return
        runtime.model.lifecycle_state = "broken"

    async def close(self, session_id: str) -> bool:
        runtime = self._sessions.get(session_id)
        if runtime is None:
            return False
        runtime.model.lifecycle_state = "closing"
        await self._browser_manager.close(runtime.browser)
        runtime.model.telecom.browser_open = False
        runtime.model.lifecycle_state = "closed"
        del self._sessions[session_id]
        return True
