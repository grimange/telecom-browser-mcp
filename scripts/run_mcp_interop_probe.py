#!/usr/bin/env python
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MCP stdio interop probe with environment diagnostics")
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=30.0,
        help="Overall timeout for the wire-level probe session.",
    )
    parser.add_argument(
        "--step-timeout-seconds",
        type=float,
        default=10.0,
        help="Per-step timeout for initialize/list-tools calls.",
    )
    parser.add_argument(
        "--retry-count",
        type=int,
        default=1,
        help="Number of retry attempts after the initial attempt.",
    )
    parser.add_argument(
        "--dry-run-preflight",
        action="store_true",
        help="Only emit preflight diagnostics payload without launching the stdio server.",
    )
    return parser.parse_args()


def _preflight() -> dict[str, object]:
    checks: list[dict[str, object]] = []
    for module_name in ("mcp", "telecom_browser_mcp"):
        ok = True
        detail = "import ok"
        try:
            __import__(module_name)
        except Exception as exc:  # pragma: no cover - environment dependent
            ok = False
            detail = f"{type(exc).__name__}: {exc}"
        checks.append({"name": f"import:{module_name}", "ok": ok, "detail": detail})
    checks.append(
        {
            "name": "cwd_exists",
            "ok": Path.cwd().exists(),
            "detail": str(Path.cwd()),
        }
    )
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "cwd": str(Path.cwd()),
        "env_path": os.environ.get("PATH", ""),
        "checks": checks,
    }


async def _run_probe(ts: str, logs_dir: Path, *, timeout_seconds: float, step_timeout_seconds: float) -> Path:
    errlog_path = logs_dir / "mcp-interop-probe-stderr.log"
    result_path = logs_dir / "mcp-interop-probe.json"
    started = time.monotonic()

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "telecom_browser_mcp"],
    )
    phase = "spawn_server"
    with errlog_path.open("w", encoding="utf-8") as errlog:
        try:
            async with asyncio.timeout(timeout_seconds):
                async with stdio_client(server_params, errlog=errlog) as (read_stream, write_stream):
                    phase = "initialize_session"
                    async with ClientSession(read_stream, write_stream) as session:
                        phase = "initialize"
                        async with asyncio.timeout(step_timeout_seconds):
                            init_result = await session.initialize()
                        phase = "list_tools_first"
                        async with asyncio.timeout(step_timeout_seconds):
                            list_tools_result = await session.list_tools()
                        phase = "list_tools_second"
                        async with asyncio.timeout(step_timeout_seconds):
                            list_tools_repeat = await session.list_tools()
        except Exception as exc:
            tb_text = traceback.format_exc()
            stderr_tail = ""
            if errlog_path.exists():
                stderr_tail = "\n".join(errlog_path.read_text(encoding="utf-8").splitlines()[-30:])
            timeout_like = (
                "TimeoutError" in f"{type(exc).__name__}: {exc}"
                or "timeout" in str(exc).lower()
                or "TimeoutError" in tb_text
            )
            classification = "environment_blocked"
            failure = "probe_exception"
            if timeout_like and not stderr_tail.strip():
                classification = "environment_blocked_stdio_no_response"
                failure = "initialize_timeout_no_server_response"
            payload = {
                "timestamp": ts,
                "probe": "wire-level-stdio-initialize-and-discovery",
                "ok": False,
                "classification": classification,
                "failure": failure,
                "phase": phase,
                "reason": f"{type(exc).__name__}: {exc}",
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "preflight": _preflight(),
                "evidence": {
                    "stderr_log": str(errlog_path),
                    "stderr_tail": stderr_tail,
                    "traceback": tb_text.splitlines()[-20:],
                },
                "likely_environment_limitations": (
                    ["stdio transport process started but no initialize response observed"]
                    if classification == "environment_blocked_stdio_no_response"
                    else []
                ),
            }
            result_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            return result_path

    first_names = [tool.name for tool in list_tools_result.tools]
    second_names = [tool.name for tool in list_tools_repeat.tools]
    stable = first_names == second_names

    payload = {
        "timestamp": ts,
        "probe": "wire-level-stdio-initialize-and-discovery",
        "ok": True,
        "stable_discovery": stable,
        "tool_count": len(first_names),
        "tool_names": first_names,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "preflight": _preflight(),
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
    args = _parse_args()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path("docs/validation/telecom-browser-mcp-v0.2/artifacts") / ts / "logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.dry_run_preflight:
        out_path = out_dir / "mcp-interop-probe.json"
        out_path.write_text(
            json.dumps(
                {
                    "timestamp": ts,
                    "probe": "wire-level-stdio-initialize-and-discovery",
                    "ok": True,
                    "classification": "preflight_only",
                    "preflight": _preflight(),
                    "evidence": {},
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        print(str(out_path))
        return 0
    attempts = max(1, args.retry_count + 1)
    last_path: Path | None = None
    for _ in range(attempts):
        last_path = asyncio.run(
            _run_probe(
                ts,
                out_dir,
                timeout_seconds=args.timeout_seconds,
                step_timeout_seconds=args.step_timeout_seconds,
            )
        )
        payload = json.loads(last_path.read_text(encoding="utf-8"))
        if payload.get("ok") is True:
            print(str(last_path))
            return 0
    if last_path is None:  # pragma: no cover - defensive
        return 1
    print(str(last_path))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
