from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

CONTRACT_VERSION = "v1"


class ToolMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_version: str = CONTRACT_VERSION
    adapter_id: str | None = None
    adapter_name: str | None = None
    adapter_version: str | None = None
    scenario_id: str | None = None


class ToolError(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    classification: str = "unknown"
    retryable: bool = False


class DiagnosticItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    classification: str
    message: str
    confidence: Literal["low", "medium", "high"] = "medium"
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ArtifactRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    path: str
    captured: bool = True
    message: str | None = None


class ToolResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    tool: str
    session_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    error: ToolError | None = None
    diagnostics: list[DiagnosticItem] = Field(default_factory=list)
    artifacts: list[ArtifactRef] = Field(default_factory=list)
    meta: ToolMeta = Field(default_factory=ToolMeta)
