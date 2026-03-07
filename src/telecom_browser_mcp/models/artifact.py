from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ArtifactRef(BaseModel):
    type: str
    label: str
    path: str
    redacted: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
