from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

SESSION_ID_PATTERN = r"^[A-Za-z0-9_.:-]{1,128}$"
ADAPTER_ID_PATTERN = r"^[a-z0-9_:-]{1,64}$"


class OpenAppInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_url: str = Field(min_length=1, max_length=2048)
    adapter_id: str | None = Field(default=None, pattern=ADAPTER_ID_PATTERN)
    headless: bool = True
    session_label: str | None = Field(default=None, max_length=120)


class EmptyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SessionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(pattern=SESSION_ID_PATTERN)


class TimeoutInput(SessionInput):
    timeout_ms: int = Field(default=15000, ge=100, le=120000)


class LoginInput(TimeoutInput):
    credentials: dict[str, Any] = Field(default_factory=dict)


class CollectDebugBundleInput(SessionInput):
    reason: str | None = Field(default=None, max_length=240)
