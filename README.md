# telecom-browser-mcp

Telecom-aware browser MCP server for debugging WebRTC softphones and browser dialers with domain-specific tools.

## What it does

`telecom-browser-mcp` exposes telecom intent through MCP tools, including:

- session lifecycle: `open_app`, `list_sessions`, `close_session`, `reset_session`
- registration: `get_registration_status`, `wait_for_registration`, `assert_registered`
- inbound/answer flow: `wait_for_incoming_call`, `answer_call`, `hangup_call`
- runtime inspection: `get_active_session_snapshot`, `get_store_snapshot`, `get_peer_connection_summary`, `get_webrtc_stats`
- diagnostics and evidence: `diagnose_registration_failure`, `diagnose_incoming_call_failure`, `diagnose_answer_failure`, `collect_debug_bundle`

All tool outputs follow a structured response envelope with explicit failure metadata.

## Architecture

Package root: `src/telecom_browser_mcp/`

- `server/`: MCP entrypoints (`stdio`, `streamable-http`, `sse` compatibility)
- `sessions/`, `browser/`: browser lifecycle and session tracking
- `adapters/`: app-specific selectors/runtime hooks (APNTalk + generic scaffolds + harness)
- `inspectors/`: read-only inspection helpers
- `diagnostics/`: explainable failure analysis
- `evidence/`: artifact and debug-bundle generation
- `models/`: stable schemas and enums
- `tools/`: orchestration layer for MCP-exposed operations

## Install

```bash
python -m pip install -e .[dev]
python -m playwright install chromium
```

Or use the bootstrap script:

```bash
./scripts/bootstrap.sh
```

## Run

Default (stdio):

```bash
python -m telecom_browser_mcp
```

Explicit entrypoints:

```bash
telecom-browser-mcp-stdio
telecom-browser-mcp-http
telecom-browser-mcp-sse
```

## Environment

Copy `.env.example` and adjust:

- `TELECOM_BROWSER_MCP_TRANSPORT`
- `TELECOM_BROWSER_MCP_HOST`
- `TELECOM_BROWSER_MCP_PORT`
- `TELECOM_BROWSER_MCP_DEFAULT_ADAPTER`
- `TELECOM_BROWSER_MCP_ALLOWED_ORIGINS`
- `TELECOM_BROWSER_MCP_ARTIFACT_ROOT`

## Fake dialer harness

A deterministic harness fixture is provided at:

- `tests/fixtures/fake_dialer.html`
- `adapters/harness.py` for predictable registration/inbound/answer paths

Use `adapter_name="harness"` in tests and local tool-smoke runs.

## Testing

```bash
pytest -q
```

Test coverage currently focuses on:

- import/bootstrap integrity
- schema/envelope validation
- adapter registry shape
- harness-based integration flow
- stdio quickstart smoke behavior

Lifecycle fault-injection harness (deterministic crash/closure/stale-selector scenarios):

```bash
.venv/bin/python scripts/run_lifecycle_fault_harness.py
```

Browser diagnostics bundles (manifest + console/network/pageerror metadata):

```bash
# via MCP tools: collect_browser_logs / collect_debug_bundle
# artifacts are written under each session run directory in browser-diagnostics/
```

Diagnostics-aware validation integration:

```bash
.venv/bin/python scripts/validate_v0_2_contracts.py
```

Telecom UI failure signature library build:

```bash
.venv/bin/python scripts/build_failure_signature_library.py
```

Closed-loop pipeline governor orchestration:

```bash
.venv/bin/python scripts/run_pipeline_governor.py
```

Architecture guardrails pre/post governance checks:

```bash
.venv/bin/python scripts/run_architecture_guardrails.py
```

## Artifact layout

Debug bundles are written under:

```text
docs/audit/telecom-browser-mcp/YYYY-MM-DD/run-YYYYMMDDTHHMMSSZ/
```

Bundle contents include:

- `summary.json`
- `report.md`
- `runtime/*.json`
- screenshots/logs when available in environment

## Notes

- Browser launch failures are classified as environment limitations with structured failure output.
- Adapter-specific selectors and runtime hooks remain isolated in `adapters/`.
- v1 intentionally avoids arbitrary JS/selector tools.
