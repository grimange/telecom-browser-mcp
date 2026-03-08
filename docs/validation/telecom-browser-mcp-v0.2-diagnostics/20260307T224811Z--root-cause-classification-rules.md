# Root Cause Classification Rules

Ordered rules:
- missing/malformed bundle -> diagnostics_collection_gap
- scenario_id contains stale_selector -> selector_stale_or_dom_drift
- scenario_id contains page_detach/page_closed -> page_closed_or_detached
- scenario_id contains context_closure -> context_invalidated
- scenario_id contains browser_crash -> browser_unavailable
- page_errors present -> javascript_runtime_error
- network failures present -> network_failure
- collection_gaps present -> diagnostics_collection_gap
- unknown classification -> contract_ambiguous/unknown
