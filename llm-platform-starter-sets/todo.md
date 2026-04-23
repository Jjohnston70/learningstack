# todo.md — Modular LLM Platform Build Plan

This file defines the phased build plan. Each phase includes a goal, deliverables, expected outputs, and a standalone build prompt you can hand to an AI assistant or developer.

---

# Phase 1 — Core Skeleton

## Goal
Multi-client modular architecture with client config, module registry, basic routing, and basic runtime.

## Deliverables
- Root README
- Python starter with client + module config
- TypeScript starter
- Simple routing and runtime
- Basic tests

## Outputs
- [ ] Runnable Python starter
- [ ] Runnable TypeScript starter
- [ ] Config loading verified
- [ ] Request routed to correct module

## Standalone Build Prompt

```
Role: Senior platform architect and implementation engineer.

Task: Build a starter architecture for a multi-client modular LLM platform.

Constraints:
- No per-client forks
- Shared modules and client configuration
- Knowledge separate from behavior
- Beginner-readable with comments
- Both Python and TypeScript starter versions

Required Deliverables:
- folder layout
- JSON client config examples
- JSON module config examples
- module loader
- router
- runtime orchestration
- minimal tests

Expected Outputs:
- One runnable Python starter
- One runnable TypeScript starter
- Explanation of every folder and file
```

---

# Phase 2 — Prompt Assembly, Context Builder, Redaction, Validation

## Goal
Turn the skeleton into a safer execution layer with real prompt assembly, PII protection, output validation, and structured logging.

## Deliverables
- prompt_builder (assembles final prompt from config + instructions + request)
- context_builder (structured execution context object)
- redactor (masks PII before logging)
- validator (checks output matches schema)
- execution logger (safe structured events)
- module instruction files
- tests for redaction and validation

## Outputs
- [ ] Request pipeline builds a deterministic final prompt
- [ ] PII-sensitive fields redacted before logging
- [ ] Output validated against schema
- [ ] Request trace logged safely

## Standalone Build Prompt

```
Role: Senior AI platform engineer building a production-minded modular LLM execution layer.

Constraints:
- Preserve tenant isolation
- Do not log raw sensitive values
- Separate module instructions from client config
- Beginner-readable with comments
- Both Python and TypeScript implementations
- Show exact request flow from input to validated output

Task: Extend the starter to add:
- module instruction files
- prompt assembly
- context builder
- redaction utility
- output validation
- structured execution logs
- tests

Expected Outputs:
- Final prompt assembled from client + module + user request
- Safe log object with redacted values
- Validated structured response object
- Example mapped to real business workflow
```

---

# Phase 3 — Module Registry and Version Control

## Goal
Independently versioned modules with controlled client rollout.

## Deliverables
- Module manifest versioning
- Compatibility checks
- Pinned version support per client
- Fallback behavior
- Release notes field in manifests

## Outputs
- [ ] Client can pin or float module versions
- [ ] Runtime resolves correct module version
- [ ] Compatibility errors surfaced clearly
- [ ] Module update rollout is controlled

## Standalone Build Prompt

```
Role: Platform engineer implementing controlled module lifecycle management.

Constraints:
- Modules independently versioned
- Clients may pin versions
- Runtime fails clearly on missing or incompatible versions
- Manifests readable and explicit

Task: Add version resolution to the modular platform and support pinned client module versions.

Required Deliverables:
- manifest updates
- version resolver
- compatibility checker
- test cases
```

---

# Phase 4 — Tenant-Safe Retrieval Layer

## Goal
Per-client retrieval boundaries so Client A's knowledge never leaks into Client B's context.

## Deliverables
- Retrieval namespace model
- Data source registry
- Document selection logic
- Retrieval trace metadata
- Test fixtures

## Outputs
- [ ] Client data isolation verified
- [ ] Retrieval only from approved sources
- [ ] Context injection traceable

## Standalone Build Prompt

```
Role: Senior retrieval systems engineer for a multi-tenant AI platform.

Constraints:
- Never mix cross-client data
- Retrieval namespaced per tenant
- Log only safe retrieval metadata
- Keep starter implementation understandable

Task: Add tenant-safe retrieval patterns and context source selection.

Required Deliverables:
- retrieval architecture
- retrieval abstractions
- sample retrieval metadata
- safe trace logs
- tests
```

---

# Phase 5 — Tool Adapters and Permission Gate

## Goal
Tool calling with module-level and client-level permission enforcement.

## Deliverables
- Tool registry
- Permission checks
- Execution guard
- Audit events for denied actions

## Outputs
- [ ] Tools callable only if allowed
- [ ] Denied actions logged safely
- [ ] Module-tool alignment enforced

## Standalone Build Prompt

```
Role: Secure AI systems engineer implementing tool execution controls.

Constraints:
- Tools must be explicitly registered
- Clients only get approved tools
- Modules only call allowed tools
- All denied actions visible in logs
- Simple and auditable

Task: Implement tool adapters and a permission gate for module execution.

Required Deliverables:
- tool registry
- permission enforcement
- audit logging
- tests
```

---

# Phase 6 — Plugin Interface for Exceptions

## Goal
Client-specific custom logic without forking the core platform.

## Deliverables
- Plugin contract interface
- Lifecycle hooks (before_prompt, after_response, allowed_tools)
- One example client plugin
- Tests
- Documentation of when to use plugin vs config

## Outputs
- [ ] Client-specific code isolated from core
- [ ] Hooks explicit and limited
- [ ] Core stays stable

## Standalone Build Prompt

```
Role: Platform architect implementing exception-safe extensibility.

Constraints:
- Use plugins only for real exceptions
- Config-first design
- Hooks must be explicit and limited
- No hidden magic behavior

Task: Add a plugin interface and one example plugin.

Required Deliverables:
- plugin contract
- lifecycle hooks
- sample plugin
- test coverage
- explanation of plugin vs config guidance
```

---

# Phase 7 — Provider Integration

## Goal
Connect the runtime to a real LLM provider safely with provider abstraction.

## Deliverables
- Provider interface (abstraction layer)
- Provider adapter (Claude, OpenAI, Gemini, Ollama)
- Request/response mapping
- Retry and timeout handling
- Error handling

## Outputs
- [ ] Live model execution working
- [ ] Provider abstraction holds (swappable)
- [ ] Secrets never in logs
- [ ] Timeout and retry paths clear

## Standalone Build Prompt

```
Role: Senior AI integration engineer.

Constraints:
- Abstract provider logic behind an interface
- Do not leak secrets in logs
- Handle timeout and retry paths clearly
- Keep provider integration swappable

Task: Add real LLM provider integration.

Required Deliverables:
- provider interface
- one sample provider adapter
- safe config handling
- tests/mocks
```

---

# Phase 8 — Admin Controls, Observability, and Rollout

## Goal
Production operations readiness: staged rollout, metrics, audit events, rollback.

## Deliverables
- Rollout flags (internal → beta → production)
- Module promotion states
- Execution metrics
- Audit dashboard shape
- Rollback guidance

## Outputs
- [ ] Staged rollout and rollback working
- [ ] Execution visibility confirmed
- [ ] Incident-friendly design in place

## Standalone Build Prompt

```
Role: Production platform engineer preparing a modular AI system for operational use.

Constraints:
- Visibility over cleverness
- Auditability first
- Staged rollout support
- Rollback explicit

Task: Add admin control concepts, observability structure, and rollout mechanics.

Required Deliverables:
- rollout model
- metrics model
- audit event model
- rollback guidance
```
