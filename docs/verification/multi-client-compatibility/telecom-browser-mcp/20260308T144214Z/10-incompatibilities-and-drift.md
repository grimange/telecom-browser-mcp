# 10 - Incompatibilities and Drift

## Confirmed Issues Found and Remediated
1. SSE/HTTP module launch path defect (`python -m` exited without running server).
2. FASTMCP host/port bootstrap defect (ignored dynamic env port in server factory).

## Drift Status
- No schema drift detected.
- No envelope contract drift detected.
- Transport startup drift was present and is now remediated in working tree.
