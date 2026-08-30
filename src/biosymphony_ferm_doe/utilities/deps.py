"""Lazy optional dependency reporting for utility backends."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
from typing import Any

from . import SUPPORTED_BACKENDS


BACKEND_MODULES = {
    "numpy": ["numpy"],
    "scipy": ["scipy"],
    "pydoe": ["pyDOE2", "pyDOE", "pydoe"],
    "bofire": ["bofire"],
    "botorch": ["botorch", "torch"],
}


# Map BACKEND_MODULES key to the tool_id used in docs/tool-registry.json.
# This lets us look up status, install extra, and install hint per backend
# without requiring the registry author to know the BACKEND_MODULES key.
BACKEND_TO_REGISTRY_ID = {
    "bofire": "bofire",
    "botorch": "botorch",
    "pydoe": "pydoe3",
    "ax": "ax",
    "baybe": "baybe",
    "entmoot": "entmoot",
    "omlt": "omlt",
    "tabpfn": "tabpfn_v2",
    "plotly": "plotly",
    "salib": "salib",
    "frictionless": "frictionless",
}
EVALUATION_BACKEND_MODULES = {
    "ax": ["ax"],
    "baybe": ["baybe"],
    "entmoot": ["entmoot"],
    "omlt": ["omlt", "pyomo", "highspy", "lightgbm", "onnxmltools"],
    "tabpfn": ["tabpfn", "torch", "botorch", "gpytorch"],
}
OPTIONAL_CAPABILITY_MODULES = {
    "plotly": ["plotly"],
    "salib": ["SALib"],
    "frictionless": ["frictionless"],
}
TOKEN_ENV_VARS = {
    "tabpfn": "TABPFN_TOKEN",
}


_REGISTRY_PATH = Path(__file__).resolve().parents[3] / "docs" / "tool-registry.json"
_PROJECT_NAME = "biosymphony-ferm-doe"


def _load_registry_index() -> dict[str, dict[str, Any]]:
    if not _REGISTRY_PATH.is_file():
        return {}
    try:
        data = json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    tools = data.get("tools", [])
    if not isinstance(tools, list):
        return {}
    return {tool["tool_id"]: tool for tool in tools if isinstance(tool, dict) and "tool_id" in tool}


def _registry_attachment(backend: str, registry_index: dict[str, dict[str, Any]]) -> dict[str, Any]:
    tool_id = BACKEND_TO_REGISTRY_ID.get(backend)
    if not tool_id:
        return {}
    entry = registry_index.get(tool_id)
    if not entry:
        return {}
    extra = entry.get("pyproject_extra") or ""
    attachment: dict[str, Any] = {
        "registry": {
            "tool_id": entry.get("tool_id"),
            "status": entry.get("status"),
            "priority": entry.get("priority"),
            "posture": entry.get("posture"),
            "claim_level": entry.get("claim_level"),
            "license": entry.get("license"),
        }
    }
    if extra:
        attachment["install_extra"] = extra
        attachment["install_hint"] = f"pip install '{_PROJECT_NAME}[{extra}]'"
    return attachment


def dependency_status() -> dict[str, Any]:
    registry_index = _load_registry_index()
    backends = {
        "stdlib": {
            "requested": "stdlib",
            "available": True,
            "modules": [],
            "status": "available",
            "note": "Dependency-free local fallback.",
        }
    }
    for backend, modules in BACKEND_MODULES.items():
        found = [module for module in modules if importlib.util.find_spec(module) is not None]
        available = bool(found) if backend != "botorch" else len(found) == len(modules)
        entry: dict[str, Any] = {
            "requested": backend,
            "available": available,
            "modules": modules,
            "found_modules": found,
            "status": "available" if available else "not_available",
            "note": "Optional adapter can be used." if available else "Optional dependency is not installed; stdlib fallback remains valid.",
        }
        entry.update(_registry_attachment(backend, registry_index))
        backends[backend] = entry
    evaluation_backends = {}
    for backend, modules in EVALUATION_BACKEND_MODULES.items():
        found = [module for module in modules if importlib.util.find_spec(module) is not None]
        available = len(found) == len(modules)
        entry: dict[str, Any] = {
            "requested": backend,
            "available": available,
            "modules": modules,
            "found_modules": found,
            "status": "available" if available else "not_available",
            "note": "Evaluation backend can be smoke-tested." if available else "Evaluation dependency is not installed; offline validation remains valid.",
        }
        entry.update(_registry_attachment(backend, registry_index))
        token_env = TOKEN_ENV_VARS.get(backend)
        if token_env:
            entry["runtime_token_env_var"] = token_env
            entry["runtime_token_required"] = True
            entry["runtime_token_present"] = bool(os.environ.get(token_env))
        evaluation_backends[backend] = entry
    optional_capabilities = {}
    for capability, modules in OPTIONAL_CAPABILITY_MODULES.items():
        found = [module for module in modules if importlib.util.find_spec(module) is not None]
        available = len(found) == len(modules)
        entry = {
            "requested": capability,
            "available": available,
            "modules": modules,
            "found_modules": found,
            "status": "available" if available else "not_available",
            "note": "Optional support capability is available." if available else "Optional support capability is not installed.",
        }
        entry.update(_registry_attachment(capability, registry_index))
        optional_capabilities[capability] = entry
    return {
        "schema_version": 1,
        "dependency_status_kind": "ferm_doe_utility_dependencies",
        "supported_backends": SUPPORTED_BACKENDS,
        "backends": backends,
        "evaluation_backends": evaluation_backends,
        "optional_capabilities": optional_capabilities,
    }


def resolve_backend(requested: str | None = None) -> dict[str, Any]:
    requested = (requested or "auto").lower()
    status = dependency_status()
    if requested not in SUPPORTED_BACKENDS:
        return {
            "requested": requested,
            "selected": "stdlib",
            "status": "not_available",
            "fallback": "stdlib",
            "caveat": f"Unsupported backend {requested}; using stdlib fallback.",
            "dependency_status": status,
        }
    if requested == "stdlib":
        return _selected("stdlib", requested, status, "available", "")
    if requested == "auto":
        for backend in ["scipy", "numpy", "pydoe", "bofire", "botorch"]:
            if status["backends"].get(backend, {}).get("available"):
                return _selected(backend, requested, status, "adapter_backed", "")
        return _selected("stdlib", requested, status, "available", "No optional DOE adapters installed; using stdlib fallback.")
    if status["backends"].get(requested, {}).get("available"):
        return _selected(requested, requested, status, "adapter_backed", "")
    return _selected("stdlib", requested, status, "not_available", f"{requested} is not installed; using stdlib fallback.")


def _selected(selected: str, requested: str, status: dict[str, Any], state: str, caveat: str) -> dict[str, Any]:
    return {
        "requested": requested,
        "selected": selected,
        "status": state,
        "fallback": "stdlib" if selected == "stdlib" and requested != "stdlib" else "",
        "caveat": caveat,
        "dependency_status": status,
    }
