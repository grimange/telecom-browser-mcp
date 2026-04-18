# Guide Generation Report

- status: `full`
- artifact_dir: `/home/ramjf/python-projects/telecom-browser-mcp/docs/agent-integration/generated/20260308T152717Z`
- startup_contract_extracted: `True`
- tool_count: `14`
- source_failure_count: `0`

## Evidence Sources
- Startup contract: pyproject + server entrypoints
- Registry snapshot: export_mcp_registry runtime-safe export
- Workflow evidence: tests/e2e + verification docs
- Agent patterns: script-defined snippets with provenance

## Quality Gate Intent
- Every generated agent guide includes the mandatory section contract.
- Thin stub guides are rejected by `guide-quality-audit.json`.
- Unsupported runtime claims are downgraded to unverified integration pattern.
