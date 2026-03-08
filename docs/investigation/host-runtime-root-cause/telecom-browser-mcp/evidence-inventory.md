# Evidence Inventory

Primary durable evidence:

- `docs/validation/telecom-browser-mcp-v0.2/artifacts/20260308T070104Z/logs/mcp-interop-probe.json`
  - Official MCP Python SDK client probe.
  - Result: `environment_blocked_stdio_no_response`.
- `docs/validation/telecom-browser-mcp-v0.2/artifacts/20260308T070104Z/logs/mcp-interop-probe-stderr.log`
  - Result: `0` bytes.
- `docs/live-verification/telecom-browser-mcp/evidence/mcp-interop-probe.json`
  - Raw newline-delimited JSON handshake probe.
  - Result: `handshake_timeout`, no responses recorded.
- `docs/live-verification/telecom-browser-mcp/evidence/live-tool-checks.json`
  - Integrated browser lifecycle failure.
  - Result: `TargetClosedError` with Chromium fatal `sandbox_host_linux.cc:41`.

Source and implementation evidence:

- `src/telecom_browser_mcp/server/stdio_server.py`
  - Current server startup path and custom stdio bridge.
- `src/telecom_browser_mcp/mcp_handshake_probe.py`
  - Raw probe framing and timeout behavior.
- `scripts/run_mcp_interop_probe.py`
  - Official MCP SDK client probe and timeout classification logic.
- `.venv/lib/python3.12/site-packages/mcp/server/stdio.py`
  - SDK server stdio transport uses `anyio.wrap_file(TextIOWrapper(sys.stdin.buffer, ...))`.
- `.venv/lib/python3.12/site-packages/mcp/client/stdio/__init__.py`
  - SDK client uses subprocess pipes and newline-delimited JSON.

Control experiment outputs captured during this investigation:

- Server startup timings:
  - `TelecomBrowserApp()` init: `0.000052s`
  - `FastMCP()` init: `0.002094s`
  - Tool registration: `0.012285s`
- Idle server contamination check:
  - `stdout_bytes=0`
  - `stderr_bytes=0`
  - process remains alive while idle
- Stdin controls:
  - Plain subprocess child using `sys.stdin.readline()` returns `PLAIN:hello\n`.
  - Child using `anyio.to_thread.run_sync(sys.stdin.readline)` times out after 3s.
  - Child using `anyio.wrap_file(TextIOWrapper(sys.stdin.buffer, ...))` times out after 3s.
- Standalone Playwright launch:
  - Fails before page creation with `TargetClosedError`.
  - Chromium stderr contains `FATAL:content/browser/sandbox_host_linux.cc:41`.
- Direct `chrome-headless-shell` launch:
  - Exit code `-5`.
  - Same fatal `sandbox_host_linux.cc:41`.
- Host fingerprint:
  - Kernel: `Linux 6.6.87.2-microsoft-standard-WSL2`
  - `NoNewPrivs: 1`
  - `Seccomp: 2`
  - `mcp=1.26.0`, `anyio=4.12.1`, `playwright=1.58.0`

Dependency evidence:

- `ldd` for `chrome-headless-shell` resolves required shared libraries including `libnspr4.so` and `libnss3.so`.
- This rejects the missing-library hypothesis for the observed browser failure.
