from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict[str, Any] | list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _module_from_file(src_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(src_root)
    parts = ["telecom_browser_mcp", *rel.with_suffix("").parts]
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _layer_from_module(module: str) -> str:
    parts = module.split(".")
    return parts[1] if len(parts) > 1 else "root"


def _safe_latest(path: Path, pattern: str) -> Path | None:
    matches = sorted(path.glob(pattern))
    if not matches:
        return None
    return matches[-1]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class ImportEdge:
    src_module: str
    src_layer: str
    dst_module: str
    dst_layer: str


class DependencyGraphExtractor:
    def __init__(self, *, src_root: Path) -> None:
        self.src_root = src_root

    def extract(self) -> list[ImportEdge]:
        edges: list[ImportEdge] = []
        for py_file in sorted(self.src_root.rglob("*.py")):
            src_module = _module_from_file(self.src_root, py_file)
            src_layer = _layer_from_module(src_module)
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.name
                        if name.startswith("telecom_browser_mcp"):
                            edges.append(
                                ImportEdge(
                                    src_module=src_module,
                                    src_layer=src_layer,
                                    dst_module=name,
                                    dst_layer=_layer_from_module(name),
                                )
                            )
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith("telecom_browser_mcp"):
                        edges.append(
                            ImportEdge(
                                src_module=src_module,
                                src_layer=src_layer,
                                dst_module=node.module,
                                dst_layer=_layer_from_module(node.module),
                            )
                        )
        return edges


class ModuleBoundaryAnalyzer:
    def analyze(self, *, edges: list[ImportEdge]) -> list[dict[str, Any]]:
        violations: list[dict[str, Any]] = []
        for edge in edges:
            if edge.src_layer == "server" and edge.dst_layer not in {
                "server",
                "tools",
                "models",
                "config",
                "resources",
            }:
                violations.append(
                    {
                        "violation_id": "BOUNDARY-SERVER-BYPASS",
                        "severity": "high",
                        "src_module": edge.src_module,
                        "dst_module": edge.dst_module,
                        "message": "server layer should communicate via tools/contracts",
                    }
                )
            if edge.src_layer == "models" and edge.dst_layer != "models":
                violations.append(
                    {
                        "violation_id": "BOUNDARY-MODEL-LEAK",
                        "severity": "critical",
                        "src_module": edge.src_module,
                        "dst_module": edge.dst_module,
                        "message": "models layer must not depend on higher-level modules",
                    }
                )
        return violations


class DependencyDriftAnalyzer:
    def analyze(self, *, edges: list[ImportEdge]) -> dict[str, Any]:
        unique_edges = {(e.src_module, e.dst_module) for e in edges if e.src_module != e.dst_module}
        nodes = {e.src_module for e in edges} | {e.dst_module for e in edges}
        coupling_by_layer: dict[str, set[str]] = {}
        for e in edges:
            if e.src_layer == e.dst_layer:
                continue
            coupling_by_layer.setdefault(e.src_layer, set()).add(e.dst_layer)

        # Simple cycle indicator: reciprocal dependency between module pairs.
        reciprocal_pairs = 0
        for src, dst in unique_edges:
            if (dst, src) in unique_edges:
                reciprocal_pairs += 1
        reciprocal_pairs //= 2

        return {
            "generated_at": _now_iso(),
            "module_count": len(nodes),
            "dependency_edge_count": len(unique_edges),
            "cross_layer_edge_count": sum(1 for e in edges if e.src_layer != e.dst_layer),
            "reciprocal_dependency_pair_count": reciprocal_pairs,
            "coupling_by_layer": {k: sorted(v) for k, v in coupling_by_layer.items()},
        }


class DriftScoreEngine:
    def score(
        self,
        *,
        dependency_drift: dict[str, Any],
        boundary_violations: list[dict[str, Any]],
        prior_scorecard: dict[str, Any] | None,
    ) -> dict[str, Any]:
        edge_count = int(dependency_drift.get("dependency_edge_count", 0))
        cross_layer = int(dependency_drift.get("cross_layer_edge_count", 0))
        reciprocal = int(dependency_drift.get("reciprocal_dependency_pair_count", 0))

        critical = sum(1 for row in boundary_violations if row.get("severity") == "critical")
        high = sum(1 for row in boundary_violations if row.get("severity") == "high")
        moderate = sum(1 for row in boundary_violations if row.get("severity") == "moderate")

        score = 0
        score += min(20, edge_count // 12)
        score += min(20, cross_layer // 8)
        score += min(20, reciprocal * 10)
        score += critical * 25 + high * 12 + moderate * 5

        prior = float((prior_scorecard or {}).get("architecture_drift_score", 0.0))
        drift_delta = round(score - prior, 2)

        if score >= 60:
            severity = "severe"
            outcome = "severe_drift_detected"
        elif score >= 40:
            severity = "moderate"
            outcome = "moderate_drift_detected"
        elif score >= 20:
            severity = "mild"
            outcome = "mild_drift_detected"
        else:
            severity = "low"
            outcome = "architecture_stable"

        return {
            "generated_at": _now_iso(),
            "architecture_drift_score": round(float(score), 2),
            "drift_delta_vs_prior": drift_delta,
            "drift_severity": severity,
            "drift_outcome": outcome,
            "boundary_violation_count": len(boundary_violations),
            "dependency_cycle_count": reciprocal,
            "coupling_growth_rate": 0.0,
            "architecture_invariant_violations": critical + high,
        }


class DriftReportGenerator:
    def write(
        self,
        *,
        output_dir: Path,
        ts: str,
        boundary_violations: list[dict[str, Any]],
        dependency_drift: dict[str, Any],
        drift_scorecard: dict[str, Any],
        architecture_drift_report: dict[str, Any],
    ) -> None:
        recommendation_lines = [
            f"- {item}" for item in architecture_drift_report.get("refactoring_recommendations", [])
        ] or ["- none"]

        def _lines(rows: list[dict[str, Any]], key: str) -> list[str]:
            if not rows:
                return ["- none"]
            return [f"- {r.get(key)} severity={r.get('severity','low')} src={r.get('src_module','')} dst={r.get('dst_module','')}" for r in rows]

        docs = {
            f"{ts}--architecture-conformance.md": [
                "# Architecture Conformance",
                "",
                f"- drift_outcome: {drift_scorecard['drift_outcome']}",
                f"- architecture_drift_score: {drift_scorecard['architecture_drift_score']}",
                f"- drift_severity: {drift_scorecard['drift_severity']}",
            ],
            f"{ts}--dependency-analysis.md": [
                "# Dependency Analysis",
                "",
                f"- module_count: {dependency_drift['module_count']}",
                f"- dependency_edge_count: {dependency_drift['dependency_edge_count']}",
                f"- cross_layer_edge_count: {dependency_drift['cross_layer_edge_count']}",
                f"- reciprocal_dependency_pair_count: {dependency_drift['reciprocal_dependency_pair_count']}",
            ],
            f"{ts}--boundary-violations.md": [
                "# Boundary Violations",
                "",
                f"- count: {len(boundary_violations)}",
                *_lines(boundary_violations, "violation_id"),
            ],
            f"{ts}--drift-risk-assessment.md": [
                "# Drift Risk Assessment",
                "",
                f"- drift_severity: {drift_scorecard['drift_severity']}",
                f"- architecture_invariant_violations: {drift_scorecard['architecture_invariant_violations']}",
                f"- dependency_cycle_count: {drift_scorecard['dependency_cycle_count']}",
            ],
            f"{ts}--refactoring-recommendations.md": [
                "# Refactoring Recommendations",
                "",
                *recommendation_lines,
            ],
        }

        for name, lines in docs.items():
            (output_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_system_drift_detector(*, src_root: Path, output_dir: Path) -> dict[str, Any]:
    edges = DependencyGraphExtractor(src_root=src_root).extract()
    boundary_violations = ModuleBoundaryAnalyzer().analyze(edges=edges)
    dependency_drift = DependencyDriftAnalyzer().analyze(edges=edges)

    prior_scorecard = None
    prior_path = _safe_latest(output_dir, "*--drift-scorecard.json")
    if prior_path is not None:
        prior_scorecard = _load_json(prior_path)

    drift_scorecard = DriftScoreEngine().score(
        dependency_drift=dependency_drift,
        boundary_violations=boundary_violations,
        prior_scorecard=prior_scorecard,
    )

    blocked_subsystems: list[str] = []
    if drift_scorecard["drift_severity"] in {"moderate", "severe"}:
        blocked_subsystems.append("architecture")

    recommendations = [
        "maintain adapter isolation and avoid cross-layer imports",
        "review reciprocal dependencies and remove unnecessary cycles",
    ]
    if drift_scorecard["drift_severity"] in {"moderate", "severe"}:
        recommendations.append("run architecture cleanup cycle before expansionary remediation")

    architecture_drift_report = {
        "generated_at": _now_iso(),
        "architecture_drift_score": drift_scorecard["architecture_drift_score"],
        "drift_severity": drift_scorecard["drift_severity"],
        "blocked_subsystems": blocked_subsystems,
        "refactoring_recommendations": recommendations,
    }

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir.mkdir(parents=True, exist_ok=True)

    _write_json(output_dir / f"{ts}--module-boundary-violations.json", {"violations": boundary_violations})
    _write_json(output_dir / f"{ts}--dependency-drift.json", dependency_drift)
    _write_json(output_dir / f"{ts}--drift-scorecard.json", drift_scorecard)
    _write_json(output_dir / f"{ts}--architecture-drift-report.json", architecture_drift_report)

    DriftReportGenerator().write(
        output_dir=output_dir,
        ts=ts,
        boundary_violations=boundary_violations,
        dependency_drift=dependency_drift,
        drift_scorecard=drift_scorecard,
        architecture_drift_report=architecture_drift_report,
    )

    return {
        "timestamp": ts,
        "architecture_drift_report_path": str(output_dir / f"{ts}--architecture-drift-report.json"),
        "drift_scorecard_path": str(output_dir / f"{ts}--drift-scorecard.json"),
        "drift_severity": drift_scorecard["drift_severity"],
        "architecture_drift_score": drift_scorecard["architecture_drift_score"],
    }
