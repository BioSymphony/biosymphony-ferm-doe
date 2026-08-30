"""Validate the public adaptive-backend evaluation surface."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from .tool_registry import load_tool_registry_index


DEFAULT_SURFACE = Path("docs/adaptive-backend-evaluation.json")
DEFAULT_REGISTRY = Path("docs/tool-registry.json")
REQUIRED_OWNED_BOUNDARIES = {
    "scale_bridge",
    "assay_readiness",
    "evidence_dossier",
    "cost_realism",
    "handoff_packet",
    "campaign_manifest",
    "response_semantics",
    "readiness_verdict",
}
REQUIRED_BACKENDS = {"bofire", "baybe", "botorch", "ax", "entmoot"}
REQUIRED_ALTERNATIVE_ROUTES = {"baybe", "ax", "botorch"}
PERMISSIVE_LICENSES = {"Apache-2.0", "BSD-3-Clause", "BSD-3", "MIT"}
IMPORT_MODULES = {
    "ax": "ax",
    "baybe": "baybe",
    "bofire": "bofire",
    "botorch": "botorch",
    "entmoot": "entmoot",
}


@dataclass(frozen=True)
class SurfaceFinding:
    severity: str
    item_id: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def load_surface(path: Path = DEFAULT_SURFACE) -> dict[str, Any]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"expected adaptive backend surface object: {path}")
    return data


def validate_surface(
    path: Path,
    *,
    registry_path: Path = DEFAULT_REGISTRY,
    pyproject_path: Path = Path("pyproject.toml"),
    live_imports: bool = False,
) -> dict[str, Any]:
    data = load_surface(path)
    registry = load_tool_registry_index(registry_path)
    pyproject_extras = _load_pyproject_extras(pyproject_path)
    root = _resolve_repo_root(path)
    findings: list[SurfaceFinding] = []

    if data.get("schema_version") != 1:
        findings.append(SurfaceFinding("error", "_surface", "schema_version must be 1"))
    if data.get("surface_kind") != "biosymphony_biomanufacturing_adaptive_backend_selection":
        findings.append(SurfaceFinding("error", "_surface", "surface_kind is invalid"))

    owned = set(str(item) for item in data.get("owned_by_biosymphony", []) if item)
    for boundary in sorted(REQUIRED_OWNED_BOUNDARIES - owned):
        findings.append(SurfaceFinding("error", "_surface", f"missing BioSymphony-owned boundary: {boundary}"))

    candidate_index: dict[str, dict[str, Any]] = {}
    candidates = data.get("backend_candidates")
    if not isinstance(candidates, list) or not candidates:
        findings.append(SurfaceFinding("error", "_surface", "backend_candidates must be a non-empty list"))
        candidates = []

    for raw in candidates:
        if not isinstance(raw, dict):
            findings.append(SurfaceFinding("error", "_surface", "backend candidate must be an object"))
            continue
        tool_id = str(raw.get("tool_id") or "")
        if not tool_id:
            findings.append(SurfaceFinding("error", "_surface", "backend candidate missing tool_id"))
            continue
        if tool_id in candidate_index:
            findings.append(SurfaceFinding("error", tool_id, "duplicate backend candidate"))
        candidate_index[tool_id] = raw
        findings.extend(
            _validate_candidate(
                tool_id,
                raw,
                registry,
                pyproject_extras=pyproject_extras,
                live_imports=live_imports,
            )
        )

    missing_required = REQUIRED_BACKENDS - set(candidate_index)
    for tool_id in sorted(missing_required):
        findings.append(SurfaceFinding("error", tool_id, "required backend candidate is missing"))

    findings.extend(_validate_workflow_position(data, candidate_index))

    default_candidates = [
        tool_id
        for tool_id, candidate in candidate_index.items()
        if candidate.get("default_position") == "default_for_static_constrained_doe_bo"
    ]
    if default_candidates != ["bofire"]:
        findings.append(
            SurfaceFinding(
                "error",
                "_surface",
                "BoFire must be the only default_for_static_constrained_doe_bo candidate",
            )
        )

    scenarios = data.get("scenario_matrix")
    if not isinstance(scenarios, list) or not scenarios:
        findings.append(SurfaceFinding("error", "_surface", "scenario_matrix must be a non-empty list"))
        scenarios = []
    for raw in scenarios:
        if not isinstance(raw, dict):
            findings.append(SurfaceFinding("error", "_surface", "scenario must be an object"))
            continue
        findings.extend(_validate_scenario(raw, candidate_index, registry, root=root))

    errors = [finding for finding in findings if finding.severity == "error"]
    warnings = [finding for finding in findings if finding.severity == "warning"]
    return {
        "schema_version": 1,
        "surface_check_kind": "biosymphony_adaptive_backend_surface_check",
        "path": str(path),
        "registry_path": str(registry_path),
        "pyproject_path": str(pyproject_path),
        "status": "FAIL" if errors else "PASS",
        "candidate_count": len(candidate_index),
        "scenario_count": len(scenarios),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "live_imports": live_imports,
        "findings": [finding.to_dict() for finding in findings],
    }


def _validate_candidate(
    tool_id: str,
    candidate: dict[str, Any],
    registry: dict[str, dict[str, Any]],
    *,
    pyproject_extras: dict[str, set[str]],
    live_imports: bool,
) -> list[SurfaceFinding]:
    findings: list[SurfaceFinding] = []
    required = {"role", "default_position", "fit_for", "not_for", "known_caveats", "smoke_contract"}
    for field in sorted(required - set(candidate)):
        findings.append(SurfaceFinding("error", tool_id, f"missing required field: {field}"))
    if tool_id not in registry:
        findings.append(SurfaceFinding("error", tool_id, "tool_id is not present in docs/tool-registry.json"))
    else:
        license_text = str(registry[tool_id].get("license") or "")
        normalized = _normalize_license(license_text)
        if normalized not in PERMISSIVE_LICENSES:
            license_gate = candidate.get("license_gate")
            if (
                not isinstance(license_gate, dict)
                or license_gate.get("required") is not True
                or not str(license_gate.get("restriction") or "").strip()
                or not str(license_gate.get("action") or "").strip()
            ):
                findings.append(
                    SurfaceFinding(
                        "error",
                        tool_id,
                        f"restricted license requires an explicit license_gate: {license_text}",
                    )
                )
        registry_extra = str(registry[tool_id].get("pyproject_extra") or "")
        candidate_extra = str(candidate.get("install_extra") or "")
        if registry_extra and candidate_extra and registry_extra != candidate_extra:
            findings.append(
                SurfaceFinding(
                    "error",
                    tool_id,
                    f"install_extra disagrees with registry pyproject_extra: {candidate_extra} != {registry_extra}",
                )
            )
    install_extra = str(candidate.get("install_extra") or "")
    if install_extra and pyproject_extras and install_extra not in pyproject_extras:
        findings.append(SurfaceFinding("error", tool_id, f"install_extra is not declared in pyproject.toml: {install_extra}"))
    elif install_extra and pyproject_extras and tool_id not in {"stdlib"}:
        package_names = pyproject_extras.get(install_extra, set())
        expected_names = {
            "ax": "ax-platform",
            "baybe": "baybe",
            "bofire": "bofire",
            "botorch": "botorch",
            "entmoot": "entmoot",
        }
        expected = expected_names.get(tool_id)
        if expected and expected not in package_names:
            findings.append(SurfaceFinding("error", tool_id, f"install_extra {install_extra} does not include package {expected}"))
    for field in ("fit_for", "not_for", "known_caveats"):
        if not isinstance(candidate.get(field), list) or not candidate.get(field):
            findings.append(SurfaceFinding("error", tool_id, f"{field} must be a non-empty list"))
    smoke = candidate.get("smoke_contract")
    if not isinstance(smoke, dict):
        findings.append(SurfaceFinding("error", tool_id, "smoke_contract must be an object"))
    elif not smoke.get("minimum_surface") or not isinstance(smoke.get("must_check"), list) or not smoke.get("must_check"):
        findings.append(SurfaceFinding("error", tool_id, "smoke_contract must name minimum_surface and must_check"))
    if live_imports:
        module = IMPORT_MODULES.get(tool_id)
        if module:
            try:
                importlib.import_module(module)
            except Exception as exc:  # pragma: no cover - depends on optional packages
                findings.append(SurfaceFinding("error", tool_id, f"live import failed for module {module}: {exc}"))
    return findings


def _validate_workflow_position(
    data: dict[str, Any],
    candidates: dict[str, dict[str, Any]],
) -> list[SurfaceFinding]:
    findings: list[SurfaceFinding] = []
    workflow = data.get("workflow_position")
    if not isinstance(workflow, dict):
        return [SurfaceFinding("error", "_surface", "workflow_position must be an object")]
    summary = str(workflow.get("summary") or "")
    for phrase in ("BoFire", "BioSymphony", "BayBE", "Ax", "BoTorch"):
        if phrase not in summary:
            findings.append(SurfaceFinding("error", "_surface", f"workflow_position.summary must mention {phrase}"))
    default_stack = workflow.get("default_stack")
    if not isinstance(default_stack, list) or not default_stack:
        findings.append(SurfaceFinding("error", "_surface", "workflow_position.default_stack must be a non-empty list"))
    else:
        default_text = " ".join(str(item) for item in default_stack)
        if "bofire" not in default_text.lower():
            findings.append(SurfaceFinding("error", "_surface", "workflow_position.default_stack must include BoFire"))
        if "biosymphony" not in default_text.lower():
            findings.append(SurfaceFinding("error", "_surface", "workflow_position.default_stack must include BioSymphony layers"))
    routes = workflow.get("alternative_backend_routes")
    if not isinstance(routes, list) or not routes:
        findings.append(SurfaceFinding("error", "_surface", "workflow_position.alternative_backend_routes must be a non-empty list"))
        route_ids: set[str] = set()
    else:
        route_ids = {str(route.get("tool_id") or "") for route in routes if isinstance(route, dict)}
        for route in routes:
            if not isinstance(route, dict):
                findings.append(SurfaceFinding("error", "_surface", "workflow_position route must be an object"))
                continue
            tool_id = str(route.get("tool_id") or "")
            if tool_id and tool_id not in candidates:
                findings.append(SurfaceFinding("error", tool_id, "workflow_position route is not a backend candidate"))
            if not str(route.get("when") or "").strip():
                findings.append(SurfaceFinding("error", tool_id or "_surface", "workflow_position route must explain when to use it"))
    for tool_id in sorted(REQUIRED_ALTERNATIVE_ROUTES - route_ids):
        findings.append(SurfaceFinding("error", tool_id, "workflow_position is missing required alternative route"))
    retained_raw = workflow.get("retained_biosymphony_layers")
    if not isinstance(retained_raw, list):
        findings.append(SurfaceFinding("error", "_surface", "workflow_position.retained_biosymphony_layers must be a list"))
        retained: set[str] = set()
    else:
        retained = set(str(item) for item in retained_raw if item)
    required_retained = REQUIRED_OWNED_BOUNDARIES - {"campaign_manifest"}
    for boundary in sorted(required_retained - retained):
        findings.append(SurfaceFinding("error", "_surface", f"workflow_position missing retained BioSymphony layer: {boundary}"))
    return findings


def _validate_scenario(
    scenario: dict[str, Any],
    candidates: dict[str, dict[str, Any]],
    registry: dict[str, dict[str, Any]],
    *,
    root: Path,
) -> list[SurfaceFinding]:
    scenario_id = str(scenario.get("scenario_id") or "_scenario")
    findings: list[SurfaceFinding] = []
    primary = str(scenario.get("primary_tool") or "")
    if not primary:
        findings.append(SurfaceFinding("error", scenario_id, "primary_tool is required"))
    elif primary not in candidates:
        findings.append(SurfaceFinding("error", scenario_id, f"primary_tool is not a backend candidate: {primary}"))
    fallback_tools = scenario.get("fallback_tools")
    if not isinstance(fallback_tools, list):
        findings.append(SurfaceFinding("error", scenario_id, "fallback_tools must be a list"))
        fallback_tools = []
    for tool_id in fallback_tools:
        if str(tool_id) not in candidates and str(tool_id) not in registry and str(tool_id) != "stdlib":
            findings.append(SurfaceFinding("error", scenario_id, f"unknown fallback tool: {tool_id}"))
    criteria = scenario.get("acceptance_criteria")
    if not isinstance(criteria, list) or len(criteria) < 3:
        findings.append(SurfaceFinding("error", scenario_id, "acceptance_criteria must include at least 3 checks"))
    if not str(scenario.get("backend_role") or "").strip():
        findings.append(SurfaceFinding("error", scenario_id, "backend_role is required"))
    fixture_path = str(scenario.get("fixture_path") or "").strip()
    if not fixture_path:
        findings.append(SurfaceFinding("error", scenario_id, "fixture_path is required"))
    else:
        fixture = Path(fixture_path)
        if not fixture.is_absolute():
            fixture = root / fixture
        smoke_plan = fixture / "smoke_plan.json"
        if not smoke_plan.exists():
            findings.append(SurfaceFinding("error", scenario_id, f"fixture smoke_plan.json is missing: {fixture_path}"))
        else:
            findings.extend(_validate_smoke_plan(smoke_plan, scenario_id, primary))
    return findings


def _validate_smoke_plan(path: Path, scenario_id: str, primary_tool: str) -> list[SurfaceFinding]:
    findings: list[SurfaceFinding] = []
    try:
        plan = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        return [SurfaceFinding("error", scenario_id, f"invalid smoke_plan.json: {exc}")]
    if plan.get("scenario_id") != scenario_id:
        findings.append(SurfaceFinding("error", scenario_id, "smoke_plan scenario_id does not match scenario matrix"))
    if plan.get("primary_tool") != primary_tool:
        findings.append(SurfaceFinding("error", scenario_id, "smoke_plan primary_tool does not match scenario matrix"))
    for field in ("inputs", "commands", "expected_artifacts", "acceptance_checks"):
        if not isinstance(plan.get(field), list) or not plan.get(field):
            findings.append(SurfaceFinding("error", scenario_id, f"smoke_plan {field} must be a non-empty list"))
    if isinstance(plan.get("inputs"), list):
        for item in plan["inputs"]:
            input_path = item.get("path") if isinstance(item, dict) else item
            if not input_path:
                findings.append(SurfaceFinding("error", scenario_id, "smoke_plan input is missing path"))
                continue
            resolved = path.parent / str(input_path)
            if not resolved.exists():
                findings.append(SurfaceFinding("error", scenario_id, f"smoke_plan input path is missing: {input_path}"))
    return findings


def _load_pyproject_extras(path: Path) -> dict[str, set[str]]:
    if not path.exists():
        return {}
    try:
        data = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError:
        return {}
    optional = data.get("project", {}).get("optional-dependencies", {})
    if not isinstance(optional, dict):
        return {}
    extras: dict[str, set[str]] = {}
    for extra, requirements in optional.items():
        if isinstance(requirements, list):
            extras[str(extra)] = {_requirement_name(str(requirement)) for requirement in requirements}
    return extras


def _requirement_name(requirement: str) -> str:
    name = []
    for char in requirement.strip():
        if char.isalnum() or char in {"-", "_", "."}:
            name.append(char)
        else:
            break
    return "".join(name).lower().replace("_", "-")


def _resolve_repo_root(path: Path) -> Path:
    base = path.resolve().parent
    for candidate in (base, *base.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    if base.name == "docs":
        return base.parent
    return Path.cwd()


def _normalize_license(value: str) -> str:
    if "Apache-2.0" in value:
        return "Apache-2.0"
    if "BSD-3-Clause" in value:
        return "BSD-3-Clause"
    if value.strip() == "BSD-3":
        return "BSD-3"
    if value.strip() == "MIT":
        return "MIT"
    return value.strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate adaptive backend evaluation surface.")
    parser.add_argument("path", nargs="?", default=str(DEFAULT_SURFACE))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--pyproject", default="pyproject.toml")
    parser.add_argument("--out", help="Optional JSON report path.")
    parser.add_argument("--live-imports", action="store_true", help="Require candidate backend modules to import.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    report = validate_surface(
        Path(args.path),
        registry_path=Path(args.registry),
        pyproject_path=Path(args.pyproject),
        live_imports=args.live_imports,
    )
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "status": report["status"],
                "candidates": report["candidate_count"],
                "scenarios": report["scenario_count"],
                "errors": report["error_count"],
                "warnings": report["warning_count"],
            },
            sort_keys=True,
        )
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
