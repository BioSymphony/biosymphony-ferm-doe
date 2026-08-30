from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from biosymphony_ferm_doe.adaptive_backend_surface import validate_surface  # noqa: E402


class AdaptiveBackendSurfaceTests(unittest.TestCase):
    def test_current_surface_passes_and_names_expected_roles(self) -> None:
        report = validate_surface(ROOT / "docs" / "adaptive-backend-evaluation.json")
        self.assertEqual(report["status"], "PASS", report)
        data = json.loads((ROOT / "docs" / "adaptive-backend-evaluation.json").read_text())
        by_id = {candidate["tool_id"]: candidate for candidate in data["backend_candidates"]}
        self.assertEqual(by_id["bofire"]["default_position"], "default_for_static_constrained_doe_bo")
        self.assertEqual(by_id["baybe"]["default_position"], "evaluate_next")
        self.assertTrue(by_id["tabpfn_v2"]["license_gate"]["required"])
        self.assertIn("scale_bridge", set(data["owned_by_biosymphony"]))
        self.assertIn("response_semantics", set(data["owned_by_biosymphony"]))
        self.assertIn("readiness_verdict", set(data["owned_by_biosymphony"]))
        self.assertIn("cost_realism", set(data["owned_by_biosymphony"]))
        workflow = data["workflow_position"]
        self.assertIn("BoFire plus BioSymphony-owned layers", workflow["summary"])
        route_ids = {route["tool_id"] for route in workflow["alternative_backend_routes"]}
        self.assertTrue({"baybe", "ax", "botorch"}.issubset(route_ids))
        self.assertIn("scale_bridge", set(workflow["retained_biosymphony_layers"]))
        for scenario in data["scenario_matrix"]:
            fixture = ROOT / scenario["fixture_path"]
            self.assertTrue((fixture / "smoke_plan.json").exists(), scenario["scenario_id"])
            self.assertTrue((fixture / "campaign_manifest.json").exists(), scenario["scenario_id"])
            self.assertTrue((fixture / "inputs" / "prior_runs.csv").exists(), scenario["scenario_id"])

    def test_missing_biosymphony_boundary_fails(self) -> None:
        data = json.loads((ROOT / "docs" / "adaptive-backend-evaluation.json").read_text())
        data["owned_by_biosymphony"] = [item for item in data["owned_by_biosymphony"] if item != "scale_bridge"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "surface.json"
            path.write_text(json.dumps(data))
            report = validate_surface(path)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("scale_bridge" in finding["message"] for finding in report["findings"]))

    def test_missing_workflow_alternative_route_fails(self) -> None:
        data = json.loads((ROOT / "docs" / "adaptive-backend-evaluation.json").read_text())
        data["workflow_position"]["alternative_backend_routes"] = [
            route for route in data["workflow_position"]["alternative_backend_routes"] if route["tool_id"] != "baybe"
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "surface.json"
            path.write_text(json.dumps(data))
            report = validate_surface(path)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("baybe" in finding["item_id"] for finding in report["findings"]))

    def test_restricted_backend_requires_explicit_license_gate(self) -> None:
        data = json.loads((ROOT / "docs" / "adaptive-backend-evaluation.json").read_text())
        tabpfn = next(candidate for candidate in data["backend_candidates"] if candidate["tool_id"] == "tabpfn_v2")
        tabpfn.pop("license_gate")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "surface.json"
            path.write_text(json.dumps(data))
            report = validate_surface(path)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("explicit license_gate" in finding["message"] for finding in report["findings"]))

    def test_unknown_scenario_tool_fails(self) -> None:
        data = json.loads((ROOT / "docs" / "adaptive-backend-evaluation.json").read_text())
        data["scenario_matrix"][0]["primary_tool"] = "made_up_optimizer"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "surface.json"
            path.write_text(json.dumps(data))
            report = validate_surface(path)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("made_up_optimizer" in finding["message"] for finding in report["findings"]))

    def test_missing_fixture_path_fails(self) -> None:
        data = json.loads((ROOT / "docs" / "adaptive-backend-evaluation.json").read_text())
        data["scenario_matrix"][0]["fixture_path"] = "examples/adaptive-backend-eval/missing"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "surface.json"
            path.write_text(json.dumps(data))
            report = validate_surface(path)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("smoke_plan.json is missing" in finding["message"] for finding in report["findings"]))


if __name__ == "__main__":
    unittest.main()
