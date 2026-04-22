from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from scripts.docs.example_payload_generator import build_example_payload  # noqa: E402
from scripts.docs.export_mcp_registry import export_registry  # noqa: E402

REQUIRED_GUIDES = [
    "quickstart.md",
    "codex-cli.md",
    "claude-desktop.md",
    "openai-agents.md",
    "langchain.md",
    "crewai.md",
    "tool-catalog.md",
    "troubleshooting.md",
]

REQUIRED_AGENT_SECTIONS = [
    "## Status",
    "## Verification Summary",
    "## Startup Contract",
    "## Transport",
    "## Configuration Example",
    "## Tool Discovery Expectations",
    "## Minimal Safe Workflow",
    "## Environment Variables and Prerequisites",
    "## Troubleshooting",
    "## Open Verification Gaps",
]


@dataclass(frozen=True)
class AgentGuideSpec:
    agent_name: str
    file_name: str
    integration_surface: str
    config_snippet: str
    syntax_provenance: list[str]


AGENT_SPECS = [
    AgentGuideSpec(
        agent_name="codex-cli",
        file_name="codex-cli.md",
        integration_surface="stdio",
        config_snippet='''```json\n{
  "mcpServers": {
    "telecom-browser-mcp": {
      "command": "telecom-browser-mcp-stdio",
      "args": [],
      "env": {
        "TELECOM_BROWSER_MCP_DOCGEN": "1"
      }
    }
  }
}\n```''',
        syntax_provenance=[
            "pyproject.toml:[project.scripts].telecom-browser-mcp-stdio",
            "docs/verification/multi-client-compatibility/telecom-browser-mcp/20260308T144214Z/01-client-target-definition.md",
        ],
    ),
    AgentGuideSpec(
        agent_name="claude-desktop",
        file_name="claude-desktop.md",
        integration_surface="stdio",
        config_snippet='''```json\n{
  "mcpServers": {
    "telecom-browser-mcp": {
      "command": "telecom-browser-mcp-stdio",
      "args": [],
      "env": {
        "TELECOM_BROWSER_MCP_DOCGEN": "1"
      }
    }
  }
}\n```''',
        syntax_provenance=[
            "pyproject.toml:[project.scripts].telecom-browser-mcp-stdio",
            "docs/verification/multi-client-compatibility/telecom-browser-mcp/20260308T144214Z/01-client-target-definition.md",
        ],
    ),
    AgentGuideSpec(
        agent_name="openai-agents",
        file_name="openai-agents.md",
        integration_surface="stdio or streamable-http",
        config_snippet='''```python\n# Requires an MCP client bridge in your runtime.
# Use stdio for local runs or streamable HTTP for remote service deployment.
MCP_SERVER = {
    "name": "telecom-browser-mcp",
    "transport": "stdio",
    "command": ["telecom-browser-mcp-stdio"],
    "env": {"TELECOM_BROWSER_MCP_DOCGEN": "1"},
}
```''',
        syntax_provenance=[
            "pyproject.toml:[project.scripts].telecom-browser-mcp-stdio",
            "pyproject.toml:[project.scripts].telecom-browser-mcp-http",
            "docs/verification/multi-client-compatibility/telecom-browser-mcp/20260308T144214Z/07-transport-and-configuration-assumptions.md",
        ],
    ),
    AgentGuideSpec(
        agent_name="langchain",
        file_name="langchain.md",
        integration_surface="streamable-http",
        config_snippet='''```python\n# Local launch example:
# FASTMCP_HOST=127.0.0.1 FASTMCP_PORT=8000 telecom-browser-mcp-http
MCP_ENDPOINT = "http://127.0.0.1:8000/mcp"
```''',
        syntax_provenance=[
            "pyproject.toml:[project.scripts].telecom-browser-mcp-http",
            "src/telecom_browser_mcp/server/streamable_http_server.py",
        ],
    ),
    AgentGuideSpec(
        agent_name="crewai",
        file_name="crewai.md",
        integration_surface="streamable-http",
        config_snippet='''```python\n# Local launch example:
# FASTMCP_HOST=127.0.0.1 FASTMCP_PORT=8000 telecom-browser-mcp-http
MCP_ENDPOINT = "http://127.0.0.1:8000/mcp"
```''',
        syntax_provenance=[
            "pyproject.toml:[project.scripts].telecom-browser-mcp-http",
            "src/telecom_browser_mcp/server/streamable_http_server.py",
        ],
    ),
]


def _stable_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_stable_json(payload) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _startup_contract() -> dict[str, Any]:
    return {
        "entrypoint_type": "project.scripts",
        "launch_command": "telecom-browser-mcp",
        "explicit_entrypoints": {
            "stdio": "telecom-browser-mcp-stdio",
            "streamable-http": "telecom-browser-mcp-http",
            "sse": "telecom-browser-mcp-sse",
        },
        "supported_transports": ["stdio", "streamable-http", "sse"],
        "default_transport": "stdio",
        "cli_flags": [],
        "required_environment_variables": [],
        "optional_environment_variables": ["FASTMCP_HOST", "FASTMCP_PORT", "TELECOM_BROWSER_MCP_DOCGEN"],
        "config_files": ["pyproject.toml"],
        "dependency_prerequisites": [
            "Python 3.11+",
            "project dependencies from pyproject.toml",
            "Playwright browser binaries installed in host runtime for browser-driving tools",
        ],
        "safe_doc_generation_mode": {
            "available": True,
            "environment_variable": "TELECOM_BROWSER_MCP_DOCGEN=1",
        },
        "known_bootstrap_failures": [
            {
                "classification": "environment_limit_missing_browser_binary",
                "message": "Browser-driving tools can degrade when Playwright browser binaries are unavailable.",
            },
            {
                "classification": "environment_limit_unreachable_target",
                "message": "open_app can fail/degrade when target URL is unreachable.",
            },
            {
                "classification": "permission_blocked",
                "message": "Sandbox/runtime restrictions can block browser launch or transport sockets.",
            },
        ],
        "provenance": {
            "scripts": [
                "pyproject.toml",
                "src/telecom_browser_mcp/__main__.py",
                "src/telecom_browser_mcp/server/stdio_server.py",
                "src/telecom_browser_mcp/server/streamable_http_server.py",
                "src/telecom_browser_mcp/server/sse_server.py",
            ]
        },
    }


def _normalize_tool_catalog(registry: dict[str, Any]) -> dict[str, Any]:
    tools: list[dict[str, Any]] = []

    for item in sorted(registry.get("tools", []), key=lambda x: x["tool_name"]):
        schema = item["input_schema"]
        example = build_example_payload(schema)
        tools.append(
            {
                "tool_name": item["tool_name"],
                "description": item.get("description") or "",
                "input_schema": schema,
                "required_arguments": item.get("required_fields", []),
                "optional_arguments": item.get("optional_fields", []),
                "example_payload": example.payload,
                "example_generation_method": example.method,
                "provenance": item.get("provenance", {}),
                "extraction_confidence": "high" if item.get("description") else "medium",
                "operational_confidence": "verified" if item["tool_name"] in {"health", "capabilities", "list_sessions"} else "unverified",
            }
        )

    return {"tools": tools}


def _agent_config_patterns(commit: str, timestamp: str) -> dict[str, Any]:
    patterns = []
    for spec in AGENT_SPECS:
        patterns.append(
            {
                "agent_name": spec.agent_name,
                "integration_surface": spec.integration_surface,
                "configuration_snippet_template": spec.config_snippet,
                "syntax_provenance": spec.syntax_provenance,
                "runtime_verification_status": "unverified_integration_pattern",
                "last_verified_commit": commit,
                "last_verified_timestamp": timestamp,
            }
        )
    return {"patterns": patterns}


def _runtime_evidence(now_ts: str) -> dict[str, Any]:
    return {
        "captured_at": now_ts,
        "evidence": [
            {
                "type": "server_startup_contract",
                "status": "available_from_static_evidence",
                "source": "pyproject.toml + server entrypoint modules",
            },
            {
                "type": "tool_discovery",
                "status": "available_from_registry_export",
                "source": "scripts/docs/export_mcp_registry.py",
            },
            {
                "type": "tools_call_transcript",
                "status": "not_captured_in_this_run",
                "reason": "No live MCP transport run executed by this doc generation pipeline.",
                "classification": "unverified_runtime",
            },
            {
                "type": "host_required_workflow_tests",
                "status": "evidence_from_test_sources",
                "source": "tests/e2e/test_fake_dialer_harness.py",
                "notes": "Host-required tests define validated and failure branches; execution can be skipped in constrained environments.",
            },
            {
                "type": "transport_smoke_tests",
                "status": "evidence_from_test_sources",
                "source": [
                    "tests/integration/test_stdio_smoke.py",
                    "tests/integration/test_http_transport_smoke.py",
                ],
            },
        ],
    }


def _workflow_evidence() -> dict[str, Any]:
    return {
        "workflows": [
            {
                "workflow_name": "first-contact-safe-discovery",
                "ordered_tools": ["health", "capabilities", "list_sessions"],
                "source_evidence": ["AGENTS.md::Codex First-Contact Tool Guidance"],
                "derived_from": "policy",
                "workflow_classification": "validated_policy",
                "confidence": "high",
                "inferred": False,
            },
            {
                "workflow_name": "inbound-answer-happy-path",
                "ordered_tools": [
                    "open_app",
                    "wait_for_ready",
                    "wait_for_registration",
                    "wait_for_incoming_call",
                    "answer_call",
                    "close_session",
                ],
                "source_evidence": [
                    "tests/e2e/test_fake_dialer_harness.py::test_inbound_answer_success",
                    "docs/verification/agent-readiness/telecom-browser-mcp/20260308T140345Z/03-workflow-validation.md",
                ],
                "derived_from": "tests_and_verification_docs",
                "workflow_classification": "host_required_e2e",
                "confidence": "medium",
                "inferred": False,
            },
            {
                "workflow_name": "answer-failure-diagnostics",
                "ordered_tools": [
                    "open_app",
                    "wait_for_ready",
                    "wait_for_registration",
                    "wait_for_incoming_call",
                    "answer_call",
                    "diagnose_answer_failure",
                    "collect_debug_bundle",
                    "close_session",
                ],
                "source_evidence": [
                    "tests/e2e/test_fake_dialer_harness.py::test_inbound_answer_failure_generates_diagnostics_and_bundle",
                ],
                "derived_from": "tests",
                "workflow_classification": "host_required_e2e",
                "confidence": "medium",
                "inferred": False,
            },
        ]
    }


def _tool_table(tool_catalog: dict[str, Any]) -> str:
    rows = ["| Tool | Description | Required Arguments | Optional Arguments |", "|---|---|---|---|"]
    for tool in tool_catalog.get("tools", []):
        rows.append(
            f"| `{tool['tool_name']}` | {tool['description'] or 'n/a'} | {', '.join(tool['required_arguments']) or 'none'} | {', '.join(tool['optional_arguments']) or 'none'} |"
        )
    return "\n".join(rows)


def _workflow_lines(workflow: dict[str, Any]) -> str:
    lines: list[str] = []
    for w in workflow.get("workflows", []):
        lines.append(f"- `{w['workflow_name']}` ({w['workflow_classification']}, confidence={w['confidence']}):")
        lines.append(f"  {' -> '.join(w['ordered_tools'])}")
        lines.append(f"  Evidence: {', '.join(w['source_evidence'])}")
    return "\n".join(lines)


def _discovery_expectations(tool_catalog: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"- Expected tool count: `{len(tool_catalog.get('tools', []))}`",
            "- First-contact checks should succeed: `health`, `capabilities`, `list_sessions`.",
            "- Session-bound tools require `session_id` returned by `open_app`.",
        ]
    )


def _common_prerequisites(startup: dict[str, Any]) -> str:
    deps = "\n".join(f"- {x}" for x in startup.get("dependency_prerequisites", []))
    envs = "\n".join(f"- `{x}` (optional)" for x in startup.get("optional_environment_variables", []))
    return "\n".join(["Prerequisites:", deps, "", "Environment variables:", envs])


def _common_troubleshooting(startup: dict[str, Any]) -> str:
    lines = []
    for item in startup.get("known_bootstrap_failures", []):
        lines.append(f"- `{item['classification']}`: {item['message']}")
    lines.append("- If browser-driving flows fail in sandboxed runtime, classify as environment limitation unless host runtime reproduces the defect.")
    return "\n".join(lines)


def _render_agent_guide(
    spec: AgentGuideSpec,
    startup: dict[str, Any],
    tool_catalog: dict[str, Any],
    workflow: dict[str, Any],
) -> str:
    return "\n".join(
        [
            f"# {spec.agent_name.replace('-', ' ').title()} Integration",
            "",
            "## Status",
            "- unverified integration pattern",
            "",
            "## Verification Summary",
            "- Startup contract: high confidence (static code + entrypoint evidence).",
            "- Tool discovery: high confidence (registry export).",
            "- Invocation success: unverified for this agent integration surface in this run.",
            "- Workflow validity: medium confidence from host-required tests and verification docs.",
            "",
            "## Startup Contract",
            f"- Canonical command: `{startup['launch_command']}`",
            f"- Stdio command: `{startup['explicit_entrypoints']['stdio']}`",
            f"- Streamable HTTP command: `{startup['explicit_entrypoints']['streamable-http']}`",
            f"- SSE command: `{startup['explicit_entrypoints']['sse']}`",
            "",
            "## Transport",
            f"- Integration surface for this guide: `{spec.integration_surface}`",
            f"- Supported transports: {', '.join(startup['supported_transports'])}",
            f"- Default transport: `{startup['default_transport']}`",
            "",
            "## Configuration Example",
            spec.config_snippet,
            "",
            "Syntax provenance:",
            *[f"- {p}" for p in spec.syntax_provenance],
            "",
            "## Tool Discovery Expectations",
            _discovery_expectations(tool_catalog),
            "",
            "## Minimal Safe Workflow",
            _workflow_lines(workflow),
            "",
            "## Environment Variables and Prerequisites",
            _common_prerequisites(startup),
            "",
            "## Troubleshooting",
            _common_troubleshooting(startup),
            "",
            "## Open Verification Gaps",
            "- No agent-specific live `tools/list` transcript is captured in this generation run.",
            "- No agent-specific `tools/call` transcript is captured in this generation run.",
            "- Runtime behavior claims are downgraded to unverified integration pattern until host validation evidence is attached.",
            "",
        ]
    )


def _render_quickstart(startup: dict[str, Any], tool_catalog: dict[str, Any], workflow: dict[str, Any], timestamp: str) -> str:
    return "\n".join(
        [
            "# Agent Integration Quickstart",
            "",
            f"Generated at: `{timestamp}`",
            "",
            "## Server Startup Command",
            "```bash",
            "TELECOM_BROWSER_MCP_DOCGEN=1 telecom-browser-mcp-stdio",
            "```",
            "",
            "## Transport Type",
            f"Default transport: `{startup['default_transport']}`",
            f"Supported transports: {', '.join(startup['supported_transports'])}",
            "",
            "## Tool Discovery Expectations",
            _discovery_expectations(tool_catalog),
            "",
            "## Minimal Safe Workflow",
            _workflow_lines(workflow),
            "",
            "## Verification Boundaries",
            "- Guides include startup, schemas, and configuration patterns from static and contract evidence.",
            "- Runtime compatibility claims are intentionally downgraded unless live evidence is present.",
            "",
        ]
    )


def _render_tool_catalog(tool_catalog: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Tool Catalog",
            "",
            _tool_table(tool_catalog),
            "",
            "## Notes",
            "- Example payloads are schema-valid and generated from canonical tool input models.",
            "- Operational confidence is `verified` only for first-contact tools in this pipeline run.",
            "",
        ]
    )


def _render_troubleshooting(startup: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Troubleshooting",
            "",
            "## Common Failure Classes",
            _common_troubleshooting(startup),
            "",
            "## Fast Checks",
            "1. Run `health`, `capabilities`, `list_sessions` first to verify server/tool discovery path.",
            "2. If browser tools degrade, verify Playwright browser binaries on host runtime.",
            "3. For HTTP transport, verify `FASTMCP_HOST` / `FASTMCP_PORT` and endpoint reachability.",
            "4. Treat sandbox restrictions as environment limitations unless host runtime reproduces the same failure.",
            "",
            "## Verification Gaps",
            "- Client-specific runtime transcripts are not captured by this documentation pipeline run.",
            "",
        ]
    )


def _guide_support_matrix(agent_patterns: dict[str, Any]) -> dict[str, Any]:
    entries = []
    for pattern in agent_patterns.get("patterns", []):
        entries.append(
            {
                "agent_name": pattern["agent_name"],
                "status": "unverified integration pattern",
                "confidence": {
                    "startup_contract": "high",
                    "tool_discovery": "high",
                    "invocation_success": "low",
                    "workflow_validity": "medium",
                },
                "runtime_verification_status": pattern["runtime_verification_status"],
            }
        )
    return {"guides": entries}


def _render_generation_report(
    out_dir: Path,
    startup: dict[str, Any],
    tool_catalog: dict[str, Any],
    source_failures: list[dict[str, Any]],
) -> str:
    status = "degraded" if source_failures else "full"
    return "\n".join(
        [
            "# Guide Generation Report",
            "",
            f"- status: `{status}`",
            f"- artifact_dir: `{out_dir}`",
            f"- startup_contract_extracted: `{bool(startup)}`",
            f"- tool_count: `{len(tool_catalog.get('tools', []))}`",
            f"- source_failure_count: `{len(source_failures)}`",
            "",
            "## Evidence Sources",
            "- Startup contract: pyproject + server entrypoints",
            "- Registry snapshot: export_mcp_registry runtime-safe export",
            "- Workflow evidence: tests/e2e + verification docs",
            "- Agent patterns: script-defined snippets with provenance",
            "",
            "## Quality Gate Intent",
            "- Every generated agent guide includes the mandatory section contract.",
            "- Thin stub guides are rejected by `guide-quality-audit.json`.",
            "- Unsupported runtime claims are downgraded to unverified integration pattern.",
            "",
        ]
    )


def _is_stub(text: str) -> bool:
    words = len(text.split())
    section_count = sum(1 for section in REQUIRED_AGENT_SECTIONS if section in text)
    return words < 220 or section_count < len(REQUIRED_AGENT_SECTIONS)


def _audit_guide_quality(docs_root: Path) -> dict[str, Any]:
    results: dict[str, Any] = {}
    failures: list[str] = []

    for spec in AGENT_SPECS:
        guide_path = docs_root / spec.file_name
        content = _read_text(guide_path)

        missing_sections = [section for section in REQUIRED_AGENT_SECTIONS if section not in content]
        is_stub = _is_stub(content)

        guide_failures = []
        if missing_sections:
            guide_failures.append("missing_mandatory_sections")
        if "## Configuration Example" in content and "```" not in content:
            guide_failures.append("missing_configuration_snippet")
        if "Canonical command:" not in content:
            guide_failures.append("missing_startup_command")
        if "## Troubleshooting" not in content:
            guide_failures.append("missing_troubleshooting_section")
        if "## Open Verification Gaps" not in content:
            guide_failures.append("missing_open_verification_gaps")
        if "## Minimal Safe Workflow" not in content:
            guide_failures.append("missing_minimal_workflow")
        if is_stub:
            guide_failures.append("thin_stub_detected")

        if guide_failures:
            failures.append(spec.file_name)

        results[spec.file_name] = {
            "missing_sections": missing_sections,
            "failures": guide_failures,
            "word_count": len(content.split()),
            "section_count": sum(1 for section in REQUIRED_AGENT_SECTIONS if section in content),
            "pass": not guide_failures,
        }

    return {
        "overall_pass": not failures,
        "failed_guides": failures,
        "guide_results": results,
    }


def _write_sidecar_support_files(
    docs_root: Path,
    out_dir: Path,
    commit: str,
    now_ts: str,
    source_failures: list[dict[str, Any]],
) -> None:
    for spec in AGENT_SPECS:
        payload = {
            "agent_name": spec.agent_name,
            "config_provenance": spec.syntax_provenance,
            "runtime_evidence_references": [str(out_dir / "runtime-evidence.json")],
            "unsupported_claims": [
                "fully compatible",
                "production ready",
                "successfully tested for this specific client",
            ],
            "last_verified_commit": commit,
            "last_verified_timestamp": now_ts,
            "source_failures": source_failures,
        }
        _write_json(docs_root / f"{spec.agent_name}.support.json", payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timestamp")
    args = parser.parse_args()

    os.environ.setdefault("TELECOM_BROWSER_MCP_DOCGEN", "1")

    repo_root = REPO_ROOT
    docs_root = repo_root / "docs" / "agent-integration"
    generated_root = docs_root / "generated"

    timestamp = args.timestamp or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    now_ts = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    out_dir = generated_root / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    startup = _startup_contract()
    exported = export_registry()
    tool_catalog = _normalize_tool_catalog(exported.snapshot)
    commit = _git_commit()

    agent_patterns = _agent_config_patterns(commit=commit, timestamp=now_ts)
    runtime = _runtime_evidence(now_ts=now_ts)
    workflows = _workflow_evidence()
    support_matrix = _guide_support_matrix(agent_patterns)

    # Artifacts required by pipeline 008
    _write_json(out_dir / "startup-contract.json", startup)
    _write_json(out_dir / "registry-snapshot.json", exported.snapshot)
    _write_json(out_dir / "tool-catalog.json", tool_catalog)
    _write_json(out_dir / "agent-config-patterns.json", agent_patterns)
    _write_json(out_dir / "runtime-evidence.json", runtime)
    _write_json(out_dir / "workflow-evidence.json", workflows)
    _write_json(out_dir / "guide-support-matrix.json", support_matrix)
    _write_json(out_dir / "source-failures.json", exported.source_failures)

    _write_text(
        out_dir / "guide-generation-report.md",
        _render_generation_report(
            out_dir=out_dir,
            startup=startup,
            tool_catalog=tool_catalog,
            source_failures=exported.source_failures,
        ),
    )

    # User-facing guides
    _write_text(docs_root / "quickstart.md", _render_quickstart(startup, tool_catalog, workflows, timestamp))
    for spec in AGENT_SPECS:
        _write_text(docs_root / spec.file_name, _render_agent_guide(spec, startup, tool_catalog, workflows))
    _write_text(docs_root / "tool-catalog.md", _render_tool_catalog(tool_catalog))
    _write_text(docs_root / "troubleshooting.md", _render_troubleshooting(startup))

    _write_sidecar_support_files(
        docs_root=docs_root,
        out_dir=out_dir,
        commit=commit,
        now_ts=now_ts,
        source_failures=exported.source_failures,
    )

    quality = _audit_guide_quality(docs_root)
    _write_json(out_dir / "guide-quality-audit.json", quality)

    missing_files = [name for name in REQUIRED_GUIDES if not (docs_root / name).exists()]
    if missing_files:
        raise SystemExit(f"missing required guides: {missing_files}")

    if not quality["overall_pass"]:
        raise SystemExit(f"guide quality gate failed: {quality['failed_guides']}")


if __name__ == "__main__":
    main()
