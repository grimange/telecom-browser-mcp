# 11 - Residual Compatibility Risk

## Residual Risks
1. Universal runtime compatibility is unverified
- Level: critical
- Impact: high risk of integration failure in at least one real MCP client.

2. Claude Desktop remains untested in executable environment
- Level: high
- Impact: desktop user path may fail at registration, invocation, or parsing boundaries.

3. OpenAI Agents SDK transport runtime proof is absent in this environment
- Level: high
- Impact: SSE/streamable-http behavior may diverge at runtime despite schema correctness.

4. Codex CLI runtime proof is incomplete
- Level: moderate
- Impact: invocation envelope normalization could still differ in live client path.

## Overall Residual Risk
- Current global compatibility risk level: `high`
