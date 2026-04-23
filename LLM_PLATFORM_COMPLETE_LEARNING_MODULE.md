# LLM Platform Architecture — Complete Learning Module
**Owner:** Jacob Johnston, True North Data Strategies LLC
**Source:** Compiled from Q&A sessions, Phase 1 and Phase 2 build sessions, April 2026
**Purpose:** Complete reference for understanding, building, and extending a modular LLM platform

---

## Table of Contents

1. [What Most "AI Products" Actually Are](#1-what-most-ai-products-actually-are)
2. [LLM System Layers Explained](#2-llm-system-layers-explained)
3. [Module Architecture — The Core Concept](#3-module-architecture--the-core-concept)
4. [What Goes In Each Folder](#4-what-goes-in-each-folder)
5. [Client Configuration vs. Code Forks](#5-client-configuration-vs-code-forks)
6. [RAG Systems — Vector vs. Graph vs. Hybrid](#6-rag-systems--vector-vs-graph-vs-hybrid)
7. [The Orchestrator Pattern](#7-the-orchestrator-pattern)
8. [Plugins and Extension Points](#8-plugins-and-extension-points)
9. [How Request Flow Actually Works](#9-how-request-flow-actually-works)
10. [Phase 2 — The Execution Layer](#10-phase-2--the-execution-layer)
11. [Prompt Assembly — Building the Final Prompt](#11-prompt-assembly--building-the-final-prompt)
12. [Context Builder — Structuring What Goes to the Model](#12-context-builder--structuring-what-goes-to-the-model)
13. [Redaction — Protecting Sensitive Data in Logs](#13-redaction--protecting-sensitive-data-in-logs)
14. [Output Validation — Making Sure the Model Actually Answered](#14-output-validation--making-sure-the-model-actually-answered)
15. [Execution Logging — Seeing What Happened Without Seeing Too Much](#15-execution-logging--seeing-what-happened-without-seeing-too-much)
16. [Module Instruction Files — Behavior vs. Config](#16-module-instruction-files--behavior-vs-config)
17. [Connecting Real-World Modules to the Platform](#17-connecting-real-world-modules-to-the-platform)
18. [Documentation Libraries as Action Modules](#18-documentation-libraries-as-action-modules)
19. [Analyzing and Wrapping Existing Automation Modules](#19-analyzing-and-wrapping-existing-automation-modules)
20. [The Platform Starter Kit Architecture](#20-the-platform-starter-kit-architecture)
21. [Business Operations Content Packs](#21-business-operations-content-packs)
22. [8-Phase Build Roadmap](#22-8-phase-build-roadmap)
23. [Key Mistakes to Avoid](#23-key-mistakes-to-avoid)
24. [Mental Model Summary](#24-mental-model-summary)

---

## 1. What Most "AI Products" Actually Are

Most products marketed as "AI" are software systems wrapped around another company's LLM. This is called an **LLM wrapper** or **AI wrapper**.

```
User
  │
App / UI
  │
Wrapper System (prompts, tools, memory, RAG, routing)
  │
Underlying LLM (OpenAI, Anthropic, Gemini, etc.)
```

The wrapper is software that controls how the LLM is used. The intelligence comes from the underlying model. Companies build wrappers because it is much faster than training a model from scratch.

### The Three Wrapper Types

**Thin wrapper** — 90% prompt engineering and UI
- Prompt template → API call → format response
- Example: AI writing tools, AI website builders, Chrome AI assistants

**Middleware wrapper** — Adds infrastructure around the model
- RAG retrieval, safety filters, caching, logging, tool calling, agent workflows
- Frameworks used: LangChain, LlamaIndex, LiteLLM, Semantic Kernel

**Multi-LLM orchestrator** — Routes across multiple models
- Router → reasoning model / coding model / search model → aggregator
- Some run models in parallel and combine outputs

### How to Identify a Wrapper

- Company never says what model they trained
- App asks for OpenAI/Anthropic API key
- Network requests go to `api.openai.com` or `api.anthropic.com`

### Who Actually Trains Foundation Models

Only a handful of organizations: OpenAI, Google DeepMind, Anthropic, Meta, xAI, Mistral, DeepSeek. Everyone else builds systems around those models.

**For builders, wrappers are the correct architecture today.** The real innovation is in the orchestration layer.

---

## 2. LLM System Layers Explained

```
                    ┌─────────────────────────────┐
                    │         Client A            │
                    │ modules: 1,2,4,7            │
                    │ branding, rules, data       │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────┴───────────────┐
                    │      Client Configuration   │
                    │ enabled modules, permissions │
                    │ system prompt, routing rules │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────┴───────────────┐
                    │     Orchestration Layer      │
                    │ prompt assembly              │
                    │ tool calling                 │
                    │ retrieval / RAG              │
                    │ guardrails / logging         │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────┴───────────────┐
                    │       Shared Modules         │
                    │ module 1...module N          │
                    │ each independently versioned │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────┴───────────────┐
                    │        Base LLM API          │
                    │ OpenAI / Anthropic / etc.    │
                    └─────────────────────────────┘
```

**The key principle:** One core platform. Shared modules. Per-client config. When a module improves, every client using it gets the improvement.

---

## 3. Module Architecture — The Core Concept

A module is one independently maintainable, optional component. Each client's configuration tells the system which modules are active.

**What counts as a module:**
- A knowledge domain
- A workflow
- A prompt pack
- A toolset
- A retrieval source
- A rules engine
- An output formatter
- A decision policy

**Example modules in a TNDS-style system:**
- `proposal-command` — Generate proposals
- `financial-command` — Financial analysis
- `fleet-command` — DOT compliance
- `realty-command` — Property management
- `onboarding-command` — New client setup
- `workspace-command` — Drive/Sheets/Gmail operations

### Normalized Module Structure

Every module uses the same target shape. This is what makes them interchangeable:

```
module/
├── manifest.json           ← who this module is
├── instructions.md         ← how this module behaves
├── policies.yaml           ← what it's allowed to do
├── dependencies.yaml       ← what it needs to run
├── output_schema.json      ← what it must return
├── retrieval_sources.yaml  ← what knowledge it uses (optional)
├── tool_registry.json      ← what actions it can take (optional)
├── tests/                  ← verify it works
├── adapters/
│   ├── python/
│   │   └── module.py       ← Python runtime wrapper
│   └── typescript/
│       └── module.ts       ← TypeScript runtime wrapper
└── docs/
    └── integration-notes.md
```

### manifest.json Example

```json
{
  "name": "financial-command",
  "version": "1.2.0",
  "description": "Handles financial analysis and reporting workflows",
  "required_tools": ["calculator", "sheets"],
  "required_permissions": ["finance.read"],
  "output_mode": "structured",
  "output_fields": ["summary", "risks", "recommended_actions"],
  "keywords": ["budget", "invoice", "profit", "forecast", "cash flow"]
}
```

---

## 4. What Goes In Each Folder

### Knowledge Base (`/knowledge/` or `/retrieval/`)

**What it is:** Documents, embeddings, FAQs, examples — the information the system retrieves from.

```
knowledge/
├── core/            ← Platform-level help, workflows, templates
├── industry/        ← Regulations, compliance, domain docs
├── tenants/         ← Customer private docs (scoped by tenant_id)
└── indexes/         ← Vector indexes and graph indexes
```

**Key rule:** Knowledge ≠ Behavior. Two clients can share the same module behavior but use completely different knowledge stores.

### Module Folder (`/modules/`)

**What it is:** Behavior — how the system acts.

```
modules/
├── base/            ← Every tenant gets these
└── industry/        ← Install on demand
```

### Instructions File (`instructions.md`)

The behavioral specification for the module. Contains:
- What the module does
- What it refuses to do
- What format it answers in
- What compliance rules apply
- Output expectations

**Do NOT put prompts in client config. Put them here.**

### Tools Folder (`/tools/`)

Functions the model can actually call — read data, compute, query APIs.

Examples for `workspace-command`:
- `run_drive_inventory()` — Scan Drive files
- `setup_folder_structure()` — Create Drive folders
- `send_gmail()` — Send email with template

**Why separate from prompts:** Tools execute in your code. Prompts execute in the LLM. Testing is independent.

### Services Folder (`/services/`)

The runtime infrastructure:

```
services/
├── api-gateway/       ← Request routing, auth, rate limiting
├── ai-orchestrator/   ← Model selection, tool policy, retries
├── ingestion-service/ ← Document processing, chunking, embedding
├── retrieval-service/ ← RAG coordination, reranking
└── worker-service/    ← Async jobs, cron
```

### Packages Folder (`/packages/`)

Shared code used across apps and services:

```
packages/
├── rag-core/      ← Vector + graph retrieval
├── model-router/  ← Provider adapters
├── command-sdk/   ← Module contract interface
└── tenant-sdk/    ← Multi-tenant config
```

---

## 5. Client Configuration vs. Code Forks

**The rule:** Client differences live in configuration, not code forks.

### What Goes In Config

```json
{
  "client_id": "client-alpha",
  "active_modules": ["financial-command", "proposal-command"],
  "module_versions": {
    "financial-command": "1.2.0",
    "proposal-command": "2.0.1"
  },
  "branding": { "company_name": "Client Alpha", "tone": "direct, practical" },
  "data_sources": ["alpha-drive", "alpha-crm"],
  "permissions": {
    "financial-command": ["read"],
    "proposal-command": ["read", "draft"]
  }
}
```

### What Becomes a Plugin (Not Config)

Use plugins only when the difference is:
- Custom API integration
- Unique approval workflow
- Client-specific output transform
- Genuinely different process that can't be config-driven

For everything else (wording, thresholds, enabled/disabled), use config.

### Module Versioning

```json
{
  "client_id": "client-alpha",
  "module_versions": {
    "financial-command": "1.2.0"
  }
}
```

Pin versions so updates are controlled. Roll out incrementally: internal test → one client → all clients.

---

## 6. RAG Systems — Vector vs. Graph vs. Hybrid

RAG = Retrieval-Augmented Generation. Before answering, the system retrieves relevant documents and includes them in context.

### Vector-Only RAG

Converts text to embeddings. Similarity search finds closest chunks.

**Strengths:** Fast. Good at semantic similarity.
**Weakness:** Bad at exact identifiers, multi-hop questions, regulatory citation numbers.

### Graph RAG

Stores relationships as a typed graph:

```
(§ 382.211) -[:REQUIRES]-> (Remove Driver) -[:TRIGGERS]-> (Clearinghouse Report)
```

**Strengths:** Can answer "what happens if...?" — traverses relationships.
**Weakness:** Higher build complexity.

### Hybrid RAG (Target Architecture)

```
User Query
    │
Intent Classifier
    │
    ├── Graph Query     ← "what triggers what" questions
    ├── Vector Query    ← "what does § X say" questions
    └── Hybrid          ← default for ambiguous queries
    │
Context Merger
    │
LLM
```

**Hybrid Search Enhancement (BM25 + Vector):**
Run lexical BM25 search AND dense vector search in parallel, fuse with RRF (Reciprocal Rank Fusion), optionally rerank with cross-encoder. Catches exact identifiers AND semantic matches.

---

## 7. The Orchestrator Pattern

The orchestrator receives every request and decides what to do with it:

```python
def handle_request(client_id: str, user_input: str):
    client = load_client(client_id)
    enabled_modules = load_enabled_modules(client_id)
    matched_modules = route_request(user_input, enabled_modules)
    context = build_context(client=client, modules=matched_modules, user_input=user_input)
    response = call_llm(context)
    validated = validate_response(response, matched_modules, client)
    return validated
```

### Routing Options

- **Rules first:** Keywords map to modules (cheapest, start here)
- **LLM classifier:** Small model decides routing
- **Hybrid (recommended):** Rules first, classifier as fallback

---

## 8. Plugins and Extension Points

Plugins allow client-specific customization without forking the core:

```python
class ClientPlugin:
    def before_prompt(self, context): ...    # modify before LLM call
    def after_response(self, response): ...  # transform before return
    def allowed_tools(self): ...             # restrict tool access
```

**Use config when:** difference is wording, tone, thresholds, enabled/disabled.
**Use plugins when:** difference is custom API, custom business logic, unique approval workflow.

---

## 9. How Request Flow Actually Works

```
User asks question
    ↓
Identify client
    ↓
Load client config
    ↓
Determine enabled modules
    ↓
Route request to module(s)
    ↓
Pull approved knowledge/tools for that client
    ↓
Assemble prompt + context          ← Phase 2 starts here
    ↓
Call LLM
    ↓
Validate output against policy/schema
    ↓
Redact before logging
    ↓
Return answer
```

---

## 10. Phase 2 — The Execution Layer

**Phase 1 answered:** "Which client? Which modules?"

**Phase 2 answers:** "Exactly what prompt do we build, what context goes in, what gets redacted, what gets logged, and how do we validate the output?"

Phase 2 adds five new capabilities to the runtime:

| Component | Job |
|---|---|
| Prompt Builder | Assembles final prompt from client + module + request |
| Context Builder | Creates structured execution object (not raw text) |
| Redaction Utility | Prevents PII from reaching logs |
| Validator | Confirms output matches expected schema |
| Execution Logger | Records what happened safely |

**Why this order matters:** If you skip to provider integration before these exist, you get a fast machine with no brakes. Build brakes first.

### Phase 2 Folder Layout

```
python-starter/
├── app/
│   ├── core/
│   │   ├── types.py
│   │   ├── config_loader.py
│   │   ├── module_loader.py
│   │   ├── router.py
│   │   ├── runtime.py
│   │   ├── prompt_builder.py       ← NEW
│   │   ├── context_builder.py      ← NEW
│   │   ├── redactor.py             ← NEW
│   │   ├── validator.py            ← NEW
│   │   └── logger.py               ← NEW
│   ├── modules/
│   │   ├── financial_command/
│   │   │   └── instructions.md     ← NEW
│   │   └── proposal_command/
│   │       └── instructions.md     ← NEW
│   └── main.py
├── tests/
│   ├── test_redactor.py            ← NEW
│   └── test_validator.py           ← NEW
```

---

## 11. Prompt Assembly — Building the Final Prompt

The prompt builder takes structured inputs and assembles a deterministic final prompt. This is what ends the era of "I copy-pasted the prompt and hoped for the best."

### What Goes In

- Client branding and tone
- Module instructions
- User request
- Approved data source names
- Required output field list

### What Comes Out

One clean, deterministic prompt string.

### Python Implementation

```python
def build_prompt(
    client_name: str,
    tone: str,
    module_name: str,
    module_instructions: str,
    user_request: str,
    data_sources: list,
    output_fields: list,
) -> str:
    data_source_text = ", ".join(data_sources) if data_sources else "none provided"
    output_field_text = ", ".join(output_fields) if output_fields else "freeform"

    return f"""
You are operating for client: {client_name}.
Response tone: {tone}.
Selected module: {module_name}.

Module instructions:
{module_instructions}

Approved data sources:
{data_source_text}

User request:
{user_request}

Required output fields:
{output_field_text}

Rules:
- Do not invent unavailable facts.
- Clearly mark assumptions.
- Return a concise, structured response.
""".strip()
```

### TypeScript Implementation

```typescript
export function buildPrompt(args: {
  clientName: string;
  tone: string;
  moduleName: string;
  moduleInstructions: string;
  userRequest: string;
  dataSources: string[];
  outputFields: string[];
}): string {
  const dataSourceText = args.dataSources.length > 0
    ? args.dataSources.join(", ") : "none provided";
  const outputFieldText = args.outputFields.length > 0
    ? args.outputFields.join(", ") : "freeform";

  return `
You are operating for client: ${args.clientName}.
Response tone: ${args.tone}.
Selected module: ${args.moduleName}.

Module instructions:
${args.moduleInstructions}

Approved data sources:
${dataSourceText}

User request:
${args.userRequest}

Required output fields:
${outputFieldText}

Rules:
- Do not invent unavailable facts.
- Clearly mark assumptions.
- Return a concise, structured response.
`.trim();
}
```

---

## 12. Context Builder — Structuring What Goes to the Model

Instead of tossing random strings at the LLM, build a formal execution context object. Structure beats chaos.

```python
def build_context(client_config, module_config, user_request):
    return {
        "client_id": client_config["client_id"],
        "client_name": client_config["name"],
        "tone": client_config.get("branding", {}).get("tone", "clear"),
        "module_name": module_config["name"],
        "module_version": module_config["version"],
        "user_request": user_request,
        "data_sources": client_config.get("data_sources", []),
        "permissions": client_config.get("permissions", {}).get(module_config["name"], []),
        "output_fields": module_config.get("output_fields", []),
    }
```

**TypeScript interface:**

```typescript
export interface ExecutionContext {
  clientId: string;
  clientName: string;
  tone: string;
  moduleName: string;
  moduleVersion: string;
  userRequest: string;
  dataSources: string[];
  permissions: string[];
  outputFields: string[];
}
```

---

## 13. Redaction — Protecting Sensitive Data in Logs

Logs love to become accidental confession booths. Redaction prevents PII from reaching any log sink — Datadog, Sentry, console.log, or anywhere else.

### What Gets Redacted

- Email addresses → `[REDACTED_EMAIL]`
- Phone numbers → `[REDACTED_PHONE]`
- Account IDs, SSNs → masked patterns
- Credentials → never log these

### Python Implementation

```python
import re
from typing import Any, Dict

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b")

def redact_text(value: str) -> str:
    value = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", value)
    value = PHONE_PATTERN.sub("[REDACTED_PHONE]", value)
    return value

def redact_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: redact_text(value) if isinstance(value, str) else value
        for key, value in data.items()
    }
```

### TypeScript Implementation

```typescript
const EMAIL_PATTERN = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g;
const PHONE_PATTERN = /\b(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b/g;

export function redactText(value: string): string {
  return value
    .replace(EMAIL_PATTERN, "[REDACTED_EMAIL]")
    .replace(PHONE_PATTERN, "[REDACTED_PHONE]");
}

export function redactRecord(input: Record<string, unknown>): Record<string, unknown> {
  const output: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(input)) {
    output[key] = typeof value === "string" ? redactText(value) : value;
  }
  return output;
}
```

---

## 14. Output Validation — Making Sure the Model Actually Answered

"The model said something plausible" ≠ "The system produced a valid output." A validator checks that required fields exist and are not empty.

### Python Implementation

```python
from typing import Any, Dict, List, Tuple

def validate_output(output: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
    errors = []
    for field in required_fields:
        if field not in output:
            errors.append(f"Missing required field: {field}")
            continue
        value = output[field]
        if value is None:
            errors.append(f"Field is null: {field}")
        elif isinstance(value, str) and not value.strip():
            errors.append(f"Field is empty string: {field}")
        elif isinstance(value, list) and len(value) == 0:
            errors.append(f"Field is empty list: {field}")
    return (len(errors) == 0, errors)
```

### TypeScript Implementation

```typescript
export function validateOutput(
  output: Record<string, unknown>,
  requiredFields: string[]
): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];
  for (const field of requiredFields) {
    if (!(field in output)) {
      errors.push(`Missing required field: ${field}`);
      continue;
    }
    const value = output[field];
    if (value === null || value === undefined) {
      errors.push(`Field is null or undefined: ${field}`);
    } else if (typeof value === "string" && value.trim().length === 0) {
      errors.push(`Field is empty string: ${field}`);
    } else if (Array.isArray(value) && value.length === 0) {
      errors.push(`Field is empty list: ${field}`);
    }
  }
  return { isValid: errors.length === 0, errors };
}
```

---

## 15. Execution Logging — Seeing What Happened Without Seeing Too Much

A structured execution log records operational facts without recording sensitive content. It passes through the redactor before writing.

**What belongs in a log event:**
- event type
- client_id (not client name — just the ID)
- module name and version
- data sources used (names only, not content)
- whether output was valid
- timestamp

**What never belongs in a log event:**
- raw prompt text
- raw LLM response
- user data
- PII of any kind

### Python Implementation

```python
from app.core.redactor import redact_dict

def build_log_event(event_type, context, output_valid):
    raw_event = {
        "event_type": event_type,
        "client_id": context["client_id"],
        "module_name": context["module_name"],
        "module_version": context["module_version"],
        "user_request": context["user_request"],  # will be redacted
        "data_sources": ", ".join(context.get("data_sources", [])),
        "output_valid": str(output_valid),
    }
    return redact_dict(raw_event)
```

---

## 16. Module Instruction Files — Behavior vs. Config

**instructions.md** is where module behavior lives. It is not a client config file. It is not a giant system prompt. It is the operating spec for one module.

### What Goes In instructions.md

```markdown
# financial-command instructions

Purpose:
Support financial analysis and decision support.

Behavior rules:
- Focus on operational clarity and financial risk.
- Prioritize overdue invoices, cash flow, margin pressure, and forecast exposure.
- Do not invent numbers not present in the provided context.
- When assumptions are necessary, label them clearly.

Output expectations:
- summary
- risks
- recommended_actions

Style:
- direct
- concise
- action-oriented
```

### Why This Matters

Without instructions.md, prompts sprawl into client configs and nobody knows which version is the real one. With instructions.md, behavior is owned by the module, not copy-pasted everywhere.

**The discipline:** Module instructions live in the module. Client config lives in config. Never swap them.

---

## 17. Connecting Real-World Modules to the Platform

If you have existing automation modules (Apps Script, Python scripts, PowerShell, JS), the connection pattern is:

```
User Request
     │
LLM Runtime (Python/TypeScript starter)
     │
Module Selected
(proposal-command / workspace-command / financial-command)
     │
Module Instructions + Schema
     │
Tool Adapter
     │
Workspace Tools / Apps Script / APIs
```

### Your Existing Modules Map Like This

| What You Have | Platform Role |
|---|---|
| Apps Script automation | Tool layer (callable via web app endpoint) |
| Python scripts | Direct tool or adapter |
| PowerShell scripts | Tool adapter (subprocess or API call) |
| Google Sheets | Data source / tool target |
| Google Docs templates | Tool target for document generation |

### The Integration Pattern

```
LLM Runtime
   │
   ├── proposal-command
   │      └── tools
   │          ├── proposal_builder
   │          └── presentation_generator
   │
   ├── workspace-command
   │      └── tools
   │          ├── drive_inventory
   │          ├── folder_setup
   │          └── gmail_automation
   │
   └── financial-command
          └── tools
              ├── invoice_summary
              └── cashflow_analysis
```

### Tool Adapter Pattern (Apps Script → Python)

```python
import requests

def run_drive_inventory() -> dict:
    """Calls the deployed Apps Script web app endpoint."""
    url = "https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec"
    response = requests.post(url, json={"action": "drive_inventory"})
    return response.json()
```

### Integration Order (Least Pain)

1. **proposal-command first** — clearest workflow, defined output, fewest dependencies
2. **workspace-command second** — good tool bundle, becomes reusable
3. **financial-command last** — most spreadsheet-context-heavy, more assumptions to unwind

### Before Wiring Anything

Run this analysis per module first:

1. What business workflow does it support?
2. Is it a module, a tool bundle, or both?
3. What Google/external resources does it depend on?
4. Does it use `SpreadsheetApp.getActiveSpreadsheet()`? (If yes, it needs a web app wrapper before Python can call it)
5. What are the inputs and outputs?

---

## 18. Documentation Libraries as Action Modules

Your chunked third-party docs in a vector DB can become action-capable modules — but only if you separate three things clearly:

```
Third-Party App Module
│
├── Documentation Layer    → what the app does, API patterns
├── Reasoning Layer        → instructions, decision rules
├── Tool Layer             → actual callable actions
└── Policy Layer           → permissions, approval rules
```

### Action Capability Levels

| Level | Description |
|---|---|
| Knowledge-only | Can answer questions, can't change anything |
| Read-only action | Can query/list/get, no writes |
| Approval-gated write | Can write, but requires human confirmation |
| Autonomous write | Can write without approval (use sparingly) |

### Module Types for Common Doc Sets

| Documentation | Module Type | Notes |
|---|---|---|
| HubSpot API docs | Action-capable (CRM) | create/update contact with approval |
| Firebase docs | Hybrid retrieval + tool | auth, Firestore, storage |
| Stripe docs | Read-heavy, approval-gated write | never autonomous payment execution |
| CFR 49 / DOT | Compliance/policy module | advisory, checklisting, validation |
| Realty compliance | Compliance/policy module | validation, audit prep, policy support |
| Handbook/SOP | Workflow guidance module | retrieval + decision support |
| Next.js / Tailwind | Knowledge-only | framework reference |

### The Warning

**Do NOT let vector retrieval become your action engine.**

Bad pattern:
```
Retrieve docs → Model infers endpoint → Tool executes directly
```

Good pattern:
```
Retrieve docs → Model chooses approved tool → Tool validates input
    → Policy checks permission → Action executes → Result logged
```

### tool_registry.json for Action Modules

```json
{
  "tools": [
    {
      "name": "create_contact",
      "description": "Create a CRM contact",
      "action_type": "write",
      "requires_approval": true
    },
    {
      "name": "get_contact",
      "description": "Retrieve contact by email",
      "action_type": "read",
      "requires_approval": false
    }
  ]
}
```

---

## 19. Analyzing and Wrapping Existing Automation Modules

When bringing an existing module (Apps Script, JS, Python, PowerShell) into the platform, do this in order:

### Step 1 — Inventory the module

Classify every file into:
- runtime logic
- tool logic
- UI asset (sidebar/dashboard HTML)
- setup script
- config
- template
- documentation
- test/sample

### Step 2 — Extract the runtime contract

```json
{
  "name": "proposal-command",
  "input_fields": ["client_name", "services", "timeline", "budget"],
  "output_fields": ["summary", "deliverables", "timeline", "next_steps"],
  "required_tools": ["proposal_generator", "document_template_loader"],
  "required_resources": ["FORM_ID", "SPREADSHEET_ID", "TEMPLATE_IDS", "PROPOSALS_FOLDER_ID"]
}
```

### Step 3 — Isolate non-runtime assets

Do not try to cram these into the runtime:
- Dashboard.html, Sidebar.html, Help.html
- Sample/preview HTML files
- Historical archive docs
- Unused config variants

### Step 4 — Create Python and TypeScript wrapper stubs

```python
# adapters/python/module.py
def run(context: dict) -> dict:
    """
    Entry point for proposal-command module.
    context contains: client_id, client_name, tone, user_request, data_sources
    """
    # TODO: Load instructions.md
    # TODO: Call proposal_tools.build_proposal(context)
    # TODO: Validate output against output_schema.json
    return {
        "summary": "Placeholder summary",
        "deliverables": [],
        "timeline": "",
        "next_steps": []
    }
```

### Step 5 — Create dependencies.yaml

```yaml
required_google_resources:
  - type: spreadsheet
    description: Proposal tracking spreadsheet
    env_var: SPREADSHEET_ID

  - type: folder
    description: Proposals output folder in Drive
    env_var: PROPOSALS_FOLDER_ID

  - type: doc_template
    description: Proposal document template
    env_var: PROPOSAL_TEMPLATE_ID

deployment:
  apps_script_web_app: true
  web_app_url_env_var: PROPOSAL_SCRIPT_URL
```

### Feasibility Verdicts

| Verdict | Meaning |
|---|---|
| Ready to wrap now | Clean workflow, clear I/O, minimal dependencies |
| Wrapable with minor cleanup | Small active-sheet or session assumptions to fix |
| Wrapable with medium refactor | Needs web app deployment + dependency mapping |
| Better treated as tool bundle only | No single module identity — split into tools |
| Not worth wrapping yet | Too tightly coupled to UI context |

---

## 20. The Platform Starter Kit Architecture

A complete modular LLM platform starter kit has this shape:

```
modular-llm-platform/
├── README.md
├── todo.md                          ← phased build plan
│
├── python-starter/
│   ├── app/
│   │   ├── core/                    ← runtime engine
│   │   ├── modules/                 ← module wrappers
│   │   └── tools/                   ← tool adapters
│   ├── config/
│   │   ├── clients/                 ← one JSON per client
│   │   └── modules/                 ← one JSON per module
│   └── tests/
│
├── typescript-starter/
│   ├── src/
│   │   ├── core/                    ← same pattern
│   │   ├── modules/
│   │   └── tools/
│   ├── config/
│   └── tests/
│
├── module-template/                 ← copy this to create a new module
│   ├── manifest.json
│   ├── instructions.md
│   ├── policies.yaml
│   ├── dependencies.yaml
│   ├── output_schema.json
│   ├── retrieval_sources.yaml
│   ├── tool_registry.json
│   ├── tests/
│   ├── adapters/
│   │   ├── python/module.py
│   │   └── typescript/module.ts
│   └── docs/integration-notes.md
│
├── packs/                           ← domain content packs
│   └── operations-onboarding-sales/
│
└── prompts/                         ← reusable prompts for analysis
    ├── module-review-prompt.md
    └── doc-library-review-prompt.md
```

### Starter Kit Design Principles

1. **Shared core, not client forks** — All clients run on one platform
2. **Modules are reusable** — A module is a behavior package
3. **Clients enable only what they need** — Config drives which modules are active
4. **Knowledge and behavior are separate** — Never mix them
5. **Plugins are for exceptions** — Use config for normal variation

---

## 21. Business Operations Content Packs

A content pack is a bundle of related assets across a domain — not a single module, but a collection that seeds multiple modules.

Example: `operations-onboarding-sales` pack contains:

| Asset Type | Goes To |
|---|---|
| SOPs and workflows | retrieval sources |
| Proposal templates | proposal-command |
| Contract templates | contract-command |
| Onboarding email templates | onboarding-command |
| Pricing guides | pricing-command |
| Apps Script command code | module adapters |

### Four Asset Classes in a Typical Pack

1. **Business operations knowledge and SOPs** — become retrieval sources and workflow guidance modules
2. **Reusable document assets** — become template references for action modules
3. **Apps Script command candidates** — become tool adapters and module wrappers
4. **Archive / historical material** — keep as docs, do not add to runtime

### Module Candidates Inside a Typical Operations Pack

| Module | Backed By |
|---|---|
| proposal-command | proposal generator, templates, pricing docs |
| contract-command | contract templates, service agreements |
| onboarding-command | onboarding bot, email templates, checklists |
| pricing-command | pricing docs and guides |
| ops-playbook | workflows, operations map, team quickstart |

### Staging Approach

Do not normalize everything at once.

- **Stage 1:** Add as a pack under `packs/`
- **Stage 2:** Extract manifests for each module candidate
- **Stage 3:** Map docs into retrieval sources
- **Stage 4:** Wrap command source code into adapters
- **Stage 5:** Register in marketplace/registry

---

## 22. Eight-Phase Build Roadmap

### Phase 1 — Core Skeleton

**Goal:** Multi-client modular architecture with routing and runtime

**Deliverables:**
- Root README and todo.md
- Python starter with client + module config
- TypeScript starter
- Simple routing and runtime
- Basic tests

**When done:** You can route a request to the right module and return a placeholder response.

---

### Phase 2 — Prompt Assembly, Context Builder, Redaction, Validation

**Goal:** Safer and more realistic execution layer

**Deliverables:**
- prompt_builder
- context_builder
- redactor (PII masking)
- validator (output schema checking)
- execution logger
- module instruction files
- tests for redaction and validation

**When done:** The system builds real prompts, validates real outputs, and logs safely.

---

### Phase 3 — Module Registry and Version Control

**Goal:** Independently versioned modules, controlled rollout

**Deliverables:**
- Module manifest versioning
- Compatibility checks
- Pinned version support
- Fallback behavior

**When done:** You can update a module for one client without affecting others.

---

### Phase 4 — Tenant-Safe Retrieval Layer

**Goal:** Per-client retrieval boundaries

**Deliverables:**
- Retrieval namespace model
- Data source registry
- Document selection logic
- Retrieval trace metadata

**When done:** Client A's knowledge never leaks into Client B's context.

---

### Phase 5 — Tool Adapters and Permission Gate

**Goal:** Tool calling with module-level and client-level enforcement

**Deliverables:**
- Tool registry
- Permission checks
- Execution guard
- Audit events for denied actions

**When done:** Tools are called only when allowed. All denied actions are logged.

---

### Phase 6 — Plugin Interface for Exceptions

**Goal:** Client-specific custom logic without forking core

**Deliverables:**
- Plugin contract interface
- Lifecycle hooks (before_prompt, after_response)
- One example client plugin
- Tests

**When done:** Client-specific weirdness lives in a controlled box, not in the core.

---

### Phase 7 — Provider Integration

**Goal:** Connect runtime to a real LLM provider

**Deliverables:**
- Provider interface (abstraction layer)
- Provider adapter (Claude, OpenAI, Gemini, Ollama)
- Request/response mapping
- Retry and timeout handling

**When done:** Real model calls with provider-agnostic runtime.

---

### Phase 8 — Admin Controls, Observability, and Rollout

**Goal:** Production operations readiness

**Deliverables:**
- Rollout flags (staged release)
- Module promotion states (internal → beta → production)
- Execution metrics
- Audit dashboard shape
- Rollback notes

**When done:** You can release module updates incrementally and roll back if something breaks.

---

## 23. Key Mistakes to Avoid

### Prompt Sprawl
Copy-pasting and editing prompts per client until nobody knows which is real.

**Fix:** Central prompt registry. Module instruction files own behavior. Client overrides only in tiny scoped fields.

### Cross-Client Data Leakage
Client A's data appears in Client B's context.

**Fix:** Strict tenant isolation. Separate retrieval namespaces. Permission checks before every tool/data access. Redact logs — never dump raw context.

### Module Dependency Chaos
Module 4 quietly depends on Module 2. Something breaks and nobody knows why.

**Fix:** Declare dependencies in `manifest.json`. Validate at startup.

### Static Knowledge in Dynamic Environments
Regulations change. The knowledge base doesn't. Users get outdated advice.

**Fix:** Daily hash comparison of source URLs. Alert when content changes. Warn users in responses.

### Letting Retrieval Become the Action Engine
Model retrieves docs → guesses endpoint → executes write action directly.

**Fix:** Retrieval informs decisions. Tools perform actions. Policy gates what's allowed.

### Skipping Redaction and Validation
"It works" is not the same as "it's safe."

**Fix:** Build redactor and validator in Phase 2 before adding any real provider integration.

### Treating All Docs as Action-Capable
Not every documentation set should trigger live writes.

**Fix:** Assign each doc set a capability level: knowledge-only, read-only, approval-gated write, or autonomous write. Default to knowledge-only.

---

## 24. Mental Model Summary

### The Most Important Shift

**Do not think:** one client = one app

**Think:** one client = one policy/config package attached to a shared app

### The Formula

**Shared across all clients:**
- Module logic
- Prompts and instructions
- Tool wrappers
- Validation and schemas
- Orchestration

**Per client (configuration, not code):**
- Enabled modules
- Data sources
- Permissions
- Branding and tone
- Version pins
- Optional plugins

### The Real Product Is Not the Model

The model is the engine. The product is:

- Routing
- Context assembly
- Tool execution
- Permission enforcement
- Output validation
- Tenant isolation
- Version control
- Audit trail

### Three Wrong Ways People Build LLM Systems

1. **One repo per client** → maintainability dies wearing a fake mustache
2. **Giant system prompt with all behavior** → prompt sprawl with no ownership
3. **Retrieval → model → direct write** → confident intern with root access

### The Stack of Cognition Machines

```
LLM
 wrapped by Agent
  wrapped by Framework
   wrapped by Platform
    wrapped by Module
     wrapped by Client Config
      wrapped by Company branding
```

The real innovation is not the model. It is the orchestration, policy, and module architecture that controls what the model does and doesn't do.

---

*True North Data Strategies LLC | Jacob Johnston | April 2026*
*Compiled from Phase 1 and Phase 2 build sessions and Q&A — for public learning reference*
