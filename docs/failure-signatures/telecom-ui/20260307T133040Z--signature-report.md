# Telecom UI Failure Signature Report

## Executive Summary
- total signatures: 3
- total occurrences: 28

## Top Signature Families
- `SIG-001` diagnostics_bundle_missing_on_failure (count=26, confidence=exact)
- `SIG-002` javascript_runtime_error (count=1, confidence=moderate)
- `SIG-003` selector_stale_after_dom_refresh (count=1, confidence=strong)

## Signature Quality
- high-confidence signatures: 2

## Product vs Environment Failures
- product signatures: 2
- environment signatures: 0

## Diagnostics Gaps
- diagnostics gap signatures: 1

## Recommended Next Actions
- expand signature families for telecom call-state races
- add webrtc readiness signatures
- increase contract-to-bundle linkage coverage
