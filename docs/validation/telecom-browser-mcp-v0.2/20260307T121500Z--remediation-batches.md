# Remediation Batches (20260307T121500Z)

## A --- protocol/schema normalization
- Remaining issue: wire-level handshake timeout.
- Scope: probe diagnostics + host-side transcript capture.

## B --- browser lifecycle stabilization
- Remaining issue: crash and stale-selector recovery scenario coverage.
- Scope: add deterministic lifecycle fault injectors/tests.

## C --- telecom flow corrections
- Status: complete for identified gaps in this cycle.

## D --- diagnostics improvements
- Remaining issue: console/network capture depth.
- Scope: wire real Playwright event capture with bounded output.

## E --- interoperability hardening
- Remaining issue: environment/runtime handshake blocking.
- Scope: validate on alternate host/runtime and preserve wire traces.

## F --- contract clarifications
- clarify `diagnose_one_way_audio` minimum depth and protocol evidence acceptance criteria.
