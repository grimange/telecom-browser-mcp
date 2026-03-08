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


def _safe_latest(path: Path, pattern: str) -> Path | None:
    matches = sorted(path.glob(pattern))
    if not matches:
        return None
    return matches[-1]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _module_from_file(src_root: Path, file_path: Path) -> str:
    rel = file_path.relative_to(src_root)
    parts = ["telecom_browser_mcp", *rel.with_suffix("").parts]
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _layer_from_module(module: str) -> str:
    parts = module.split(".")
    return parts[1] if len(parts) > 1 else "root"


@dataclass(frozen=True)
class ImportEdge:
    src_module: str
    src_layer: str
    dst_module: str
    dst_layer: str


class ArchitectureRuleLoader:
    def __init__(self, *, src_root: Path) -> None:
        self.src_root = src_root

    def collect_internal_import_edges(self) -> list[ImportEdge]:
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
                    if not node.module:
                        continue
                    module = node.module
                    if module.startswith("telecom_browser_mcp"):
                        edges.append(
                            ImportEdge(
                                src_module=src_module,
                                src_layer=src_layer,
                                dst_module=module,
                                dst_layer=_layer_from_module(module),
                            )
                        )
        return edges


class BoundaryRuleEvaluator:
    PUBLIC_ADAPTER_MODULES = {
        "telecom_browser_mcp.adapters",
        "telecom_browser_mcp.adapters.base",
        "telecom_browser_mcp.adapters.registry",
        "telecom_browser_mcp.adapters.harness",
    }

    def evaluate(self, *, edges: list[ImportEdge]) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []
        for edge in edges:
            if (
                edge.src_layer != "adapters"
                and edge.dst_layer == "adapters"
                and edge.dst_module not in self.PUBLIC_ADAPTER_MODULES
            ):
                violations.append(
                    {
                        "rule_id": "BOUNDARY-ADAPTER-ISOLATION-001",
                        "severity": "high",
                        "src_module": edge.src_module,
                        "dst_module": edge.dst_module,
                        "message": "non-adapter module imports concrete adapter implementation",
                    }
                )

            if edge.src_layer == "models" and edge.dst_layer != "models":
                violations.append(
                    {
                        "rule_id": "BOUNDARY-MODEL-PURITY-001",
                        "severity": "critical",
                        "src_module": edge.src_module,
                        "dst_module": edge.dst_module,
                        "message": "models layer must remain dependency-minimal and not import other product layers",
                    }
                )

        return {
            "generated_at": _now_iso(),
            "violation_count": len(violations),
            "violations": violations,
        }


class DependencyRuleEvaluator:
    LAYER_LEVEL = {
        "models": 0,
        "evidence": 0,
        "config": 0,
        "resources": 0,
        "adapters": 1,
        "inspectors": 1,
        "diagnostics": 1,
        "browser": 1,
        "sessions": 1,
        "validation": 1,
        "tools": 2,
        "server": 3,
    }

    def evaluate(self, *, edges: list[ImportEdge]) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []
        for edge in edges:
            src_level = self.LAYER_LEVEL.get(edge.src_layer)
            dst_level = self.LAYER_LEVEL.get(edge.dst_layer)
            if src_level is None or dst_level is None:
                continue
            if src_level < dst_level:
                violations.append(
                    {
                        "rule_id": "DEPENDENCY-DIRECTION-001",
                        "severity": "moderate",
                        "src_module": edge.src_module,
                        "dst_module": edge.dst_module,
                        "message": "lower layer imports higher layer",
                    }
                )

        return {
            "generated_at": _now_iso(),
            "violation_count": len(violations),
            "violations": violations,
        }


class ContractLayerRuleEvaluator:
    def evaluate(self, *, edges: list[ImportEdge]) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []
        server_allowed = {"server", "tools", "config", "models", "resources"}
        for edge in edges:
            if edge.src_layer == "server" and edge.dst_layer not in server_allowed:
                violations.append(
                    {
                        "rule_id": "CONTRACT-LAYER-BYPASS-001",
                        "severity": "high",
                        "src_module": edge.src_module,
                        "dst_module": edge.dst_module,
                        "message": "server layer bypasses tools contract boundary",
                    }
                )
            if edge.src_layer == "tools" and edge.dst_layer == "server":
                violations.append(
                    {
                        "rule_id": "CONTRACT-LAYER-BYPASS-002",
                        "severity": "high",
                        "src_module": edge.src_module,
                        "dst_module": edge.dst_module,
                        "message": "tools layer depends on server transport layer",
                    }
                )

        return {
            "generated_at": _now_iso(),
            "violation_count": len(violations),
            "violations": violations,
        }


class AdapterIsolationEvaluator:
    def evaluate(self, *, edges: list[ImportEdge]) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []
        for edge in edges:
            if edge.src_layer != "adapters" or edge.dst_layer != "adapters":
                continue
            src_parts = edge.src_module.split(".")
            dst_parts = edge.dst_module.split(".")
            src_leaf = src_parts[2] if len(src_parts) > 2 else ""
            dst_leaf = dst_parts[2] if len(dst_parts) > 2 else ""
            if src_leaf in {"registry", "base", "harness", ""}:
                continue
            if dst_leaf in {"registry", "base", "harness", ""}:
                continue
            if src_leaf != dst_leaf:
                violations.append(
                    {
                        "rule_id": "ADAPTER-ISOLATION-001",
                        "severity": "moderate",
                        "src_module": edge.src_module,
                        "dst_module": edge.dst_module,
                        "message": "concrete adapter depends on another concrete adapter",
                    }
                )

        return {
            "generated_at": _now_iso(),
            "violation_count": len(violations),
            "violations": violations,
        }


class ScopeGuardrailEvaluator:
    def evaluate(self, *, closed_loop_dir: Path) -> dict[str, Any]:
        latest_batches = _safe_latest(closed_loop_dir, "*--batch-execution-results.json")
        if latest_batches is None:
            return {
                "generated_at": _now_iso(),
                "violation_count": 0,
                "violations": [],
                "source_path": "",
            }

        payload = _load_json(latest_batches)
        selected = payload.get("selected_batches", [])
        domains = sorted({str(row.get("domain", "unknown")) for row in selected})
        violations: list[dict[str, Any]] = []

        if len(domains) >= 3:
            violations.append(
                {
                    "rule_id": "SCOPE-GUARDRAIL-001",
                    "severity": "moderate",
                    "message": "selected remediation spans many subsystem domains",
                    "selected_domains": domains,
                }
            )

        return {
            "generated_at": _now_iso(),
            "violation_count": len(violations),
            "violations": violations,
            "source_path": str(latest_batches),
        }


class GuardrailVerdictEngine:
    def decide(self, *, violations: list[dict[str, Any]]) -> str:
        severities = [str(row.get("severity", "low")) for row in violations]
        if "critical" in severities:
            return "guardrails_block"
        if "high" in severities or "moderate" in severities or "low" in severities:
            return "guardrails_warn"
        return "guardrails_pass"


class GuardrailReportGenerator:
    def write(
        self,
        *,
        output_dir: Path,
        precheck: dict[str, Any],
        postcheck: dict[str, Any],
        boundary_results: dict[str, Any],
        dependency_results: dict[str, Any],
        contract_layer_results: dict[str, Any],
    ) -> None:
        md_files = {
            "guardrails-precheck.md": [
                "# Guardrails Precheck",
                "",
                f"- verdict: {precheck['verdict']}",
                f"- violation_count: {precheck['violation_count']}",
            ],
            "guardrails-postcheck.md": [
                "# Guardrails Postcheck",
                "",
                f"- verdict: {postcheck['verdict']}",
                f"- violation_count: {postcheck['violation_count']}",
            ],
            "boundary-rule-results.md": [
                "# Boundary Rule Results",
                "",
                f"- violation_count: {boundary_results['violation_count']}",
                *[
                    f"- {row['rule_id']} severity={row['severity']} src={row.get('src_module', '')} dst={row.get('dst_module', '')}"
                    for row in boundary_results["violations"]
                ],
            ],
            "dependency-rule-results.md": [
                "# Dependency Rule Results",
                "",
                f"- violation_count: {dependency_results['violation_count']}",
                *[
                    f"- {row['rule_id']} severity={row['severity']} src={row.get('src_module', '')} dst={row.get('dst_module', '')}"
                    for row in dependency_results["violations"]
                ],
            ],
            "contract-layer-rule-results.md": [
                "# Contract Layer Rule Results",
                "",
                f"- violation_count: {contract_layer_results['violation_count']}",
                *[
                    f"- {row['rule_id']} severity={row['severity']} src={row.get('src_module', '')} dst={row.get('dst_module', '')}"
                    for row in contract_layer_results["violations"]
                ],
            ],
            "guardrails-verdict.md": [
                "# Guardrails Verdict",
                "",
                f"- precheck_verdict: {precheck['verdict']}",
                f"- postcheck_verdict: {postcheck['verdict']}",
                f"- precheck_violation_count: {precheck['violation_count']}",
                f"- postcheck_violation_count: {postcheck['violation_count']}",
            ],
        }
        for file_name, lines in md_files.items():
            lines = lines if len(lines) > 3 else [*lines, "- no violations"]
            (output_dir / file_name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_verdict_payload(
    *,
    mode: str,
    verdict: str,
    violations: list[dict[str, Any]],
    boundary_results: dict[str, Any],
    dependency_results: dict[str, Any],
    contract_layer_results: dict[str, Any],
) -> dict[str, Any]:
    return {
        "generated_at": _now_iso(),
        "mode": mode,
        "verdict": verdict,
        "violation_count": len(violations),
        "boundary_violation_flags": [row["rule_id"] for row in boundary_results["violations"]],
        "dependency_violation_flags": [row["rule_id"] for row in dependency_results["violations"]],
        "contract_layer_violation_flags": [
            row["rule_id"] for row in contract_layer_results["violations"]
        ],
        "violations": violations,
    }


def run_architecture_guardrails(
    *,
    src_root: Path,
    closed_loop_dir: Path,
    output_dir: Path,
) -> dict[str, Any]:
    loader = ArchitectureRuleLoader(src_root=src_root)
    edges = loader.collect_internal_import_edges()

    boundary_results = BoundaryRuleEvaluator().evaluate(edges=edges)
    dependency_results = DependencyRuleEvaluator().evaluate(edges=edges)
    contract_layer_results = ContractLayerRuleEvaluator().evaluate(edges=edges)
    adapter_isolation_results = AdapterIsolationEvaluator().evaluate(edges=edges)
    scope_results = ScopeGuardrailEvaluator().evaluate(closed_loop_dir=closed_loop_dir)

    all_violations = [
        *boundary_results["violations"],
        *dependency_results["violations"],
        *contract_layer_results["violations"],
        *adapter_isolation_results["violations"],
        *scope_results["violations"],
    ]

    verdict_engine = GuardrailVerdictEngine()
    precheck_verdict = verdict_engine.decide(violations=all_violations)
    postcheck_verdict = verdict_engine.decide(violations=all_violations)

    precheck_payload = _build_verdict_payload(
        mode="precheck",
        verdict=precheck_verdict,
        violations=all_violations,
        boundary_results=boundary_results,
        dependency_results=dependency_results,
        contract_layer_results=contract_layer_results,
    )
    postcheck_payload = _build_verdict_payload(
        mode="postcheck",
        verdict=postcheck_verdict,
        violations=all_violations,
        boundary_results=boundary_results,
        dependency_results=dependency_results,
        contract_layer_results=contract_layer_results,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    _write_json(output_dir / "guardrail-violations.json", all_violations)
    _write_json(output_dir / "dependency-rule-results.json", dependency_results)
    _write_json(output_dir / "boundary-rule-results.json", boundary_results)
    _write_json(output_dir / "contract-layer-rule-results.json", contract_layer_results)
    _write_json(output_dir / "adapter-isolation-rule-results.json", adapter_isolation_results)
    _write_json(output_dir / "scope-guardrail-results.json", scope_results)
    _write_json(output_dir / "guardrails-verdict.json", {"precheck": precheck_payload, "postcheck": postcheck_payload})

    _write_json(output_dir / f"{ts}--precheck-verdict.json", precheck_payload)
    _write_json(output_dir / f"{ts}--postcheck-verdict.json", postcheck_payload)

    GuardrailReportGenerator().write(
        output_dir=output_dir,
        precheck=precheck_payload,
        postcheck=postcheck_payload,
        boundary_results=boundary_results,
        dependency_results=dependency_results,
        contract_layer_results=contract_layer_results,
    )

    return {
        "timestamp": ts,
        "precheck_verdict_path": str(output_dir / f"{ts}--precheck-verdict.json"),
        "postcheck_verdict_path": str(output_dir / f"{ts}--postcheck-verdict.json"),
        "guardrails_verdict": postcheck_verdict,
        "violation_count": len(all_violations),
    }
