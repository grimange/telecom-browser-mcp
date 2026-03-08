# Codex MCP Add Examples

## Canonical

```bash
codex mcp add telecom-browser -- python -m telecom_browser_mcp
```

## Console script variant

```bash
codex mcp add telecom-browser -- telecom-browser-mcp-stdio
```

## Validation after registration

```bash
.venv/bin/python scripts/run_mcp_interop_probe.py --timeout-seconds 30 --step-timeout-seconds 10 --retry-count 1
```

Expected readiness signal:

- `ok=true`
- `stable_discovery=true`
- `tool_count=25`

If sandbox output is `environment_blocked_stdio_no_response`, escalate to host evidence workflow instead of immediate code remediation.
