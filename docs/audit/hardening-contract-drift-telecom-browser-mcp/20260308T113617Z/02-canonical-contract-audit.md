# 02 Canonical Contract Audit

## Result
- M1 tools: explicit canonical input models and strict validation (`extra=forbid`) are in place.
- M1 tools: canonical output envelope (`ToolResponse`) is in place.

## Findings
id: CD-001
title: Non-canonical envelope for registered tools health/capabilities
severity: high
confidence: high
impacted_modules:
- src/telecom_browser_mcp/server/app.py
- src/telecom_browser_mcp/contracts/m1_contracts.py

evidence_type:
- static

evidence:
- `health` and `capabilities` are registered MCP tools but are not represented in canonical map.
- Both tools return ad hoc dictionaries, not `ToolResponse`.

why_it_matters:
- Clients cannot treat all registered tools uniformly; this expands integration risk.

recommended_fix:
- Define canonical contract models for `health` and `capabilities` and include them in schema generation.

recommended_regression_guard:
- Add a test that every registered `@mcp.tool` name has canonical input/output mapping.
