# Investigation Plan (20260308T005518Z)

## Objective
Determine whether MCP stdio no-response is project-specific or execution-environment specific using a 2x2 matrix.

## Prior blocked cycle inputs
- `docs/closed-loop/telecom-browser-mcp/20260308T003457Z--cycle-summary.json`
- `docs/closed-loop/telecom-browser-mcp/20260308T003457Z--transport-triage.json`
- `docs/closed-loop/telecom-browser-mcp/20260308T003457Z--execution-context-differential.md`
- `docs/closed-loop/telecom-browser-mcp/20260308T003457Z--cycle-verdict.json`

## Probe commands
1. Sandbox / Project: `.venv/bin/python scripts/run_mcp_interop_probe.py --timeout-seconds 20 --step-timeout-seconds 10`
2. Sandbox / Minimal Control: `.venv/bin/python` one-off client probe to a standalone FastMCP stdio server.
3. Host / Project: same as #1 executed outside sandbox.
4. Host / Minimal Control: same as #2 executed outside sandbox.

## Decision policy
Apply decision table from `docs/pipelines/investigate_mcp_stdio_no_response_outside_sandbox.md`, then emit classification and re-entry guidance.
