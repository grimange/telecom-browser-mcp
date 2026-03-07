# Browser Session Validation (20260307T113620Z)

## Scenarios
- fresh session: PASS
- reuse session/reset: PASS
- teardown after success: PASS
- teardown after failure: PARTIAL (validated missing-session path, not crash-injected browser)
- browser crash recovery: INCONCLUSIVE (no crash injection harness)
- parallel sessions: INCONCLUSIVE (not executed)
- stale selector recovery: PARTIAL (scaffold adapters return explicit unavailable reasons)
