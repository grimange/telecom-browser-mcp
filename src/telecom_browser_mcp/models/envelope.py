from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from telecom_browser_mcp.models.artifact import ArtifactRef
from telecom_browser_mcp.models.enums import ErrorCode, FailureCategory


class ToolSuccess(BaseModel):
    ok: bool = True
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: int = 0
    session_id: str | None = None
    artifacts: list[ArtifactRef] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)
    message: str = "ok"


class ToolFailure(ToolSuccess):
    ok: bool = False
    error_code: ErrorCode = ErrorCode.UNKNOWN
    failure_category: FailureCategory = FailureCategory.DIAGNOSTIC
    retryable: bool = False
    likely_causes: list[str] = Field(default_factory=list)
    next_recommended_tools: list[str] = Field(default_factory=list)


def success_response(
    *,
    message: str,
    data: dict[str, Any] | None = None,
    duration_ms: int = 0,
    session_id: str | None = None,
    artifacts: list[ArtifactRef] | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    return ToolSuccess(
        message=message,
        data=data or {},
        duration_ms=duration_ms,
        session_id=session_id,
        artifacts=artifacts or [],
        warnings=warnings or [],
    ).model_dump(mode="json")


def failure_response(
    *,
    message: str,
    error_code: ErrorCode,
    failure_category: FailureCategory,
    retryable: bool,
    likely_causes: list[str] | None = None,
    next_recommended_tools: list[str] | None = None,
    data: dict[str, Any] | None = None,
    duration_ms: int = 0,
    session_id: str | None = None,
    artifacts: list[ArtifactRef] | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    return ToolFailure(
        message=message,
        error_code=error_code,
        failure_category=failure_category,
        retryable=retryable,
        likely_causes=likely_causes or [],
        next_recommended_tools=next_recommended_tools or [],
        data=data or {},
        duration_ms=duration_ms,
        session_id=session_id,
        artifacts=artifacts or [],
        warnings=warnings or [],
    ).model_dump(mode="json")
