# Artifact Ingestion Update

Implemented release-hardening ingestion in `PipelineVerdictCollector` using:

- `docs/release-hardening/telecom-browser-mcp/release-hardening-verdict.json`
- `docs/release-hardening/telecom-browser-mcp/release-check-results.json`
- `docs/release-hardening/telecom-browser-mcp/release-risk-register.json`

Behavior:

- missing files do not crash governor
- missing all files maps to `release_hardening_not_available`
- partial availability records `missing_artifacts`
- ingested fields include `release_hardening_verdict`, `release_track_allowed`, `release_block_reason`, `release_hardening_required`
