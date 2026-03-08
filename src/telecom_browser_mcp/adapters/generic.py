from __future__ import annotations

from telecom_browser_mcp.adapters.base import AdapterBase
from telecom_browser_mcp.models.session import AdapterCapabilities


class GenericAdapter(AdapterBase):
    adapter_id = "generic"
    adapter_version = "0.1"
    capabilities = AdapterCapabilities(
        supports_login=False,
        supports_registration_detection=False,
        supports_incoming_call_detection=False,
        supports_answer_action=False,
        supports_hangup_action=False,
        supports_webrtc_summary=False,
    )
