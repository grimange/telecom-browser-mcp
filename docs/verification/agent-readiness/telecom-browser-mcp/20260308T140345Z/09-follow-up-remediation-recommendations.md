# 09 - Follow-Up Remediation Recommendations

## Unresolved / Partially Resolved Items

1. B-901 runtime verification closure
- Execute `tests/integration/test_http_transport_smoke.py` and `tests/integration/test_stdio_smoke.py` in a host environment that permits socket + stdio process operations.
- Capture command outputs and tool-call payloads as closure evidence.
- Reclassify compatibility to `runtime-compatible` only after Tier 3 evidence exists.

2. B-903 diagnostics taxonomy normalization
- Introduce a normalization layer mapping current diagnostic families to a documented taxonomy.
- Keep backward-compatible raw codes, but add normalized category field for agent routing.
- Add contract tests asserting normalized categories across `wait_*`, `answer_call`, and `session_broken` paths.

3. Pipeline/documentation consistency hardening
- Align pipeline input path references with actual repository structure (`docs/agent-readiness/...`).
- Add a preflight verifier that fails early when authoritative input paths are absent.

## Suggested Next Pipelines
1. `docs/pipelines/021--live-client-transport-runtime-verification.md` (new): host execution proof for stdio/SSE/HTTP.
2. `docs/pipelines/022--diagnostics-taxonomy-normalization.md` (new): structured classification harmonization.
3. `docs/pipelines/023--verification-preflight-path-contracts.md` (new): audit/remediation path contract checks.
