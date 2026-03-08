# Remediation Plan

## Objective

Restore Codex tool invocation compatibility for `telecom-browser-mcp` by removing synthetic `kwargs` binding failure and adding deterministic first-contact tools.

## Plan

1. Inventory registered tools and implementation signatures.
2. Audit stdio registration wrapper and dispatcher forwarding path.
3. Align exported tool signatures with orchestrator callables.
4. Add backward-compatible unwrapping for legacy `{ "kwargs": ... }` payloads.
5. Add safe no-arg tools for deterministic first contact (`health`, `capabilities`).
6. Run unit tests and smoke validation.
7. Publish compatibility verdict and contract guidance artifacts.

## Constraints

- Preserve existing tool response envelopes.
- Use additive contract changes only.
- Classify sandbox subprocess bootstrap failures as environment limitations when not reproducible in process.

## Exit Criteria

- no `unexpected keyword argument 'kwargs'` in smoke validation
- at least two tools successfully invoked without arguments
- at least one optional-arg invocation succeeds
- dispatcher/schema mismatch location documented
