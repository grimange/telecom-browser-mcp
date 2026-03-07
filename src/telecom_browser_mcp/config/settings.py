from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    transport: str = "stdio"
    host: str = "127.0.0.1"
    port: int = 8765
    headless: bool = True
    default_adapter: str = "generic_sipjs"
    allowed_origins: tuple[str, ...] = ("http://localhost:3000", "http://127.0.0.1:3000")
    artifact_root: str = "docs/audit/telecom-browser-mcp"
    redact: bool = True
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        allowed = os.getenv(
            "TELECOM_BROWSER_MCP_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
        )
        return cls(
            transport=os.getenv("TELECOM_BROWSER_MCP_TRANSPORT", "stdio"),
            host=os.getenv("TELECOM_BROWSER_MCP_HOST", "127.0.0.1"),
            port=int(os.getenv("TELECOM_BROWSER_MCP_PORT", "8765")),
            headless=os.getenv("TELECOM_BROWSER_MCP_HEADLESS", "true").lower() == "true",
            default_adapter=os.getenv("TELECOM_BROWSER_MCP_DEFAULT_ADAPTER", "generic_sipjs"),
            allowed_origins=tuple(x.strip() for x in allowed.split(",") if x.strip()),
            artifact_root=os.getenv("TELECOM_BROWSER_MCP_ARTIFACT_ROOT", "docs/audit/telecom-browser-mcp"),
            redact=os.getenv("TELECOM_BROWSER_MCP_REDACT", "true").lower() == "true",
            log_level=os.getenv("TELECOM_BROWSER_MCP_LOG_LEVEL", "INFO"),
        )
