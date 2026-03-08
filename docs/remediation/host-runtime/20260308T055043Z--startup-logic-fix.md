# Startup Logic Fix

Implemented:
- Removed timeout-based startup proof from live verification.
- Startup stage is now derived from handshake startup states:
  - `process_spawned`
  - `awaiting_handshake`
  - `startup_timeout_without_handshake`
  - `startup_crash`
  - `startup_ready_via_handshake`

Current observed state on this host:
- `startup_timeout_without_handshake`

Impact:
- startup is truthfully `blocked` until initialize response is observed.
