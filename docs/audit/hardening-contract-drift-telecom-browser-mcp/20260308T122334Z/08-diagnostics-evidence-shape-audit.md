# 08 Diagnostics Evidence Shape Audit

## Result
- Diagnostics use structured model fields (`code`, `classification`, `confidence`, etc.).
- Evidence bundle manifest/artifact refs are consistent and typed.
- Redaction covers common secret forms including bearer/auth/token/cookie/api_key/secret/sip identities.

## Finding
id: DE-003
title: Redaction strategy is static regex-based with limited contextual awareness
severity: low
confidence: medium
impacted_modules:
- src/telecom_browser_mcp/evidence/bundle.py

evidence_type:
- static_inference

evidence:
- Redaction behavior depends on hardcoded regex list.

why_it_matters:
- New secret patterns can be missed unless regex list is maintained.

recommended_fix:
- Externalize redaction policy and add versioned pattern sets.

recommended_regression_guard:
- Expand redaction fixtures with per-pattern coverage tracking.
