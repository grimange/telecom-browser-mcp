from telecom_browser_mcp.server.app import create_mcp_server


def main() -> None:
    create_mcp_server().run(transport="streamable-http")
