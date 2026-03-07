# Failure Triage (20260307T122303Z)

Failures extracted from validation `20260307T121500Z`:

- PROTOCOL::stdio_initialize_timeout
  - class: MCP protocol/server issue
  - severity: high
  - reproducibility: reproducible
  - evidence: `docs/validation/telecom-browser-mcp-v0.2/artifacts/20260307T122309Z/logs/mcp-interop-probe.json`

- BROWSER::crash_recovery_unvalidated
  - class: browser lifecycle issue
  - severity: medium
  - reproducibility: unknown

- BROWSER::stale_selector_recovery_unvalidated
  - class: browser lifecycle issue
  - severity: medium
  - reproducibility: unknown

- DIAGNOSTICS::browser_logs_placeholder_depth
  - class: diagnostics/evidence issue
  - severity: medium
  - reproducibility: reproducible

- CONTRACT::one_way_audio_depth_ambiguity
  - class: contract definition issue
  - severity: low
  - reproducibility: n/a
