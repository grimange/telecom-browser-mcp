from telecom_browser_mcp.server.app import create_mcp_server


def test_server_bootstrap() -> None:
    server = create_mcp_server()
    assert server is not None
