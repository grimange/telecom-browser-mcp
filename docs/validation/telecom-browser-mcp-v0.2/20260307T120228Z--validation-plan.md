# Validation Plan (20260307T120228Z)

Scope: validate telecom-browser-mcp against v0.2 contracts across protocol, tool, lifecycle, telecom-flow, diagnostics, failure-mode, and interop layers.

Execution evidence:
- `.venv/bin/pytest -q` -> `13 passed in 0.14s`
- `.venv/bin/python scripts/run_mcp_interop_probe.py` -> timeout artifact at `docs/validation/telecom-browser-mcp-v0.2/artifacts/20260307T120117Z/logs/mcp-interop-probe.json`

Contract source precedence applied:
1. `docs/contracts/telecom-browser-mcp-v0.2*.md` (missing)
2. `docs/spec/telecom-browser-mcp*.md` (missing)
3. `README.md`
4. `docs/architecture/*.md` (missing)
5. Source models/tool schemas under `src/telecom_browser_mcp/models/`
6. Tests under `tests/`
7. Prior validation/remediation artifacts under `docs/validation/` and `docs/remediation/`

Method:
- Build a canonical tool contract inventory from `docs/telecom-browser-mcp-implementation-plan-v0.2.md` section 11 + `src/telecom_browser_mcp/server/stdio_server.py` `TOOL_NAMES`.
- Validate envelope/schema behavior from model tests and orchestrator behavior.
- Validate protocol/interop using the stdio probe script and classify environment limits explicitly.
