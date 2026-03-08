# 05 - Diagnostics Validation

## Machine-Consumable Diagnostics
- Diagnostic model is structured (`code`, `classification`, `message`, `confidence`, `observed_at`) (`src/telecom_browser_mcp/models/common.py:27`).
- Error responses include diagnostics arrays in envelope contract (`src/telecom_browser_mcp/models/common.py:54`, `tests/contract/test_m1_tool_envelopes.py:12`).

## Classification Usability Check
Requested classes to verify: `retryable`, `terminal`, `configuration_error`, `environment_error`.

Observed implementation:
- Retryability is exposed as boolean on `error.retryable` (`src/telecom_browser_mcp/models/common.py:24`).
- Classifications are domain strings (for example `session_busy`, `session_not_ready`, `answer_action_failed`) (`src/telecom_browser_mcp/tools/service.py:171`, `src/telecom_browser_mcp/tools/service.py:383`, `src/telecom_browser_mcp/tools/service.py:484`).
- Busy and session-state diagnostics are explicit and test-covered (`tests/unit/test_agent_integration_remediation.py:30`, `tests/unit/test_agent_integration_remediation.py:52`).
- Answer diagnostics taxonomy remains distinct (`src/telecom_browser_mcp/diagnostics/engine.py:8`).

## Assessment
- Diagnostics are machine-consumable and deterministic in structure.
- Taxonomy is not normalized into the four requested classes; consumers still need mapping logic.

Evidence tier: `static_verified` + `test_verified` (structure), `static_only_insufficient` (taxonomy normalization).

## Diagnostics Verdict
- Partial closure only (B-903 remains open as residual).
