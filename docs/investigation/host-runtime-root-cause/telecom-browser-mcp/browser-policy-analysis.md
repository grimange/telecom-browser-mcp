# Browser Policy Analysis

Standalone Playwright launch result:

- Command path: Playwright Chromium headless shell.
- Launch args included:
  - `--no-sandbox`
  - `--disable-setuid-sandbox`
  - `--disable-dev-shm-usage`
- Playwright launch option `chromium_sandbox=False` was also set.
- Result: failure before page creation with `TargetClosedError`.

Observed Chromium fatal:

- `FATAL:content/browser/sandbox_host_linux.cc:41`
- `Check failed: . shutdown: Operation not permitted (1)`

Direct binary reproduction:

- Direct `chrome-headless-shell --no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage --headless --dump-dom about:blank`
  fails with the same fatal and exit code `-5`.

Host context:

- WSL2 kernel: `6.6.87.2-microsoft-standard-WSL2`
- `NoNewPrivs: 1`
- `Seccomp: 2`

Dependency check:

- `ldd` resolves the browser's required shared libraries.
- Missing host dependency is not supported by the observed evidence.

Conclusion:

- The browser blocker is a host policy/runtime constraint, not a missing flag or missing library.
- `chromium_sandbox_policy_block` is the supported classification.
