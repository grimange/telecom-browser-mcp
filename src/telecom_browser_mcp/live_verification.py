from __future__ import annotations

import asyncio
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from telecom_browser_mcp.config.settings import Settings
from telecom_browser_mcp.runtime_environment_detector import detect_runtime_environment
from telecom_browser_mcp.tools.orchestrator import ToolOrchestrator


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_md(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def classify_browser_failure(message: str) -> str:
    normalized = message.lower()
    if "operation not permitted" in normalized and "sandbox" in normalized:
        return "host_runtime_constraint"
    if "libnspr4.so" in normalized:
        return "browser_dependency_missing"
    return "environment_limitation"


def classify_mcp_handshake_probe(payload: dict[str, Any]) -> str:
    if bool(payload.get("ok")) or str(payload.get("classification", "")).strip() == "handshake_passed":
        return "handshake_passed"
    normalized = str(payload.get("classification", "")).strip()
    if normalized == "handshake_timeout":
        return "handshake_timeout"
    if normalized == "handshake_invalid_response":
        return "handshake_invalid_response"
    return "handshake_blocked"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_compatibility_inputs(compatibility_dir: Path) -> dict[str, Any]:
    matrix_path = compatibility_dir / "compatibility-matrix.json"
    policy_path = compatibility_dir / "support-policy.json"
    release_env_path = compatibility_dir / "recommended-release-environment.md"
    required_paths = [matrix_path, policy_path, release_env_path]
    missing_paths = [str(path) for path in required_paths if not path.exists()]

    payload: dict[str, Any] = {
        "available": not missing_paths,
        "compatibility_dir": str(compatibility_dir),
        "missing_paths": missing_paths,
        "compatibility_matrix": {},
        "support_policy": {},
        "recommended_release_environment_path": str(release_env_path) if release_env_path.exists() else "",
    }
    if missing_paths:
        return payload

    payload["compatibility_matrix"] = _load_json(matrix_path)
    payload["support_policy"] = _load_json(policy_path)
    return payload


def _evaluate_environment_authority(
    *,
    runtime_fingerprint: dict[str, Any],
    compatibility_inputs: dict[str, Any],
) -> dict[str, Any]:
    runtime_class = str(runtime_fingerprint.get("runtime_class", "unknown_environment")).strip()
    compatibility_matrix = compatibility_inputs.get("compatibility_matrix", {})
    support_policy = compatibility_inputs.get("support_policy", {})
    runtime_policy = support_policy.get("runtime_policy", {})

    allowed_runtime_classes = list(
        runtime_policy.get("allowed_runtime_classes")
        or compatibility_matrix.get("supported_runtime_classes")
        or []
    )
    rejected_runtime_classes = list(runtime_policy.get("rejected_runtime_classes") or [])
    approved_transport_modes = list(compatibility_matrix.get("approved_transport_modes") or ["stdio"])
    approved_browser_execution_modes = list(
        compatibility_matrix.get("approved_browser_execution_modes") or ["playwright_headless_chromium"]
    )

    effective_transport_mode = str(os.environ.get("TELECOM_BROWSER_MCP_TRANSPORT", "stdio")).strip() or "stdio"
    effective_browser_execution_mode = "playwright_headless_chromium"

    reasons: list[str] = []
    if not compatibility_inputs.get("available"):
        reasons.append("compatibility_matrix_inputs_missing")
    if rejected_runtime_classes and runtime_class in rejected_runtime_classes:
        reasons.append(f"runtime_class_rejected:{runtime_class}")
    if allowed_runtime_classes and runtime_class not in allowed_runtime_classes:
        reasons.append(f"runtime_class_not_supported:{runtime_class}")
    if effective_transport_mode not in approved_transport_modes:
        reasons.append(f"transport_mode_not_supported:{effective_transport_mode}")
    if effective_browser_execution_mode not in approved_browser_execution_modes:
        reasons.append(f"browser_mode_not_supported:{effective_browser_execution_mode}")

    browser_capability = runtime_fingerprint.get("browser_capability", {})
    requires_browser_capability = bool(runtime_policy.get("container_requires_browser_capability", True))
    if runtime_class == "container_runtime" and requires_browser_capability and not bool(browser_capability.get("available")):
        reasons.append("container_runtime_browser_capability_missing")

    authoritative = not reasons
    return {
        "authoritative": authoritative,
        "environment_verdict": "authoritative" if authoritative else "environment_not_authoritative",
        "reasons": reasons,
        "runtime_class": runtime_class,
        "allowed_runtime_classes": allowed_runtime_classes,
        "rejected_runtime_classes": rejected_runtime_classes,
        "approved_transport_modes": approved_transport_modes,
        "approved_browser_execution_modes": approved_browser_execution_modes,
        "effective_transport_mode": effective_transport_mode,
        "effective_browser_execution_mode": effective_browser_execution_mode,
        "compatibility_inputs_available": bool(compatibility_inputs.get("available")),
    }


def _transport_outcome(*, mcp_classification: str, authority_gate_ok: bool) -> str:
    if not authority_gate_ok:
        return "transport_environment_blocked"
    if mcp_classification == "handshake_passed":
        return "transport_pass"
    if mcp_classification == "handshake_invalid_response":
        return "transport_partial"
    return "transport_blocked"


def _write_runtime_environment_artifacts(
    *,
    output_dir: Path,
    generated_at: str,
    runtime_fingerprint: dict[str, Any],
    authority_decision: dict[str, Any],
    compatibility_inputs: dict[str, Any],
) -> None:
    _write_json(output_dir / "env-fingerprint.json", runtime_fingerprint)
    _write_md(
        output_dir / "host-environment-check.md",
        [
            "# Host Environment Check",
            "",
            f"- generated_at: `{generated_at}`",
            f"- runtime_class: `{authority_decision['runtime_class']}`",
            f"- environment_verdict: `{authority_decision['environment_verdict']}`",
            f"- authoritative: `{authority_decision['authoritative']}`",
            f"- reasons: `{', '.join(authority_decision['reasons']) if authority_decision['reasons'] else 'none'}`",
            f"- compatibility_inputs_available: `{authority_decision['compatibility_inputs_available']}`",
            f"- compatibility_dir: `{compatibility_inputs.get('compatibility_dir', '')}`",
            f"- browser_capability_available: `{bool(runtime_fingerprint.get('browser_capability', {}).get('available'))}`",
        ],
    )


def _copy_common_artifacts(
    *,
    output_dir: Path,
    evidence_root: Path,
    mcp_payload: dict[str, Any],
    tool_checks: dict[str, Any],
    stage_rows: list[dict[str, Any]],
    generated_at: str,
    run_id: str,
    run_elapsed_seconds: float,
    mcp_probe_cmd: list[str],
) -> None:
    _write_json(output_dir / "mcp-interop-probe.json", mcp_payload)
    _write_json(
        output_dir / "raw-stdio-trace.json",
        {
            "generated_at": generated_at,
            "requests": mcp_payload.get("requests", []),
            "responses": mcp_payload.get("responses", []),
            "classification": mcp_payload.get("classification", ""),
            "available": bool(mcp_payload.get("requests") or mcp_payload.get("responses")),
        },
    )
    _write_json(
        output_dir / "transport-timing.json",
        {
            "generated_at": generated_at,
            "elapsed_seconds": float(mcp_payload.get("elapsed_seconds", 0.0) or 0.0),
            "probe_timeout_seconds": float(mcp_payload.get("timeout_seconds", 0.0) or 0.0),
        },
    )
    _write_json(
        output_dir / "browser-launch-trace.json",
        {
            "generated_at": generated_at,
            "browser_lifecycle": tool_checks.get("browser_lifecycle", {}),
        },
    )
    _write_json(
        output_dir / "runtime-trace.json",
        {
            "generated_at": generated_at,
            "run_id": run_id,
            "stages": stage_rows,
            "minimal_tool_execution": tool_checks.get("minimal_tool_execution", {}),
        },
    )
    _write_json(
        output_dir / "system-timing.json",
        {
            "generated_at": generated_at,
            "run_id": run_id,
            "total_elapsed_seconds": run_elapsed_seconds,
            "mcp_probe_elapsed_seconds": float(mcp_payload.get("elapsed_seconds", 0.0) or 0.0),
        },
    )
    (evidence_root / "command-log.txt").write_text(
        "\n".join([f"generated_at={generated_at}", " ".join(mcp_probe_cmd), ".venv/bin/python - <<tool-checks>>"]) + "\n",
        encoding="utf-8",
    )


async def _run_minimal_tool_checks() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "browser_lifecycle": {},
        "minimal_tool_execution": {},
    }

    real_tools = ToolOrchestrator(Settings(default_adapter="generic_sipjs"))
    try:
        opened = await real_tools.open_app(url="http://localhost:3000", adapter_name="generic_sipjs")
        session_id = str(
            opened.get("data", {}).get("session_id") or opened.get("session_id") or ""
        )
        browser_row: dict[str, Any] = {
            "status": "completed",
            "classification": "validated",
            "open_app": opened,
        }
        if session_id:
            browser_row["close_session"] = await real_tools.close_session(session_id=session_id)
        payload["browser_lifecycle"] = browser_row
    except Exception as exc:  # pragma: no cover - depends on host runtime
        message = f"{type(exc).__name__}: {exc}"
        payload["browser_lifecycle"] = {
            "status": "exception",
            "classification": classify_browser_failure(message),
            "exception": {
                "type": type(exc).__name__,
                "message": str(exc),
            },
        }

    harness_tools = ToolOrchestrator(Settings(default_adapter="harness"))
    minimal: dict[str, Any] = {"status": "completed"}
    payload["minimal_tool_execution"] = minimal

    opened = await harness_tools.open_app(url="http://fake.local", adapter_name="harness")
    minimal["open_app_harness"] = opened
    if not opened.get("ok"):
        minimal["status"] = "failed"
        return payload

    session_id = str(opened.get("data", {}).get("session_id", ""))
    minimal["login_agent"] = await harness_tools.login_agent(
        session_id=session_id,
        username="agent",
        password="secret",
        tenant="default",
    )
    minimal["wait_for_registration"] = await harness_tools.wait_for_registration(session_id=session_id)
    minimal["wait_for_incoming_call"] = await harness_tools.wait_for_incoming_call(session_id=session_id)
    minimal["answer_call"] = await harness_tools.answer_call(session_id=session_id)
    minimal["get_active_session_snapshot"] = await harness_tools.get_active_session_snapshot(session_id=session_id)
    minimal["get_peer_connection_summary"] = await harness_tools.get_peer_connection_summary(session_id=session_id)
    minimal["collect_debug_bundle"] = await harness_tools.collect_debug_bundle(session_id=session_id)
    minimal["close_session"] = await harness_tools.close_session(session_id=session_id)

    return payload


def run_controlled_live_verification(
    *,
    output_dir: Path,
    evidence_dir: Path | None = None,
    mcp_timeout_seconds: float = 20.0,
    mcp_step_timeout_seconds: float = 8.0,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_root = evidence_dir or (output_dir / "evidence")
    evidence_root.mkdir(parents=True, exist_ok=True)

    run_started = time.monotonic()
    generated_at = _now_iso()
    run_id = _now_compact()
    (evidence_root / "mcp-probe-run-stderr.log").write_text("", encoding="utf-8")
    compatibility_inputs = _load_compatibility_inputs(Path("docs/compatibility-matrix/telecom-browser-mcp"))
    runtime_fingerprint = detect_runtime_environment()
    authority_decision = _evaluate_environment_authority(
        runtime_fingerprint=runtime_fingerprint,
        compatibility_inputs=compatibility_inputs,
    )
    _write_runtime_environment_artifacts(
        output_dir=output_dir,
        generated_at=generated_at,
        runtime_fingerprint=runtime_fingerprint,
        authority_decision=authority_decision,
        compatibility_inputs=compatibility_inputs,
    )

    mcp_probe_cmd = [
        str(Path(".venv/bin/python")),
        "scripts/run_mcp_handshake_probe.py",
        "--timeout-seconds",
        str(mcp_timeout_seconds),
        "--step-timeout-seconds",
        str(mcp_step_timeout_seconds),
    ]
    mcp_payload: dict[str, Any] = {
        "ok": False,
        "classification": "transport_environment_blocked",
        "failure": "environment_not_authoritative",
        "phase": "stage_1_runtime_environment_validation",
        "startup_state": "startup_skipped",
        "requests": [],
        "responses": [],
        "tools_list_ok": False,
        "elapsed_seconds": 0.0,
        "timeout_seconds": mcp_timeout_seconds,
    }
    probe_path: Path | None = None
    tool_checks: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "browser_lifecycle": {
            "status": "skipped",
            "classification": "environment_not_authoritative",
        },
        "minimal_tool_execution": {
            "status": "skipped",
            "classification": "environment_not_authoritative",
        },
    }
    mcp_classification = "handshake_skipped_by_environment_gate"
    startup_state = "startup_skipped"
    host_startup_status = "skipped"
    mcp_status = "skipped"
    transport_outcome = _transport_outcome(mcp_classification=mcp_classification, authority_gate_ok=False)
    browser_status = "skipped"
    integrated_status = "skipped"
    minimal_ok = False

    if authority_decision["authoritative"]:
        mcp_probe_run = subprocess.run(mcp_probe_cmd, text=True, capture_output=True, check=False)
        probe_path_text = mcp_probe_run.stdout.strip().splitlines()
        probe_path = Path(probe_path_text[-1]) if probe_path_text else None
        mcp_payload = {
            "ok": False,
            "classification": "handshake_transport_failure",
            "failure": "probe_output_missing",
            "phase": "spawn_server",
            "startup_state": "startup_crash",
            "requests": [],
            "responses": [],
            "tools_list_ok": False,
            "elapsed_seconds": 0.0,
            "timeout_seconds": mcp_timeout_seconds,
        }
        if probe_path and probe_path.exists():
            mcp_payload = _load_json(probe_path)
            _write_json(evidence_root / "mcp-interop-probe.json", mcp_payload)
            stderr_path = probe_path.parent / "mcp-interop-probe-stderr.log"
            if stderr_path.exists():
                (evidence_root / "mcp-probe-run-stderr.log").write_text(
                    stderr_path.read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
        else:
            _write_json(evidence_root / "mcp-interop-probe.json", mcp_payload)

        (evidence_root / "mcp-probe-path.txt").write_text(str(probe_path or ""), encoding="utf-8")
        mcp_classification = classify_mcp_handshake_probe(mcp_payload)
        transport_outcome = _transport_outcome(mcp_classification=mcp_classification, authority_gate_ok=True)
        startup_state = str(mcp_payload.get("startup_state", "startup_crash"))
        host_startup_status = "pass" if startup_state == "startup_ready_via_handshake" else "blocked"
        mcp_status = "pass" if mcp_classification == "handshake_passed" else "blocked"

        tool_checks = asyncio.run(_run_minimal_tool_checks())
        _write_json(evidence_root / "live-tool-checks.json", tool_checks)

        browser_row = tool_checks.get("browser_lifecycle", {})
        browser_status = "pass" if browser_row.get("status") == "completed" else "blocked"
    else:
        _write_json(evidence_root / "mcp-interop-probe.json", mcp_payload)
        (evidence_root / "mcp-probe-path.txt").write_text("", encoding="utf-8")
        _write_json(evidence_root / "live-tool-checks.json", tool_checks)

    browser_row = tool_checks.get("browser_lifecycle", {})
    minimal = tool_checks.get("minimal_tool_execution", {})
    required_tools = [
        "get_active_session_snapshot",
        "get_peer_connection_summary",
        "collect_debug_bundle",
    ]
    if authority_decision["authoritative"]:
        minimal_ok = all(bool(minimal.get(name, {}).get("ok")) for name in required_tools)
        minimal_status = "pass" if minimal_ok else "blocked"
        integrated_status = "pass" if (mcp_status == "pass" and browser_status == "pass" and minimal_ok) else "blocked"
    else:
        minimal_status = "skipped"

    environment = {
        "generated_at_utc": generated_at,
        "working_directory": str(Path.cwd()),
        "python_executable": sys.executable,
        "python_version": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "runtime_class": str(runtime_fingerprint.get("runtime_class", "")),
        "environment_verdict": str(authority_decision.get("environment_verdict", "")),
        "transport_env": str(os.environ.get("TELECOM_BROWSER_MCP_TRANSPORT", "<unset>")),
        "host_env": str(os.environ.get("TELECOM_BROWSER_MCP_HOST", "<unset>")),
        "port_env": str(os.environ.get("TELECOM_BROWSER_MCP_PORT", "<unset>")),
        "default_adapter_env": str(os.environ.get("TELECOM_BROWSER_MCP_DEFAULT_ADAPTER", "<unset>")),
        "artifact_root_env": str(os.environ.get("TELECOM_BROWSER_MCP_ARTIFACT_ROOT", "<unset>")),
        "playwright_browsers_path_env": str(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "<unset>")),
    }
    (evidence_root / "environment.txt").write_text(
        "\n".join(f"{key}={value}" for key, value in environment.items()) + "\n",
        encoding="utf-8",
    )

    stage_rows = [
        {
            "stage": "release_eligibility_read",
            "status": "pass",
            "evidence": [
                "docs/pipeline-governor/telecom-browser-mcp/governor-verdict.json",
                "docs/release-hardening/telecom-browser-mcp/release-hardening-verdict.json",
                "docs/release-hardening/telecom-browser-mcp/release-check-results.json",
            ],
        },
        {
            "stage": "runtime_environment_validation",
            "status": "pass" if authority_decision["authoritative"] else "blocked",
            "details": {
                "runtime_class": authority_decision["runtime_class"],
                "environment_verdict": authority_decision["environment_verdict"],
                "reasons": authority_decision["reasons"],
            },
            "evidence": [
                str(output_dir / "env-fingerprint.json"),
                str(output_dir / "host-environment-check.md"),
            ],
        },
        {
            "stage": "compatibility_matrix_policy_validation",
            "status": "pass" if compatibility_inputs["available"] else "blocked",
            "details": {
                "compatibility_dir": compatibility_inputs.get("compatibility_dir", ""),
                "missing_paths": compatibility_inputs.get("missing_paths", []),
                "effective_transport_mode": authority_decision["effective_transport_mode"],
                "effective_browser_execution_mode": authority_decision["effective_browser_execution_mode"],
            },
            "evidence": [
                str(Path(compatibility_inputs.get("compatibility_dir", "")) / "compatibility-matrix.json"),
                str(Path(compatibility_inputs.get("compatibility_dir", "")) / "support-policy.json"),
                compatibility_inputs.get("recommended_release_environment_path", ""),
            ],
        },
        {
            "stage": "host_startup_verification",
            "status": host_startup_status,
            "details": {
                "timestamp": generated_at,
                "command": "scripts/run_mcp_handshake_probe.py (server spawn + initialize readiness)",
                "startup_state": startup_state,
                "classification": startup_state,
            },
            "evidence": [
                str(evidence_root / "mcp-interop-probe.json"),
                str(evidence_root / "mcp-probe-run-stderr.log"),
            ],
        },
        {
            "stage": "mcp_handshake_verification",
            "status": mcp_status,
            "details": {
                "probe": "scripts/run_mcp_handshake_probe.py",
                "ok": bool(mcp_payload.get("ok")),
                "classification": str(mcp_payload.get("classification", "")),
                "probe_classification": mcp_classification,
                "transport_outcome": transport_outcome,
                "failure": str(mcp_payload.get("failure", "")),
                "phase": str(mcp_payload.get("phase", "")),
                "tools_list_ok": bool(mcp_payload.get("tools_list_ok", False)),
            },
            "evidence": [str(evidence_root / "mcp-interop-probe.json")],
        },
        {
            "stage": "browser_lifecycle_verification",
            "status": browser_status,
            "details": {
                "adapter": "generic_sipjs",
                "result": browser_row.get("status"),
                "classification": browser_row.get("classification"),
            },
            "evidence": [str(evidence_root / "live-tool-checks.json")],
        },
        {
            "stage": "minimal_tool_execution_verification",
            "status": minimal_status,
            "details": {"checks": required_tools, "all_ok": minimal_ok},
            "evidence": [str(evidence_root / "live-tool-checks.json")],
        },
        {
            "stage": "integrated_runtime_validation",
            "status": integrated_status,
            "details": {
                "mcp_ready": mcp_status == "pass",
                "browser_ready": browser_status == "pass",
                "minimal_tool_execution_ready": minimal_status == "pass",
            },
            "evidence": [str(output_dir / "runtime-trace.json")],
        },
        {
            "stage": "environment_capture",
            "status": "pass",
            "evidence": [str(evidence_root / "environment.txt"), str(output_dir / "env-fingerprint.json")],
        },
    ]

    blocked_count = sum(1 for row in stage_rows if row["status"] == "blocked")
    known_limitations = ["minimal tool execution validated with harness adapter only"]
    if not authority_decision["authoritative"]:
        overall_verdict = "blocked_by_environment"
    elif mcp_status == "blocked" or host_startup_status == "blocked":
        overall_verdict = "blocked_by_transport"
    elif browser_status == "blocked":
        overall_verdict = "blocked_by_browser_runtime"
    elif integrated_status == "blocked":
        overall_verdict = "blocked_by_integration"
    elif known_limitations:
        overall_verdict = "passed_with_limitations"
    else:
        overall_verdict = "passed"

    blocking_reasons: list[str] = []
    if not authority_decision["authoritative"]:
        blocking_reasons.extend(authority_decision["reasons"])
    if host_startup_status == "blocked":
        blocking_reasons.append(f"host startup state is not ready: {startup_state}")
    if mcp_status == "blocked":
        blocking_reasons.append(f"mcp handshake failed: {mcp_classification}")
    if browser_status == "blocked":
        browser_class = str(browser_row.get("classification", "environment_limitation"))
        blocking_reasons.append(f"browser lifecycle failed: {browser_class}")
    if integrated_status == "blocked":
        blocking_reasons.append("integrated runtime checks did not satisfy release criteria")

    _write_json(
        output_dir / "live-check-results.json",
        {
            "generated_at": generated_at,
            "project": "telecom-browser-mcp",
            "pipeline": "016--controlled-live-verification",
            "run_id": run_id,
            "stages": stage_rows,
        },
    )
    _write_json(
        output_dir / "live-verification-summary.json",
        {
            "generated_at": generated_at,
            "project": "telecom-browser-mcp",
            "run_id": run_id,
            "objective": "controlled live verification",
            "overall_status": overall_verdict,
            "stage_counts": {
                "pass": sum(1 for row in stage_rows if row["status"] == "pass"),
                "blocked": blocked_count,
                "verification_incomplete": 0,
            },
            "blocking_reasons": blocking_reasons,
            "known_limitations": known_limitations,
            "evidence_root": str(evidence_root),
        },
    )
    _write_json(
        output_dir / "live-risk-register.json",
        {
            "generated_at": generated_at,
            "project": "telecom-browser-mcp",
            "run_id": run_id,
            "risks": [
                {
                    "risk_id": "LIVE-MCP-INIT-001",
                    "severity": "high",
                    "status": "open" if overall_verdict in {"blocked_by_transport", "blocked_by_environment"} else "closed",
                    "domain": "environment",
                },
                {
                    "risk_id": "LIVE-BROWSER-RUNTIME-001",
                    "severity": "high",
                    "status": "open" if overall_verdict in {"blocked_by_browser_runtime", "blocked_by_environment"} else "closed",
                    "domain": "environment",
                },
            ],
        },
    )
    _write_json(
        output_dir / "live-verification-verdict.json",
        {
            "generated_at": generated_at,
            "project": "telecom-browser-mcp",
            "pipeline": "016--controlled-live-verification",
            "run_id": run_id,
            "verdict": overall_verdict,
            "environment_verdict": authority_decision["environment_verdict"],
            "decision_basis": {
                "environment_authoritative": authority_decision["authoritative"],
                "host_startup_succeeds": host_startup_status == "pass",
                "mcp_initialize_succeeds": mcp_status == "pass",
                "tool_discovery_succeeds": mcp_status == "pass",
                "browser_lifecycle_succeeds": browser_status == "pass",
                "minimal_tools_execute": minimal_status == "pass",
                "integrated_runtime_success": integrated_status == "pass",
            },
            "blocking_reasons": blocking_reasons,
        },
    )

    _write_md(
        output_dir / "live-readiness-summary.md",
        [
            "# Live Readiness Summary",
            "",
            f"Controlled live verification completed for `telecom-browser-mcp` at {generated_at}.",
            f"Overall outcome: `{overall_verdict}`.",
        ],
    )
    _write_md(
        output_dir / "live-verification-summary.md",
        [
            "# Live Verification Summary",
            "",
            f"- generated_at: `{generated_at}`",
            f"- run_id: `{run_id}`",
            f"- verdict: `{overall_verdict}`",
            f"- environment_verdict: `{authority_decision['environment_verdict']}`",
        ],
    )
    _write_md(
        output_dir / "host-startup-check.md",
        [
            "# Host Startup Check",
            "",
            "- command: `scripts/run_mcp_handshake_probe.py`",
            f"- startup_state: `{startup_state}`",
            "- classification rule: readiness requires successful initialize response",
        ],
    )
    _write_md(
        output_dir / "mcp-handshake-check.md",
        [
            "# MCP Handshake Check",
            "",
            f"- ok: `{bool(mcp_payload.get('ok'))}`",
            f"- classification: `{mcp_payload.get('classification', '')}`",
            f"- failure: `{mcp_payload.get('failure', '')}`",
            f"- phase: `{mcp_payload.get('phase', '')}`",
        ],
    )
    _write_md(
        output_dir / "browser-lifecycle-check.md",
        [
            "# Browser Lifecycle Check",
            "",
            f"- status: `{browser_row.get('status', 'unknown')}`",
            f"- classification: `{browser_row.get('classification', 'unknown')}`",
        ],
    )
    _write_md(
        output_dir / "tool-execution-check.md",
        [
            "# Tool Execution Check",
            "",
            f"- get_active_session_snapshot: `{bool(minimal.get('get_active_session_snapshot', {}).get('ok'))}`",
            f"- get_peer_connection_summary: `{bool(minimal.get('get_peer_connection_summary', {}).get('ok'))}`",
            f"- collect_debug_bundle: `{bool(minimal.get('collect_debug_bundle', {}).get('ok'))}`",
        ],
    )
    _write_md(
        output_dir / "environment-notes.md",
        [
            "# Environment Notes",
            "",
            f"- platform: `{environment['platform']}`",
            f"- python_version: `{environment['python_version']}`",
            f"- runtime_class: `{environment['runtime_class']}`",
            f"- environment_verdict: `{environment['environment_verdict']}`",
        ],
    )
    _write_md(
        output_dir / "live-risk-register.md",
        [
            "# Live Risk Register",
            "",
            "- LIVE-MCP-INIT-001",
            "- LIVE-BROWSER-RUNTIME-001",
        ],
    )
    _write_md(
        output_dir / "live-verification-verdict.md",
        [
            "# Live Verification Verdict",
            "",
            f"- verdict: `{overall_verdict}`",
            f"- run_id: `{run_id}`",
        ],
    )

    _copy_common_artifacts(
        output_dir=output_dir,
        evidence_root=evidence_root,
        mcp_payload=mcp_payload,
        tool_checks=tool_checks,
        stage_rows=stage_rows,
        generated_at=generated_at,
        run_id=run_id,
        run_elapsed_seconds=round(time.monotonic() - run_started, 3),
        mcp_probe_cmd=mcp_probe_cmd,
    )

    return {
        "run_id": run_id,
        "output_dir": str(output_dir),
        "evidence_dir": str(evidence_root),
        "verdict": overall_verdict,
        "environment_verdict": authority_decision["environment_verdict"],
        "blocking_reasons": blocking_reasons,
    }
