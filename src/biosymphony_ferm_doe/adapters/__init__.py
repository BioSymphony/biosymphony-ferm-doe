"""Optional adapter layer for biosymphony-ferm-doe.

The core skill is stdlib-only at runtime — that is the moat. Adapters are
opt-in dependencies that *upgrade* claim levels or replace heuristic
approximations with exact / canonical implementations from established
libraries:

- ``scipy_pvalues``: real Student-t and F distributions in place of the
  normal approximation used in ``analysis`` and ``doe_power``. Tightens
  small-sample p-values and MDE estimates.
- ``nist_citations``: NIST/SEMATECH e-Handbook references for each DoE
  family. Adds citations to ``recommend_family`` decision paths. No
  external dependency — pure data.
- ``pydoe3_designs``: extended Box-Behnken coverage and maximin Latin
  hypercube designs via pyDOE3.
- ``botorch_wave2``: Bayesian optimization for follow-up candidate selection
  via BoTorch + GPyTorch. Replaces geometric narrowing with GP-surrogate
  + acquisition-function-driven next-points. Upgrades follow-up claim level
  to ``bayesian_optimization_planned``.
- ``bofire_strategy``: routed BoFire powerup for constrained DoE,
  multi-objective BO, and scale/fidelity sequential planning. The module is
  importable without BoFire installed so the engine can record route
  decisions and fall back cleanly.
- ``salib``: global sensitivity analysis (PAWN, delta, Sobol) for
  post-hoc analysis of sequential responses. PAWN and delta are model-free
  and run on any (X, Y) pair; Sobol requires a Saltelli sample.
- ``entmoot``: tree-ensemble Bayesian optimization with MIP-encoded
  NChooseK / linear constraints via ENTMOOT v2 + Pyomo + HiGHS. It is
  the conservative route for campaigns affected by the NChooseK behavior
  found in this repository's BoFire 0.3.1 audit. The module is importable
  without ENTMOOT so the engine can still record routing decisions.
- ``omlt``: MIP-optimized surrogate planning through OMLT + Pyomo. The
  module is importable without OMLT installed and degrades to an explicit
  ``not_available`` or ``solver_unavailable`` report.
- ``tabpfn``: foundation-model surrogate route for low-data sequential
  planning. This repository's noninteractive adapter is inert unless the
  package is installed and the operator supplies a runtime ``TABPFN_TOKEN``.

Each adapter checks importability at first call. CLI subcommands accept
``--backend`` flags that route to adapters when available and fall back
to the stdlib path with a clear note when not.

Use :func:`get_adapter` to fetch an adapter module or ``None``. Use
:func:`is_available` for a boolean check.
"""

from __future__ import annotations

from typing import Any

ADAPTERS = ("scipy", "nist", "pydoe3", "botorch", "bofire", "salib", "entmoot", "omlt", "tabpfn")


def get_adapter(name: str) -> Any | None:
    """Return an adapter module or ``None`` when its dependencies are missing."""
    if name == "scipy":
        try:
            from . import scipy_pvalues
            return scipy_pvalues
        except ImportError:
            return None
    if name == "nist":
        from . import nist_citations
        return nist_citations
    if name == "pydoe3":
        try:
            from . import pydoe3_designs
            return pydoe3_designs
        except ImportError:
            return None
    if name == "botorch":
        try:
            from . import botorch_wave2
            return botorch_wave2
        except ImportError:
            return None
    if name == "bofire":
        try:
            from . import bofire_strategy
        except ImportError:
            return None
        return bofire_strategy if bofire_strategy.is_available() else None
    if name == "salib":
        try:
            from . import salib_sensitivity
            return salib_sensitivity
        except ImportError:
            return None
    if name == "entmoot":
        try:
            from . import entmoot_strategy
        except ImportError:
            return None
        return entmoot_strategy if entmoot_strategy.is_available() else None
    if name == "omlt":
        try:
            from . import omlt_strategy
        except ImportError:
            return None
        return omlt_strategy if omlt_strategy.is_available() else None
    if name == "tabpfn":
        try:
            from . import tabpfn_strategy
        except ImportError:
            return None
        return tabpfn_strategy if tabpfn_strategy.is_available() else None
    return None


def is_available(name: str) -> bool:
    return get_adapter(name) is not None


__all__ = ["get_adapter", "is_available", "ADAPTERS"]
