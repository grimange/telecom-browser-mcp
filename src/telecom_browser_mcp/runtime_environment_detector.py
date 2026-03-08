from __future__ import annotations

import getpass
import importlib.util
import os
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

KNOWN_RUNTIME_CLASSES = {
    "authoritative_host",
    "container_runtime",
    "wsl_runtime",
    "ci_runtime",
    "restricted_runtime",
    "sandbox_runtime",
    "unknown_environment",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_cgroup_text() -> str:
    for path in (Path("/proc/1/cgroup"), Path("/proc/self/cgroup")):
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    return ""


def _read_proc_status() -> dict[str, Any]:
    status = {"available": False, "seccomp_mode": None, "no_new_privs": None}
    path = Path("/proc/self/status")
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return status

    status["available"] = True
    for line in content.splitlines():
        if line.startswith("Seccomp:"):
            try:
                status["seccomp_mode"] = int(line.split(":", 1)[1].strip())
            except ValueError:
                status["seccomp_mode"] = None
        if line.startswith("NoNewPrivs:"):
            try:
                status["no_new_privs"] = int(line.split(":", 1)[1].strip())
            except ValueError:
                status["no_new_privs"] = None
    return status


def _read_unprivileged_userns_clone() -> int | None:
    path = Path("/proc/sys/kernel/unprivileged_userns_clone")
    try:
        return int(path.read_text(encoding="utf-8", errors="replace").strip())
    except (OSError, ValueError):
        return None


def _detect_browser_capability() -> dict[str, Any]:
    has_playwright = importlib.util.find_spec("playwright") is not None
    search_roots: list[Path] = []
    env_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "").strip()
    if env_path and env_path != "0":
        search_roots.append(Path(env_path).expanduser())
    search_roots.append((Path.home() / ".cache" / "ms-playwright").expanduser())

    chromium_binaries_present = False
    checked_paths: list[str] = []
    for root in search_roots:
        checked_paths.append(str(root))
        if not root.exists():
            continue
        if any(root.glob("chromium-*")) or any(root.glob("chromium_headless_shell-*")):
            chromium_binaries_present = True
            break

    if not has_playwright:
        return {
            "available": False,
            "reason": "playwright_not_installed",
            "playwright_installed": False,
            "chromium_binaries_present": chromium_binaries_present,
            "checked_paths": checked_paths,
        }
    if not chromium_binaries_present:
        return {
            "available": False,
            "reason": "chromium_binary_not_detected",
            "playwright_installed": True,
            "chromium_binaries_present": False,
            "checked_paths": checked_paths,
        }
    return {
        "available": True,
        "reason": "",
        "playwright_installed": True,
        "chromium_binaries_present": True,
        "checked_paths": checked_paths,
    }


def detect_runtime_environment() -> dict[str, Any]:
    system = platform.system()
    release = platform.release()
    version = platform.version()
    env = os.environ

    override = env.get("TELECOM_BROWSER_MCP_RUNTIME_CLASS", "").strip()
    ci_signals = [name for name in ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILD_NUMBER") if env.get(name)]
    sandbox_signals = [
        name
        for name in ("CODEX_SANDBOX", "OPENAI_SANDBOX", "RUNNING_IN_SANDBOX", "TELECOM_BROWSER_MCP_SANDBOX")
        if env.get(name)
    ]
    cgroup_text = _read_cgroup_text().lower()
    container_signals: list[str] = []
    if Path("/.dockerenv").exists():
        container_signals.append("dockerenv")
    if any(token in cgroup_text for token in ("docker", "containerd", "kubepods", "podman", "lxc")):
        container_signals.append("cgroup_container_token")

    proc_status = _read_proc_status()
    userns_clone = _read_unprivileged_userns_clone()
    restricted = bool(proc_status.get("seccomp_mode") == 2 and proc_status.get("no_new_privs") == 1)

    if override in KNOWN_RUNTIME_CLASSES:
        runtime_class = override
        runtime_reason = "operator_override"
    elif sandbox_signals:
        runtime_class = "sandbox_runtime"
        runtime_reason = "sandbox_environment_signal_detected"
    elif ci_signals:
        runtime_class = "ci_runtime"
        runtime_reason = "ci_environment_signal_detected"
    elif "microsoft" in release.lower() or "wsl" in version.lower():
        runtime_class = "wsl_runtime"
        runtime_reason = "wsl_kernel_detected"
    elif container_signals:
        runtime_class = "container_runtime"
        runtime_reason = "container_signal_detected"
    elif restricted:
        runtime_class = "restricted_runtime"
        runtime_reason = "restricted_namespace_detected"
    elif system.lower() in {"linux", "darwin", "windows"}:
        runtime_class = "authoritative_host"
        runtime_reason = "direct_host_runtime_detected"
    else:
        runtime_class = "unknown_environment"
        runtime_reason = "unsupported_platform_signature"

    is_root = False
    euid: int | None = None
    if hasattr(os, "geteuid"):
        euid = os.geteuid()
        is_root = euid == 0

    return {
        "detected_at": _now_iso(),
        "runtime_class": runtime_class,
        "runtime_reason": runtime_reason,
        "os": system,
        "kernel": release,
        "python_version": platform.python_version(),
        "user_privileges": {
            "user": getpass.getuser(),
            "is_root": is_root,
            "euid": euid,
        },
        "namespace_restrictions": {
            **proc_status,
            "unprivileged_userns_clone": userns_clone,
            "restricted": restricted,
        },
        "browser_capability": _detect_browser_capability(),
        "signals": {
            "sandbox": sandbox_signals,
            "ci": ci_signals,
            "container": container_signals,
        },
    }
