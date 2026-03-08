# Probe Execution Log (20260308T005518Z)

- Sandbox project probe command: `.venv/bin/python scripts/run_mcp_interop_probe.py --timeout-seconds 20 --step-timeout-seconds 10`
- Sandbox project artifact: `docs/validation/telecom-browser-mcp-v0.2/artifacts/20260308T005119Z/logs/mcp-interop-probe.json`
- Sandbox project result: `ok=False classification=environment_blocked_stdio_no_response failure=initialize_timeout_no_server_response phase=initialize`

- Sandbox minimal control probe command: `.venv/bin/python` one-off minimal FastMCP stdio differential probe
- Sandbox minimal control artifact: `docs/closed-loop/telecom-browser-mcp/20260308T005208Z--minimal-control-probe.json`
- Sandbox minimal control result: `ok=False classification=environment_blocked_stdio_no_response failure=initialize_timeout_no_server_response phase=initialize`

- Host project probe command: `.venv/bin/python scripts/run_mcp_interop_probe.py --timeout-seconds 20 --step-timeout-seconds 10` (outside sandbox)
- Host project artifact: `docs/validation/telecom-browser-mcp-v0.2/artifacts/20260308T005343Z/logs/mcp-interop-probe.json`
- Host project result: `ok=True tool_count=25 phase=initialize/list_tools`

- Host minimal control probe command: `.venv/bin/python` one-off minimal FastMCP stdio differential probe (outside sandbox)
- Host minimal control artifact: `docs/closed-loop/telecom-browser-mcp/20260308T005405Z--minimal-control-probe.json`
- Host minimal control result: `ok=True tool_count=0 phase=list_tools`
