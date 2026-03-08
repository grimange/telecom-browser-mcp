# 13 - Follow-Up Remediation Recommendations

## R-001
- Issue: missing direct Codex CLI MCP transcript evidence.
- Impact scope: Codex users.
- Root cause category: client-specific validation gap.
- Fix strategy: add scripted Codex MCP registration + first-contact + malformed-input capture.
- Required pipeline after fix: `007--multi-client-mcp-compatibility-validation`.

## R-002
- Issue: Claude Desktop remains unvalidated.
- Impact scope: Claude users.
- Root cause category: environment/access gap.
- Fix strategy: run desktop validation session with captured config + tool transcripts.
- Required pipeline after fix: `007`.

## R-003
- Issue: OpenAI Agents path is transport-proven but not fully app-proven.
- Impact scope: Agents SDK consumers.
- Root cause category: evidence depth gap.
- Fix strategy: execute full agents workflow using real tool calls and capture runtime logs.
- Required pipeline after fix: `007` plus client-specific agents validation pipeline.
