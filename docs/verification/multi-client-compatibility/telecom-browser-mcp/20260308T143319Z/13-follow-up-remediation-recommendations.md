# 13 - Follow-Up Remediation Recommendations

## R-001: Add host-lane runtime gate for multi-client compatibility
- Issue: runtime tiers remain `unable_to_verify` under constrained environment.
- Impact scope: Codex CLI, OpenAI Agents SDK path, reference harness.
- Root cause category: environment limitation / validation gap.
- Fix strategy: run strict mode (`MCP_REQUIRE_LIVE_TRANSPORT_RUNTIME=1`) in host lane CI or controlled host runner; persist logs/artifacts.
- Required pipeline after fix: this same pipeline (`007--multi-client-mcp-compatibility-validation`).

## R-002: Add executable Codex CLI MCP integration script
- Issue: Codex client-specific runtime proof is missing.
- Impact scope: Codex CLI users.
- Root cause category: client-specific validation gap.
- Fix strategy: add scripted Codex MCP registration + first-contact tool call trace capture.
- Required pipeline after fix: `007` plus client-specific Codex live validation pipeline.

## R-003: Add executable Claude Desktop validation evidence path
- Issue: Claude Desktop is `not_accessible` in this run.
- Impact scope: Claude Desktop users.
- Root cause category: client access gap.
- Fix strategy: add desktop validation checklist + captured session logs/screenshots + tool-call transcripts in controlled environment.
- Required pipeline after fix: `007` plus Claude-specific runtime workflow validation.

## R-004: Strengthen response parsing interoperability checks
- Issue: runtime parsing behavior in external clients not directly observed.
- Impact scope: all clients.
- Root cause category: potential client normalization/parsing divergence.
- Fix strategy: add harness assertions for both `structuredContent` and text-content fallback across transports, with malformed-input and unknown-arg cases.
- Required pipeline after fix: `007` re-run with updated evidence.
