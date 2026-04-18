# 03 Schema Runtime Parity Audit

## Result
- Strong parity for M1 tools: generated schemas and runtime validators align.
- `tests/contract/test_schema_runtime_parity.py` enforces schema artifact parity and undeclared-input rejection.

## Drift Findings
id: CD-001
title: Non-canonical envelope for registered tools health/capabilities
severity: high
confidence: high
impacted_modules:
- src/telecom_browser_mcp/server/app.py

evidence_type:
- static

evidence:
- Parity tests cover M1 map only.
- `health`/`capabilities` are outside canonical schema generation and envelope model.

why_it_matters:
- Registered tools outside parity enforcement are a contract drift vector.

recommended_fix:
- Extend canonical map + schema generation to include non-M1 registered tools.

recommended_regression_guard:
- Add parity test that compares registered tool names with canonical-map names.
