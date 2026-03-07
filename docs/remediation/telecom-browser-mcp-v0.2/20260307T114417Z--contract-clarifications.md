# Contract Clarifications

1. `diagnose_one_way_audio` appears both as deferred and as catalog item in v0.2 documents.
- Current remediation stance: implemented with lightweight browser-side diagnosis schema.
- Clarification needed: is deep one-way-audio causal analysis mandatory for v0.2 release?

2. `screenshot` and `collect_browser_logs` requirements in environments without active Playwright pages.
- Current remediation stance: tools are exposed with structured outcomes; screenshot can fail diagnostically when page is absent.
- Clarification needed: should this count as full PASS or PARTIAL in harness-only runs?
