"""Validate the curated BioSymphony external-tool registry."""

from __future__ import annotations

import argparse
import ast
import json
import re
import shlex
import sys
from dataclasses import asdict, dataclass

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


DEFAULT_REGISTRY = Path("docs/tool-registry.json")
ACTIVE_STATUSES = {"adopted_optional", "evaluate_next"}
PACKAGE_ALIGNMENT_STATUSES = ACTIVE_STATUSES | {"compatibility_only"}
VALID_PRIORITIES = {"P0", "P1", "P2", "P3", "Watch", "Avoid"}
VALID_STATUSES = {
    "adopted_optional",
    "evaluate_next",
    "watch",
    "boundary_only",
    "compatibility_only",
    "avoid",
}
REQUIRED_TOOL_FIELDS = {
    "tool_id",
    "name",
    "category",
    "priority",
    "status",
    "posture",
    "license",
    "links",
    "last_checked",
    "current_signal",
    "fit",
    "risks",
    "route",
    "claim_level",
    "fail_closed_behavior",
}
COPYLEFT_MARKERS = ("GPL", "AGPL")
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "Watch": 4, "Avoid": 5}


@dataclass(frozen=True)
class RegistryFinding:
    severity: str
    tool_id: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_tool_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    """Load the registry JSON document."""

    data = json.loads(Path(path).read_text())
    if not isinstance(data, dict):
        raise ValueError(f"expected tool registry object: {path}")
    return data


def load_tool_registry_index(path: Path = DEFAULT_REGISTRY) -> dict[str, dict[str, Any]]:
    """Return registry entries keyed by tool_id.

    Missing registry files intentionally return an empty index so installed
    packages can still report dependency status outside a repo checkout.
    """

    registry_path = Path(path)
    if not registry_path.exists():
        return {}
    data = load_tool_registry(registry_path)
    return {str(tool.get("tool_id")): tool for tool in data.get("tools", []) if isinstance(tool, dict) and tool.get("tool_id")}


def validate_tool_registry(
    path: Path,
    *,
    today: date | None = None,
    fail_on_stale: bool = False,
    pyproject_path: Path | None = None,
    noxfile_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    checked_on = today or date.today()
    registry_path = Path(path)
    data = load_tool_registry(registry_path)
    findings: list[RegistryFinding] = []

    if data.get("schema_version") != 1:
        findings.append(RegistryFinding("error", "_registry", "schema_version must be 1"))
    if data.get("registry_kind") != "biosymphony_ferm_doe_tool_registry":
        findings.append(RegistryFinding("error", "_registry", "registry_kind is invalid"))

    tools = data.get("tools")
    if not isinstance(tools, list) or not tools:
        findings.append(RegistryFinding("error", "_registry", "tools must be a non-empty list"))
        tools = []

    ids: set[str] = set()
    valid_tools: list[dict[str, Any]] = []
    default_refresh_days = int(data.get("refresh_policy", {}).get("default_refresh_days", 90))
    for raw in tools:
        if not isinstance(raw, dict):
            findings.append(RegistryFinding("error", "_registry", "tool entry must be an object"))
            continue
        tool_id = str(raw.get("tool_id") or "")
        if not tool_id:
            findings.append(RegistryFinding("error", "_registry", "tool_id is required"))
            continue
        if tool_id in ids:
            findings.append(RegistryFinding("error", tool_id, "duplicate tool_id"))
        ids.add(tool_id)
        valid_tools.append(raw)
        findings.extend(validate_tool(raw, today=checked_on, default_refresh_days=default_refresh_days, fail_on_stale=fail_on_stale))

    root = _resolve_repo_root(registry_path, repo_root)
    alignment = validate_pyproject_alignment(
        valid_tools,
        Path(pyproject_path) if pyproject_path else root / "pyproject.toml",
        required=pyproject_path is not None,
    )
    lane_check = validate_action_lanes(
        valid_tools,
        root=root,
        noxfile_path=Path(noxfile_path) if noxfile_path else root / "noxfile.py",
        required=noxfile_path is not None,
    )
    route_check = validate_route_alignment(valid_tools)
    public_path_check = validate_public_paths(data, valid_tools, root=root, registry_path=registry_path)
    findings.extend(alignment.pop("findings"))
    findings.extend(lane_check.pop("findings"))
    findings.extend(route_check.pop("findings"))
    findings.extend(public_path_check.pop("findings"))

    errors = [finding for finding in findings if finding.severity == "error"]
    warnings = [finding for finding in findings if finding.severity == "warning"]
    summary = summarize_tools(valid_tools)
    return {
        "schema_version": 1,
        "registry_check_kind": "biosymphony_tool_registry_check",
        "path": str(registry_path),
        "repo_root": str(root),
        "checked_on": checked_on.isoformat(),
        "status": "FAIL" if errors else "PASS",
        "tool_count": len(ids),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "summary": summary,
        "pyproject_alignment": alignment,
        "action_lane_check": lane_check,
        "route_rule_check": route_check,
        "public_path_check": public_path_check,
        "findings": [finding.to_dict() for finding in findings],
    }


def validate_tool(
    tool: dict[str, Any],
    *,
    today: date,
    default_refresh_days: int,
    fail_on_stale: bool,
) -> list[RegistryFinding]:
    tool_id = str(tool.get("tool_id") or "_unknown")
    findings: list[RegistryFinding] = []

    missing = sorted(REQUIRED_TOOL_FIELDS - set(tool))
    for field in missing:
        findings.append(RegistryFinding("error", tool_id, f"missing required field: {field}"))

    if tool.get("priority") not in VALID_PRIORITIES:
        findings.append(RegistryFinding("error", tool_id, f"priority must be one of {sorted(VALID_PRIORITIES)}"))
    if tool.get("status") not in VALID_STATUSES:
        findings.append(RegistryFinding("error", tool_id, f"status must be one of {sorted(VALID_STATUSES)}"))
    if not isinstance(tool.get("links"), dict) or not tool.get("links"):
        findings.append(RegistryFinding("error", tool_id, "links must be a non-empty object"))
    elif not all(str(value).startswith("https://") for value in tool["links"].values() if value):
        findings.append(RegistryFinding("error", tool_id, "all non-empty links must be https URLs"))
    if not isinstance(tool.get("route"), list):
        findings.append(RegistryFinding("error", tool_id, "route must be a list"))

    checked = parse_date(tool.get("last_checked"))
    if checked is None:
        findings.append(RegistryFinding("error", tool_id, "last_checked must be YYYY-MM-DD"))
    else:
        if checked > today + timedelta(days=1):
            findings.append(RegistryFinding("warning", tool_id, f"last_checked is in the future: {checked.isoformat()}"))
        stale_after = checked + timedelta(days=default_refresh_days)
        if stale_after < today:
            severity = "error" if fail_on_stale else "warning"
            findings.append(RegistryFinding(severity, tool_id, f"tool check is stale; refresh after {stale_after.isoformat()}"))

    license_text = str(tool.get("license") or "").upper()
    status = str(tool.get("status") or "")
    if any(marker in license_text for marker in COPYLEFT_MARKERS) and status in ACTIVE_STATUSES:
        findings.append(RegistryFinding("error", tool_id, "copyleft tool cannot be adopted/evaluate_next without an explicit boundary status"))
    if status in ACTIVE_STATUSES and not str(tool.get("fail_closed_behavior") or "").strip():
        findings.append(RegistryFinding("error", tool_id, "active/evaluate tools must define fail_closed_behavior"))
    return findings


def validate_pyproject_alignment(tools: list[dict[str, Any]], pyproject_path: Path, *, required: bool = False) -> dict[str, Any]:
    findings: list[RegistryFinding] = []
    result: dict[str, Any] = {
        "checked": False,
        "path": str(pyproject_path),
        "extras": [],
        "covered_extras": [],
        "packages_checked": 0,
        "findings": findings,
    }
    if not pyproject_path.exists():
        if required:
            findings.append(RegistryFinding("error", "_registry", f"pyproject.toml not found: {pyproject_path}"))
        return result

    try:
        pyproject = tomllib.loads(pyproject_path.read_text())
    except tomllib.TOMLDecodeError as exc:
        findings.append(RegistryFinding("error", "_registry", f"pyproject.toml could not be parsed: {exc}"))
        return result

    optional = pyproject.get("project", {}).get("optional-dependencies", {})
    if not isinstance(optional, dict):
        findings.append(RegistryFinding("error", "_registry", "pyproject.toml missing [project.optional-dependencies]"))
        return result

    result["checked"] = True
    result["extras"] = sorted(str(extra) for extra in optional)
    extra_packages = {
        str(extra): {_requirement_name(str(requirement)) for requirement in requirements if _requirement_name(str(requirement))}
        for extra, requirements in optional.items()
        if isinstance(requirements, list)
    }

    registry_packages: set[str] = set()
    for tool in tools:
        tool_id = str(tool.get("tool_id") or "_unknown")
        status = str(tool.get("status") or "")
        package = str(tool.get("package") or "").strip()
        extra = str(tool.get("pyproject_extra") or "").strip()
        if status not in PACKAGE_ALIGNMENT_STATUSES:
            continue
        package_name = _requirement_name(package)
        if package_name:
            registry_packages.add(package_name)
        if package and not extra:
            findings.append(RegistryFinding("error", tool_id, "active tool declares package but no pyproject_extra"))
            continue
        if not package or not extra:
            continue
        result["packages_checked"] += 1
        if extra not in extra_packages:
            findings.append(RegistryFinding("error", tool_id, f"pyproject extra is missing: {extra}"))
        elif package_name not in extra_packages[extra]:
            findings.append(RegistryFinding("error", tool_id, f"package {package_name} is not listed in pyproject extra {extra}"))

    covered_extras = sorted(extra for extra, packages in extra_packages.items() if packages & registry_packages)
    result["covered_extras"] = covered_extras
    for extra in sorted(set(extra_packages) - set(covered_extras)):
        findings.append(RegistryFinding("error", "_registry", f"pyproject extra has no matching registry package: {extra}"))
    return result


def validate_action_lanes(tools: list[dict[str, Any]], *, root: Path, noxfile_path: Path, required: bool = False) -> dict[str, Any]:
    findings: list[RegistryFinding] = []
    result: dict[str, Any] = {
        "checked": False,
        "noxfile": str(noxfile_path),
        "nox_sessions": [],
        "lane_count": 0,
        "runpod_lane_count": 0,
        "findings": findings,
    }
    lane_fields = ("local_lane", "live_lane")
    has_declared_lanes = any(str(tool.get(field) or "").strip() for tool in tools for field in lane_fields)
    nox_sessions: set[str] = set()
    if noxfile_path.exists():
        result["checked"] = True
        nox_sessions = _nox_sessions(noxfile_path)
        result["nox_sessions"] = sorted(nox_sessions)
    elif required or has_declared_lanes:
        findings.append(RegistryFinding("error", "_registry", f"noxfile not found for declared lanes: {noxfile_path}"))

    for tool in tools:
        if str(tool.get("status") or "") not in ACTIVE_STATUSES:
            continue
        tool_id = str(tool.get("tool_id") or "_unknown")
        for field in lane_fields:
            lane = str(tool.get(field) or "").strip()
            if not lane:
                continue
            result["lane_count"] += 1
            session_name = _nox_lane_session(lane)
            if lane.startswith("nox") and not session_name:
                findings.append(RegistryFinding("error", tool_id, f"{field} does not name a nox session: {lane}"))
            elif session_name and noxfile_path.exists() and session_name not in nox_sessions:
                findings.append(RegistryFinding("error", tool_id, f"{field} references missing nox session: {session_name}"))
        runpod_lane = str(tool.get("runpod_lane") or "").strip()
        if runpod_lane:
            result["runpod_lane_count"] += 1
            runpod_path = Path(runpod_lane)
            if not runpod_path.is_absolute():
                runpod_path = root / runpod_path
            if not runpod_path.exists():
                findings.append(RegistryFinding("error", tool_id, f"runpod_lane path does not exist: {runpod_lane}"))
    return result


def validate_route_alignment(tools: list[dict[str, Any]]) -> dict[str, Any]:
    from .adapters.bofire_strategy import BOFIRE_ROUTE_REASONS, CLAIM_LEVEL as BOFIRE_CLAIM_LEVEL
    from .adapters.entmoot_strategy import ENTMOOT_ROUTE_REASONS, CLAIM_LEVEL as ENTMOOT_CLAIM_LEVEL
    from .adapters.omlt_strategy import OMLT_ROUTE_REASONS, CLAIM_LEVEL as OMLT_CLAIM_LEVEL
    from .adapters.tabpfn_strategy import TABPFN_ROUTE_REASONS, CLAIM_LEVEL as TABPFN_CLAIM_LEVEL

    findings: list[RegistryFinding] = []
    expected_by_tool = {
        "bofire": (BOFIRE_CLAIM_LEVEL, BOFIRE_ROUTE_REASONS),
        "entmoot": (ENTMOOT_CLAIM_LEVEL, ENTMOOT_ROUTE_REASONS),
        "omlt": (OMLT_CLAIM_LEVEL, OMLT_ROUTE_REASONS),
        "tabpfn_v2": (TABPFN_CLAIM_LEVEL, TABPFN_ROUTE_REASONS),
    }
    result: dict[str, Any] = {
        "checked": True,
        "expected": {
            tool_id: {"claim_level": claim_level, "route_reasons": list(route_reasons)}
            for tool_id, (claim_level, route_reasons) in expected_by_tool.items()
        },
        "findings": findings,
    }
    for tool in tools:
        tool_id = str(tool.get("tool_id") or "")
        if tool_id not in expected_by_tool:
            continue
        expected_claim, expected_reasons = expected_by_tool[tool_id]
        actual_claim = str(tool.get("runtime_claim_level") or tool.get("claim_level") or "")
        if actual_claim != expected_claim:
            findings.append(
                RegistryFinding(
                    "error",
                    tool_id,
                    f"runtime claim level drifted from adapter constant: expected {expected_claim}, got {actual_claim}",
                )
            )
        expected = set(expected_reasons)
        actual = set(str(item) for item in tool.get("route_reasons", []) if item)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            details = []
            if missing:
                details.append(f"missing {missing}")
            if extra:
                details.append(f"extra {extra}")
            findings.append(RegistryFinding("error", tool_id, "route reasons drifted from adapter constants: " + "; ".join(details)))
    return result


def validate_public_paths(
    data: dict[str, Any],
    tools: list[dict[str, Any]],
    *,
    root: Path,
    registry_path: Path,
) -> dict[str, Any]:
    findings: list[RegistryFinding] = []
    result: dict[str, Any] = {
        "checked": True,
        "source_count": 0,
        "tool_doc_count": 0,
        "mirror_count": 0,
        "findings": findings,
    }

    source_notes = data.get("source_notes", [])
    if not isinstance(source_notes, list):
        findings.append(RegistryFinding("error", "_registry", "source_notes must be a list"))
        source_notes = []
    for source in source_notes:
        source_path = _portable_public_path(source, "source_notes", findings)
        if source_path is None:
            continue
        result["source_count"] += 1
        if not (root / source_path).is_file():
            findings.append(RegistryFinding("error", "_registry", f"source_notes path does not exist: {source_path.as_posix()}"))

    for tool in tools:
        tool_id = str(tool.get("tool_id") or "_unknown")
        docs = tool.get("docs_in_repo", [])
        if not isinstance(docs, list):
            findings.append(RegistryFinding("error", tool_id, "docs_in_repo must be a list"))
            continue
        for doc in docs:
            doc_path = _portable_public_path(doc, "docs_in_repo", findings, tool_id=tool_id)
            if doc_path is None:
                continue
            result["tool_doc_count"] += 1
            if not (root / doc_path).is_file():
                findings.append(RegistryFinding("error", tool_id, f"docs_in_repo path does not exist: {doc_path.as_posix()}"))

    expected_registry = root / "docs" / "tool-registry.json"
    skill_docs = root / "skills" / "biosymphony-ferm-doe" / "references" / "docs"
    if registry_path.resolve() == expected_registry.resolve() and skill_docs.is_dir():
        mirror_pairs = (
            (expected_registry, skill_docs / "tool-registry.json"),
            (root / "docs" / "TOOL_REGISTRY.md", skill_docs / "TOOL_REGISTRY.md"),
            (root / "docs" / "ADAPTER_MAP.md", skill_docs / "ADAPTER_MAP.md"),
        )
        for public_path, skill_path in mirror_pairs:
            result["mirror_count"] += 1
            if not public_path.is_file() or not skill_path.is_file():
                findings.append(RegistryFinding("error", "_registry", f"public mirror pair is incomplete: {public_path.relative_to(root)}"))
            elif public_path.read_bytes() != skill_path.read_bytes():
                findings.append(RegistryFinding("error", "_registry", f"public mirror is out of sync: {public_path.relative_to(root)}"))
    return result


def _portable_public_path(
    value: Any,
    field: str,
    findings: list[RegistryFinding],
    *,
    tool_id: str = "_registry",
) -> Path | None:
    text = str(value or "").strip()
    if not text:
        findings.append(RegistryFinding("error", tool_id, f"{field} contains an empty path"))
        return None
    path = Path(text)
    if path.is_absolute() or ".." in path.parts:
        findings.append(RegistryFinding("error", tool_id, f"{field} path must be repository-relative: {text}"))
        return None
    if path.parts and path.parts[0] in {".runtime", "logs"}:
        findings.append(RegistryFinding("error", tool_id, f"{field} path must point to a public repository surface: {text}"))
        return None
    return path


def summarize_tools(tools: list[dict[str, Any]]) -> dict[str, Any]:
    by_status: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    for tool in tools:
        status = str(tool.get("status") or "unknown")
        priority = str(tool.get("priority") or "unknown")
        by_status[status] = by_status.get(status, 0) + 1
        by_priority[priority] = by_priority.get(priority, 0) + 1
    return {"by_status": by_status, "by_priority": by_priority}


def render_tool_registry_markdown(report: dict[str, Any], registry_path: Path | None = None) -> str:
    path = registry_path or Path(str(report.get("path") or DEFAULT_REGISTRY))
    data = load_tool_registry(path)
    tools = sorted(
        [tool for tool in data.get("tools", []) if isinstance(tool, dict)],
        key=lambda tool: (PRIORITY_ORDER.get(str(tool.get("priority")), 99), str(tool.get("tool_id") or "")),
    )
    alignment = report.get("pyproject_alignment", {})
    lanes = report.get("action_lane_check", {})
    lines = [
        "# BioSymphony Tool Registry",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Tools: `{report.get('tool_count')}`",
        f"- Findings: `{report.get('error_count')} errors`, `{report.get('warning_count')} warnings`",
        f"- Checked on: `{report.get('checked_on')}`",
    ]
    if alignment.get("checked"):
        lines.append(f"- Pyproject alignment: `{alignment.get('packages_checked')}` packages across `{len(alignment.get('extras', []))}` extras")
    if lanes.get("checked"):
        lines.append(f"- Action lanes: `{lanes.get('lane_count')}` nox lanes, `{lanes.get('runpod_lane_count')}` remote lanes")
    lines.extend(
        [
            "",
            "`Supported` is the repository requirement. `Upstream` is the newest official release observed on the checked date; it is not an adapter-compatibility claim.",
            "",
            "| Tool | Priority | Status | Supported | Upstream | Checked | Extra | Claim | Route |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for tool in tools:
        route = ", ".join(str(item) for item in tool.get("route", [])[:3])
        if len(tool.get("route", [])) > 3:
            route += ", ..."
        lines.append(
            "| "
            + " | ".join(
                [
                    str(tool.get("tool_id") or ""),
                    str(tool.get("priority") or ""),
                    str(tool.get("status") or ""),
                    str(tool.get("package") or ""),
                    str(tool.get("upstream_version") or ""),
                    str(tool.get("last_checked") or ""),
                    str(tool.get("pyproject_extra") or ""),
                    str(tool.get("runtime_claim_level") or tool.get("claim_level") or ""),
                    route,
                ]
            )
            + " |"
        )
    findings = report.get("findings", [])
    if findings:
        lines.extend(["", "## Findings", "", "| Severity | Tool | Message |", "| --- | --- | --- |"])
        for finding in findings:
            lines.append(f"| {finding.get('severity')} | {finding.get('tool_id')} | {finding.get('message')} |")
    return "\n".join(lines) + "\n"


def parse_date(value: Any) -> date | None:
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate docs/tool-registry.json.")
    parser.add_argument("path", nargs="?", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--out", help="Optional JSON report path.")
    parser.add_argument("--md-out", help="Optional Markdown summary path.")
    parser.add_argument("--pyproject", help="Optional pyproject.toml path to enforce against.")
    parser.add_argument("--noxfile", help="Optional noxfile.py path to enforce declared lanes against.")
    parser.add_argument("--repo-root", help="Optional repository root for relative lane paths.")
    parser.add_argument("--fail-on-stale", action="store_true", help="Treat stale last_checked values as errors.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    report = validate_tool_registry(
        Path(args.path),
        fail_on_stale=args.fail_on_stale,
        pyproject_path=Path(args.pyproject) if args.pyproject else None,
        noxfile_path=Path(args.noxfile) if args.noxfile else None,
        repo_root=Path(args.repo_root) if args.repo_root else None,
    )
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    if args.md_out:
        md_out = Path(args.md_out)
        md_out.parent.mkdir(parents=True, exist_ok=True)
        md_out.write_text(render_tool_registry_markdown(report, Path(args.path)))
    print(json.dumps({"status": report["status"], "tools": report["tool_count"], "errors": report["error_count"], "warnings": report["warning_count"]}, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


def _resolve_repo_root(path: Path, explicit_root: Path | None) -> Path:
    if explicit_root:
        return explicit_root.resolve()
    base = path.resolve().parent
    for candidate in (base, *base.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    if base.name == "docs":
        return base.parent
    return base


def _requirement_name(requirement: str) -> str:
    match = re.match(r"\s*([A-Za-z0-9_.-]+)", requirement)
    if not match:
        return ""
    return match.group(1).lower().replace("_", "-")


def _nox_sessions(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError:
        return set()
    sessions: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            target = decorator.func if isinstance(decorator, ast.Call) else decorator
            if isinstance(target, ast.Attribute) and target.attr == "session":
                sessions.add(node.name)
    return sessions


def _nox_lane_session(lane: str) -> str:
    try:
        parts = shlex.split(lane)
    except ValueError:
        return ""
    if not parts or Path(parts[0]).name != "nox":
        return ""
    for index, part in enumerate(parts):
        if part in {"-s", "--session", "--sessions"} and index + 1 < len(parts):
            return parts[index + 1]
        if part.startswith("-s") and len(part) > 2:
            return part[2:]
        if part.startswith("--session="):
            return part.split("=", 1)[1]
        if part.startswith("--sessions="):
            return part.split("=", 1)[1]
    return ""


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
