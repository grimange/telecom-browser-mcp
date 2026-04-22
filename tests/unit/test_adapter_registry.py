import pytest

from telecom_browser_mcp.adapters.apntalk import APNTalkAdapter
from telecom_browser_mcp.adapters.registry import AdapterRegistry, AdapterTargetMismatchError


def test_apntalk_domain_resolution() -> None:
    registry = AdapterRegistry()
    registry.register(APNTalkAdapter, domains=["s022-067.apntelecom.com", "apntalk.com"])
    adapter, source, confidence = registry.resolve("https://s022-067.apntelecom.com/agent")
    assert adapter.adapter_id == "apntalk"
    assert source == "domain_map"
    assert confidence == 0.95


def test_apntalk_target_rejects_explicit_generic_override() -> None:
    registry = AdapterRegistry()
    registry.register(APNTalkAdapter, domains=["s022-067.apntelecom.com", "apntalk.com"])

    with pytest.raises(AdapterTargetMismatchError):
        registry.resolve("https://s022-067.apntelecom.com/agent", adapter_id="generic")


def test_registry_descriptors_expose_adapter_metadata() -> None:
    registry = AdapterRegistry()
    registry.register(APNTalkAdapter, domains=["s022-067.apntelecom.com", "apntalk.com"])

    descriptors = registry.descriptors()
    apntalk = next(item for item in descriptors if item["adapter_id"] == "apntalk")

    assert apntalk["adapter_name"] == "APNTalk"
    assert apntalk["contract_version"] == "apntalk.v1"
    assert apntalk["support_status"] == "login_ui_only"
    assert apntalk["capabilities"]["supports_login"] is True
    assert "s022-067.apntelecom.com" in apntalk["domains"]
