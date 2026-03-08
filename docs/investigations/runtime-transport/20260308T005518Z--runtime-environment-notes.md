# Runtime Environment Notes (20260308T005518Z)

## Repository and interpreter
- git_revision: `f3322921338158e2312e4541b8a32a83ba7a352c`
- python_version: `3.12.3`
- python_executable: `/home/ramjf/python-projects/telecom-browser-mcp/.venv/bin/python`
- platform: `Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.39`

## Observed transport differential
- sandbox: both project and minimal control timed out in initialize with no stderr output.
- host (outside sandbox): both project and minimal control completed initialize/list-tools successfully.

## Implication
The failure behavior does not reproduce on host using the same repository and interpreter path. Evidence points to sandbox execution constraints affecting stdio transport/handshake.
