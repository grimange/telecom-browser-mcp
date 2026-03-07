# Failure Triage (20260307T121016Z)

## Classified failures from validation `20260307T120228Z`
- PROTOCOL::stdio_initialize_timeout: category 2 (MCP protocol/server), severity high, reproducible in this environment.
- BROWSER::crash_recovery_unvalidated: category 4 (browser lifecycle), severity medium, reproducibility unknown.
- BROWSER::stale_selector_recovery_unvalidated: category 4, severity medium, reproducibility unknown.
- TELECOM::registration_delayed_scenario_missing: category 5, severity medium, reproducible and now fixed.
- TELECOM::incoming_signal_absent_scenario_partial: category 5, severity medium, reproducible and now fixed.
- TELECOM::answer_timeout_scenario_missing: category 5, severity medium, reproducible and now fixed.
- DIAGNOSTICS::browser_logs_placeholder_depth: category 6, severity medium, reproducible.
- CONTRACT::one_way_audio_depth_ambiguity: category 1 (contract definition ambiguity), severity low.
