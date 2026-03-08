# MCP Registration Checklist

## Canonical command

- [x] Canonical registration command documented:
  - `codex mcp add telecom-browser -- python -m telecom_browser_mcp`
- [x] Alternate console-script command documented:
  - `codex mcp add telecom-browser -- telecom-browser-mcp-stdio`

## Launch determinism

- [x] Python module entrypoint exists: `src/telecom_browser_mcp/__main__.py`
- [x] Console scripts declared in `pyproject.toml`
- [x] Main stdio server tool registration list is static (`TOOL_NAMES`)

## Environment expectations

- [x] Required Python/runtime requirements documented
- [x] Environment variables listed in `.env.example` and `README.md`
- [x] Working directory assumption documented (`cwd` set to repo root in example config)
- [x] Virtualenv usage documented (examples use `.venv/bin/python`)

## Operator verification

- [x] Interop probe command documented: `scripts/run_mcp_interop_probe.py`
- [x] Artifact output path documented for probe logs

## Outcome

Registration readiness: `ready`
