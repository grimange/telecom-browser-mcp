# 08a - Runtime Failure Attribution

## Initial Failures (Observed Earlier in This Session)
- SSE/HTTP startup timeout due module entrypoint and port bootstrap issues.

## Isolated Root Causes
1. Missing `__main__` invocation guards in SSE/HTTP entry modules.
2. Server bootstrap fixed host/port defaults prevented dynamic `FASTMCP_PORT` test binding.

## Attribution
- Category: `server defect`
- Secondary: `transport/config issue`
- Confidence: high

## Current State
After remediation, strict runtime transport smoke passes (`3 passed`).
