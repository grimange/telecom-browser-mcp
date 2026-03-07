# Event Capture Plan (20260307T131300Z)

## Capture Layer
`BrowserDiagnosticsCollector` attaches to:
- page: `console`, `pageerror`
- context: `request`, `response`, `requestfailed`
- tracing API: `context.tracing.start/stop`

## Capture Flow
1. Collector is created during browser open.
2. Collector attaches to context/page listeners before page navigation.
3. Timing markers are recorded (`collector_attached`, `goto_started`, `goto_completed`, bundle markers).
4. On diagnostics collection, bundle writer emits JSON artifacts + summary + manifest.
5. If runtime is unavailable, collector still writes bundle with `collection_gaps`.

## Deterministic Scope
- Tests use deterministic fake context/page/tracing emitters.
- No sleeps or manual tooling required.
