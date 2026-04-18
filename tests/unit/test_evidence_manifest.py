from __future__ import annotations

import json
from pathlib import Path

import pytest

from telecom_browser_mcp.tools.service import ToolService


@pytest.mark.asyncio
async def test_debug_bundle_manifest_includes_adapter_identity() -> None:
    service = ToolService()
    open_result = await service.open_app({"target_url": "https://example.com"})
    session_id = open_result["data"]["session_id"]

    bundle_result = await service.collect_debug_bundle({"session_id": session_id, "reason": "phase-0"})

    assert bundle_result["ok"] is True
    bundle_path = Path(bundle_result["data"]["bundle_path"])
    manifest_path = bundle_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["adapter_id"] == open_result["meta"]["adapter_id"]
    assert manifest["adapter_name"] == open_result["meta"]["adapter_name"]
    assert manifest["adapter_version"] == open_result["meta"]["adapter_version"]
    assert manifest["contract_version"] == open_result["meta"]["contract_version"]
    assert manifest["scenario_id"] == open_result["meta"]["scenario_id"]
    assert manifest["runtime_metadata"]["target_classification"] == "generic_web"
    assert "environment_vs_product" in manifest["verdict_summary"]

    verdict_summary_path = bundle_path / "diagnostics" / "verdict_summary.json"
    verdict_summary = json.loads(verdict_summary_path.read_text(encoding="utf-8"))
    assert verdict_summary["adapter_id"] == open_result["meta"]["adapter_id"]
    assert verdict_summary["verdict"] in {"ok", "failed"}


@pytest.mark.asyncio
async def test_bundle_retention_prunes_oldest_bundles() -> None:
    service = ToolService(max_bundles_per_session=2)
    open_result = await service.open_app({"target_url": "https://example.com"})
    session_id = open_result["data"]["session_id"]

    for idx in range(3):
        result = await service.collect_debug_bundle({"session_id": session_id, "reason": f"bundle-{idx}"})
        assert result["ok"] is True

    artifact_root = Path(service.sessions.get(session_id).model.artifact_root)  # type: ignore[union-attr]
    bundles = sorted(path.name for path in artifact_root.iterdir() if path.is_dir() and path.name.startswith("bundle-"))
    assert len(bundles) == 2
