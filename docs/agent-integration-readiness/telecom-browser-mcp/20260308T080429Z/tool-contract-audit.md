# Tool Contract Audit

## Inventory and discoverability

- Source of truth: `src/telecom_browser_mcp/server/stdio_server.py` (`TOOL_NAMES`)
- Expected tool count: `25`
- Contract guard test: `tests/unit/test_tool_discovery_contract.py`
- Naming style: telecom-intent verbs and read operations (`open_app`, `wait_for_registration`, `diagnose_answer_failure`)

## Envelope quality

- Success/failure response models are centralized in `src/telecom_browser_mcp/models/envelope.py`.
- Core fields for agent use are stable and explicit: `ok`, `message`, `data`, `warnings`, `error_code`, `failure_category`, `retryable`, `likely_causes`, `next_recommended_tools`.

## Error classification

- Classification enums are explicit in `src/telecom_browser_mcp/models/enums.py`.
- Failure responses in orchestration include likely causes and next-step tooling for most high-risk actions.

## Contract findings

1. `partial` consistency for adapter action failure branching:
   - `login_agent` returns success envelope unconditionally after adapter call (`orchestrator.py` around line 236).
   - `hangup_call` returns success envelope without checking for explicit failure state in returned snapshot (`orchestrator.py` around line 459).
2. Error object shape differs from some external guidance templates that expect nested `error` object; current contract uses top-level error fields. This is stable internally but should be documented as canonical.

## Verdict

Tool contract readiness: `pass_with_followups`

- External API is stable and discoverable.
- Follow-up hardening should focus on consistency, not redesign.
