from telecom_browser_mcp.adapters.registry import AdapterRegistry


def test_registry_has_expected_adapters() -> None:
    registry = AdapterRegistry()
    names = registry.names()
    assert "generic_sipjs" in names
    assert "generic_jssip" in names
    assert "apntalk" in names
    assert "harness" in names
