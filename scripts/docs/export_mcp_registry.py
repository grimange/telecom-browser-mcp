from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from telecom_browser_mcp.contracts import CANONICAL_TOOL_INPUT_MODELS  # noqa: E402
from telecom_browser_mcp.server.app import create_mcp_server  # noqa: E402

TOOL_SUMMARY_HINTS = {
    "health": "Read-only service health check.",
    "capabilities": "Read-only capability discovery.",
    "open_app": "Create a telecom browser session.",
    "list_sessions": "List currently tracked sessions.",
    "close_session": "Close a managed session.",
    "login_agent": "Run adapter login flow.",
    "wait_for_ready": "Wait until UI/app is ready.",
    "wait_for_registration": "Wait until telecom registration is observed.",
    "wait_for_incoming_call": "Wait until an incoming call is observed.",
    "answer_call": "Attempt to answer an incoming call.",
    "get_active_session_snapshot": "Read session-level runtime snapshot.",
    "get_peer_connection_summary": "Read WebRTC peer connection summary.",
    "collect_debug_bundle": "Capture structured troubleshooting artifacts.",
    "diagnose_answer_failure": "Run answer-failure diagnostic classification.",
}


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, indent=2)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_stable_json(data) + "\n", encoding="utf-8")


def _git_commit() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], text=True)
            .strip()
        )
    except Exception:
        return "unknown"


def _startup_contract() -> dict[str, Any]:
    return {
        "entrypoint_type": "project.scripts",
        "launch_command": "telecom-browser-mcp",
        "transport_modes_supported": ["sse", "stdio", "streamable-http"],
        "default_transport": "stdio",
        "arguments": [],
        "required_env_vars": [],
        "optional_env_vars": ["FASTMCP_HOST", "FASTMCP_PORT", "TELECOM_BROWSER_MCP_DOCGEN"],
        "configuration_files": ["pyproject.toml"],
        "config_resolution_order": [
            "process env",
            "tool defaults",
        ],
        "external_runtime_dependencies": [
            "playwright browser binary",
            "target web application reachability",
        ],
        "safe_docgen_mode_available": True,
        "known_bootstrap_failures": [
            "environment_limit_missing_browser_binary",
            "permission_blocked",
            "environment_limit_unreachable_target",
        ],
        "provenance": {
            "entrypoint_type": "extracted",
            "launch_command": "extracted",
            "transport_modes_supported": "extracted",
            "default_transport": "extracted",
            "arguments": "extracted",
            "required_env_vars": "inferred",
            "optional_env_vars": "extracted",
            "configuration_files": "extracted",
            "config_resolution_order": "inferred",
            "external_runtime_dependencies": "inferred",
            "safe_docgen_mode_available": "inferred",
            "known_bootstrap_failures": "extracted",
        },
    }


@dataclass
class RegistryExport:
    snapshot: dict[str, Any]
    provenance_map: dict[str, Any]
    field_confidence_map: dict[str, Any]
    source_failures: list[dict[str, str]]


def _operational_confidence(tool_name: str) -> str:
    if tool_name in {"health", "capabilities", "list_sessions"}:
        return "verified"
    return "unverified"


def _side_effect_level(tool_name: str) -> str:
    if tool_name in {
        "health",
        "capabilities",
        "list_sessions",
        "get_active_session_snapshot",
        "get_peer_connection_summary",
        "diagnose_answer_failure",
    }:
        return "read"
    if tool_name in {"open_app", "close_session", "login_agent", "answer_call", "collect_debug_bundle"}:
        return "write"
    return "mixed"


def export_registry() -> RegistryExport:
    os.environ.setdefault("TELECOM_BROWSER_MCP_DOCGEN", "1")
    source_failures: list[dict[str, str]] = []

    snapshot_tools: list[dict[str, Any]] = []
    provenance_map: dict[str, Any] = {}
    field_confidence_map: dict[str, Any] = {}

    strategy = "runtime_export"
    try:
        server = create_mcp_server()
        runtime_tools = getattr(server, "_tool_manager")._tools
    except Exception as exc:
        strategy = "import_introspection"
        source_failures.append(
            {
                "source": "runtime_export",
                "error": str(exc),
                "classification": "extraction_failed",
            }
        )
        runtime_tools = {}

    if not runtime_tools:
        strategy = "static_contract_models"

    for tool_name in sorted(CANONICAL_TOOL_INPUT_MODELS.keys()):
        model = CANONICAL_TOOL_INPUT_MODELS[tool_name]
        input_schema = model.model_json_schema()

        required_fields = sorted(input_schema.get("required", []))
        optional_fields = sorted(set(input_schema.get("properties", {}).keys()) - set(required_fields))

        metadata_annotations: dict[str, Any] = {
            "side_effect_level": _side_effect_level(tool_name),
            "session_required": "session_id" in required_fields,
            "adapter_required": tool_name == "login_agent",
            "browser_required": tool_name
            in {
                "open_app",
                "close_session",
                "login_agent",
                "wait_for_ready",
                "wait_for_registration",
                "wait_for_incoming_call",
                "answer_call",
                "get_active_session_snapshot",
                "get_peer_connection_summary",
                "collect_debug_bundle",
                "diagnose_answer_failure",
            },
        }

        description = ""
        if tool_name in runtime_tools:
            description = (runtime_tools[tool_name].description or "").strip()
        if not description:
            description = TOOL_SUMMARY_HINTS.get(tool_name, "")

        snapshot_tools.append(
            {
                "tool_name": tool_name,
                "description": description,
                "input_schema": input_schema,
                "required_fields": required_fields,
                "optional_fields": optional_fields,
                "metadata_annotations": metadata_annotations,
                "provenance": {
                    "tool_name": "extracted",
                    "description": "extracted" if tool_name in runtime_tools else "inferred",
                    "input_schema": "extracted",
                    "required_fields": "extracted",
                    "optional_fields": "extracted",
                    "metadata_annotations": "inferred",
                },
            }
        )

        provenance_map[tool_name] = {
            "description": "runtime_registry" if tool_name in runtime_tools else "summary_hints",
            "input_schema": "canonical_tool_input_models",
            "metadata_annotations": "docgen_inference",
        }
        field_confidence_map[tool_name] = {
            "extraction_confidence": "high" if tool_name in runtime_tools else "medium",
            "operational_confidence": _operational_confidence(tool_name),
            "description": "medium" if tool_name in runtime_tools else "low",
            "input_schema": "high",
            "metadata_annotations": "medium",
        }

    snapshot = {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "safe_mode": os.environ.get("TELECOM_BROWSER_MCP_DOCGEN") == "1",
        "extraction_strategy_used": strategy,
        "tools": snapshot_tools,
    }

    return RegistryExport(
        snapshot=snapshot,
        provenance_map=provenance_map,
        field_confidence_map=field_confidence_map,
        source_failures=source_failures,
    )


def build_manifest(snapshot: dict[str, Any], generation_status: str, unknown_field_count: int, unavailable_sources: list[str]) -> dict[str, Any]:
    registry_hash = hashlib.sha256(_stable_json(snapshot).encode("utf-8")).hexdigest()
    return {
        "generation_status": generation_status,
        "extraction_strategy_used": snapshot.get("extraction_strategy_used", "unknown"),
        "unavailable_sources": unavailable_sources,
        "unknown_field_count": unknown_field_count,
        "registry_hash": registry_hash,
        "generation_commit": _git_commit(),
        "template_version": "v0.3",
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    exported = export_registry()
    startup = _startup_contract()

    _write_json(out_dir / "registry-snapshot.json", exported.snapshot)
    _write_json(out_dir / "startup-contract.json", startup)
    _write_json(out_dir / "provenance-map.json", exported.provenance_map)
    _write_json(out_dir / "field-confidence-map.json", exported.field_confidence_map)
    _write_json(out_dir / "source-failures.json", exported.source_failures)


if __name__ == "__main__":
    main()
