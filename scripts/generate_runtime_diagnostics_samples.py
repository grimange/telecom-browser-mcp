#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate runtime diagnostics sample manifests for tool-level contract linkage"
    )
    parser.add_argument(
        "--artifact-root",
        default=None,
        help="Root directory for generated runtime artifacts. Defaults under docs/harness/browser-diagnostics-wiring/<ts>-runtime",
    )
    parser.add_argument(
        "--output-summary",
        default=None,
        help="Optional output JSON summary path. Defaults to <artifact-root>/generation-summary.json",
    )
    return parser.parse_args()


async def _run_scenarios(artifact_root: Path) -> dict[str, Any]:
    from telecom_browser_mcp.config.settings import Settings
    from telecom_browser_mcp.tools.orchestrator import ToolOrchestrator

    settings = Settings(default_adapter="harness", artifact_root=str(artifact_root))
    tools = ToolOrchestrator(settings)

    results: dict[str, Any] = {}

    # Scenario set A: delayed registration failure.
    opened = await tools.open_app(url="http://fake.local", adapter_name="harness")
    session_id = opened.get("data", {}).get("session_id")
    if session_id:
        session = tools.session_manager.get(session_id)
        if session is not None:
            observation_scenarios = [
                ("tool-open-app-observation", "open_app"),
                ("tool-login-agent-observation", "login_agent"),
                ("tool-wait-for-ready-observation", "wait_for_ready"),
                ("tool-list-sessions-observation", "list_sessions"),
                ("tool-close-session-observation", "close_session"),
                ("tool-reset-session-observation", "reset_session"),
                ("tool-get-registration-status-observation", "get_registration_status"),
                ("tool-assert-registered-observation", "assert_registered"),
                ("tool-hangup-call-observation", "hangup_call"),
                ("tool-get-ui-call-state-observation", "get_ui_call_state"),
                ("tool-get-active-session-snapshot-observation", "get_active_session_snapshot"),
                ("tool-get-store-snapshot-observation", "get_store_snapshot"),
                ("tool-get-peer-connection-summary-observation", "get_peer_connection_summary"),
                ("tool-get-webrtc-stats-observation", "get_webrtc_stats"),
                ("tool-get-environment-snapshot-observation", "get_environment_snapshot"),
                ("tool-screenshot-observation", "screenshot"),
                ("protocol-initialize-discovery-observation", "initialize_and_discovery"),
            ]
            generated_observations: list[dict[str, str]] = []
            for scenario_id, injection_point in observation_scenarios:
                artifacts, warnings, data = await tools._collect_browser_diagnostics_bundle(
                    session=session,
                    scenario_id=scenario_id,
                    fault_type="tool_observation",
                    injection_point=injection_point,
                    status="ok",
                    failure_classification="diagnostic",
                )
                generated_observations.append(
                    {
                        "scenario_id": scenario_id,
                        "manifest_path": data.get("manifest_path", ""),
                        "bundle_dir": data.get("bundle_dir", ""),
                        "warnings_count": str(len(warnings)),
                        "artifacts_count": str(len(artifacts)),
                    }
                )
            results["tool_observations"] = generated_observations

        await tools.login_agent(
            session_id=session_id,
            username="agent",
            password="secret",
            tenant="registration_delayed",
        )
        results["wait_for_registration_failure"] = await tools.wait_for_registration(session_id=session_id)
        await tools.close_session(session_id=session_id)

    # Scenario set B: incoming absent and answer timeout failures.
    opened = await tools.open_app(url="http://fake.local", adapter_name="harness")
    session_id = opened.get("data", {}).get("session_id")
    if session_id:
        await tools.login_agent(
            session_id=session_id,
            username="agent",
            password="secret",
            tenant="incoming_absent,answer_timeout",
        )
        await tools.wait_for_registration(session_id=session_id)
        results["wait_for_incoming_call_failure"] = await tools.wait_for_incoming_call(
            session_id=session_id,
            timeout_ms=1,
        )
        results["answer_call_failure"] = await tools.answer_call(session_id=session_id, timeout_ms=1)
        results["diagnose_registration_failure"] = await tools.diagnose_registration_failure(
            session_id=session_id
        )
        results["diagnose_incoming_call_failure"] = await tools.diagnose_incoming_call_failure(
            session_id=session_id
        )
        results["diagnose_answer_failure"] = await tools.diagnose_answer_failure(session_id=session_id)
        results["diagnose_one_way_audio"] = await tools.diagnose_one_way_audio(session_id=session_id)
        results["collect_browser_logs"] = await tools.collect_browser_logs(session_id=session_id)
        results["collect_debug_bundle"] = await tools.collect_debug_bundle(session_id=session_id)
        await tools.close_session(session_id=session_id)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "artifact_root": str(artifact_root),
        "results": results,
    }


def main() -> int:
    args = _parse_args()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_root = (
        Path(args.artifact_root)
        if args.artifact_root
        else Path("docs/harness/browser-diagnostics-wiring") / f"{ts}-runtime"
    )
    artifact_root.mkdir(parents=True, exist_ok=True)

    payload = asyncio.run(_run_scenarios(artifact_root))
    summary_path = Path(args.output_summary) if args.output_summary else artifact_root / "generation-summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    sys.stderr.write(f"[generate_runtime_diagnostics_samples] wrote {summary_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
