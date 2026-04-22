import os

from telecom_browser_mcp.server.app import create_mcp_server
from telecom_browser_mcp.server.transport_security import (
    load_transport_security_config,
    validate_transport_security,
)


def main() -> None:
    validate_transport_security(
        "sse",
        load_transport_security_config(os.environ.get("FASTMCP_HOST", "127.0.0.1")),
    )
    create_mcp_server().run(transport="sse")


if __name__ == "__main__":
    main()
