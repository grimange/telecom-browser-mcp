# Root Cause Synthesis

MCP blocker:

- Primary classification: `environment_specific_stdio_behavior`
- Why:
  - server startup is fast
  - there is no stdout/stderr contamination
  - raw probe and official SDK client both receive no initialize response
  - plain blocking stdin works in a control child
  - async stdio wrappers used by the SDK and current workaround both hang under the same host conditions

Browser blocker:

- Primary classification: `chromium_sandbox_policy_block`
- Why:
  - Playwright launch fails even with explicit no-sandbox flags
  - direct browser binary launch fails with the same fatal
  - dependency resolution is intact
  - integrated and standalone failures are identical

Combined interpretation:

- The current release blockers are host-runtime driven, but they affect two different subsystems:
  - async stdio transport behavior for MCP
  - Chromium sandbox/policy execution for browser launch

Rejected overall explanation:

- A general server startup regression does not explain the evidence.
