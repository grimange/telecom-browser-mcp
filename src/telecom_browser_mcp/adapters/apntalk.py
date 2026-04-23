from __future__ import annotations

import asyncio
from time import monotonic
from typing import Any

from telecom_browser_mcp.adapters.apntalk_contract import (
    APNTALK_CONTRACT_VERSION,
    APNTALK_RUNTIME_BRIDGE_CONTRACT,
    get_apntalk_surface_contract,
    validate_apntalk_runtime_bridge,
)
from telecom_browser_mcp.adapters.base import AdapterBase, AdapterOperationResult
from telecom_browser_mcp.models.session import AdapterCapabilities, TelecomStatus


class APNTalkAdapter(AdapterBase):
    adapter_id = "apntalk"
    adapter_name = "APNTalk"
    adapter_version = "0.1"
    contract_version = APNTALK_CONTRACT_VERSION
    scenario_id = "apntalk-modernization-baseline"
    support_status = "login_ui_plus_bridge_observation"
    capabilities = AdapterCapabilities(
        supports_login=True,
        supports_registration_detection=True,
        supports_incoming_call_detection=True,
        supports_answer_action=True,
        supports_hangup_action=True,
        supports_webrtc_summary=True,
    )

    _EMAIL_SELECTORS = (
        "input[type='email']",
        "input[name='email']",
        "input[autocomplete='username']",
        "input[placeholder*='Email' i]",
        "input[id*='email' i]",
    )
    _PASSWORD_SELECTORS = (
        "input[type='password']",
        "input[name='password']",
        "input[autocomplete='current-password']",
        "input[placeholder*='Password' i]",
        "input[id*='password' i]",
    )
    _SUBMIT_SELECTORS = (
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('Sign In')",
        "button:has-text('Log In')",
        "button:has-text('Login')",
    )

    @staticmethod
    async def _find_first_visible(page: Any, selectors: tuple[str, ...]) -> tuple[Any | None, str | None]:
        for selector in selectors:
            locator = page.locator(selector)
            try:
                if await locator.count() == 0:
                    continue
                if await locator.first.is_visible():
                    return locator.first, selector
            except Exception:
                continue
        return None, None

    @staticmethod
    def _credential_value(credentials: dict[str, Any], *keys: str) -> str | None:
        for key in keys:
            value = credentials.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

    @staticmethod
    async def _extract_login_error(page: Any) -> str | None:
        try:
            payload = await page.evaluate(
                """
                () => {
                  const nodes = Array.from(
                    document.querySelectorAll('[role="alert"], .alert, .error, .errors, [data-testid*="error"]')
                  );
                  for (const node of nodes) {
                    const text = (node.textContent || '').trim();
                    if (text) {
                      return text;
                    }
                  }
                  return null;
                }
                """
            )
        except Exception:
            return None
        return payload if isinstance(payload, str) and payload.strip() else None

    @staticmethod
    async def _post_login_probe(page: Any) -> dict[str, Any]:
        try:
            payload = await page.evaluate(
                """
                () => {
                  const bodyText = (document.body?.innerText || '').replace(/\\s+/g, ' ').trim();
                  const title = (document.title || '').trim();
                  const path = (window.location.pathname || '').toLowerCase();
                  const href = window.location.href;
                  const hasPasswordField = !!document.querySelector("input[type='password']");
                  const hasEmailField = !!document.querySelector("input[type='email'], input[name='email'], input[autocomplete='username']");
                  const authText = /(dashboard|admin report|sign out|logout)/i.test(bodyText) || /(dashboard|admin report)/i.test(title);
                  const awayFromLogin = !/\\/login(?:\\/|$)?/.test(path) && !/login/i.test(title);
                  return {
                    success: authText || (awayFromLogin && !hasPasswordField && !hasEmailField),
                    url: href,
                    title,
                    away_from_login: awayFromLogin,
                    auth_text: authText,
                    has_password_field: hasPasswordField
                  };
                }
                """
            )
        except Exception:
            return {"success": False}
        return payload if isinstance(payload, dict) else {"success": False}

    @staticmethod
    async def _raw_runtime_bridge_payload(page: Any) -> Any:
        try:
            return await page.evaluate(
                """
                () => {
                  const bridge = window.__apnTalkTestBridge;
                  if (bridge === undefined || bridge === null) {
                    return null;
                  }
                  if (typeof bridge !== "object") {
                    return "__non_object__";
                  }
                  const section = (value, keys) => {
                    if (value === undefined) {
                      return undefined;
                    }
                    if (value === null || typeof value !== "object") {
                      return value;
                    }
                    const out = {};
                    for (const key of keys) {
                      if (Object.prototype.hasOwnProperty.call(value, key)) {
                        out[key] = value[key];
                      }
                    }
                    return out;
                  };
                  const out = {};
                  for (const key of ["version", "readOnly", "mode"]) {
                    if (Object.prototype.hasOwnProperty.call(bridge, key)) {
                      out[key] = bridge[key];
                    }
                  }
                  if (Object.prototype.hasOwnProperty.call(bridge, "sessionAuth")) {
                    out.sessionAuth = section(bridge.sessionAuth, [
                      "availability",
                      "isAuthenticated",
                      "hasUser",
                      "hasSelectedCampaign",
                      "hasCampaigns"
                    ]);
                  }
                  if (Object.prototype.hasOwnProperty.call(bridge, "agent")) {
                    out.agent = section(bridge.agent, [
                      "availability",
                      "lifecycleStatus",
                      "sessionInitialized",
                      "hasUserId",
                      "hasSessionId",
                      "hasExtension"
                    ]);
                  }
                  if (Object.prototype.hasOwnProperty.call(bridge, "registration")) {
                    out.registration = section(bridge.registration, [
                      "availability",
                      "isRegistered",
                      "callStatus",
                      "hasRegisterer",
                      "hasSession",
                      "hasCallerInfo"
                    ]);
                  }
                  if (Object.prototype.hasOwnProperty.call(bridge, "call")) {
                    out.call = section(bridge.call, [
                      "availability",
                      "hasActiveCall",
                      "callStatus",
                      "direction",
                      "isMuted",
                      "isOnHold",
                      "durationSeconds",
                      "hasBridgeId"
                    ]);
                  }
                  if (Object.prototype.hasOwnProperty.call(bridge, "readiness")) {
                    out.readiness = section(bridge.readiness, [
                      "availability",
                      "isAuthenticated",
                      "sessionInitialized",
                      "lifecycleStatus",
                      "isRegistered",
                      "requestedAvailability",
                      "effectiveAvailability"
                    ]);
                  }
                  if (Object.prototype.hasOwnProperty.call(bridge, "incomingCall")) {
                    out.incomingCall = section(bridge.incomingCall, [
                      "availability",
                      "isIncomingPresent",
                      "ringingState",
                      "direction",
                      "ambiguity"
                    ]);
                  }
                  if (Object.prototype.hasOwnProperty.call(bridge, "webRTC")) {
                    out.webRTC = section(bridge.webRTC, [
                      "availability",
                      "hasRemoteAudioElement",
                      "remoteAudioAttached",
                      "hasRingtoneElement"
                    ]);
                  }
                  if (Object.prototype.hasOwnProperty.call(bridge, "peerConnection")) {
                    out.peerConnection = section(bridge.peerConnection, [
                      "availability",
                      "hasPeerConnection",
                      "ambiguity",
                      "signalingState",
                      "iceConnectionState",
                      "connectionState",
                      "hasLocalDescription",
                      "hasRemoteDescription",
                      "senderCount",
                      "receiverCount",
                      "transceiverCount"
                    ]);
                  }
                  if (Object.prototype.hasOwnProperty.call(bridge, "controls")) {
                    out.controls = {};
                    if (
                      bridge.controls
                      && typeof bridge.controls === "object"
                      && Object.prototype.hasOwnProperty.call(bridge.controls, "answer")
                    ) {
                      out.controls.answer = section(bridge.controls.answer, [
                        "availability",
                        "visible",
                        "enabled",
                        "actionAllowed",
                        "ambiguity",
                        "controlKind",
                        "controlScope",
                        "stableControlId",
                        "selectorContract"
                      ]);
                    }
                    if (
                      bridge.controls
                      && typeof bridge.controls === "object"
                      && Object.prototype.hasOwnProperty.call(bridge.controls, "hangup")
                    ) {
                      out.controls.hangup = section(bridge.controls.hangup, [
                        "availability",
                        "visible",
                        "enabled",
                        "actionAllowed",
                        "ambiguity",
                        "controlKind",
                        "controlScope",
                        "stableControlId",
                        "selectorContract"
                      ]);
                    }
                  }
                  return out;
                }
                """
            )
        except Exception:
            return {"_probe_failed": True}

    @staticmethod
    async def _resolve_unique_visible_control(
        page: Any,
        selector: str,
    ) -> tuple[Any | None, dict[str, Any]]:
        locator = page.locator(selector)
        try:
            total_matches = await locator.count()
        except Exception:
            return None, {
                "available": False,
                "reason": "APNTalk selector contract probe failed",
                "reason_code": "selector_contract_probe_failed",
                "selector_contract": selector,
                "total_matches": 0,
                "visible_matches": 0,
            }

        visible_matches: list[Any] = []
        for index in range(total_matches):
            candidate = locator.nth(index)
            try:
                if await candidate.is_visible():
                    visible_matches.append(candidate)
            except Exception:
                continue

        if total_matches == 0 or not visible_matches:
            return None, {
                "available": False,
                "reason": "APNTalk stable control selector did not match a visible control",
                "reason_code": "selector_contract_mismatch",
                "selector_contract": selector,
                "total_matches": total_matches,
                "visible_matches": len(visible_matches),
            }

        if total_matches > 1 or len(visible_matches) > 1:
            return None, {
                "available": False,
                "reason": "APNTalk stable control selector matched multiple visible controls",
                "reason_code": "multiple_selector_matches",
                "selector_contract": selector,
                "total_matches": total_matches,
                "visible_matches": len(visible_matches),
            }

        return visible_matches[0], {
            "available": True,
            "selector_contract": selector,
            "total_matches": total_matches,
            "visible_matches": len(visible_matches),
        }

    async def _runtime_bridge_diagnostics(self, page: Any) -> dict[str, Any]:
        if page is None:
            return {
                "bridge_name": APNTALK_RUNTIME_BRIDGE_CONTRACT.bridge_name,
                "consumer_support": "supported_with_runtime_probe",
                "status": "not_checked",
                "validation_verdict": "not_checked",
                "bridge_version": None,
                "read_only": None,
                "mode": None,
                "sections_present": [],
                "sections_missing": [],
                "malformed_fields": [],
                "why_unavailable": "page unavailable",
            }
        payload = await self._raw_runtime_bridge_payload(page)
        if payload == {"_probe_failed": True}:
            return {
                "bridge_name": APNTALK_RUNTIME_BRIDGE_CONTRACT.bridge_name,
                "consumer_support": "supported_with_runtime_probe",
                "status": "not_checked",
                "validation_verdict": "not_checked",
                "bridge_version": None,
                "read_only": None,
                "mode": None,
                "sections_present": [],
                "sections_missing": [],
                "malformed_fields": [],
                "why_unavailable": "bridge probe failed",
            }
        if payload == "__non_object__":
            payload = "__non_object__"
        result = validate_apntalk_runtime_bridge(payload)
        verdict_to_status = {
            "bridge_absent": "bridge_absent",
            "bridge_malformed": "bridge_malformed",
            "bridge_partial": "bridge_partial",
            "bridge_version_mismatch": "bridge_version_mismatch",
            "bridge_valid": "bridge_present",
        }
        return {
            "bridge_name": result.bridge_name,
            "consumer_support": "supported_with_runtime_probe",
            "status": verdict_to_status[result.verdict],
            "validation_verdict": result.verdict,
            "bridge_version": result.bridge_version,
            "read_only": result.read_only,
            "mode": result.mode,
            "sections_present": list(result.sections_present),
            "sections_missing": list(result.sections_missing),
            "malformed_fields": list(result.malformed_fields),
            "why_unavailable": result.why_unavailable,
        }

    async def _validated_runtime_bridge_payload(
        self,
        page: Any,
    ) -> tuple[dict[str, Any] | None, dict[str, Any]]:
        diagnostics = await self._runtime_bridge_diagnostics(page)
        if diagnostics.get("validation_verdict") != "bridge_valid":
            return None, diagnostics
        payload = await self._raw_runtime_bridge_payload(page)
        if not isinstance(payload, dict):
            return None, diagnostics
        return payload, diagnostics

    async def _bridge_registration_observation(self, page: Any) -> dict[str, Any]:
        base = {
            "available": False,
            "registration_state": "unknown",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        if page is None:
            return {
                **base,
                "reason": "page unavailable",
                "reason_code": "runtime_probe_unavailable",
            }

        payload, diagnostics = await self._validated_runtime_bridge_payload(page)
        if payload is None:
            return {
                **base,
                "reason": diagnostics.get("why_unavailable") or "APNTalk runtime bridge is not valid",
                "reason_code": diagnostics.get("validation_verdict"),
                "bridge_version": diagnostics.get("bridge_version"),
            }

        registration = payload.get("registration")
        if not isinstance(registration, dict):
            return {
                **base,
                "reason": "APNTalk runtime bridge registration section is unavailable",
                "reason_code": "bridge_partial",
                "bridge_version": diagnostics.get("bridge_version"),
            }

        availability = registration.get("availability")
        if availability not in {"available", "partial"}:
            return {
                **base,
                "reason": "APNTalk runtime bridge registration section is not available",
                "reason_code": "bridge_registration_unavailable",
                "bridge_version": diagnostics.get("bridge_version"),
            }

        is_registered = registration.get("isRegistered")
        if not isinstance(is_registered, bool):
            return {
                **base,
                "reason": "APNTalk runtime bridge does not expose isRegistered",
                "reason_code": "bridge_registration_state_missing",
                "bridge_version": diagnostics.get("bridge_version"),
            }

        return {
            **base,
            "available": True,
            "registration_state": "registered" if is_registered else "unregistered",
            "bridge_version": diagnostics.get("bridge_version"),
            "availability": availability,
            "reason": None,
            "reason_code": None,
        }

    async def _bridge_registration_wait_observation(self, page: Any) -> dict[str, Any]:
        base = {
            "available": False,
            "registration_state": "unknown",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        if page is None:
            return {
                **base,
                "reason": "page unavailable",
                "reason_code": "runtime_probe_unavailable",
            }

        payload, diagnostics = await self._validated_runtime_bridge_payload(page)
        if payload is None:
            return {
                **base,
                "reason": diagnostics.get("why_unavailable") or "APNTalk runtime bridge is not valid",
                "reason_code": diagnostics.get("validation_verdict"),
                "bridge_version": diagnostics.get("bridge_version"),
            }

        registration = payload.get("registration")
        if not isinstance(registration, dict):
            return {
                **base,
                "reason": "APNTalk runtime bridge registration section is unavailable",
                "reason_code": "bridge_partial",
                "bridge_version": diagnostics.get("bridge_version"),
            }

        facts = {
            "availability": registration.get("availability"),
            "isRegistered": registration.get("isRegistered"),
            "callStatus": registration.get("callStatus"),
            "hasRegisterer": registration.get("hasRegisterer"),
            "hasSession": registration.get("hasSession"),
            "hasCallerInfo": registration.get("hasCallerInfo"),
        }
        is_registered = facts["availability"] == "available" and facts["isRegistered"] is True
        if not is_registered:
            return {
                **base,
                "registration_state": (
                    "unregistered" if isinstance(facts["isRegistered"], bool) and not facts["isRegistered"] else "unknown"
                ),
                "reason": "APNTalk registration facts do not satisfy the consumer registration contract",
                "reason_code": (
                    "registration_not_registered"
                    if facts["availability"] == "available" and facts["isRegistered"] is False
                    else "bridge_registration_unavailable"
                ),
                "bridge_version": diagnostics.get("bridge_version"),
                "facts": facts,
            }

        return {
            **base,
            "available": True,
            "registration_state": "registered",
            "bridge_version": diagnostics.get("bridge_version"),
            "facts": facts,
            "reason": None,
            "reason_code": None,
        }

    async def _bridge_ready_observation(self, page: Any) -> dict[str, Any]:
        base = {
            "available": False,
            "ui_ready": False,
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        if page is None:
            return {
                **base,
                "reason": "page unavailable",
                "reason_code": "runtime_probe_unavailable",
            }

        payload, diagnostics = await self._validated_runtime_bridge_payload(page)
        if payload is None:
            return {
                **base,
                "reason": diagnostics.get("why_unavailable") or "APNTalk runtime bridge is not valid",
                "reason_code": diagnostics.get("validation_verdict"),
                "bridge_version": diagnostics.get("bridge_version"),
            }

        readiness = payload.get("readiness")
        if not isinstance(readiness, dict):
            return {
                **base,
                "reason": "APNTalk runtime bridge readiness section is unavailable",
                "reason_code": "bridge_partial",
                "bridge_version": diagnostics.get("bridge_version"),
            }

        facts = {
            "availability": readiness.get("availability"),
            "isAuthenticated": readiness.get("isAuthenticated"),
            "sessionInitialized": readiness.get("sessionInitialized"),
            "lifecycleStatus": readiness.get("lifecycleStatus"),
            "isRegistered": readiness.get("isRegistered"),
            "requestedAvailability": readiness.get("requestedAvailability"),
            "effectiveAvailability": readiness.get("effectiveAvailability"),
        }
        is_ready = (
            facts["availability"] == "available"
            and facts["isAuthenticated"] is True
            and facts["sessionInitialized"] is True
            and facts["isRegistered"] is True
            and facts["lifecycleStatus"] == "READY"
            and facts["requestedAvailability"] == "READY"
            and facts["effectiveAvailability"] == "AVAILABLE"
        )
        if not is_ready:
            return {
                **base,
                "reason": "APNTalk readiness facts do not satisfy the consumer ready contract",
                "reason_code": "ready_state_not_satisfied",
                "bridge_version": diagnostics.get("bridge_version"),
                "facts": facts,
            }

        return {
            **base,
            "available": True,
            "ui_ready": True,
            "bridge_version": diagnostics.get("bridge_version"),
            "facts": facts,
            "reason": None,
            "reason_code": None,
        }

    async def _bridge_incoming_call_observation(self, page: Any) -> dict[str, Any]:
        base = {
            "available": False,
            "incoming_call_state": "unknown",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        if page is None:
            return {
                **base,
                "reason": "page unavailable",
                "reason_code": "runtime_probe_unavailable",
            }

        payload, diagnostics = await self._validated_runtime_bridge_payload(page)
        if payload is None:
            return {
                **base,
                "reason": diagnostics.get("why_unavailable") or "APNTalk runtime bridge is not valid",
                "reason_code": diagnostics.get("validation_verdict"),
                "bridge_version": diagnostics.get("bridge_version"),
            }

        incoming = payload.get("incomingCall")
        if not isinstance(incoming, dict):
            return {
                **base,
                "reason": "APNTalk runtime bridge incomingCall section is unavailable",
                "reason_code": "bridge_partial",
                "bridge_version": diagnostics.get("bridge_version"),
            }

        facts = {
            "availability": incoming.get("availability"),
            "isIncomingPresent": incoming.get("isIncomingPresent"),
            "ringingState": incoming.get("ringingState"),
            "direction": incoming.get("direction"),
            "ambiguity": incoming.get("ambiguity"),
        }
        is_safe_ringing = (
            facts["availability"] == "available"
            and facts["isIncomingPresent"] is True
            and facts["ringingState"] == "ringing"
            and facts["direction"] == "incoming"
            and facts["ambiguity"] == "none"
        )
        if not is_safe_ringing:
            return {
                **base,
                "reason": "APNTalk incoming-call facts do not satisfy the consumer ringing contract",
                "reason_code": (
                    "incoming_call_ambiguous"
                    if facts["ambiguity"] != "none" or facts["availability"] == "partial"
                    else "incoming_call_not_present"
                ),
                "bridge_version": diagnostics.get("bridge_version"),
                "facts": facts,
            }

        return {
            **base,
            "available": True,
            "incoming_call_state": "ringing",
            "bridge_version": diagnostics.get("bridge_version"),
            "facts": facts,
            "reason": None,
            "reason_code": None,
        }

    async def _bridge_peer_connection_observation(self, page: Any) -> dict[str, Any]:
        base = {
            "available": False,
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        if page is None:
            return {
                **base,
                "reason": "page unavailable",
                "reason_code": "runtime_probe_unavailable",
            }

        payload, diagnostics = await self._validated_runtime_bridge_payload(page)
        if payload is None:
            return {
                **base,
                "reason": diagnostics.get("why_unavailable") or "APNTalk runtime bridge is not valid",
                "reason_code": diagnostics.get("validation_verdict"),
                "bridge_version": diagnostics.get("bridge_version"),
            }

        peer_connection = payload.get("peerConnection")
        if not isinstance(peer_connection, dict):
            return {
                **base,
                "reason": "APNTalk runtime bridge peerConnection section is unavailable",
                "reason_code": "bridge_partial",
                "bridge_version": diagnostics.get("bridge_version"),
            }

        facts = {
            "availability": peer_connection.get("availability"),
            "hasPeerConnection": peer_connection.get("hasPeerConnection"),
            "ambiguity": peer_connection.get("ambiguity"),
            "signalingState": peer_connection.get("signalingState"),
            "iceConnectionState": peer_connection.get("iceConnectionState"),
            "connectionState": peer_connection.get("connectionState"),
            "hasLocalDescription": peer_connection.get("hasLocalDescription"),
            "hasRemoteDescription": peer_connection.get("hasRemoteDescription"),
            "senderCount": peer_connection.get("senderCount"),
            "receiverCount": peer_connection.get("receiverCount"),
            "transceiverCount": peer_connection.get("transceiverCount"),
        }
        is_concrete_summary = (
            facts["availability"] == "available"
            and facts["hasPeerConnection"] is True
            and facts["ambiguity"] == "none"
        )
        if not is_concrete_summary:
            return {
                **base,
                "reason": "APNTalk peer-connection facts do not satisfy the consumer summary contract",
                "reason_code": (
                    "peer_connection_ambiguous"
                    if facts["ambiguity"] not in {None, "none"} or facts["availability"] == "partial"
                    else "peer_connection_unavailable"
                ),
                "bridge_version": diagnostics.get("bridge_version"),
                "facts": facts,
            }

        return {
            **base,
            "available": True,
            "bridge_version": diagnostics.get("bridge_version"),
            "facts": facts,
            "reason": None,
            "reason_code": None,
        }

    async def _bridge_hangup_control_observation(self, page: Any) -> dict[str, Any]:
        base = {
            "available": False,
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        if page is None:
            return {
                **base,
                "reason": "page unavailable",
                "reason_code": "runtime_probe_unavailable",
            }

        payload, diagnostics = await self._validated_runtime_bridge_payload(page)
        if payload is None:
            return {
                **base,
                "reason": diagnostics.get("why_unavailable") or "APNTalk runtime bridge is not valid",
                "reason_code": diagnostics.get("validation_verdict"),
                "bridge_version": diagnostics.get("bridge_version"),
            }

        controls = payload.get("controls")
        if not isinstance(controls, dict):
            return {
                **base,
                "reason": "APNTalk runtime bridge controls section is unavailable",
                "reason_code": "bridge_partial",
                "bridge_version": diagnostics.get("bridge_version"),
            }

        hangup = controls.get("hangup")
        if not isinstance(hangup, dict):
            return {
                **base,
                "reason": "APNTalk runtime bridge hangup control section is unavailable",
                "reason_code": "bridge_partial",
                "bridge_version": diagnostics.get("bridge_version"),
            }

        call = payload.get("call")
        call_facts = {
            "availability": call.get("availability") if isinstance(call, dict) else None,
            "hasActiveCall": call.get("hasActiveCall") if isinstance(call, dict) else None,
            "callStatus": call.get("callStatus") if isinstance(call, dict) else None,
        }
        facts = {
            "availability": hangup.get("availability"),
            "visible": hangup.get("visible"),
            "enabled": hangup.get("enabled"),
            "actionAllowed": hangup.get("actionAllowed"),
            "ambiguity": hangup.get("ambiguity"),
            "controlKind": hangup.get("controlKind"),
            "controlScope": hangup.get("controlScope"),
            "stableControlId": hangup.get("stableControlId"),
            "selectorContract": hangup.get("selectorContract"),
            "activeCallAvailability": call_facts["availability"],
            "hasActiveCall": call_facts["hasActiveCall"],
            "activeCallStatus": call_facts["callStatus"],
        }
        if facts["activeCallAvailability"] != "available" or facts["hasActiveCall"] is not True:
            return {
                **base,
                "reason": "APNTalk runtime bridge does not prove an active call target for hangup",
                "reason_code": "no_active_call_target",
                "bridge_version": diagnostics.get("bridge_version"),
                "facts": facts,
            }

        is_available = (
            facts["availability"] == "available"
            and facts["visible"] is True
            and facts["enabled"] is True
            and facts["actionAllowed"] is True
            and facts["ambiguity"] == "none"
            and facts["controlKind"] == "hangup"
            and facts["controlScope"] == "main-call"
            and facts["stableControlId"] == "softphone-main-hangup"
            and facts["selectorContract"] == '[data-apntalk-bridge-control-id="softphone-main-hangup"]'
        )
        if not is_available:
            reason_code = "hangup_control_unavailable"
            if facts["ambiguity"] not in {None, "none"} or facts["availability"] == "partial":
                reason_code = "hangup_control_ambiguous"
            elif facts["visible"] is not True:
                reason_code = "hangup_control_hidden"
            elif facts["enabled"] is not True:
                reason_code = "hangup_control_disabled"
            elif facts["actionAllowed"] is not True:
                reason_code = "hangup_action_disallowed"
            elif facts["selectorContract"] != '[data-apntalk-bridge-control-id="softphone-main-hangup"]':
                reason_code = "selector_contract_mismatch"
            return {
                **base,
                "reason": "APNTalk hangup control facts do not satisfy the consumer control contract",
                "reason_code": reason_code,
                "bridge_version": diagnostics.get("bridge_version"),
                "facts": facts,
            }

        return {
            **base,
            "available": True,
            "bridge_version": diagnostics.get("bridge_version"),
            "facts": facts,
            "reason": None,
            "reason_code": None,
        }

    async def _bridge_answer_control_observation(self, page: Any) -> dict[str, Any]:
        base = {
            "available": False,
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        if page is None:
            return {
                **base,
                "reason": "page unavailable",
                "reason_code": "runtime_probe_unavailable",
            }

        payload, diagnostics = await self._validated_runtime_bridge_payload(page)
        if payload is None:
            return {
                **base,
                "reason": diagnostics.get("why_unavailable") or "APNTalk runtime bridge is not valid",
                "reason_code": diagnostics.get("validation_verdict"),
                "bridge_version": diagnostics.get("bridge_version"),
            }

        controls = payload.get("controls")
        if not isinstance(controls, dict):
            return {
                **base,
                "reason": "APNTalk runtime bridge controls section is unavailable",
                "reason_code": "bridge_partial",
                "bridge_version": diagnostics.get("bridge_version"),
            }

        answer = controls.get("answer")
        if not isinstance(answer, dict):
            return {
                **base,
                "reason": "APNTalk runtime bridge answer control section is unavailable",
                "reason_code": "bridge_partial",
                "bridge_version": diagnostics.get("bridge_version"),
            }

        incoming = payload.get("incomingCall")
        incoming_facts = {
            "availability": incoming.get("availability") if isinstance(incoming, dict) else None,
            "isIncomingPresent": incoming.get("isIncomingPresent") if isinstance(incoming, dict) else None,
            "ringingState": incoming.get("ringingState") if isinstance(incoming, dict) else None,
            "direction": incoming.get("direction") if isinstance(incoming, dict) else None,
            "ambiguity": incoming.get("ambiguity") if isinstance(incoming, dict) else None,
        }
        facts = {
            "availability": answer.get("availability"),
            "visible": answer.get("visible"),
            "enabled": answer.get("enabled"),
            "actionAllowed": answer.get("actionAllowed"),
            "ambiguity": answer.get("ambiguity"),
            "controlKind": answer.get("controlKind"),
            "controlScope": answer.get("controlScope"),
            "stableControlId": answer.get("stableControlId"),
            "selectorContract": answer.get("selectorContract"),
            "incomingAvailability": incoming_facts["availability"],
            "isIncomingPresent": incoming_facts["isIncomingPresent"],
            "ringingState": incoming_facts["ringingState"],
            "incomingDirection": incoming_facts["direction"],
            "incomingAmbiguity": incoming_facts["ambiguity"],
        }
        if not (
            facts["incomingAvailability"] == "available"
            and facts["isIncomingPresent"] is True
            and facts["ringingState"] == "ringing"
            and facts["incomingDirection"] == "incoming"
            and facts["incomingAmbiguity"] == "none"
        ):
            return {
                **base,
                "reason": "APNTalk runtime bridge does not prove a safe incoming-call target for answer",
                "reason_code": (
                    "incoming_call_ambiguous"
                    if facts["incomingAmbiguity"] not in {None, "none"} or facts["incomingAvailability"] == "partial"
                    else "no_incoming_call_target"
                ),
                "bridge_version": diagnostics.get("bridge_version"),
                "facts": facts,
            }

        is_available = (
            facts["availability"] == "available"
            and facts["visible"] is True
            and facts["enabled"] is True
            and facts["actionAllowed"] is True
            and facts["ambiguity"] == "none"
            and facts["controlKind"] == "answer"
            and facts["controlScope"] == "incoming-call"
            and facts["stableControlId"] == "softphone-main-answer"
            and facts["selectorContract"] == '[data-apntalk-bridge-control-id="softphone-main-answer"]'
        )
        if not is_available:
            reason_code = "answer_control_unavailable"
            if facts["ambiguity"] not in {None, "none"} or facts["availability"] == "partial":
                reason_code = "answer_control_ambiguous"
            elif facts["visible"] is not True:
                reason_code = "answer_control_hidden"
            elif facts["enabled"] is not True:
                reason_code = "answer_control_disabled"
            elif facts["actionAllowed"] is not True:
                reason_code = "answer_action_disallowed"
            elif facts["selectorContract"] != '[data-apntalk-bridge-control-id="softphone-main-answer"]':
                reason_code = "selector_contract_mismatch"
            return {
                **base,
                "reason": "APNTalk answer control facts do not satisfy the consumer control contract",
                "reason_code": reason_code,
                "bridge_version": diagnostics.get("bridge_version"),
                "facts": facts,
            }

        return {
            **base,
            "available": True,
            "bridge_version": diagnostics.get("bridge_version"),
            "facts": facts,
            "reason": None,
            "reason_code": None,
        }

    async def _bridge_answer_connected_observation(self, page: Any) -> dict[str, Any]:
        base = {
            "available": False,
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        payload, diagnostics = await self._validated_runtime_bridge_payload(page)
        if payload is None:
            return {
                **base,
                "reason": diagnostics.get("why_unavailable") or "APNTalk runtime bridge is not valid",
                "reason_code": diagnostics.get("validation_verdict"),
                "bridge_version": diagnostics.get("bridge_version"),
            }

        call = payload.get("call")
        incoming = payload.get("incomingCall")
        peer_connection = payload.get("peerConnection")
        controls = payload.get("controls")
        answer = controls.get("answer") if isinstance(controls, dict) else None
        facts = {
            "callAvailability": call.get("availability") if isinstance(call, dict) else None,
            "hasActiveCall": call.get("hasActiveCall") if isinstance(call, dict) else None,
            "callStatus": call.get("callStatus") if isinstance(call, dict) else None,
            "incomingAvailability": incoming.get("availability") if isinstance(incoming, dict) else None,
            "isIncomingPresent": incoming.get("isIncomingPresent") if isinstance(incoming, dict) else None,
            "ringingState": incoming.get("ringingState") if isinstance(incoming, dict) else None,
            "incomingDirection": incoming.get("direction") if isinstance(incoming, dict) else None,
            "incomingAmbiguity": incoming.get("ambiguity") if isinstance(incoming, dict) else None,
            "peerAvailability": peer_connection.get("availability") if isinstance(peer_connection, dict) else None,
            "hasPeerConnection": peer_connection.get("hasPeerConnection") if isinstance(peer_connection, dict) else None,
            "peerAmbiguity": peer_connection.get("ambiguity") if isinstance(peer_connection, dict) else None,
            "answerAvailability": answer.get("availability") if isinstance(answer, dict) else None,
            "answerVisible": answer.get("visible") if isinstance(answer, dict) else None,
            "answerActionAllowed": answer.get("actionAllowed") if isinstance(answer, dict) else None,
            "answerAmbiguity": answer.get("ambiguity") if isinstance(answer, dict) else None,
        }
        connected = (
            facts["incomingAvailability"] == "available"
            and facts["ringingState"] != "ringing"
            and facts["isIncomingPresent"] is False
            and facts["incomingAmbiguity"] == "none"
            and facts["callAvailability"] == "available"
            and facts["hasActiveCall"] is True
            and facts["callStatus"] in {"ANSWERED", "BRIDGING", "TALKING"}
        )
        if not connected:
            return {
                **base,
                "reason": "APNTalk post-answer bridge facts did not reach a connected state",
                "reason_code": "answer_connected_transition_missing",
                "bridge_version": diagnostics.get("bridge_version"),
                "facts": facts,
            }

        return {
            **base,
            "available": True,
            "bridge_version": diagnostics.get("bridge_version"),
            "facts": facts,
            "reason": None,
            "reason_code": None,
        }

    async def _bridge_hangup_terminal_observation(self, page: Any) -> dict[str, Any]:
        base = {
            "available": False,
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        payload, diagnostics = await self._validated_runtime_bridge_payload(page)
        if payload is None:
            return {
                **base,
                "reason": diagnostics.get("why_unavailable") or "APNTalk runtime bridge is not valid",
                "reason_code": diagnostics.get("validation_verdict"),
                "bridge_version": diagnostics.get("bridge_version"),
            }

        call = payload.get("call")
        incoming = payload.get("incomingCall")
        peer_connection = payload.get("peerConnection")
        controls = payload.get("controls")
        hangup = controls.get("hangup") if isinstance(controls, dict) else None
        facts = {
            "callAvailability": call.get("availability") if isinstance(call, dict) else None,
            "hasActiveCall": call.get("hasActiveCall") if isinstance(call, dict) else None,
            "callStatus": call.get("callStatus") if isinstance(call, dict) else None,
            "incomingAvailability": incoming.get("availability") if isinstance(incoming, dict) else None,
            "isIncomingPresent": incoming.get("isIncomingPresent") if isinstance(incoming, dict) else None,
            "ringingState": incoming.get("ringingState") if isinstance(incoming, dict) else None,
            "peerAvailability": peer_connection.get("availability") if isinstance(peer_connection, dict) else None,
            "hasPeerConnection": peer_connection.get("hasPeerConnection") if isinstance(peer_connection, dict) else None,
            "peerAmbiguity": peer_connection.get("ambiguity") if isinstance(peer_connection, dict) else None,
            "hangupAvailability": hangup.get("availability") if isinstance(hangup, dict) else None,
            "hangupVisible": hangup.get("visible") if isinstance(hangup, dict) else None,
            "hangupActionAllowed": hangup.get("actionAllowed") if isinstance(hangup, dict) else None,
            "hangupAmbiguity": hangup.get("ambiguity") if isinstance(hangup, dict) else None,
        }
        terminal = (
            facts["callAvailability"] == "available"
            and facts["hasActiveCall"] is False
            and facts["hangupVisible"] is False
            and facts["hangupActionAllowed"] is False
            and facts["ringingState"] != "ringing"
            and facts["hasPeerConnection"] is not True
        )
        if not terminal:
            return {
                **base,
                "reason": "APNTalk post-hangup bridge facts did not reach a terminal state",
                "reason_code": "hangup_terminal_transition_missing",
                "bridge_version": diagnostics.get("bridge_version"),
                "facts": facts,
            }

        return {
            **base,
            "available": True,
            "bridge_version": diagnostics.get("bridge_version"),
            "facts": facts,
            "reason": None,
            "reason_code": None,
        }

    def capability_truth(self, observation: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        runtime_bridge = observation.get("runtime_bridge") if isinstance(observation, dict) else None
        bridge_live_detection = "not_checked"
        bridge_why_unavailable = None
        if isinstance(runtime_bridge, dict):
            bridge_live_detection = runtime_bridge.get("validation_verdict", "not_checked")
            bridge_why_unavailable = runtime_bridge.get("why_unavailable")

        def _live_detection(observation_payload: dict[str, Any] | None) -> tuple[str, str | None]:
            if not isinstance(observation_payload, dict):
                return bridge_live_detection, "bridge-backed observation has not been checked"
            if observation_payload.get("available") is True:
                return "detected", None
            reason_code = observation_payload.get("reason_code")
            if reason_code in {
                "bridge_absent",
                "bridge_malformed",
                "bridge_partial",
                "bridge_version_mismatch",
            }:
                return reason_code, observation_payload.get("reason")
            if reason_code == "runtime_probe_unavailable":
                return "not_checked", observation_payload.get("reason")
            return (
                "bridge_present" if bridge_live_detection == "bridge_valid" else bridge_live_detection,
                observation_payload.get("reason"),
            )

        ready_live_detection, ready_why_unavailable = _live_detection(
            observation.get("ready_observation") if isinstance(observation, dict) else None
        )
        registration_wait_live_detection, registration_wait_why_unavailable = _live_detection(
            observation.get("registration_wait_observation") if isinstance(observation, dict) else None
        )
        registration_live_detection, registration_why_unavailable = _live_detection(
            observation.get("registration_observation") if isinstance(observation, dict) else None
        )
        incoming_live_detection, incoming_why_unavailable = _live_detection(
            observation.get("incoming_call_observation") if isinstance(observation, dict) else None
        )
        answer_live_detection, answer_why_unavailable = _live_detection(
            observation.get("answer_control_observation") if isinstance(observation, dict) else None
        )
        peer_connection_live_detection, peer_connection_why_unavailable = _live_detection(
            observation.get("peer_connection_observation") if isinstance(observation, dict) else None
        )
        hangup_live_detection, hangup_why_unavailable = _live_detection(
            observation.get("hangup_control_observation") if isinstance(observation, dict) else None
        )

        return [
            {
                "capability": "apntalk_runtime_bridge_contract",
                "declared_support": "supported_with_runtime_probe",
                "binding_status": "runtime_probe_bound",
                "live_detection_status": bridge_live_detection,
                "why_unavailable": bridge_why_unavailable,
            },
            {
                "capability": "login_agent",
                "declared_support": "supported_with_selector_binding",
                "binding_status": "selector_bound",
                "live_detection_status": "not_checked",
                "why_unavailable": None,
            },
            {
                "capability": "wait_for_ready",
                "declared_support": "supported_with_runtime_probe",
                "binding_status": "runtime_probe_bound",
                "live_detection_status": ready_live_detection,
                "why_unavailable": ready_why_unavailable,
            },
            {
                "capability": "wait_for_registration",
                "declared_support": "supported_with_runtime_probe",
                "binding_status": "runtime_probe_bound",
                "live_detection_status": registration_wait_live_detection,
                "why_unavailable": registration_wait_why_unavailable,
            },
            {
                "capability": "wait_for_incoming_call",
                "declared_support": "supported_with_runtime_probe",
                "binding_status": "runtime_probe_bound",
                "live_detection_status": incoming_live_detection,
                "why_unavailable": incoming_why_unavailable,
            },
            {
                "capability": "answer_call",
                "declared_support": "supported_with_selector_binding",
                "binding_status": "selector_bound",
                "live_detection_status": answer_live_detection,
                "why_unavailable": answer_why_unavailable,
            },
            {
                "capability": "hangup_call",
                "declared_support": "supported_with_selector_binding",
                "binding_status": "selector_bound",
                "live_detection_status": hangup_live_detection,
                "why_unavailable": hangup_why_unavailable,
            },
            {
                "capability": "get_registration_status",
                "declared_support": "supported_with_runtime_probe",
                "binding_status": "runtime_probe_bound",
                "live_detection_status": registration_live_detection,
                "why_unavailable": registration_why_unavailable,
            },
            {
                "capability": "get_store_snapshot",
                "declared_support": "scaffold_only",
                "binding_status": "unbound",
                "live_detection_status": "not_checked",
                "why_unavailable": "bounded APNTalk runtime snapshot binding is not implemented",
            },
            {
                "capability": "get_peer_connection_summary",
                "declared_support": "supported_with_runtime_probe",
                "binding_status": "runtime_probe_bound",
                "live_detection_status": peer_connection_live_detection,
                "why_unavailable": peer_connection_why_unavailable,
            },
        ]

    async def phase0_observation(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        observation = await super().phase0_observation(status, page)
        contract_notes: list[dict[str, Any]] = []
        for tool_name, contract in (
            ("wait_for_ready", get_apntalk_surface_contract("wait_for_ready")),
            ("wait_for_registration", get_apntalk_surface_contract("wait_for_registration")),
            ("wait_for_incoming_call", get_apntalk_surface_contract("wait_for_incoming_call")),
            ("answer_call", get_apntalk_surface_contract("answer_call")),
            ("hangup_call", get_apntalk_surface_contract("hangup_call")),
            ("get_registration_status", get_apntalk_surface_contract("get_registration_status")),
            ("get_store_snapshot", get_apntalk_surface_contract("get_store_snapshot")),
            ("get_peer_connection_summary", get_apntalk_surface_contract("get_peer_connection_summary")),
        ):
            contract_notes.append(
                {
                    "tool": tool_name,
                    "binding_status": "bound" if contract.is_implemented else "unbound",
                    "missing_requirements": contract.missing_requirements(),
                }
            )

        login_selectors: dict[str, dict[str, Any]] = {}
        runtime_bridge = {
            "bridge_name": APNTALK_RUNTIME_BRIDGE_CONTRACT.bridge_name,
            "consumer_support": "supported_with_runtime_probe",
            "status": "not_checked",
            "validation_verdict": "not_checked",
            "bridge_version": None,
            "read_only": None,
            "mode": None,
            "sections_present": [],
            "sections_missing": [],
            "malformed_fields": [],
            "why_unavailable": None,
        }
        microphone_permission = {"available": False, "state": "unknown"}
        registration_observation = {
            "available": False,
            "registration_state": status.registration_state,
            "reason": "bridge-backed registration observation not checked",
            "reason_code": "not_checked",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        registration_wait_observation = {
            "available": False,
            "registration_state": status.registration_state,
            "reason": "bridge-backed registration wait observation not checked",
            "reason_code": "not_checked",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        ready_observation = {
            "available": False,
            "ui_ready": status.ui_ready,
            "reason": "bridge-backed readiness observation not checked",
            "reason_code": "not_checked",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        incoming_call_observation = {
            "available": False,
            "incoming_call_state": status.incoming_call_state,
            "reason": "bridge-backed incoming-call observation not checked",
            "reason_code": "not_checked",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        peer_connection_observation = {
            "available": False,
            "reason": "bridge-backed peer-connection observation not checked",
            "reason_code": "not_checked",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        answer_control_observation = {
            "available": False,
            "reason": "bridge-backed answer control observation not checked",
            "reason_code": "not_checked",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }
        hangup_control_observation = {
            "available": False,
            "reason": "bridge-backed hangup control observation not checked",
            "reason_code": "not_checked",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
        }

        if page is not None:
            try:
                login_selectors = await page.evaluate(
                    """
                    () => {
                      const groups = {
                        email_input: [
                          "input[type='email']",
                          "input[name='email']",
                          "input[autocomplete='username']",
                          "input[placeholder*='Email' i]",
                          "input[id*='email' i]"
                        ],
                        password_input: [
                          "input[type='password']",
                          "input[name='password']",
                          "input[autocomplete='current-password']",
                          "input[placeholder*='Password' i]",
                          "input[id*='password' i]"
                        ],
                        submit_button: [
                          "button[type='submit']",
                          "input[type='submit']"
                        ]
                      };
                      const visible = (element) => {
                        if (!element) return false;
                        const style = window.getComputedStyle(element);
                        const rect = element.getBoundingClientRect();
                        return style.visibility !== "hidden" && style.display !== "none" && rect.width > 0 && rect.height > 0;
                      };
                      const results = {};
                      for (const [name, selectors] of Object.entries(groups)) {
                        let matched = null;
                        for (const selector of selectors) {
                          const node = document.querySelector(selector);
                          if (visible(node)) {
                            matched = selector;
                            break;
                          }
                        }
                        results[name] = {
                          status: matched ? "selector_present" : "selector_absent",
                          matched_selector: matched
                        };
                      }
                      return results;
                    }
                    """
                )
            except Exception:
                login_selectors = {}

            try:
                runtime_bridge = await self._runtime_bridge_diagnostics(page)
            except Exception:
                runtime_bridge = {
                    "bridge_name": APNTALK_RUNTIME_BRIDGE_CONTRACT.bridge_name,
                    "consumer_support": "supported_with_runtime_probe",
                    "status": "not_checked",
                    "validation_verdict": "not_checked",
                    "bridge_version": None,
                    "read_only": None,
                    "mode": None,
                    "sections_present": [],
                    "sections_missing": [],
                    "malformed_fields": [],
                    "why_unavailable": "bridge probe failed",
                }

            try:
                registration_observation = await self._bridge_registration_observation(page)
            except Exception:
                registration_observation["reason"] = "APNTalk registration observation probe failed"
                registration_observation["reason_code"] = "runtime_probe_unavailable"

            try:
                registration_wait_observation = await self._bridge_registration_wait_observation(page)
            except Exception:
                registration_wait_observation["reason"] = "APNTalk registration wait probe failed"
                registration_wait_observation["reason_code"] = "runtime_probe_unavailable"

            try:
                ready_observation = await self._bridge_ready_observation(page)
            except Exception:
                ready_observation["reason"] = "APNTalk readiness observation probe failed"
                ready_observation["reason_code"] = "runtime_probe_unavailable"

            try:
                incoming_call_observation = await self._bridge_incoming_call_observation(page)
            except Exception:
                incoming_call_observation["reason"] = "APNTalk incoming-call observation probe failed"
                incoming_call_observation["reason_code"] = "runtime_probe_unavailable"

            try:
                peer_connection_observation = await self._bridge_peer_connection_observation(page)
            except Exception:
                peer_connection_observation["reason"] = "APNTalk peer-connection observation probe failed"
                peer_connection_observation["reason_code"] = "runtime_probe_unavailable"

            try:
                answer_control_observation = await self._bridge_answer_control_observation(page)
            except Exception:
                answer_control_observation["reason"] = "APNTalk answer control observation probe failed"
                answer_control_observation["reason_code"] = "runtime_probe_unavailable"

            try:
                hangup_control_observation = await self._bridge_hangup_control_observation(page)
            except Exception:
                hangup_control_observation["reason"] = "APNTalk hangup control observation probe failed"
                hangup_control_observation["reason_code"] = "runtime_probe_unavailable"

            try:
                microphone_permission = await page.evaluate(
                    """
                    async () => {
                      if (!navigator.permissions?.query) {
                        return { available: false, state: "unknown" };
                      }
                      try {
                        const status = await navigator.permissions.query({ name: "microphone" });
                        return { available: true, state: status.state || "unknown" };
                      } catch (_error) {
                        return { available: false, state: "unknown" };
                      }
                    }
                    """
                )
            except Exception:
                microphone_permission = {"available": False, "state": "unknown"}

        observation.update(
            {
                "capability_truth": self.capability_truth(
                    {
                        "runtime_bridge": runtime_bridge,
                        "registration_wait_observation": registration_wait_observation,
                        "registration_observation": registration_observation,
                        "ready_observation": ready_observation,
                        "incoming_call_observation": incoming_call_observation,
                        "answer_control_observation": answer_control_observation,
                        "peer_connection_observation": peer_connection_observation,
                        "hangup_control_observation": hangup_control_observation,
                    }
                ),
                "status_snapshot": {
                    "login_complete": status.login_complete,
                    "ui_ready": ready_observation.get("ui_ready", status.ui_ready),
                    "registration_state": registration_observation.get(
                        "registration_state",
                        status.registration_state,
                    ),
                    "incoming_call_state": incoming_call_observation.get(
                        "incoming_call_state",
                        status.incoming_call_state,
                    ),
                    "active_call_state": status.active_call_state,
                },
                "selector_observations": login_selectors,
                "contract_observations": contract_notes,
                "runtime_bridge": runtime_bridge,
                "registration_wait_observation": registration_wait_observation,
                "registration_observation": registration_observation,
                "ready_observation": ready_observation,
                "incoming_call_observation": incoming_call_observation,
                "answer_control_observation": answer_control_observation,
                "peer_connection_observation": peer_connection_observation,
                "hangup_control_observation": hangup_control_observation,
                "microphone_permission": microphone_permission,
            }
        )
        return observation

    async def wait_for_ready(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = timeout_ms
        contract = get_apntalk_surface_contract("wait_for_ready")
        observation = await self._bridge_ready_observation(page)
        if observation.get("available") is True and observation.get("ui_ready") is True:
            status.ui_ready = True
            return self._success(
                "APNTalk ready state detected from runtime bridge",
                ui_ready=True,
                bridge_version=observation.get("bridge_version"),
                ready_facts=observation.get("facts"),
                missing_requirements=contract.missing_requirements(),
            )
        return self._failure(
            observation.get("reason") or "APNTalk ready state not detected",
            error_code=observation.get("reason_code") or "runtime_probe_unavailable",
            classification="session_not_ready",
            retryable=True,
            ready_facts=observation.get("facts"),
            missing_requirements=contract.missing_requirements(),
        )

    async def login(
        self,
        status: TelecomStatus,
        page: Any,
        credentials: dict[str, Any],
        timeout_ms: int,
    ) -> AdapterOperationResult:
        if page is None:
            return self._failure(
                "page unavailable",
                error_code="runtime_probe_unavailable",
                classification="environment_limitation",
                retryable=True,
            )

        username = self._credential_value(
            credentials,
            "email",
            "username",
            "user",
            "login",
            "agent_email",
        )
        password = self._credential_value(
            credentials,
            "password",
            "pass",
            "agent_password",
        )
        if not username or not password:
            return self._failure(
                "APNTalk login requires visible-UI credentials with non-empty email/username and password",
                error_code="invalid_input",
                classification="adapter_contract_failure",
            )

        email_locator, email_selector = await self._find_first_visible(page, self._EMAIL_SELECTORS)
        password_locator, password_selector = await self._find_first_visible(page, self._PASSWORD_SELECTORS)
        submit_locator, submit_selector = await self._find_first_visible(page, self._SUBMIT_SELECTORS)

        missing_selectors: list[str] = []
        if email_locator is None:
            missing_selectors.append("email_input")
        if password_locator is None:
            missing_selectors.append("password_input")
        if submit_locator is None:
            missing_selectors.append("submit_button")
        if missing_selectors:
            return self._failure(
                "APNTalk login UI controls were not found as visible elements",
                error_code="selector_contract_missing",
                classification="ui_drift",
                retryable=True,
                missing_selectors=missing_selectors,
            )

        try:
            await email_locator.fill(username, timeout=timeout_ms)
            await password_locator.fill(password, timeout=timeout_ms)
            await submit_locator.click(timeout=timeout_ms)
            try:
                await page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
            except Exception:
                pass
            await page.wait_for_function(
                """
                () => {
                  const bodyText = (document.body?.innerText || '').replace(/\\s+/g, ' ').trim();
                  const title = (document.title || '').trim();
                  const path = (window.location.pathname || '').toLowerCase();
                  const hasPasswordField = !!document.querySelector("input[type='password']");
                  const hasEmailField = !!document.querySelector("input[type='email'], input[name='email'], input[autocomplete='username']");
                  const authText = /(dashboard|admin report|sign out|logout)/i.test(bodyText) || /(dashboard|admin report)/i.test(title);
                  const awayFromLogin = !/\\/login(?:\\/|$)?/.test(path) && !/login/i.test(title);
                  return authText || (awayFromLogin && !hasPasswordField && !hasEmailField);
                }
                """,
                timeout=timeout_ms,
            )
        except Exception:
            error_text = await self._extract_login_error(page)
            if error_text:
                return self._failure(
                    f"APNTalk login form reported an error: {error_text}",
                    error_code="state_divergence",
                    classification="state_divergence",
                    retryable=True,
                )
            probe = await self._post_login_probe(page)
            return self._failure(
                "APNTalk login submit did not reach an authenticated post-login page",
                error_code="state_divergence",
                classification="state_divergence",
                retryable=True,
                post_login_probe=probe,
            )

        probe = await self._post_login_probe(page)
        if not probe.get("success"):
            return self._failure(
                "APNTalk login submit completed but authenticated UI was not confirmed",
                error_code="state_divergence",
                classification="state_divergence",
                retryable=True,
                post_login_probe=probe,
            )

        status.login_complete = True
        return self._success(
            "APNTalk login completed via visible UI",
            login_complete=True,
            landing_url=probe.get("url"),
            landing_title=probe.get("title"),
            selectors_used={
                "email": email_selector,
                "password": password_selector,
                "submit": submit_selector,
            },
        )

    async def wait_for_registration(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = timeout_ms
        contract = get_apntalk_surface_contract("wait_for_registration")
        observation = await self._bridge_registration_wait_observation(page)
        if observation.get("available") is True and observation.get("registration_state") == "registered":
            status.registration_state = "registered"
            return self._success(
                "APNTalk registration detected from runtime bridge",
                registration_state="registered",
                bridge_version=observation.get("bridge_version"),
                registration_facts=observation.get("facts"),
                missing_requirements=contract.missing_requirements(),
            )
        return self._failure(
            observation.get("reason") or "APNTalk registration not detected",
            error_code=observation.get("reason_code") or "runtime_probe_unavailable",
            classification="registration_missing",
            retryable=True,
            registration_facts=observation.get("facts"),
            missing_requirements=contract.missing_requirements(),
        )

    async def wait_for_incoming_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        _ = timeout_ms
        contract = get_apntalk_surface_contract("wait_for_incoming_call")
        observation = await self._bridge_incoming_call_observation(page)
        if observation.get("available") is True and observation.get("incoming_call_state") == "ringing":
            status.incoming_call_state = "ringing"
            return self._success(
                "APNTalk incoming ringing state detected from runtime bridge",
                incoming_call_state="ringing",
                bridge_version=observation.get("bridge_version"),
                incoming_call_facts=observation.get("facts"),
                missing_requirements=contract.missing_requirements(),
            )
        return self._failure(
            observation.get("reason") or "APNTalk incoming call not detected",
            error_code=observation.get("reason_code") or "runtime_probe_unavailable",
            classification="incoming_call_not_present",
            retryable=True,
            incoming_call_facts=observation.get("facts"),
            missing_requirements=contract.missing_requirements(),
        )

    async def answer_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        contract = get_apntalk_surface_contract("answer_call")
        observation = await self._bridge_answer_control_observation(page)
        if observation.get("available") is not True:
            classification = "adapter_contract_failure"
            if observation.get("reason_code") in {"selector_contract_mismatch", "multiple_selector_matches"}:
                classification = "ui_drift"
            return self._failure(
                observation.get("reason") or "APNTalk answer control is not available",
                error_code=observation.get("reason_code") or "runtime_probe_unavailable",
                classification=classification,
                retryable=True,
                answer_control_facts=observation.get("facts"),
                missing_requirements=contract.missing_requirements(),
            )

        selector_contract = observation.get("facts", {}).get("selectorContract")
        control, selector_probe = await self._resolve_unique_visible_control(page, selector_contract)
        if control is None:
            return self._failure(
                selector_probe.get("reason") or "APNTalk stable answer selector did not resolve uniquely",
                error_code=selector_probe.get("reason_code") or "selector_contract_probe_failed",
                classification="ui_drift",
                retryable=True,
                answer_control_facts=observation.get("facts"),
                selector_probe=selector_probe,
                missing_requirements=contract.missing_requirements(),
            )

        try:
            await control.click(timeout=timeout_ms)
        except Exception as exc:
            return self._failure(
                f"APNTalk visible answer control click failed: {exc}",
                error_code="answer_click_failed",
                classification="ui_drift",
                retryable=True,
                answer_control_facts=observation.get("facts"),
                selector_probe=selector_probe,
                missing_requirements=contract.missing_requirements(),
            )

        deadline = monotonic() + max(timeout_ms, 1) / 1000
        last_connected_observation: dict[str, Any] | None = None
        while True:
            connected_observation = await self._bridge_answer_connected_observation(page)
            last_connected_observation = connected_observation
            if connected_observation.get("available") is True:
                status.incoming_call_state = "idle"
                status.active_call_state = "connected"
                return self._success(
                    "APNTalk answer completed via visible UI control",
                    incoming_call_state="idle",
                    active_call_state="connected",
                    bridge_version=connected_observation.get("bridge_version"),
                    answer_control_facts=observation.get("facts"),
                    selector_probe=selector_probe,
                    connected_facts=connected_observation.get("facts"),
                    missing_requirements=contract.missing_requirements(),
                )
            if monotonic() >= deadline:
                break
            await asyncio.sleep(0.05)

        return self._failure(
            (last_connected_observation or {}).get("reason")
            or "APNTalk answer did not reach a connected state before timeout",
            error_code=(last_connected_observation or {}).get("reason_code") or "answer_connected_transition_missing",
            classification="call_delivery_failure",
            retryable=True,
            answer_control_facts=observation.get("facts"),
            selector_probe=selector_probe,
            connected_facts=(last_connected_observation or {}).get("facts"),
            missing_requirements=contract.missing_requirements(),
        )

    async def hangup_call(
        self,
        status: TelecomStatus,
        page: Any,
        timeout_ms: int,
    ) -> AdapterOperationResult:
        contract = get_apntalk_surface_contract("hangup_call")
        observation = await self._bridge_hangup_control_observation(page)
        if observation.get("available") is not True:
            classification = "adapter_contract_failure"
            if observation.get("reason_code") in {"selector_contract_mismatch", "multiple_selector_matches"}:
                classification = "ui_drift"
            return self._failure(
                observation.get("reason") or "APNTalk hangup control is not available",
                error_code=observation.get("reason_code") or "runtime_probe_unavailable",
                classification=classification,
                retryable=True,
                hangup_control_facts=observation.get("facts"),
                missing_requirements=contract.missing_requirements(),
            )

        selector_contract = observation.get("facts", {}).get("selectorContract")
        control, selector_probe = await self._resolve_unique_visible_control(page, selector_contract)
        if control is None:
            return self._failure(
                selector_probe.get("reason") or "APNTalk stable hangup selector did not resolve uniquely",
                error_code=selector_probe.get("reason_code") or "selector_contract_probe_failed",
                classification="ui_drift",
                retryable=True,
                hangup_control_facts=observation.get("facts"),
                selector_probe=selector_probe,
                missing_requirements=contract.missing_requirements(),
            )

        try:
            await control.click(timeout=timeout_ms)
        except Exception as exc:
            return self._failure(
                f"APNTalk visible hangup control click failed: {exc}",
                error_code="hangup_click_failed",
                classification="ui_drift",
                retryable=True,
                hangup_control_facts=observation.get("facts"),
                selector_probe=selector_probe,
                missing_requirements=contract.missing_requirements(),
            )

        deadline = monotonic() + max(timeout_ms, 1) / 1000
        last_terminal_observation: dict[str, Any] | None = None
        while True:
            terminal_observation = await self._bridge_hangup_terminal_observation(page)
            last_terminal_observation = terminal_observation
            if terminal_observation.get("available") is True:
                status.active_call_state = "disconnected"
                status.incoming_call_state = "idle"
                return self._success(
                    "APNTalk hangup completed via visible UI control",
                    active_call_state="disconnected",
                    incoming_call_state="idle",
                    bridge_version=terminal_observation.get("bridge_version"),
                    hangup_control_facts=observation.get("facts"),
                    selector_probe=selector_probe,
                    terminal_facts=terminal_observation.get("facts"),
                    missing_requirements=contract.missing_requirements(),
                )
            if monotonic() >= deadline:
                break
            await asyncio.sleep(0.05)

        return self._failure(
            (last_terminal_observation or {}).get("reason")
            or "APNTalk hangup did not reach a terminal state before timeout",
            error_code=(last_terminal_observation or {}).get("reason_code") or "hangup_terminal_transition_missing",
            classification="call_delivery_failure",
            retryable=True,
            hangup_control_facts=observation.get("facts"),
            selector_probe=selector_probe,
            terminal_facts=(last_terminal_observation or {}).get("facts"),
            missing_requirements=contract.missing_requirements(),
        )

    async def registration_snapshot(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        contract = get_apntalk_surface_contract("get_registration_status")
        snapshot = await self._bridge_registration_observation(page)
        if snapshot.get("available") is True:
            status.registration_state = snapshot.get("registration_state", status.registration_state)
        return {
            **snapshot,
            "missing_requirements": contract.missing_requirements(),
        }

    async def store_snapshot(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = (status, page)
        contract = get_apntalk_surface_contract("get_store_snapshot")
        return {
            "available": False,
            "reason": "APNTalk store snapshot probe is not implemented",
            "reason_code": "runtime_probe_unavailable",
            "source": self.adapter_id,
            "adapter_name": self.adapter_name,
            "adapter_version": self.adapter_version,
            "contract_version": self.contract_version,
            "scenario_id": self.scenario_id,
            "missing_requirements": contract.missing_requirements(),
        }

    async def peer_connection_summary(self, status: TelecomStatus, page: Any) -> dict[str, Any]:
        _ = status
        contract = get_apntalk_surface_contract("get_peer_connection_summary")
        summary = await self._bridge_peer_connection_observation(page)
        return {
            **summary,
            "missing_requirements": contract.missing_requirements(),
        }
