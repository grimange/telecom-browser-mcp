# 12 - Compatibility Claim Governance

## Claim Policy for This Validation Snapshot

### Supported
- "`telecom-browser-mcp` has stable canonical schemas and deterministic contract-level validation."
- "Core tool envelope invariants are verified by automated tests."

### Restricted
- "Codex CLI compatible": allowed only as "partially validated; runtime proof pending in host lane".
- "OpenAI Agents SDK compatible": allowed only as "schema/invocation compatible in tests; runtime transport proof pending".
- "Reference MCP harness compatible": allowed only with note that transport runtime is environment-limited in this run.

### Unsupported
- "Works with all MCP clients"
- "Fully MCP compatible"
- "Claude compatible" (without direct executable evidence)
- "Universal MCP interoperability"

## Governance Rule
Any public compatibility claim must include:
1. validation timestamp,
2. client/environment scope,
3. transport used,
4. runtime evidence class,
5. known blockers/risk qualifiers.
