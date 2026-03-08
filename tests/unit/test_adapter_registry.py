from telecom_browser_mcp.adapters.apntalk import APNTalkAdapter
from telecom_browser_mcp.adapters.registry import AdapterRegistry


def test_apntalk_domain_resolution() -> None:
    registry = AdapterRegistry()
    registry.register(APNTalkAdapter, domains=["app.apntalk.com", "apntalk.com"])
    adapter, source, confidence = registry.resolve("https://app.apntalk.com/agent")
    assert adapter.adapter_id == "apntalk"
    assert source == "domain_map"
    assert confidence == 0.95
