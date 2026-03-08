# AGENTS.md Recommended Snippets

## Host-first browser execution

```md
For `telecom-browser-mcp`, browser-driving tools are host-first operations.
Prefer host runtime for `open_app`, `wait_for_registration`, `wait_for_incoming_call`, and `answer_call`.
```

## Sandbox classification rule

```md
Classify sandbox stdio/browser failures as environment limits unless host evidence confirms code defects.
Avoid remediation loops driven only by sandbox failures.
```

## MCP usage rule

```md
Use MCP telecom-intent tools for browser workflows; avoid generic click/query abstractions in agent-facing tool surfaces.
```
