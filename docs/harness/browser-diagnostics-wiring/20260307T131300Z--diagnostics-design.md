# Browser Diagnostics Wiring Design (20260307T131300Z)

## Executive Summary
Diagnostics are now captured at the browser boundary through a reusable collector and emitted as normalized bundles with manifests and explicit collection gaps. The lifecycle harness now writes per-scenario bundle references in its result payload.

## Gap Analysis
- `collect_browser_logs` was previously placeholder-only (`available: false` JSON stubs).
- No console/pageerror/request lifecycle listeners were attached to browser runtime.
- No bundle manifest linked fault metadata to artifact files.
- Lifecycle harness output had no diagnostics bundle path.

## Implemented Components
- `src/telecom_browser_mcp/browser/diagnostics.py`
- `src/telecom_browser_mcp/browser/playwright_driver.py` wiring
- `src/telecom_browser_mcp/tools/orchestrator.py` diagnostics integration
- `scripts/run_lifecycle_fault_harness.py` per-scenario diagnostics bundle emission

## Design Properties
- One scenario execution yields one diagnostics bundle.
- Bundle writing is file-only (no stdout output).
- Missing runtime/state is recorded in `collection_gaps`.
- Manifest remains structured even with partial capture.
