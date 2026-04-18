# 12 - Readiness Claims Ledger

| Claim ID | Claim | Status | Confidence | Evidence Class | Evidence |
|---|---|---|---|---|---|
| C-001 | Registered MCP tools align with canonical contract map | Confirmed | High | Source/Test | `server/app.py:75`, `contracts/m1_contracts.py:35` |
| C-002 | Published contract schemas are in parity with generated schemas | Confirmed | High | Test/Schema | `tests/contract/test_schema_runtime_parity.py:19`, `docs/contracts/m1/` |
| C-003 | Runtime rejects undeclared tool input fields | Confirmed | High | Test/Source | `tests/contract/test_schema_runtime_parity.py:28`, `models/tools.py:8` |
| C-004 | First-contact stdio interoperability works | Confirmed | High | Test | `tests/integration/test_stdio_smoke.py:28` |
| C-005 | Fake dialer telecom flow is executable in host-capable environments | Confirmed | Medium | Test | `tests/e2e/test_fake_dialer_harness.py:34` |
| C-006 | Lifecycle management is centralized and deterministic in code paths | Confirmed | Medium | Source | `sessions/manager.py:21`, `browser/manager.py:20` |
| C-007 | Multi-agent concurrent safety is fully enforced | Not Confirmed | Medium | Inference | no lock/lease evidence in `sessions/manager.py`/`tools/service.py` |
| C-008 | Error envelope is stable and machine-usable across tools | Confirmed | High | Source/Test | `models/common.py:46`, `tests/contract/test_m1_tool_envelopes.py:8` |
| C-009 | Diagnostics quality is broad across all failure classes | Partially Confirmed | Medium | Source | `diagnostics/engine.py:7`, `tools/service.py:374` |
| C-010 | Evidence bundles include redaction for common secrets | Confirmed | High | Source/Test | `evidence/bundle.py:13`, `tests/unit/test_evidence_redaction.py:4` |
| C-011 | SSE and streamable-http client compatibility is runtime-validated | Unverified | Low | Source | entrypoints exist, no test proof in this run |
| C-012 | Integration readiness gate (all dimensions >=4) is met | Not Met | High | Score/Method | `10-readiness-scorecard.md` |

## Notes
- Unverified runtime claims are deliberately kept separate from source-confirmed behavior.
- Host-limited skips are treated as environment constraints, not automatic defects.
