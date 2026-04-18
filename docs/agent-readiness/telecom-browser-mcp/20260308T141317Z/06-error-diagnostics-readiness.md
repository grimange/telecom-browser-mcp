# 06 - Error Diagnostics Readiness

## Current State
- Error envelope is structured and stable: `code/message/classification/retryable`.
- Session-broken and session-busy paths include machine-usable diagnostics.
- `answer_call` failure path emits diagnostics and artifacts with bundle path.

## Gaps
- Taxonomy is not fully normalized across all failure classes.
- Evidence collector still creates `console_logs/` folder without capture logic.

## Classification
- Structure quality: Confirmed by source/tests.
- Taxonomy consistency: Confirmed gap by source.
- Operational impact: Inferred for downstream client mapping cost.

## Evidence
- `src/telecom_browser_mcp/models/common.py:18`
- `src/telecom_browser_mcp/tools/service.py:117`
- `src/telecom_browser_mcp/tools/service.py:473`
- `src/telecom_browser_mcp/evidence/bundle.py:56`
- `tests/unit/test_agent_integration_remediation.py:30`
