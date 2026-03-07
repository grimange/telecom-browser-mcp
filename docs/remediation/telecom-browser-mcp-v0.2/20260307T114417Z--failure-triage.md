# Failure Triage (20260307T114417Z)

Extracted FAIL/PARTIAL/INCONCLUSIVE items from validation baseline:
- TOOL::get_environment_snapshot: fixed (Missing from exposed tool catalog and invocation path)
- TOOL::diagnose_one_way_audio: fixed (Missing from exposed tool catalog and invocation path)
- TOOL::collect_browser_logs: fixed (Missing from exposed tool catalog and evidence path)
- TOOL::screenshot: partially fixed (Missing from exposed tool catalog)
- PROTOCOL::wire_initialize_trace_missing: partially fixed (No wire-level initialize/list-tools capture)
- SCENARIO::registration_flapping: deferred (No flapping scenario harness)
- SCENARIO::incoming_duplicate_events: deferred (No duplicate event scenario harness)
- SCENARIO::answer_ui_mismatch: deferred (No UI mismatch scenario injector)