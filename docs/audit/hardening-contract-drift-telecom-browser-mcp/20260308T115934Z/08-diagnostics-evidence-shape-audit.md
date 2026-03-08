# 08 Diagnostics Evidence Shape Audit

## Result
- Diagnostics are structured objects (`code/classification/message/confidence/observed_at`).
- Evidence artifacts include manifest + typed artifact refs.
- HTML and diagnosis payloads pass through redaction helpers before persistence.

## Finding
id: DE-002
title: Redaction is pattern-based and may miss format variants
severity: low
confidence: medium
impacted_modules:
- src/telecom_browser_mcp/evidence/bundle.py

evidence_type:
- static_inference

evidence:
- Current regex set covers common `password/token/authorization/cookie/sip:` patterns only.

why_it_matters:
- Uncovered token formats may still persist in artifacts.

recommended_fix:
- Expand pattern suite and add configurable redaction policy list.

recommended_regression_guard:
- Extend redaction test corpus with more credential/token formats.
