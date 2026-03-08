from __future__ import annotations

import json
import os
import select
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def build_initialize_request(request_id: int = 1) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "live-verification", "version": "0.1"},
        },
    }


def build_initialized_notification() -> dict[str, Any]:
    return {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}


def build_tools_list_request(request_id: int = 2) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "method": "tools/list", "params": {}}


def classify_handshake_payload(payload: dict[str, Any]) -> str:
    if bool(payload.get("ok")):
        return "handshake_passed"
    failure = str(payload.get("failure", "")).strip().lower()
    if "timeout" in failure:
        return "handshake_timeout"
    if "invalid_response" in failure:
        return "handshake_invalid_response"
    return "handshake_transport_failure"


def classify_startup_state(*, handshake_classification: str) -> str:
    if handshake_classification == "handshake_passed":
        return "startup_ready_via_handshake"
    if handshake_classification == "handshake_timeout":
        return "startup_timeout_without_handshake"
    if handshake_classification == "handshake_invalid_response":
        return "awaiting_handshake"
    return "startup_crash"


@dataclass
class _LineFramer:
    buffer: bytes = b""

    @staticmethod
    def encode(message: dict[str, Any]) -> bytes:
        return json.dumps(message, separators=(",", ":")).encode("utf-8") + b"\n"

    def feed(self, chunk: bytes) -> None:
        self.buffer += chunk

    def pop_message(self) -> dict[str, Any] | None:
        idx = self.buffer.find(b"\n")
        if idx < 0:
            return None
        body = self.buffer[:idx]
        self.buffer = self.buffer[idx + 1 :]
        if not body.strip():
            return None
        return json.loads(body.decode("utf-8"))


def _read_message(proc: subprocess.Popen[bytes], framer: _LineFramer, timeout_seconds: float) -> dict[str, Any]:
    if proc.stdout is None:
        raise RuntimeError("transport_failure_missing_stdout")
    fd = proc.stdout.fileno()
    deadline = time.monotonic() + timeout_seconds
    while True:
        msg = framer.pop_message()
        if msg is not None:
            return msg
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("handshake_read_timeout")
        readable, _, _ = select.select([fd], [], [], remaining)
        if not readable:
            raise TimeoutError("handshake_read_timeout")
        chunk = os.read(fd, 65536)
        if not chunk:
            raise RuntimeError("transport_failure_stdout_closed")
        framer.feed(chunk)


def run_mcp_handshake_probe(
    *,
    timeout_seconds: float = 20.0,
    step_timeout_seconds: float = 8.0,
    output_path: Path | None = None,
) -> Path:
    started = time.monotonic()
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out_path = output_path or (
        Path("docs/validation/telecom-browser-mcp-v0.2/artifacts") / ts / "logs" / "mcp-interop-probe.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path = out_path.parent / "mcp-interop-probe-stderr.log"

    project_root = Path(__file__).resolve().parents[2]
    src_root = project_root / "src"
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "").strip()
    env["PYTHONPATH"] = f"{src_root}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else str(src_root)

    process = subprocess.Popen(
        [sys.executable, "-m", "telecom_browser_mcp"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    startup_state = "process_spawned"
    requests: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    framer = _LineFramer()

    def _write_message(message: dict[str, Any]) -> None:
        if process.stdin is None:
            raise RuntimeError("transport_failure_missing_stdin")
        process.stdin.write(_LineFramer.encode(message))
        process.stdin.flush()
        requests.append(message)

    try:
        startup_state = "awaiting_handshake"
        total_deadline = time.monotonic() + timeout_seconds
        remaining = max(0.1, total_deadline - time.monotonic())

        initialize = build_initialize_request(1)
        _write_message(initialize)
        init_response = _read_message(process, framer, min(step_timeout_seconds, remaining))
        responses.append(init_response)
        if init_response.get("id") != 1 or "result" not in init_response:
            raise ValueError("handshake_invalid_response_initialize")

        initialized = build_initialized_notification()
        _write_message(initialized)

        remaining = max(0.1, total_deadline - time.monotonic())
        tools_list = build_tools_list_request(2)
        _write_message(tools_list)
        tools_response = _read_message(process, framer, min(step_timeout_seconds, remaining))
        responses.append(tools_response)
        if tools_response.get("id") != 2 or "result" not in tools_response:
            raise ValueError("handshake_invalid_response_tools_list")

        tools = tools_response.get("result", {}).get("tools", [])
        payload: dict[str, Any] = {
            "timestamp": ts,
            "probe": "raw-stdio-jsonrpc-initialize-and-tools-list",
            "ok": True,
            "classification": "handshake_passed",
            "startup_state": "startup_ready_via_handshake",
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "requests": requests,
            "responses": responses,
            "tools_count": len(tools) if isinstance(tools, list) else 0,
            "tools_list_ok": True,
            "evidence": {"stderr_log": str(stderr_path)},
        }
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return out_path
    except TimeoutError as exc:
        payload = {
            "timestamp": ts,
            "probe": "raw-stdio-jsonrpc-initialize-and-tools-list",
            "ok": False,
            "classification": "handshake_timeout",
            "failure": str(exc),
            "startup_state": "startup_timeout_without_handshake",
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "requests": requests,
            "responses": responses,
            "tools_list_ok": False,
            "evidence": {"stderr_log": str(stderr_path)},
        }
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return out_path
    except Exception as exc:
        failure = str(exc)
        classification = "handshake_invalid_response" if "invalid_response" in failure else "handshake_transport_failure"
        startup_state = classify_startup_state(handshake_classification=classification)
        payload = {
            "timestamp": ts,
            "probe": "raw-stdio-jsonrpc-initialize-and-tools-list",
            "ok": False,
            "classification": classification,
            "failure": failure,
            "startup_state": startup_state,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "requests": requests,
            "responses": responses,
            "tools_list_ok": False,
            "evidence": {"stderr_log": str(stderr_path)},
        }
        out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return out_path
    finally:
        stderr_text = b""
        if process.stderr is not None:
            try:
                _, stderr_text = process.communicate(timeout=0.2)
            except Exception:
                pass
        if stderr_text:
            stderr_path.write_text(stderr_text.decode("utf-8", errors="replace"), encoding="utf-8")
        else:
            stderr_path.write_text("", encoding="utf-8")
        if process.poll() is None:
            try:
                process.send_signal(signal.SIGTERM)
                process.wait(timeout=0.5)
            except Exception:
                process.kill()
