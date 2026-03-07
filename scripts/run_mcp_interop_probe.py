#!/usr/bin/env python
from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def _run_probe(ts: str, logs_dir: Path) -> Path:
    errlog_path = logs_dir / "mcp-interop-probe-stderr.log"
    result_path = logs_dir / "mcp-interop-probe.json"

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "telecom_browser_mcp"],
    )

    with errlog_path.open("w", encoding="utf-8") as errlog:
        async with asyncio.timeout(30):
            async with stdio_client(server_params, errlog=errlog) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    init_result = await session.initialize()
                    list_tools_result = await session.list_tools()
                    list_tools_repeat = await session.list_tools()

    first_names = [tool.name for tool in list_tools_result.tools]
    second_names = [tool.name for tool in list_tools_repeat.tools]
    stable = first_names == second_names

    payload = {
        "timestamp": ts,
        "probe": "wire-level-stdio-initialize-and-discovery",
        "stable_discovery": stable,
        "tool_count": len(first_names),
        "tool_names": first_names,
        "initialize": {
            "protocol_version": getattr(init_result, "protocolVersion", None),
            "server_name": getattr(getattr(init_result, "serverInfo", None), "name", None),
            "server_version": getattr(getattr(init_result, "serverInfo", None), "version", None),
            "capabilities": init_result.capabilities.model_dump(mode="json"),
        },
        "evidence": {
            "stderr_log": str(errlog_path),
        },
    }
    result_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return result_path


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path("docs/validation/telecom-browser-mcp-v0.2/artifacts") / ts / "logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        out_path = asyncio.run(_run_probe(ts, out_dir))
        print(str(out_path))
        return 0
    except TimeoutError:
        failure_path = out_dir / "mcp-interop-probe.json"
        failure_path.write_text(
            json.dumps(
                {
                    "timestamp": ts,
                    "probe": "wire-level-stdio-initialize-and-discovery",
                    "ok": False,
                    "failure": "timeout",
                    "reason": "probe exceeded 30s timeout",
                    "evidence": {"stderr_log": str(out_dir / "mcp-interop-probe-stderr.log")},
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(str(failure_path))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
