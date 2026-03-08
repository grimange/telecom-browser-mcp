import json
from pathlib import Path

from telecom_browser_mcp.live_verification import (
    _evaluate_environment_authority,
    run_controlled_live_verification,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_environment_authority_rejects_unsupported_runtime_class(monkeypatch) -> None:
    monkeypatch.delenv("TELECOM_BROWSER_MCP_TRANSPORT", raising=False)
    fingerprint = {
        "runtime_class": "wsl_runtime",
        "browser_capability": {"available": True},
    }
    compatibility_inputs = {
        "available": True,
        "compatibility_matrix": {
            "approved_transport_modes": ["stdio"],
            "approved_browser_execution_modes": ["playwright_headless_chromium"],
            "supported_runtime_classes": ["authoritative_host", "container_runtime"],
        },
        "support_policy": {
            "runtime_policy": {
                "allowed_runtime_classes": ["authoritative_host", "container_runtime"],
                "rejected_runtime_classes": ["sandbox_runtime", "wsl_runtime"],
                "container_requires_browser_capability": True,
            }
        },
    }
    decision = _evaluate_environment_authority(
        runtime_fingerprint=fingerprint,
        compatibility_inputs=compatibility_inputs,
    )
    assert decision["authoritative"] is False
    assert decision["environment_verdict"] == "environment_not_authoritative"
    assert "runtime_class_rejected:wsl_runtime" in decision["reasons"]


def test_run_controlled_live_verification_stops_on_environment_gate(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TELECOM_BROWSER_MCP_RUNTIME_CLASS", "sandbox_runtime")

    matrix_dir = tmp_path / "docs/compatibility-matrix/telecom-browser-mcp"
    _write_json(
        matrix_dir / "compatibility-matrix.json",
        {
            "approved_transport_modes": ["stdio"],
            "approved_browser_execution_modes": ["playwright_headless_chromium"],
            "supported_runtime_classes": ["authoritative_host", "container_runtime"],
        },
    )
    _write_json(
        matrix_dir / "support-policy.json",
        {
            "runtime_policy": {
                "allowed_runtime_classes": ["authoritative_host", "container_runtime"],
                "rejected_runtime_classes": ["sandbox_runtime"],
                "container_requires_browser_capability": True,
            }
        },
    )
    (matrix_dir / "recommended-release-environment.md").write_text(
        "authoritative host required\n",
        encoding="utf-8",
    )

    out_dir = tmp_path / "out"
    evidence_dir = tmp_path / "evidence"
    result = run_controlled_live_verification(output_dir=out_dir, evidence_dir=evidence_dir)

    assert result["verdict"] == "blocked_by_environment"
    assert result["environment_verdict"] == "environment_not_authoritative"

    verdict = json.loads((out_dir / "live-verification-verdict.json").read_text(encoding="utf-8"))
    assert verdict["verdict"] == "blocked_by_environment"
    assert verdict["environment_verdict"] == "environment_not_authoritative"

    probe = json.loads((evidence_dir / "mcp-interop-probe.json").read_text(encoding="utf-8"))
    assert probe["classification"] == "transport_environment_blocked"
