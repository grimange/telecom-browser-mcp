# Confidence And Open Questions

Confidence:

- MCP classification confidence: `0.82`
- Browser classification confidence: `0.96`

Why MCP confidence is lower:

- The exact low-level reason why async stdio readers hang on this host was not isolated below the `anyio` layer.
- The evidence is still sufficient to reject probe formatting, startup blocking, and stdout contamination.

Open questions:

- Would a fully synchronous production stdio bridge avoid the MCP handshake blocker on this host?
- Is the stdio issue specific to this WSL2 + sandboxed execution context, or reproducible on a plain Linux host with the same package versions?
- Would a non-headless Chromium build, remote browser endpoint, or host execution outside the current seccomp/no-new-privs boundary bypass the browser blocker?

What is not open:

- Whether missing shared libraries are causing the browser failure.
- Whether the raw probe alone caused the MCP timeout.
- Whether server startup work blocks initialize handling.
