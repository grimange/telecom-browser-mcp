from datetime import datetime, timezone

from pydantic import BaseModel, Field

from telecom_browser_mcp.models.artifact import ArtifactRef
from telecom_browser_mcp.models.enums import FailureCategory


class DiagnosticResult(BaseModel):
    summary: str
    findings: list[str] = Field(default_factory=list)
    likely_causes: list[str] = Field(default_factory=list)
    severity: str = "medium"
    failure_category: FailureCategory = FailureCategory.DIAGNOSTIC
    retryable: bool = False
    artifacts: list[ArtifactRef] = Field(default_factory=list)
    next_recommended_tools: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
