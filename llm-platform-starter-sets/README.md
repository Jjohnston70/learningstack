# Modular LLM Platform Starter

A starter architecture for building a multi-client LLM platform using shared modules, client configuration, and tenant-safe execution.

This repo includes:
- `python-starter/` — Python runtime and module wrappers
- `typescript-starter/` — TypeScript runtime and module wrappers
- `module-template/` — Copy this to create a new module
- `packs/` — Domain content packs (business operations, sales, onboarding)
- `prompts/` — Reusable analysis prompts for module review

## The Core Idea

A common mistake is building one repo per client, one prompt set per client, one copy of business logic per client. That gets messy fast.

This project uses a better pattern:

```
User Request
    ↓
Identify Client
    ↓
Load Client Config
    ↓
Load Enabled Modules
    ↓
Route Request
    ↓
Build Context
    ↓
Assemble Prompt
    ↓
Call LLM
    ↓
Validate Output
    ↓
Redact + Log
    ↓
Return Response
```

One platform. Many clients. Shared modules. Per-client config.

## Design Principles

1. **Shared core, not client forks** — All clients run on one platform
2. **Modules are reusable behavior packages** — proposal-command, financial-command, workspace-command
3. **Clients enable only what they need** — Active modules, permissions, data sources in config
4. **Knowledge and behavior are separate** — Docs go in retrieval. Logic goes in modules.
5. **Plugins are for exceptions** — Use config for normal variation. Plugins only for genuinely unique client code.

## Quick Start

```bash
# Python starter
cd python-starter
pip install -r requirements.txt
python -m app.main

# TypeScript starter
cd typescript-starter
npm install
npx ts-node src/main.ts
```

## Build Phases

| Phase | What It Adds |
|---|---|
| 1 | Core skeleton: routing, modules, config |
| 2 | Prompt assembly, context builder, redaction, validation, logging |
| 3 | Module versioning and controlled rollout |
| 4 | Tenant-safe retrieval layer |
| 5 | Tool adapters and permission gate |
| 6 | Plugin interface for client exceptions |
| 7 | Real LLM provider integration |
| 8 | Admin controls, observability, staged rollout |

See `todo.md` for the full phased build plan with standalone prompts.

## Module Structure

Every module uses the same normalized shape:

```
module/
├── manifest.json           ← identity and metadata
├── instructions.md         ← behavior specification
├── policies.yaml           ← what the module can and can't do
├── dependencies.yaml       ← what it needs to run
├── output_schema.json      ← what it must return
├── retrieval_sources.yaml  ← knowledge sources (optional)
├── tool_registry.json      ← callable actions (optional)
├── tests/
├── adapters/
│   ├── python/module.py
│   └── typescript/module.ts
└── docs/integration-notes.md
```

Copy `module-template/` to get started.
