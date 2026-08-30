from __future__ import annotations

import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from biosymphony_ferm_doe.cli import main as cli_main  # noqa: E402
from biosymphony_ferm_doe.tool_registry import render_tool_registry_markdown, validate_tool_registry  # noqa: E402
from biosymphony_ferm_doe.utilities.deps import dependency_status  # noqa: E402


class ToolRegistryTests(unittest.TestCase):
    def test_current_registry_passes_and_contains_key_decisions(self) -> None:
        report = validate_tool_registry(ROOT / "docs" / "tool-registry.json", today=date(2026, 5, 15))
        self.assertEqual(report["status"], "PASS", report)
        data = json.loads((ROOT / "docs" / "tool-registry.json").read_text())
        by_id = {tool["tool_id"]: tool for tool in data["tools"]}
        self.assertEqual(by_id["bofire"]["status"], "adopted_optional")
        self.assertEqual(by_id["dwsim"]["status"], "boundary_only")
        self.assertEqual(by_id["scikit_optimize"]["status"], "avoid")
        self.assertEqual(by_id["pydoe3"]["status"], "compatibility_only")
        self.assertIn("bofire_route", {rule["rule_id"] for rule in data["decision_rules"]})
        self.assertTrue(report["pyproject_alignment"]["checked"])
        self.assertGreater(report["pyproject_alignment"]["packages_checked"], 0)
        self.assertEqual(
            report["pyproject_alignment"]["covered_extras"],
            report["pyproject_alignment"]["extras"],
        )
        self.assertEqual(report["public_path_check"]["mirror_count"], 3)
        self.assertGreater(report["public_path_check"]["source_count"], 0)
        self.assertIn("adaptive_smoke", report["action_lane_check"]["nox_sessions"])

    def test_copyleft_adoption_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tool-registry.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "registry_kind": "biosymphony_ferm_doe_tool_registry",
                        "refresh_policy": {"default_refresh_days": 90},
                        "tools": [
                            {
                                "tool_id": "bad",
                                "name": "Bad GPL Tool",
                                "category": "example",
                                "priority": "P1",
                                "status": "adopted_optional",
                                "posture": "bad",
                                "license": "GPL-3.0",
                                "links": {"repo": "https://example.com/bad"},
                                "last_checked": "2026-05-15",
                                "current_signal": "test",
                                "fit": "test",
                                "risks": "test",
                                "route": ["test"],
                                "claim_level": "test",
                                "fail_closed_behavior": "test",
                            }
                        ],
                    }
                )
            )
            report = validate_tool_registry(path, today=date(2026, 5, 15))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("copyleft" in finding["message"] for finding in report["findings"]))

    def test_stale_checks_are_warnings_by_default_and_errors_when_requested(self) -> None:
        report = validate_tool_registry(ROOT / "docs" / "tool-registry.json", today=date(2027, 1, 1))
        strict = validate_tool_registry(ROOT / "docs" / "tool-registry.json", today=date(2027, 1, 1), fail_on_stale=True)
        self.assertEqual(report["status"], "PASS")
        self.assertGreater(report["warning_count"], 0)
        self.assertEqual(strict["status"], "FAIL")

    def test_pyproject_alignment_blocks_missing_adopted_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry_path = root / "tool-registry.json"
            pyproject_path = root / "pyproject.toml"
            registry_path.write_text(json.dumps(_minimal_registry([_tool("bofire", package="bofire>=0.3.1", pyproject_extra="adaptive")])))
            pyproject_path.write_text(
                "\n".join(
                    [
                        "[project]",
                        'name = "demo"',
                        "[project.optional-dependencies]",
                        "adaptive = [",
                        '  "torch>=2.12.0"',
                        "]",
                    ]
                )
            )
            report = validate_tool_registry(registry_path, today=date(2026, 5, 15), pyproject_path=pyproject_path)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("not listed in pyproject extra adaptive" in finding["message"] for finding in report["findings"]))

    def test_declared_nox_lanes_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry_path = root / "tool-registry.json"
            noxfile = root / "noxfile.py"
            registry_path.write_text(json.dumps(_minimal_registry([_tool("bofire", local_lane="nox -s missing_lane")])))
            noxfile.write_text("import nox\n\n@nox.session\ndef adaptive_smoke(session):\n    pass\n")
            report = validate_tool_registry(registry_path, today=date(2026, 5, 15), repo_root=root, noxfile_path=noxfile)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("missing nox session" in finding["message"] for finding in report["findings"]))

    def test_pyproject_alignment_blocks_unregistered_extra_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry_path = root / "tool-registry.json"
            pyproject_path = root / "pyproject.toml"
            registry_path.write_text(json.dumps(_minimal_registry([_tool("bofire", package="bofire>=0.3.1", pyproject_extra="bofire")])))
            pyproject_path.write_text(
                "\n".join(
                    [
                        "[project]",
                        'name = "demo"',
                        "[project.optional-dependencies]",
                        'bofire = ["bofire>=0.3.1"]',
                        'report = ["plotly>=6.0"]',
                    ]
                )
            )
            report = validate_tool_registry(registry_path, today=date(2026, 5, 15), pyproject_path=pyproject_path)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("no matching registry package: report" in finding["message"] for finding in report["findings"]))

    def test_non_public_source_path_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tool-registry.json"
            registry = _minimal_registry([_tool("bofire")])
            registry["source_notes"] = [".runtime/research/notes.md"]
            path.write_text(json.dumps(registry))
            report = validate_tool_registry(path, today=date(2026, 5, 15))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("public repository surface" in finding["message"] for finding in report["findings"]))

    def test_bofire_route_reasons_must_match_adapter_constants(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "tool-registry.json"
            registry_path.write_text(json.dumps(_minimal_registry([_tool("bofire", route_reasons=["non_box_constraints"])])))
            report = validate_tool_registry(registry_path, today=date(2026, 5, 15))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("route reasons drifted" in finding["message"] for finding in report["findings"]))

    def test_markdown_summary_and_cli_entrypoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.json"
            md_out = Path(tmp) / "summary.md"
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = cli_main(["tool-registry", str(ROOT / "docs" / "tool-registry.json"), "--out", str(out), "--md-out", str(md_out)])
            self.assertEqual(code, 0)
            report = json.loads(out.read_text())
            self.assertEqual(report["status"], "PASS")
            self.assertIn("BioSymphony Tool Registry", md_out.read_text())
            self.assertIn('"tools"', stdout.getvalue())
            markdown = render_tool_registry_markdown(report, ROOT / "docs" / "tool-registry.json")
            self.assertIn("bofire", markdown)
            self.assertEqual(markdown.count("- Status:"), 1)
            self.assertIn("| Tool | Priority | Status | Supported | Upstream | Checked |", markdown)

    def test_dependency_status_includes_registry_install_hints(self) -> None:
        status = dependency_status()
        self.assertEqual(status["backends"]["bofire"]["registry"]["status"], "adopted_optional")
        self.assertEqual(status["backends"]["bofire"]["install_extra"], "bofire")
        self.assertIn("[bofire]", status["backends"]["bofire"]["install_hint"])
        self.assertEqual(status["evaluation_backends"]["omlt"]["install_extra"], "omlt")
        self.assertEqual(status["evaluation_backends"]["tabpfn"]["install_extra"], "tabpfn")
        self.assertEqual(status["evaluation_backends"]["tabpfn"]["runtime_token_env_var"], "TABPFN_TOKEN")
        self.assertEqual(status["optional_capabilities"]["plotly"]["install_extra"], "report")
        self.assertEqual(status["optional_capabilities"]["salib"]["install_extra"], "sensitivity")
        self.assertEqual(status["optional_capabilities"]["frictionless"]["install_extra"], "contracts")

    def test_doctor_cli_reports_repo_capabilities(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "doctor.json"
            code = cli_main(["doctor", "--root", str(ROOT), "--out", str(out)])
            self.assertEqual(code, 0)
            report = json.loads(out.read_text())
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["tool_registry"]["status"], "PASS")
            self.assertIn("dependency_status", report)


def _minimal_registry(tools: list[dict[str, object]]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "registry_kind": "biosymphony_ferm_doe_tool_registry",
        "refresh_policy": {"default_refresh_days": 90},
        "tools": tools,
    }


def _tool(
    tool_id: str,
    *,
    package: str = "",
    pyproject_extra: str = "",
    local_lane: str = "",
    route: list[str] | None = None,
    route_reasons: list[str] | None = None,
) -> dict[str, object]:
    tool: dict[str, object] = {
        "tool_id": tool_id,
        "name": tool_id,
        "category": "example",
        "priority": "P0",
        "status": "adopted_optional",
        "posture": "test",
        "license": "MIT",
        "links": {"repo": "https://example.com/tool"},
        "last_checked": "2026-05-15",
        "current_signal": "test",
        "fit": "test",
        "risks": "test",
        "route": route if route is not None else ["non_box_constraints", "multi_objective_responses", "scale_fidelity_structure", "operator_requested_bofire"],
        "claim_level": "bofire_adapter_planning" if tool_id == "bofire" else "test",
        "fail_closed_behavior": "test",
    }
    if tool_id == "bofire":
        tool["route_reasons"] = route_reasons if route_reasons is not None else [
            "non_box_constraints",
            "multi_objective_responses",
            "scale_fidelity_structure",
            "operator_requested_bofire",
        ]
    if package:
        tool["package"] = package
    if pyproject_extra:
        tool["pyproject_extra"] = pyproject_extra
    if local_lane:
        tool["local_lane"] = local_lane
    return tool


if __name__ == "__main__":
    unittest.main()
