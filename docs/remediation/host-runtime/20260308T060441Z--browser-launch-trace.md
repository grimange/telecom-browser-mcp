# Browser Launch Trace

Inspected launch config:
- file: `src/telecom_browser_mcp/browser/playwright_driver.py`
- launch args: `--no-sandbox,--disable-setuid-sandbox,--disable-dev-shm-usage`
- `chromium_sandbox=False`

Observed launch logs still include Chromium fatal:
- `sandbox_host_linux.cc:41 ... Operation not permitted`

Interpretation:
- browser policy constraint remains active despite compatible launch flags.
