from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REQUIRED_MANIFEST_KEYS = {
    "run_id",
    "scenario_id",
    "session_id",
    "fault_type",
    "injection_point",
    "status",
    "failure_classification",
    "artifact_paths",
    "collection_gaps",
}


@dataclass(slots=True)
class BundleIngestion:
    scenario_id: str
    bundle_path: str
    manifest_path: str
    signals_present: list[str]
    signals_missing: list[str]
    collection_gaps: list[str]
    cleanup_status: str
    bundle_health: str
    failure_classification: str
    status: str
    parse_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "bundle_path": self.bundle_path,
            "manifest_path": self.manifest_path,
            "signals_present": self.signals_present,
            "signals_missing": self.signals_missing,
            "collection_gaps": self.collection_gaps,
            "cleanup_status": self.cleanup_status,
            "bundle_health": self.bundle_health,
            "failure_classification": self.failure_classification,
            "status": self.status,
            "parse_error": self.parse_error,
        }


def ingest_manifest(manifest_path: str | Path) -> BundleIngestion:
    path = Path(manifest_path)
    if not path.exists():
        return BundleIngestion(
            scenario_id=path.parent.name,
            bundle_path=str(path.parent),
            manifest_path=str(path),
            signals_present=[],
            signals_missing=["manifest"],
            collection_gaps=["manifest missing"],
            cleanup_status="unknown",
            bundle_health="missing",
            failure_classification="unknown",
            status="unknown",
            parse_error="manifest_missing",
        )

    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return BundleIngestion(
            scenario_id=path.parent.name,
            bundle_path=str(path.parent),
            manifest_path=str(path),
            signals_present=[],
            signals_missing=["manifest"],
            collection_gaps=[f"manifest parse error: {exc}"],
            cleanup_status="unknown",
            bundle_health="malformed",
            failure_classification="unknown",
            status="unknown",
            parse_error=str(exc),
        )

    missing_top_level = sorted(REQUIRED_MANIFEST_KEYS - set(manifest.keys()))
    artifact_paths = manifest.get("artifact_paths", {})
    signals_present: list[str] = []
    signals_missing: list[str] = []
    for signal, field in (
        ("console", "console"),
        ("network", "network"),
        ("page_errors", "page_errors"),
        ("screenshot", "screenshot"),
        ("dom_snapshot", "dom_snapshot"),
        ("trace", "trace"),
    ):
        value = artifact_paths.get(field)
        if value and Path(value).exists():
            signals_present.append(signal)
        else:
            signals_missing.append(signal)

    collection_gaps = list(manifest.get("collection_gaps", []))
    if missing_top_level:
        collection_gaps.append(f"manifest missing keys: {', '.join(missing_top_level)}")

    if missing_top_level:
        bundle_health = "malformed"
    elif signals_missing:
        bundle_health = "partial"
    else:
        bundle_health = "full"

    return BundleIngestion(
        scenario_id=str(manifest.get("scenario_id", path.parent.name)),
        bundle_path=str(path.parent),
        manifest_path=str(path),
        signals_present=signals_present,
        signals_missing=signals_missing,
        collection_gaps=collection_gaps,
        cleanup_status="unknown",
        bundle_health=bundle_health,
        failure_classification=str(manifest.get("failure_classification", "unknown")),
        status=str(manifest.get("status", "unknown")),
    )


def ingest_lifecycle_results(results_path: str | Path) -> list[BundleIngestion]:
    payload = json.loads(Path(results_path).read_text(encoding="utf-8"))
    ingested: list[BundleIngestion] = []
    for result in payload.get("results", []):
        manifest_path = result.get("diagnostics_manifest_path")
        if manifest_path:
            ingested.append(ingest_manifest(manifest_path))
            continue
        ingested.append(
            BundleIngestion(
                scenario_id=str(result.get("name", "unknown")),
                bundle_path="",
                manifest_path="",
                signals_present=[],
                signals_missing=["manifest"],
                collection_gaps=["bundle path missing from lifecycle results"],
                cleanup_status="unknown",
                bundle_health="missing",
                failure_classification="unknown",
                status="unknown",
                parse_error="manifest_path_missing",
            )
        )
    return ingested
