# Failure Triage (20260307T123302Z)

From validation `20260307T123026Z`:

- PROTOCOL::stdio_initialize_timeout
  - class: MCP protocol/server
  - severity: high
  - reproducibility: reproducible
  - evidence: `docs/validation/telecom-browser-mcp-v0.2/artifacts/20260307T123306Z/logs/mcp-interop-probe.json`

- BROWSER::crash_recovery_unvalidated
  - class: browser lifecycle
  - severity: medium
  - status: deferred

- BROWSER::stale_selector_recovery_unvalidated
  - class: browser lifecycle
  - severity: medium
  - status: deferred

- DIAGNOSTICS::browser_logs_placeholder_depth
  - class: diagnostics/evidence
  - severity: medium
  - status: partially fixed

- CONTRACT::one_way_audio_depth_ambiguity
  - class: contract definition
  - severity: low
  - status: blocked by ambiguity
