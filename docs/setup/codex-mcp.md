# Codex MCP Setup

## Canonical registration

Run from repository root:

```bash
codex mcp add telecom-browser -- python -m telecom_browser_mcp
```

Alternative command:

```bash
codex mcp add telecom-browser -- telecom-browser-mcp-stdio
```

## Config example

```toml
[mcp_servers.telecom-browser]
command = "python"
args = ["-m", "telecom_browser_mcp"]
cwd = "/home/ramjf/python-projects/telecom-browser-mcp"
```

## Environment expectations

- Python 3.11+ and dependencies installed (`python -m pip install -e .[dev]`)
- MCP package importable in active runtime
- Optional browser checks: `python -m playwright install chromium`

## Validation

Run probe:

```bash
.venv/bin/python scripts/run_mcp_interop_probe.py
```

Expected output:

- JSON artifact path under `docs/validation/telecom-browser-mcp-v0.2/artifacts/<timestamp>/logs/`
- `ok=true` for handshake readiness in host-approved runtime
