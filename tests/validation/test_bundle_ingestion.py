from __future__ import annotations

import json
from pathlib import Path

from telecom_browser_mcp.validation.validation_diagnostics_ingestor import ingest_manifest


def test_ingest_manifest_partial_bundle(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    console = bundle / "console.json"
    console.write_text("{}", encoding="utf-8")
    manifest = bundle / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "run_id": "run-1",
                "scenario_id": "stale_selector_recovery",
                "session_id": "sess-1",
                "fault_type": "lifecycle_fault",
                "injection_point": "after_selector_resolved",
                "status": "failed",
                "failure_classification": "session",
                "artifact_paths": {
                    "console": str(console),
                    "network": None,
                    "page_errors": None,
                    "screenshot": None,
                    "dom_snapshot": None,
                    "trace": None,
                },
                "collection_gaps": ["trace unavailable"],
            }
        ),
        encoding="utf-8",
    )

    ingested = ingest_manifest(manifest)
    assert ingested.scenario_id == "stale_selector_recovery"
    assert "console" in ingested.signals_present
    assert ingested.bundle_health == "partial"
    assert "trace unavailable" in ingested.collection_gaps


def test_ingest_manifest_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing-manifest.json"
    ingested = ingest_manifest(missing)
    assert ingested.bundle_health == "missing"
    assert ingested.parse_error == "manifest_missing"
