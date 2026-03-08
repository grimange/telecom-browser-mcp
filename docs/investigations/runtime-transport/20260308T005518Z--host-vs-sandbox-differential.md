# Host vs Sandbox Differential (20260308T005518Z)

## 2x2 Matrix Summary
- A Sandbox/Project: `initialize_response_received=False` classification=`environment_blocked_stdio_no_response`
- B Sandbox/Minimal: `initialize_response_received=False` classification=`environment_blocked_stdio_no_response`
- C Host/Project: `initialize_response_received=True` classification=`ok`
- D Host/Minimal: `initialize_response_received=True` classification=`ok`

## Decision table match
Matched Case D (sandbox fails, host works): `sandbox_only_execution_blocker`.

## Supporting signal
Case A condition also holds for minimal control (sandbox minimal fails, host minimal works), reinforcing a runner-level transport issue rather than project logic.
