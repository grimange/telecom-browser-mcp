# Browser Launch Fix

Implemented:
- Updated Playwright launch configuration in `src/telecom_browser_mcp/browser/playwright_driver.py`:
  - default launch args: `--no-sandbox,--disable-setuid-sandbox,--disable-dev-shm-usage`
  - `chromium_sandbox=False`
  - env override: `TELECOM_BROWSER_MCP_CHROMIUM_ARGS`

Current host result:
- Browser lifecycle remains blocked with `host_runtime_constraint`.
- Chromium still exits with sandbox-host fatal `Operation not permitted`.

Interpretation:
- blocker is host policy/runtime behavior, not missing launch-arg coverage.
