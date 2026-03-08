from __future__ import annotations

from telecom_browser_mcp.models.common import ToolResponse


def as_dict(response: ToolResponse) -> dict:
    return response.model_dump(mode="json")
