# 08 Diagnostics Evidence Shape Audit

## Observed Shape
- Evidence bundle includes: `session_snapshot_json`, `html_snapshot`, `screenshot`, `diagnosis_json`, `manifest`.
- Artifact refs are structured (`type`, `path`, `captured`, `message`).
- Diagnostic items are structured with code/classification/confidence/timestamp.

## Findings
id: DE-001
title: Evidence capture lacks explicit redaction guardrails for HTML/diagnosis artifacts
severity: medium
confidence: medium
impacted_modules:
- src/telecom_browser_mcp/evidence/bundle.py

evidence_type:
- static

evidence:
- Raw page HTML is written to `page_snapshot.html`.
- No redaction step is applied before write.

why_it_matters:
- Browser snapshots can contain credentials/tokens/internal identifiers in real deployments.

recommended_fix:
- Add redaction pipeline before persisting HTML and diagnosis payloads.

recommended_regression_guard:
- Add tests with synthetic secret patterns asserting redaction before artifact write.
