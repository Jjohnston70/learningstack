# CLAUDE.md

## Mission
Publish an operator-grade, modular LLM starter and learning artifacts without exposing client data, secrets, or internal-only context.

## Non-Negotiables
- Never commit secrets, credentials, or `.env` files.
- Keep examples synthetic (`Client Alpha`, placeholder IDs, no real customer names).
- Preserve tenant isolation and redaction-first logging patterns.

## Repo Outcomes
- Clear architecture docs for modular multi-tenant LLM systems.
- Working Python/TypeScript starter scaffolds with tests.
- Content pack examples that are reusable and safe for public OSS.

## Quality Bar Before Merge
- README is accurate and runnable as written.
- Manifest paths point to real files.
- Secret + PII grep checks pass.
- License and .gitignore present at repo root.