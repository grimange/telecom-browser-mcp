# Operator Setup Checklist

## Environment

- [ ] Python 3.11+ available
- [ ] Virtualenv created and activated (or direct `.venv/bin/python` usage)
- [ ] Dependencies installed: `python -m pip install -e .[dev]`
- [ ] (For browser-driving checks) Playwright Chromium installed: `python -m playwright install chromium`

## MCP registration

- [ ] Run: `codex mcp add telecom-browser -- python -m telecom_browser_mcp`
- [ ] Confirm command works from repository root or set explicit `cwd`

## Validation

- [ ] Run handshake probe: `.venv/bin/python scripts/run_mcp_interop_probe.py`
- [ ] Confirm `mcp-interop-probe.json` artifact is generated
- [ ] Confirm host runtime result is `ok=true` before declaring integration blocker

## Host-only telecom checks

- [ ] Use host/runtime with Chromium launch capability
- [ ] Run telecom tools (`open_app`, `wait_for_registration`, `answer_call`) only in host-capable runtime

## Interpretation rules

- [ ] Sandbox-only stdio no-response => environment limitation
- [ ] Host reproducible failure => integration/product remediation candidate
