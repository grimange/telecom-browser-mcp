# AGENTS.md Snippet (Codex Tool Usage)

Recommended first calls after MCP registration:

1. `health` (no args)
2. `capabilities` (no args)
3. `list_sessions` (no args)

If any of these fail with invocation binding errors (for example synthetic `kwargs` forwarding), remediate tool registration/dispatcher contract alignment before telecom-flow troubleshooting.
