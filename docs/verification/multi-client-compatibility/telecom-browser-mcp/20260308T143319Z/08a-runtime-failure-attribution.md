# 08a - Runtime Failure Attribution

## Observed Runtime Blockers
1. stdio smoke timeout (`tests/integration/test_stdio_smoke.py`)
- Attribution: `environment limitation`
- Secondary attribution: `transport/config issue` (not isolated)
- Rationale: no deterministic server crash evidence captured; test explicitly classifies as env limitation in non-strict mode.

2. SSE smoke operation-not-permitted
- Attribution: `environment limitation`
- Secondary attribution: `external dependency limitation`
- Rationale: subprocess/network operation constraints in workspace environment.

3. streamable-http smoke operation-not-permitted
- Attribution: `environment limitation`
- Secondary attribution: `external dependency limitation`
- Rationale: same class as SSE in this run.

## Not Observed
- No direct evidence of schema/runtime drift causing these runtime blockers.
- No direct evidence of client normalization or response parsing defect in external clients.

## Attribution Confidence
- Environment limitation: high
- Any deeper root-cause category beyond environment constraints: low (`unable_to_isolate`)
