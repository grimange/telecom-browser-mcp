# Investigation Plan

Date: 2026-03-08
Pipeline: `025--investigate-root-cause-host-mcp-browser`

Objective:
- Determine whether the current host blockers are caused by server startup, probe logic, MCP SDK stdio transport behavior, browser launch configuration, missing host dependencies, or host runtime policy.

Investigation stages executed:
1. Re-read current stdio server, handshake probe, SDK probe, and Playwright launch code.
2. Re-run the raw stdio handshake probe against the current workspace source.
3. Re-run the official MCP Python SDK stdio probe against the current workspace source.
4. Run stdin control experiments to separate plain subprocess stdio from async stdio wrappers.
5. Measure server startup path cost and check for stdout/stderr contamination before handshake.
6. Re-run standalone Playwright Chromium launch with explicit no-sandbox flags.
7. Re-run direct `chrome-headless-shell` launch with the same flags.
8. Capture host fingerprint and dependency state.
9. Classify root causes and write persistent records.

Expected output:
- Persistent MCP classification with rejected hypotheses.
- Persistent browser classification with rejected hypotheses.
- Durable recommendation for the next remediation pipeline.
