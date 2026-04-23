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
    assert apntalk["support_status"] == "login_ui_plus_bridge_observation"
    assert apntalk["capabilities"]["supports_login"] is True
    assert apntalk["capabilities"]["supports_registration_detection"] is True
    assert apntalk["capabilities"]["supports_incoming_call_detection"] is True
    assert apntalk["capabilities"]["supports_answer_action"] is True
    assert apntalk["capabilities"]["supports_hangup_action"] is True
    assert apntalk["capabilities"]["supports_webrtc_summary"] is True
    ready_truth = next(item for item in apntalk["capability_truth"] if item["capability"] == "wait_for_ready")
    registration_wait_truth = next(
        item for item in apntalk["capability_truth"] if item["capability"] == "wait_for_registration"
    )
    incoming_truth = next(
        item for item in apntalk["capability_truth"] if item["capability"] == "wait_for_incoming_call"
    )
    registration_truth = next(
        item for item in apntalk["capability_truth"] if item["capability"] == "get_registration_status"
    )
    peer_connection_truth = next(
        item for item in apntalk["capability_truth"] if item["capability"] == "get_peer_connection_summary"
    )
    answer_truth = next(item for item in apntalk["capability_truth"] if item["capability"] == "answer_call")
    hangup_truth = next(item for item in apntalk["capability_truth"] if item["capability"] == "hangup_call")
    store_truth = next(item for item in apntalk["capability_truth"] if item["capability"] == "get_store_snapshot")
    assert ready_truth["declared_support"] == "supported_with_runtime_probe"
    assert ready_truth["binding_status"] == "runtime_probe_bound"
    assert registration_wait_truth["declared_support"] == "supported_with_runtime_probe"
    assert registration_wait_truth["binding_status"] == "runtime_probe_bound"
    assert incoming_truth["declared_support"] == "supported_with_runtime_probe"
    assert incoming_truth["binding_status"] == "runtime_probe_bound"
    assert registration_truth["declared_support"] == "supported_with_runtime_probe"
    assert registration_truth["binding_status"] == "runtime_probe_bound"
    assert peer_connection_truth["declared_support"] == "supported_with_runtime_probe"
    assert peer_connection_truth["binding_status"] == "runtime_probe_bound"
    assert answer_truth["declared_support"] == "supported_with_selector_binding"
    assert answer_truth["binding_status"] == "selector_bound"
    assert hangup_truth["declared_support"] == "supported_with_selector_binding"
    assert hangup_truth["binding_status"] == "selector_bound"
    assert store_truth["declared_support"] == "scaffold_only"
    assert store_truth["binding_status"] == "unbound"
    assert "s022-067.apntelecom.com" in apntalk["domains"]
