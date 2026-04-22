# Live Verification Environment Notes

## Host Context

- OS: Linux `6.6.87.2-microsoft-standard-WSL2` on `x86_64`
- Shell: `/bin/bash`
- Python: `.venv/bin/python` -> `Python 3.12.3`

## Capability Checks

- Loopback socket creation:
  - sandboxed Codex runtime: blocked with `PermissionError: [Errno 1] Operation not permitted`
  - host-capable execution outside sandbox: verified with successful bind on `127.0.0.1`
- Subprocess stdio round-trip:
  - verified with a local Python subprocess echo probe returning `PING`

## Isolation / Restriction Notes

- The Codex sandbox still restricts loopback sockets and therefore cannot be used as evidence for live HTTP/SSE runtime compatibility.
- The host runtime used for escalated verification supports loopback socket creation and subprocess execution sufficiently for stdio, HTTP, and SSE smoke checks.
- No evidence of host-local firewall or container-network interference was observed during the successful host smoke runs.

## Verification Posture

- Transport compatibility claims in this pass are based on host-capable execution outside the sandbox.
- Sandbox-only socket failures remain classified as environment limitations, not product regressions.
