# 10 - Incompatibilities and Drift

## Confirmed Incompatibilities
- None confirmed as server/client contract incompatibility in this run.

## Observed Gaps
1. Runtime evidence gap across all target clients
- Symptom: runtime tier cannot be marked pass.
- Class: evidence gap / environment-limited validation.

2. Client-specific config validation gap (Codex/Claude/OpenAI Agents real configs)
- Symptom: no direct runtime proof against actual client configuration surfaces.
- Class: discovery/invocation evidence gap.

## Drift Check
- No schema drift detected between published schemas and generated schemas.
- No contract envelope drift detected in tested handlers.
