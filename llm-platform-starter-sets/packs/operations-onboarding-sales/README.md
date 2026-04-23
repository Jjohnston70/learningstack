# operations-onboarding-sales Pack

A domain content pack containing templates, workflows, SOPs, and module source material for business operations, client onboarding, and sales workflows.

This is not a single module. It is a seed library for multiple modules.

---

## What's In This Pack

| Folder | Contents | Platform Role |
|--------|----------|---------------|
| `docs/` | SOPs, workflows, operations map, team quickstart | Retrieval sources, workflow guidance modules |
| `templates/` | Proposal, contract, onboarding, pricing templates | Template references for action modules |
| `manifests/` | Normalized module contracts | Ready to register in module registry |
| `archive/` | Historical versions, alignment docs | Reference only — not active runtime |

---

## Module Candidates Inside This Pack

| Module | Backed By | Priority |
|--------|-----------|----------|
| `proposal-command` | templates/proposals, docs/operations-map | High - clearest workflow |
| `contract-command` | templates/contracts, docs/operations-map | High - defined output |
| `onboarding-command` | templates/onboarding, docs/operations-map | Medium - more complex |
| `pricing-command` | docs/operations-map | Medium - retrieval-first |
| `ops-playbook` | docs/workflows, docs/operations-map, docs/team-quickstart | Low — knowledge-only first |

---

## How to Use This Pack

### Stage 1 — Add as a pack (now)

Keep as-is under `packs/operations-onboarding-sales/`.
Do not copy files into the runtime yet.

### Stage 2 — Extract manifests

Register modules from `manifests/` into your module registry.
Start with `proposal-command`.

### Stage 3 — Map retrieval sources

Point `retrieval_sources.yaml` for each module to the relevant docs in `docs/` and `templates/`.

### Stage 4 — Wrap module adapters

Implement adapters directly in each module using the module-template as your guide.

### Stage 5 — Register in marketplace

Once modules are tested, add to `marketplace/registry.json`.

---

## Asset Classification

### Active (use in runtime)
- `manifests/` — module contracts
- `docs/workflows.md` — retrieval source
- `docs/operations-map.md` — retrieval source
- `templates/proposals/` — proposal-command template reference
- `templates/contracts/` — contract-command template reference
- `templates/onboarding/` — onboarding-command template reference

### Reference only (don't add to runtime)
- `archive/` — historical versions
- `docs/alignment-summaries/` — internal planning docs
- `templates/internal-checklists/` — operational only, not for LLM retrieval
