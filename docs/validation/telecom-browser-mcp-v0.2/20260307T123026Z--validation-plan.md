# Validation Plan (20260307T123026Z)

Scope: validate telecom-browser-mcp against v0.2 contracts across protocol, tools, lifecycle, telecom flow, diagnostics/evidence, failure modes, and interop.

Execution evidence:
- `.venv/bin/pytest -q` -> `15 passed in 0.15s`
- `.venv/bin/python scripts/run_mcp_interop_probe.py` -> timeout artifact: `docs/validation/telecom-browser-mcp-v0.2/artifacts/20260307T123030Z/logs/mcp-interop-probe.json`

Contract source precedence applied:
1. `docs/contracts/telecom-browser-mcp-v0.2*.md` (missing)
2. `docs/spec/telecom-browser-mcp*.md` (missing)
3. `README.md`
4. `docs/architecture/*.md` (missing)
5. source models/tool schemas
6. tests
7. previous validation/remediation artifacts
