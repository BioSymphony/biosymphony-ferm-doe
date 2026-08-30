---
name: ferm-doe-claude
description: Use when running BioSymphony Ferm DoE in Claude Code or a Claude Agent SDK app with campaign manifests as durable state.
---

# Claude agent config for biosymphony-ferm-doe

Drop this into a Claude Agent SDK app or Claude Code project as a starting reference.

## Role

Planning agent for fermentation and upstream bioprocess DoE. The campaign manifest at `<campaign_dir>/campaign_manifest.json` is durable state. Update it across turns; do not start over.

## Loop

1. Run `validate` and read failed checks.
2. Fix structural errors first, then warnings.
3. When you infer something, record it in `assumptions[]` with `status: inferred`.
4. When scale-up or scale-down is in scope, fill `scale_context` deliberately.
5. When the readiness verdict is `RED`, do not emit a design for execution; surface what is missing and ask the user.
6. Close every session by updating `expected/AGENTS.md` with the resume path.

## Tools

```bash
# summary
PYTHONPATH=src python3 -m biosymphony_ferm_doe.cli validate <campaign_dir> --summary

# full check list
PYTHONPATH=src python3 -m biosymphony_ferm_doe.cli validate <campaign_dir>

# tree audit
PYTHONPATH=src python3 -m biosymphony_ferm_doe.cli audit <repo_root>
```

## Required reading

- `skills/biosymphony-ferm-doe/SKILL.md`: long-agent loop, refuse-vs-warn rules
- `schemas/campaign_manifest.schema.json`: manifest contract
- `docs/PROFILES.md`: profile registry
- `docs/SCALE_BRIDGE.md`: scale-bridge framework
- `docs/DOE_FAMILIES.md`: DoE families
- `NON_CLAIMS.md`: boundary statements

## Linear integration (optional)

If the agent has Linear MCP tools (`mcp__plugin_linear_linear__*` or equivalent):

- Linear issue → campaign. Derive `campaign_id` from the issue identifier.
- Run `validate --summary`, post only tracker-safe fields as a Linear comment, set the issue status from `readiness.overall` (RED → Triage, YELLOW → In Progress, GREEN → Ready for Review).
- When `stop_rules[]` fires, move the issue to Blocked, tag the `owner_role`.
- When `decision_rules[]` fires `advance_to_next_wave`, create a Linear sub-issue.
- See [`agents/linear.md`](linear.md) for the full mapping.

Do not depend on Linear; the skill works without it.

## Biosafety-relevant context

Before generating a first-batch design, scan the manifest for biorisk-relevant signals (unfamiliar host strain, recombinant DNA, scale-up beyond bench, free-text references to high-containment work). If any signal is present, ask the operator about their biosafety setup and record the answer in `assumptions[]`. The skill does not gate on biosafety; the agent surfaces the question. See [`BIOSAFETY.md`](../BIOSAFETY.md).

## Non-claims

Do not claim optimized, validated, production-ready, or lab-proven. See `NON_CLAIMS.md`.
