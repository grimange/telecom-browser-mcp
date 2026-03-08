# MCP SDK Comparison

Observed SDK behavior:

- The official MCP Python SDK client probe times out during `initialize`.
- No stderr is emitted by the spawned server process.
- The SDK client result is `environment_blocked_stdio_no_response`.

Relevant SDK implementation details:

- SDK server stdio transport in `.venv/lib/python3.12/site-packages/mcp/server/stdio.py` reads stdin through:
  - `anyio.wrap_file(TextIOWrapper(sys.stdin.buffer, encoding="utf-8"))`
  - `async for line in stdin: ...`
- SDK client stdio transport in `.venv/lib/python3.12/site-packages/mcp/client/stdio/__init__.py` writes newline-delimited JSON and reads newline-delimited JSON from subprocess pipes.

Control comparison:

- Plain subprocess child with blocking `sys.stdin.readline()` works.
- Minimal child using `anyio.wrap_file(TextIOWrapper(sys.stdin.buffer, ...))` does not read the same input and times out.
- Minimal child using `anyio.to_thread.run_sync(sys.stdin.readline)` also times out.

Conclusion:

- The MCP Python SDK client framing is not the issue.
- The MCP Python SDK server-side stdio approach is compatible with the failed control experiment.
- The failure is broader than the SDK alone because the custom server workaround still uses async/threaded stdin behavior that also hangs on this host.
