from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class OpenAppInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_url: str
    adapter_id: str | None = None
    headless: bool = True
    session_label: str | None = None


class EmptyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SessionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str


class TimeoutInput(SessionInput):
    timeout_ms: int = 15000


class LoginInput(TimeoutInput):
    credentials: dict[str, Any] = {}


class CollectDebugBundleInput(SessionInput):
    reason: str | None = None
