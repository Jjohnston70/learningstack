Recommended path
Instead of this
Graph RAG first
→ better reasoning
→ maybe better answers
→ still weak validation and no outcome loop
Do this
Decision Engine Layer first
→ structured decisions
→ citation validation
→ knowledge freshness
→ execution hooks
→ outcome tracking
→ then add targeted graph/relationship logic only for proven chain questions
Why I would not lead with full Graph RAG

Your architecture doc is solid, but it assumes the main problem is retrieval structure. It is only part of the problem. The graph design improves multi-hop reasoning, relationship mapping, and hybrid routing. That is real value.

But your world-model analysis already identified the more important gaps:

no knowledge freshness monitoring
no citation verification
no outcome tracking
no validation of the assistant’s predictions vs reality

So if you build graph first, you get:

smarter answers
more architecture
more maintenance

But you still do not get:

validated answers
measured outcomes
closed learning loops
operational trust

That is why I’d change the sequence.

Better architecture: Decision Engine Layer

This becomes the layer between retrieval and user response.

Core idea

Instead of:

User Query
→ Retrieval
→ LLM Answer
→ User

You move to:

User Query
→ Retrieval
→ Decision Engine
   → classify
   → validate
   → structure
   → execute / recommend
   → log
   → follow up
→ User
What the Decision Engine solves
1. Structured outputs

Right now the assistant returns prose.

That should become a decision object like:

{
  "decision_id": "dec_123",
  "query_type": "compliance_chain",
  "risk_level": "high",
  "recommended_actions": [
    {
      "action_id": "remove_driver",
      "description": "Remove driver from safety-sensitive duty",
      "deadline": "immediate",
      "responsible_party": "employer",
      "citation": "§ 382.211"
    },
    {
      "action_id": "file_clearinghouse_report",
      "description": "Report violation to FMCSA Clearinghouse",
      "deadline": "within 2 business days",
      "responsible_party": "employer",
      "citation": "§ 382.705"
    }
  ],
  "citations": [
    {
      "section": "§ 382.211",
      "status": "verified",
      "confidence": 0.94
    },
    {
      "section": "§ 382.705",
      "status": "verified",
      "confidence": 0.89
    }
  ],
  "knowledge_freshness": "current",
  "confidence": 0.91,
  "requires_human_review": false
}

That one change is massive.

2. Citation verification

Your first doc explicitly flags this as a critical gap and even lays out a straightforward post-generation validation approach.

This belongs in the Decision Engine, not as a side feature.

Rule

No answer is “trusted” unless:

extracted citations are found in retrieval context or KB
citation confidence exceeds threshold
response is downgraded or warned if not
3. Knowledge freshness

Again, your first doc already calls this critical. Static regulatory knowledge in a changing environment is a liability.

The Decision Engine should check freshness metadata before response delivery.

Rule

If source freshness is stale:

inject warning
reduce confidence
flag for admin reindex
optionally require manual review for high-risk questions
4. Outcome tracking

This is the big one.

Your doc already proposes follow-up and outcome capture.

That should be native to the module:

Decision created
→ follow-up scheduled
→ user confirms action / failure / partial
→ accuracy score updated
→ retrieval / prompting improved later

That creates your moat.

5. Execution hooks

Not full autonomy. Controlled execution.

For example:

create suspense item
send alert
open follow-up task
write audit log
draft email to fleet manager
set review reminder

That means the assistant is no longer just answering. It is helping run the system.

What to do instead of full Graph RAG
Use a lightweight relationship layer first

I would not deploy Neo4j first.

I would use a Relationship Registry inside Postgres first.

Why

Because most of your immediate compliance chains can be represented with a simpler model:

regulation
required action
trigger
deadline
responsible party
next action
related regulation

That can live in relational tables or JSONB and get you 70–80% of the graph benefit with far less operational burden.

Your graph doc already defines the core entities and relationship types well.
I would reuse that logic, but not necessarily the full graph database on day one.

Better sequence: 3-tier relationship strategy
Tier 1: Decision Engine + vector retrieval

Use what you already have.

Add:
structured response schema
citation validator
freshness checker
decision log
follow-up workflow
action executor hooks

This should happen first.

Tier 2: Relationship Registry in Postgres

Before Neo4j, create explicit tables.

Example:

CREATE TABLE regulation_nodes (
  id UUID PRIMARY KEY,
  section_id VARCHAR(50) UNIQUE NOT NULL,
  title TEXT NOT NULL,
  category TEXT,
  summary TEXT,
  last_reviewed_at TIMESTAMP,
  freshness_status VARCHAR(20) DEFAULT 'current'
);

CREATE TABLE compliance_actions (
  id UUID PRIMARY KEY,
  action_key VARCHAR(100) UNIQUE NOT NULL,
  description TEXT NOT NULL,
  default_deadline TEXT,
  responsible_party TEXT
);

CREATE TABLE regulation_action_edges (
  id UUID PRIMARY KEY,
  regulation_id UUID REFERENCES regulation_nodes(id),
  action_id UUID REFERENCES compliance_actions(id),
  edge_type VARCHAR(50) NOT NULL, -- REQUIRES, TRIGGERS, LEADS_TO
  condition_text TEXT,
  citation_section VARCHAR(50),
  confidence NUMERIC(4,3) DEFAULT 1.000
);

CREATE TABLE action_action_edges (
  id UUID PRIMARY KEY,
  from_action_id UUID REFERENCES compliance_actions(id),
  to_action_id UUID REFERENCES compliance_actions(id),
  edge_type VARCHAR(50) NOT NULL,
  condition_text TEXT,
  confidence NUMERIC(4,3) DEFAULT 1.000
);

This gives you:

deterministic compliance chains
simpler ops
easier debugging
no extra graph infra yet
Tier 3: Neo4j only if needed

Move to Neo4j only when one of these becomes true:

relationship count gets large and traversal gets painful
you need community detection and clustering
you want deeper multi-hop exploration across many domains
your Postgres relationship layer becomes hard to maintain

Until then, keep it simpler.

Decision Engine Layer module you can drop into your stack

Below is the module I’d actually recommend.

Module: decision-engine-command
Purpose

Convert the assistant from a retrieval chatbot into a validated operational decision system.

Responsibilities
1. Query classification

Determine:

factual lookup
compliance chain
deadline/risk question
policy interpretation
action recommendation
uncertain / needs human review
2. Retrieval orchestration

Use:

vector only for exact text
vector + relationship registry for chain questions
fallback warnings if confidence low
3. Structured decision generation

Produce a typed decision object.

4. Validation layer

Run:

citation verification
freshness check
schema validation
contradiction checks
confidence scoring
5. Execution layer

Optional controlled actions:

create alert
create suspense task
queue follow-up
log audit event
draft user-facing summary
6. Outcome loop

Track:

user acknowledged?
action taken?
result?
prediction accuracy?
ASCII architecture
┌─────────────────────────────┐
│       Next.js UI            │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│     FastAPI Chat API        │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   decision-engine-command   │
│                             │
│  1. classify_query          │
│  2. retrieve_context        │
│  3. generate_decision       │
│  4. validate_decision       │
│  5. execute_hooks           │
│  6. log_and_schedule        │
└───────┬───────────┬─────────┘
        │           │
        ▼           ▼
┌──────────────┐  ┌────────────────────┐
│ Vector Store │  │ Relationship Store │
│ FAISS/Neon   │  │ Postgres tables    │
└──────────────┘  └────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│ Claude / LLM Generation     │
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│ Validation + Freshness      │
│ + Citation Verification     │
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│ Decision Log / Outcomes     │
│ Alerts / Follow-ups         │
└─────────────────────────────┘
Recommended folder structure
backend/
  app/
    decision_engine/
      __init__.py
      models.py
      service.py
      classifier.py
      retriever.py
      relationship_store.py
      generator.py
      validator.py
      executor.py
      outcomes.py
      freshness.py
      citations.py
      prompts.py
Core data models
models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class CitationCheck(BaseModel):
    section: str
    status: Literal["verified", "unverified", "missing"]
    confidence: float = Field(ge=0.0, le=1.0)
    source_file: Optional[str] = None


class RecommendedAction(BaseModel):
    action_id: str
    description: str
    deadline: Optional[str] = None
    responsible_party: Optional[str] = None
    citation: Optional[str] = None
    priority: Literal["low", "medium", "high", "critical"] = "medium"


class DecisionObject(BaseModel):
    decision_id: str
    query_type: Literal[
        "factual_lookup",
        "compliance_chain",
        "deadline_risk",
        "action_recommendation",
        "policy_interpretation",
        "uncertain"
    ]
    direct_answer: str
    risk_level: Literal["low", "medium", "high", "critical"]
    recommended_actions: List[RecommendedAction] = []
    citations: List[CitationCheck] = []
    confidence: float = Field(ge=0.0, le=1.0)
    knowledge_freshness: Literal["current", "stale", "unknown"] = "unknown"
    requires_human_review: bool = False
    warning_messages: List[str] = []
    created_at: datetime
Service flow
service.py
from datetime import datetime
from uuid import uuid4
from .classifier import classify_query
from .retriever import retrieve_context
from .generator import generate_decision_object
from .validator import validate_decision_object
from .executor import run_execution_hooks
from .outcomes import create_outcome_record


async def process_query(query: str, tenant_id: str, user_id: str) -> dict:
    decision_id = f"dec_{uuid4().hex}"

    query_type = classify_query(query)

    context_bundle = await retrieve_context(
        query=query,
        query_type=query_type,
        tenant_id=tenant_id
    )

    decision = await generate_decision_object(
        query=query,
        query_type=query_type,
        decision_id=decision_id,
        context_bundle=context_bundle
    )

    decision.created_at = datetime.utcnow()

    validated = await validate_decision_object(
        decision=decision,
        context_bundle=context_bundle,
        tenant_id=tenant_id
    )

    await run_execution_hooks(validated, tenant_id=tenant_id, user_id=user_id)
    await create_outcome_record(validated, tenant_id=tenant_id, user_id=user_id)

    return validated.model_dump()
Query classifier

Keep it simple first. Rule-based is enough.

classifier.py
import re

GRAPH_LIKE_PATTERNS = [
    r"what happens if",
    r"what do i need to do",
    r"what else is required",
    r"full compliance chain",
    r"steps after",
    r"downstream",
    r"trigger",
]

FACT_PATTERNS = [
    r"what does §",
    r"what does section",
    r"exact text",
    r"definition of",
    r"quote",
]

DEADLINE_PATTERNS = [
    r"when is .* due",
    r"deadline",
    r"expires",
    r"how long do i have",
]

def classify_query(query: str) -> str:
    q = query.lower()

    if any(re.search(p, q) for p in DEADLINE_PATTERNS):
        return "deadline_risk"

    if any(re.search(p, q) for p in FACT_PATTERNS):
        return "factual_lookup"

    if any(re.search(p, q) for p in GRAPH_LIKE_PATTERNS):
        return "compliance_chain"

    return "action_recommendation"
Retrieval orchestration
retriever.py
async def retrieve_context(query: str, query_type: str, tenant_id: str) -> dict:
    vector_results = await retrieve_vector_context(query=query, tenant_id=tenant_id)

    relationship_results = []
    if query_type in ["compliance_chain", "action_recommendation", "deadline_risk"]:
        relationship_results = await retrieve_relationship_context(query=query, tenant_id=tenant_id)

    freshness = await get_freshness_status(vector_results)
    return {
        "vector_results": vector_results,
        "relationship_results": relationship_results,
        "freshness": freshness,
    }
Key point

This is where you can later swap:

Postgres relationship registry → Neo4j

without rewriting the module.

Generator

Use the LLM to generate a schema-bound decision object, not freeform text.

generator.py
from .models import DecisionObject

DECISION_PROMPT = """
You are Decision Engine Assistant.

You must return a structured decision object.
Use only the provided context.
Do not invent citations.
If context is incomplete, lower confidence and require human review.
"""

async def generate_decision_object(query: str, query_type: str, decision_id: str, context_bundle: dict) -> DecisionObject:
    # Pseudocode:
    # 1. build prompt with vector + relationship context
    # 2. call LLM with JSON schema / structured output
    # 3. parse into Pydantic model
    ...
Validator

This is the heart of the module.

validator.py
from .citations import verify_citations
from .freshness import evaluate_freshness

async def validate_decision_object(decision, context_bundle: dict, tenant_id: str):
    citation_results = await verify_citations(
        decision=decision,
        vector_results=context_bundle["vector_results"],
        tenant_id=tenant_id
    )

    decision.citations = citation_results

    freshness_status, freshness_warnings = await evaluate_freshness(
        context_bundle["freshness"]
    )
    decision.knowledge_freshness = freshness_status
    decision.warning_messages.extend(freshness_warnings)

    unverified = [c for c in citation_results if c.status != "verified"]
    if unverified:
        decision.warning_messages.append(
            "Some citations could not be fully verified. Review before acting."
        )
        decision.confidence = min(decision.confidence, 0.65)

    if freshness_status == "stale":
        decision.warning_messages.append(
            "Source knowledge may be stale. Confirm current regulation before acting."
        )
        decision.confidence = min(decision.confidence, 0.60)

    if decision.confidence < 0.70:
        decision.requires_human_review = True

    return decision
Execution hooks
executor.py

This should be controlled, not autonomous chaos.

async def run_execution_hooks(decision, tenant_id: str, user_id: str):
    if decision.query_type == "deadline_risk" and decision.risk_level in ["high", "critical"]:
        await create_alert(
            tenant_id=tenant_id,
            title="Compliance deadline risk detected",
            body=decision.direct_answer
        )

    if decision.recommended_actions:
        await create_suspense_items(
            tenant_id=tenant_id,
            decision_id=decision.decision_id,
            actions=decision.recommended_actions
        )

    await write_audit_log(
        tenant_id=tenant_id,
        user_id=user_id,
        event_type="decision_generated",
        payload=decision.model_dump()
    )
Outcomes
outcomes.py
async def create_outcome_record(decision, tenant_id: str, user_id: str):
    await db.query_outcomes.create({
        "decision_id": decision.decision_id,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "query_type": decision.query_type,
        "risk_level": decision.risk_level,
        "confidence": decision.confidence,
        "followup_scheduled_at": compute_followup_date(decision),
        "status": "pending"
    })
What to build first, in order
Phase 1 — highest ROI

Build these before any graph work:

DecisionObject schema
citation verification
knowledge freshness checks
decision logging
follow-up outcome tracking

This directly addresses the gaps from your architecture analysis.

Phase 2 — lightweight relationship layer

Add:

regulation nodes
action nodes
edge tables
simple traversal service for compliance chains

This gives you much of what your graph doc wants, but with less complexity up front.

Phase 3 — selective graph adoption

Only then decide if you need Neo4j.

Keep Neo4j if:
multi-hop accuracy remains weak
traversal gets ugly in SQL
you need clustering/community summaries
you plan multi-domain expansion fast
Skip Neo4j if:
relationship registry handles 80% of queries
latency and maintenance are better in Postgres
your real gains come from validation and outcomes, not deeper graph complexity
My blunt recommendation
Best path for you

Do not start with Neo4j.
Build:

decision-engine-command

with:

schema-bound responses
validation
freshness
action hooks
outcome tracking

Then add:

relationship-registry-command

inside Postgres

Then later, maybe:

graph-reasoning-command

if the data proves you need it

That gives you:

lower risk
faster time to production
less infra sprawl
better trust
a stronger moat
Final architecture stack I recommend
Current Stack
─────────────
Next.js
FastAPI
FAISS
Neon Postgres
Claude

Upgrade Path
────────────
1. decision-engine-command
2. relationship-registry-command
3. freshness-monitor-command
4. citation-validator-command
5. outcome-tracker-command
6. optional graph-reasoning-command later


----------------------

Bottom line

The better way is:

Decision Engine first, graph later

Because the real gap is not “can the assistant connect ideas?”

The real gap is:

can the assistant make validated decisions, trigger action, and learn from outcomes?

That is the layer I would build first.

If you want, next I’ll turn this into a full implementation spec with:

file-by-file layout
database schema
API routes
prompt contracts


------


Thought for 9s

Absolutely. Below is the full implementation spec for a Decision Engine first, graph later architecture that fits your current compliance decision system direction.

This spec is based on the gaps and strengths already identified in your architecture docs: the system already has strong operational state capture and automation, but the urgent gaps are knowledge freshness, citation verification, outcome tracking, and prediction-vs-reality validation. The existing graph-augmented proposal is valuable for multi-hop reasoning, but it should come after the Decision Engine layer, not before.

1. Architecture Decision
Recommended order
Phase 1: Decision Engine
Phase 2: Relationship Registry in Postgres
Phase 3: Optional Graph Layer later
Why

Because your biggest gaps are not retrieval structure first. They are:

no knowledge freshness monitoring
no citation verification
no outcome tracking
no validation of the assistant’s predictions vs reality

So the first win is to move from:

Query → Answer

to:

Query → Decision → Validation → Action Hooks → Outcome Tracking
2. Target System Overview
Current state
Next.js UI
  → FastAPI chat endpoint
    → embeddings
    → FAISS search
    → Neon/Postgres chunk retrieval
    → Claude response

This matches your current baseline vector architecture.

New target state
Next.js UI
  → FastAPI API
    → Decision Engine
       1. classify query
       2. retrieve context
       3. generate structured decision
       4. verify citations
       5. check freshness
       6. run execution hooks
       7. log decision
       8. schedule follow-up
  → response to user
3. Folder and File Layout

Below is the layout I recommend for your FastAPI backend.

Backend structure
backend/
  app/
    main.py
    config.py
    dependencies.py

    api/
      routes/
        chat.py
        decisions.py
        outcomes.py
        alerts.py
        admin_knowledge.py

    decision_engine/
      __init__.py
      service.py
      models.py
      classifier.py
      retriever.py
      generator.py
      validator.py
      citations.py
      freshness.py
      executor.py
      outcomes.py
      relationship_store.py
      prompts.py
      serializers.py
      scoring.py

    data_access/
      db.py
      chunk_repo.py
      decision_repo.py
      outcome_repo.py
      freshness_repo.py
      relationship_repo.py
      alert_repo.py

    integrations/
      anthropic_client.py
      openai_client.py
      datadog_client.py
      email_client.py
      task_queue.py

    jobs/
      knowledge_freshness_job.py
      followup_scheduler_job.py
      citation_audit_job.py

    schemas/
      decisions.py
      outcomes.py
      alerts.py
      admin.py

    utils/
      ids.py
      logging.py
      dates.py
      tokens.py
      regex.py
4. File-by-file explanation
main.py
Purpose

Application entrypoint.

Task
boot FastAPI
register routers
startup/shutdown hooks
initialize DB, clients, queue
Why it exists

This is the app shell. Keep it thin.

config.py
Purpose

Centralized config.

Task
env vars
feature flags
thresholds
provider config
Example keys
ENABLE_DECISION_ENGINE=true
ENABLE_RELATIONSHIP_REGISTRY=true
ENABLE_GRAPH_RETRIEVAL=false
CITATION_MIN_CONFIDENCE=0.80
STALE_KNOWLEDGE_BEHAVIOR=warn
Why it exists

You want controlled rollout and easy ops changes.

dependencies.py
Purpose

FastAPI dependency wiring.

Task
DB session injection
auth context
tenant resolution
user context
service initialization
API route files
api/routes/chat.py
Purpose

Primary user chat endpoint.

Task
receive query
call decision_engine.service.process_query()
return structured response + user-friendly text
Why

This becomes your main entrypoint for the assistant.

api/routes/decisions.py
Purpose

Decision inspection and review.

Task
fetch prior decision by ID
list recent decisions
allow internal review / override
optionally mark “reviewed by human”
Why

You need an audit trail and inspectability.

api/routes/outcomes.py
Purpose

Outcome capture.

Task
receive success / failure / partial
capture actual result notes
score prediction accuracy
close loop on decision
Why

This is how the assistant learns whether it was right.

api/routes/alerts.py
Purpose

Alert and suspense creation.

Task
create alert from decision
list alerts tied to a decision
escalate critical items
Why

Lets the system trigger controlled action.

api/routes/admin_knowledge.py
Purpose

Knowledge admin endpoints.

Task
list stale sources
trigger re-index workflow
inspect freshness status
inspect citation verification issues
Why

Operational control for your KB.

Decision engine files
decision_engine/service.py
Purpose

Main orchestrator.

Task

Runs the full flow:

classify
→ retrieve
→ generate
→ validate
→ execute
→ log
→ schedule follow-up
Why

This is the brain of the Decision Engine.

decision_engine/models.py
Purpose

Core internal models.

Task

Defines:

DecisionObject
RecommendedAction
CitationCheck
FreshnessStatus
OutcomeRecord
Why

Every layer should use typed objects, not loose dicts.

decision_engine/classifier.py
Purpose

Query type routing.

Task

Determines if query is:

factual lookup
compliance chain
deadline risk
action recommendation
policy interpretation
uncertain
Why

This controls retrieval and validation behavior.

decision_engine/retriever.py
Purpose

Retrieval orchestration.

Task
query vector store
query relationship registry when needed
package evidence bundle
return source context to generator
Why

Keeps retrieval logic separate from generation logic.

decision_engine/generator.py
Purpose

LLM decision generation.

Task
build system + user prompt
inject context bundle
request structured response
parse result into DecisionObject
Why

This is where the assistant produces a decision, not just prose.

decision_engine/validator.py
Purpose

Central validation pass.

Task
verify cited sections exist
compare citations to retrieved evidence
apply freshness results
score confidence
add warnings
decide whether human review is required
Why

This is the trust layer.

decision_engine/citations.py
Purpose

Citation-specific checks.

Task
extract citations from decision
verify sections exist in KB
verify cited text is supported by retrieved chunks
return confidence and status
Why

This directly closes one of your biggest gaps.

decision_engine/freshness.py
Purpose

Freshness checks.

Task
check whether relevant sources are current/stale
attach warning if source changed recently
downgrade confidence if stale
mark for admin action
Why

This directly closes the static-knowledge problem.

decision_engine/executor.py
Purpose

Controlled action hooks.

Task

Depending on decision:

create alert
create suspense item
draft follow-up email
write Datadog audit log
queue escalation task
Why

This moves the assistant from advisor toward operator.

decision_engine/outcomes.py
Purpose

Outcome lifecycle support.

Task
create pending outcome record
compute follow-up date
close decision after feedback
score accuracy
Why

Without this, there is no real learning loop.

decision_engine/relationship_store.py
Purpose

Lightweight chain reasoning layer.

Task
query Postgres relationship tables
find next actions
find downstream obligations
support simple multi-hop chains
Why

This gives you graph-like value before full Neo4j.

decision_engine/prompts.py
Purpose

Prompt contracts.

Task

Stores prompt templates for:

query classification fallback
decision generation
uncertainty handling
action extraction
compliance-chain response formatting
Why

Prompts are architecture. They need version control and consistency.

decision_engine/serializers.py
Purpose

UI-friendly transformation.

Task

Convert internal DecisionObject into:

frontend response shape
human-readable summary
compact list of actions
warning banners
decision_engine/scoring.py
Purpose

Confidence and accuracy scoring.

Task
combine citation score
combine freshness score
combine retrieval relevance
combine later outcome signals
Why

Lets you move from “model guessed” to “system scored.”

Data access files
data_access/db.py
Purpose

DB connection/session management.

data_access/chunk_repo.py
Purpose

Knowledge chunk retrieval.

Task
fetch chunks by IDs
search by section
support citation verification lookups
data_access/decision_repo.py
Purpose

Decision persistence.

Task
create decision
list decisions
fetch by decision ID
mark reviewed
data_access/outcome_repo.py
Purpose

Outcome storage.

Task
create pending outcome
store user feedback
calculate closure stats
data_access/freshness_repo.py
Purpose

Freshness record storage.

Task
store hashes
update status
fetch stale items
create knowledge warnings
data_access/relationship_repo.py
Purpose

Relationship registry queries.

Task
fetch downstream actions
fetch related regulations
fetch deadlines and responsible parties
data_access/alert_repo.py
Purpose

Alert creation and lookup.

Task
create alert from decision
create suspense items
resolve linked alert records
Integration files
integrations/anthropic_client.py
Purpose

Claude wrapper.

Task
model config
retries
timeout handling
response parsing
integrations/openai_client.py
Purpose

Embeddings wrapper.

Task
embedding generation
future optional classification / extraction support
integrations/datadog_client.py
Purpose

Observability wrapper.

Task
decision events
citation verification events
follow-up delivery events
confidence distribution
integrations/email_client.py
Purpose

Email/follow-up sender.

Task
send outcome follow-up
send admin stale knowledge alerts
send escalation notices
integrations/task_queue.py
Purpose

Background job scheduling abstraction.

Task
schedule follow-up
queue freshness check
queue audits
Job files
jobs/knowledge_freshness_job.py
Purpose

Scheduled source monitoring.

Task
fetch CFR sources
compare hash/version
mark stale if changed
notify admin

This is directly aligned with the freshness-monitoring gap already documented.

jobs/followup_scheduler_job.py
Purpose

Decision follow-up sender.

Task
find due follow-ups
send emails
mark follow-up sent
retry failures
jobs/citation_audit_job.py
Purpose

Ongoing QA.

Task
sample recent decisions
re-run citation checks
find drift or bad prompt behavior
report failure rate
Schema files
schemas/decisions.py
Purpose

External API request/response models for decisions.

schemas/outcomes.py
Purpose

External API schemas for outcome reporting.

schemas/alerts.py
Purpose

External API schemas for alert creation/display.

schemas/admin.py
Purpose

Admin response models for freshness and audit views.

5. Database Schema
A. Decisions table
CREATE TABLE decisions (
  decision_id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  user_id UUID,
  query_text TEXT NOT NULL,
  query_type VARCHAR(50) NOT NULL,
  direct_answer TEXT NOT NULL,
  risk_level VARCHAR(20) NOT NULL,
  confidence NUMERIC(4,3) NOT NULL,
  knowledge_freshness VARCHAR(20) DEFAULT 'unknown',
  requires_human_review BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Purpose

Main decision record.

B. Decision actions table
CREATE TABLE decision_actions (
  id UUID PRIMARY KEY,
  decision_id UUID NOT NULL REFERENCES decisions(decision_id) ON DELETE CASCADE,
  action_id VARCHAR(100) NOT NULL,
  description TEXT NOT NULL,
  deadline_text TEXT,
  responsible_party TEXT,
  citation_section VARCHAR(50),
  priority VARCHAR(20) DEFAULT 'medium',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Purpose

Stores recommended actions separately so they can be tracked and operationalized.

C. Decision warnings table
CREATE TABLE decision_warnings (
  id UUID PRIMARY KEY,
  decision_id UUID NOT NULL REFERENCES decisions(decision_id) ON DELETE CASCADE,
  warning_type VARCHAR(50) NOT NULL,
  warning_message TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Purpose

Captures trust warnings like stale knowledge or unverifiable citation.

D. Citation checks table
CREATE TABLE decision_citations (
  id UUID PRIMARY KEY,
  decision_id UUID NOT NULL REFERENCES decisions(decision_id) ON DELETE CASCADE,
  section VARCHAR(50) NOT NULL,
  status VARCHAR(20) NOT NULL, -- verified, unverified, missing
  confidence NUMERIC(4,3) NOT NULL,
  source_file VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Purpose

Creates an audit trail for citation validity.

E. Outcomes table
CREATE TABLE decision_outcomes (
  id UUID PRIMARY KEY,
  decision_id UUID NOT NULL REFERENCES decisions(decision_id) ON DELETE CASCADE,
  tenant_id UUID NOT NULL,
  user_id UUID,
  followup_scheduled_at TIMESTAMP,
  followup_sent_at TIMESTAMP,
  outcome_status VARCHAR(20), -- success, failure, partial, unknown
  outcome_details TEXT,
  prediction_accuracy NUMERIC(4,3),
  closed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
Purpose

This is your closed-loop learning table.

F. Knowledge freshness table

This follows the direction already identified in your document.

CREATE TABLE knowledge_freshness (
  source_id VARCHAR(100) PRIMARY KEY,
  source_url TEXT,
  source_hash VARCHAR(128) NOT NULL,
  status VARCHAR(20) DEFAULT 'current', -- current, stale, deprecated
  last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_changed TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
G. Knowledge warnings table
CREATE TABLE knowledge_warnings (
  id UUID PRIMARY KEY,
  source_id VARCHAR(100) NOT NULL REFERENCES knowledge_freshness(source_id),
  message TEXT NOT NULL,
  severity VARCHAR(20) DEFAULT 'warning',
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
H. Relationship registry tables

This is the “graph later, but not yet Neo4j” layer.

regulation_nodes
CREATE TABLE regulation_nodes (
  id UUID PRIMARY KEY,
  section_id VARCHAR(50) UNIQUE NOT NULL,
  title TEXT NOT NULL,
  category TEXT,
  summary TEXT,
  part VARCHAR(50),
  last_reviewed_at TIMESTAMP,
  freshness_status VARCHAR(20) DEFAULT 'current',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
compliance_actions
CREATE TABLE compliance_actions (
  id UUID PRIMARY KEY,
  action_key VARCHAR(100) UNIQUE NOT NULL,
  description TEXT NOT NULL,
  default_deadline_text TEXT,
  responsible_party TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
regulation_action_edges
CREATE TABLE regulation_action_edges (
  id UUID PRIMARY KEY,
  regulation_id UUID NOT NULL REFERENCES regulation_nodes(id) ON DELETE CASCADE,
  action_id UUID NOT NULL REFERENCES compliance_actions(id) ON DELETE CASCADE,
  edge_type VARCHAR(50) NOT NULL, -- REQUIRES, TRIGGERS, LEADS_TO
  condition_text TEXT,
  citation_section VARCHAR(50),
  confidence NUMERIC(4,3) DEFAULT 1.000,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
action_action_edges
CREATE TABLE action_action_edges (
  id UUID PRIMARY KEY,
  from_action_id UUID NOT NULL REFERENCES compliance_actions(id) ON DELETE CASCADE,
  to_action_id UUID NOT NULL REFERENCES compliance_actions(id) ON DELETE CASCADE,
  edge_type VARCHAR(50) NOT NULL,
  condition_text TEXT,
  confidence NUMERIC(4,3) DEFAULT 1.000,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
6. API Routes
POST /api/chat
Purpose

Main the assistant endpoint.

Request
{
  "tenant_id": "uuid",
  "user_id": "uuid",
  "message": "What happens if a driver fails a random drug test?"
}
Response
{
  "decision_id": "uuid",
  "direct_answer": "If a driver fails a random drug test, remove the driver from safety-sensitive duty immediately...",
  "risk_level": "high",
  "confidence": 0.91,
  "requires_human_review": false,
  "recommended_actions": [],
  "warnings": [],
  "citations": []
}
Task
calls Decision Engine
returns user-safe response object
GET /api/decisions/{decision_id}
Purpose

Fetch a prior decision with all linked actions, warnings, citations, and outcome state.

GET /api/decisions
Purpose

List recent decisions for tenant/admin review.

Filters
by status
by risk level
by requires_human_review
by date
POST /api/outcomes/{decision_id}
Purpose

Close the loop.

Request
{
  "outcome_status": "success",
  "outcome_details": "Driver was removed immediately and report filed on time."
}
Task
stores actual outcome
calculates prediction accuracy
closes outcome loop
POST /api/alerts/from-decision/{decision_id}
Purpose

Manually or automatically create operational alert from a decision.

GET /api/admin/knowledge/freshness
Purpose

List source freshness status.

POST /api/admin/knowledge/recheck
Purpose

Trigger freshness recheck for selected source.

GET /api/admin/citation-audit
Purpose

Show recent citation failures, warning counts, and trends.

7. Prompt Contracts

This is important. Prompts should not live as random inline strings. They should be versioned contracts.

A. Decision Generation Prompt
File

decision_engine/prompts.py

Purpose

Generate a structured decision object.

Contract
must only use provided context
must not invent citations
must reduce confidence when context is incomplete
must mark human review when uncertain
Template
SYSTEM:
You are Decision Engine Assistant, a DOT compliance decision assistant.

Your job is to return a structured decision object, not freeform advice.
Use only the supplied evidence.
Do not invent citations.
If evidence is incomplete, lower confidence and require human review.

Return:
- direct_answer
- risk_level
- recommended_actions
- cited_sections
- confidence
- requires_human_review
- warning_messages
Why it exists

Prevents prompt drift and enforces system behavior.

B. Uncertainty Prompt Contract
Purpose

Force conservative behavior.

Rules
if citation not found, say so
if freshness stale, warn
if context incomplete, require review
never overstate certainty
C. Action Extraction Prompt Contract
Purpose

Extract structured actions from retrieved compliance text.

Output
action description
deadline
responsible party
citation
priority
D. Relationship Extraction Prompt Contract

For later use in Postgres relationship registry.

Purpose

Extract:

regulation node
compliance actions
edge type
condition text

This is borrowed conceptually from your graph-extraction direction, but applied first to a simpler relationship store.

8. How the full flow works
End-to-end flow
1. User asks question
2. chat.py calls decision_engine.service
3. classifier identifies query type
4. retriever gets vector results
5. if needed, relationship_store adds downstream chain actions
6. generator builds DecisionObject
7. validator verifies citations + freshness
8. executor writes alerts/suspense/audit hooks
9. outcomes module creates pending follow-up
10. response returned to UI
9. What goes where and why
FastAPI route layer

Handles HTTP only.

Decision engine layer

Handles business logic and orchestration.

Data access layer

Handles DB reads/writes only.

Integrations layer

Handles external providers only.

Jobs layer

Handles scheduled or asynchronous system work.

Prompt contracts

Handle repeatable LLM behavior.

That separation matters because once you start mixing these together, the system becomes hard to debug and dangerous to trust.

10. Rollout plan
Phase 1 — foundation

Build first:

models.py
service.py
generator.py
validator.py
citations.py
freshness.py
decision_repo.py
outcome_repo.py
POST /api/chat
POST /api/outcomes/{decision_id}
Goal

Decisions become structured, validated, and tracked.

Phase 2 — trust and operations

Add:

executor.py
alerts.py
knowledge_freshness_job.py
followup_scheduler_job.py
admin routes
Goal

Decisions start triggering controlled system actions.

Phase 3 — relationship registry

Add:

relationship_store.py
relationship_repo.py
relationship tables
extraction job for regulation/action edges
Goal

Get chain reasoning without full graph infra.

Phase 4 — optional graph later

Only after data proves need.

Trigger for Neo4j:

Postgres traversal gets ugly
relationship count grows fast
deeper multi-hop reasoning clearly improves outcomes

That aligns with the spirit of your graph architecture, but defers the infrastructure jump until you have evidence.

11. What success looks like
After Decision Engine, before graph

You should be able to say:

every the assistant answer is a typed decision
every citation is checked
stale knowledge is flagged
every important decision is logged
follow-up outcomes are tracked
you can measure prediction accuracy

That alone is a major jump from “AI assistant” to “decision system.”

12. My blunt build order

If I were sequencing your next work week, I would do it in this order:

Week 1
decision schema
chat endpoint wired to Decision Engine
citation verification
knowledge freshness table + job
Week 2
outcome tracking
decision review endpoint
execution hooks for alerts/suspense
Week 3
relationship registry tables
action extraction prompt
first compliance chain support from Postgres
Week 4
evaluate if graph is still needed yet
Bottom line

Your next real milestone is not “Graph RAG completed.”

It is:

“the assistant can make validated decisions, trigger controlled action, and learn from outcomes.”

That is the right architecture move for this system. It directly addresses the critical gaps already identified in your own assessment, while preserving the option to add graph reasoning later if the data proves it.

------------


📦 File: backend/app/decision_engine/models.py

This file defines:

Decision object (core unit)
Actions (what to do)
Citations (what supports it)
Freshness + warnings (trust layer)
Outcome tracking (feedback loop)
✅ Full Starter Code (Copy/Paste Ready)
"""
Decision Engine Models

These models define the core contract for:
- Decision generation
- Validation
- Execution
- Outcome tracking

All responses from the LLM must conform to these models.
"""

from pydantic import BaseModel, Field, UUID4
from typing import List, Optional, Literal
from datetime import datetime


# =========================
# ENUM TYPES
# =========================

RiskLevel = Literal["low", "medium", "high", "critical"]

QueryType = Literal[
    "factual_lookup",
    "compliance_chain",
    "deadline_risk",
    "action_recommendation",
    "policy_interpretation",
    "uncertain"
]

CitationStatus = Literal["verified", "unverified", "missing"]

FreshnessStatus = Literal["current", "stale", "unknown"]

OutcomeStatus = Literal["success", "failure", "partial", "unknown"]


# =========================
# CITATION MODEL
# =========================

class CitationCheck(BaseModel):
    """
    Represents validation status of a CFR citation.
    """
    section: str = Field(..., description="CFR section reference (e.g., § 382.211)")
    status: CitationStatus
    confidence: float = Field(..., ge=0.0, le=1.0)
    source_file: Optional[str] = None


# =========================
# ACTION MODEL
# =========================

class RecommendedAction(BaseModel):
    """
    Action extracted from compliance logic.
    """
    action_id: str = Field(..., description="Unique action key")
    description: str

    deadline: Optional[str] = Field(
        None,
        description="Human-readable deadline (e.g., 'within 2 business days')"
    )

    responsible_party: Optional[str] = Field(
        None,
        description="Who is responsible (Employer, Driver, MRO)"
    )

    citation: Optional[str] = Field(
        None,
        description="Supporting CFR section"
    )

    priority: Literal["low", "medium", "high", "critical"] = "medium"


# =========================
# WARNING MODEL
# =========================

class DecisionWarning(BaseModel):
    """
    Warning attached to a decision.
    """
    warning_type: Literal[
        "citation_issue",
        "stale_knowledge",
        "low_confidence",
        "incomplete_context"
    ]

    message: str


# =========================
# DECISION MODEL (CORE)
# =========================

class DecisionObject(BaseModel):
    """
    Core Decision Engine output.

    This replaces freeform AI responses.
    """

    decision_id: str

    query_type: QueryType

    direct_answer: str = Field(
        ...,
        description="Human-readable answer for UI display"
    )

    risk_level: RiskLevel

    recommended_actions: List[RecommendedAction] = []

    citations: List[CitationCheck] = []

    confidence: float = Field(..., ge=0.0, le=1.0)

    knowledge_freshness: FreshnessStatus = "unknown"

    requires_human_review: bool = False

    warning_messages: List[str] = []

    created_at: datetime


# =========================
# OUTCOME TRACKING MODEL
# =========================

class DecisionOutcome(BaseModel):
    """
    Tracks what happened after a decision.
    """

    decision_id: str
    tenant_id: UUID4

    user_id: Optional[UUID4] = None

    outcome_status: Optional[OutcomeStatus] = None

    outcome_details: Optional[str] = None

    prediction_accuracy: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="System-calculated accuracy score"
    )

    followup_scheduled_at: Optional[datetime] = None
    followup_sent_at: Optional[datetime] = None

    closed_at: Optional[datetime] = None

    created_at: datetime


# =========================
# CONTEXT BUNDLE MODEL
# =========================

class ContextBundle(BaseModel):
    """
    Unified retrieval output passed to generator + validator.
    """

    vector_results: List[dict] = []
    relationship_results: List[dict] = []

    freshness: FreshnessStatus = "unknown"

    metadata: Optional[dict] = None


# =========================
# API RESPONSE MODEL
# =========================

class DecisionResponse(BaseModel):
    """
    What the frontend receives.
    """

    decision_id: str

    answer: str

    risk_level: RiskLevel

    confidence: float

    requires_human_review: bool

    actions: List[RecommendedAction]

    warnings: List[str]

    citations: List[CitationCheck]
🧠 Why These Models Matter
1. This replaces “AI responses”

Instead of:

"Hey here's what you should do..."

You now have:

DecisionObject

That means:

machine-readable
auditable
enforceable
trackable
2. This enables validation

Because now you can:

verify citations
downgrade confidence
attach warnings
block unsafe responses
3. This enables execution

Because now you can:

loop over recommended_actions
trigger alerts
create tasks
schedule follow-ups
4. This enables learning

Because now you can connect:

Decision → Outcome → Accuracy

That’s your moat.

⚠️ Important Rules (Do Not Break These)
Rule 1: LLM MUST output this structure

Never allow freeform responses in production path.

Rule 2: Confidence is system-owned

LLM can suggest, but validator adjusts.

Rule 3: Empty actions is allowed

Not every query produces actions.

Rule 4: requires_human_review is critical

Use it aggressively when:

confidence < threshold
citations fail
freshness = stale
🔧 Next Step (Recommended)

Next file you should build:

👉 generator.py

That will:

call Claude
enforce structured output
map response → DecisionObject

Then after that:

👉 validator.py

That’s where this becomes powerful.

------

1. backend/app/decision_engine/generator.py
What this file does

This is the LLM generation layer.

It:

builds the prompt
sends evidence into the model
asks for structured JSON only
parses into DecisionObject
fails safely if parsing breaks
Where it fits
retriever.py
   ↓
generator.py
   ↓
validator.py
Starter code
"""
Decision Engine Generator

Purpose:
- Build the prompt for the LLM
- Require structured JSON output
- Parse the response into a DecisionObject
- Fail safely when parsing or model output is invalid
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import ValidationError

from app.decision_engine.models import DecisionObject, ContextBundle
from app.decision_engine.prompts import build_decision_prompt
from app.integrations.anthropic_client import get_anthropic_client

logger = logging.getLogger(__name__)


def _json_schema_hint() -> Dict[str, Any]:
    """
    Minimal schema contract sent to the LLM.

    Keep this stable.
    Change deliberately and version it if needed later.
    """
    return {
        "decision_id": "string",
        "query_type": "factual_lookup | compliance_chain | deadline_risk | action_recommendation | policy_interpretation | uncertain",
        "direct_answer": "string",
        "risk_level": "low | medium | high | critical",
        "recommended_actions": [
            {
                "action_id": "string",
                "description": "string",
                "deadline": "string or null",
                "responsible_party": "string or null",
                "citation": "string or null",
                "priority": "low | medium | high | critical",
            }
        ],
        "citations": [
            {
                "section": "string",
                "status": "verified | unverified | missing",
                "confidence": "float 0..1",
                "source_file": "string or null",
            }
        ],
        "confidence": "float 0..1",
        "knowledge_freshness": "current | stale | unknown",
        "requires_human_review": "boolean",
        "warning_messages": ["string"],
        "created_at": "ISO-8601 datetime string",
    }


def _safe_context_to_text(context_bundle: ContextBundle) -> str:
    """
    Convert context bundle into compact prompt text.

    Keep the structure explicit so the model can separate:
    - vector evidence
    - relationship evidence
    - freshness metadata
    """
    parts = []

    parts.append("VECTOR_RESULTS:")
    if context_bundle.vector_results:
        for idx, item in enumerate(context_bundle.vector_results, start=1):
            parts.append(
                f"{idx}. section={item.get('section')} "
                f"score={item.get('score')} "
                f"source_file={item.get('source_file')} "
                f"text={item.get('text')}"
            )
    else:
        parts.append("None")

    parts.append("\nRELATIONSHIP_RESULTS:")
    if context_bundle.relationship_results:
        for idx, item in enumerate(context_bundle.relationship_results, start=1):
            parts.append(f"{idx}. {json.dumps(item, default=str)}")
    else:
        parts.append("None")

    parts.append(f"\nFRESHNESS_STATUS: {context_bundle.freshness}")

    if context_bundle.metadata:
        parts.append(f"\nMETADATA: {json.dumps(context_bundle.metadata, default=str)}")

    return "\n".join(parts)


def _extract_json_block(raw_text: str) -> str:
    """
    Extract JSON from model output.

    Handles:
    - plain JSON
    - fenced ```json blocks
    """
    text = raw_text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()

    return text


def _fallback_decision(
    *,
    decision_id: str,
    query_type: str,
    reason: str,
) -> DecisionObject:
    """
    Safe fallback when the model output is invalid.
    """
    return DecisionObject(
        decision_id=decision_id,
        query_type=query_type,
        direct_answer=(
            "I could not produce a fully validated compliance decision from the "
            "available evidence. Human review is required before acting."
        ),
        risk_level="medium",
        recommended_actions=[],
        citations=[],
        confidence=0.25,
        knowledge_freshness="unknown",
        requires_human_review=True,
        warning_messages=[reason],
        created_at=datetime.now(timezone.utc),
    )


async def generate_decision_object(
    *,
    query: str,
    query_type: str,
    decision_id: str,
    context_bundle: ContextBundle,
    model_name: str = "claude-sonnet-4-20250514",
) -> DecisionObject:
    """
    Generate a structured decision object from the LLM.

    Flow:
    1. Build system + user prompt
    2. Call model
    3. Extract JSON
    4. Parse into DecisionObject
    5. Return safe fallback if anything fails
    """
    client = get_anthropic_client()

    prompt_payload = build_decision_prompt(
        query=query,
        query_type=query_type,
        decision_id=decision_id,
        schema_hint=_json_schema_hint(),
        context_text=_safe_context_to_text(context_bundle),
    )

    try:
        response = await client.messages.create(
            model=model_name,
            max_tokens=1800,
            temperature=0,
            system=prompt_payload["system"],
            messages=[
                {
                    "role": "user",
                    "content": prompt_payload["user"],
                }
            ],
        )

        raw_text = response.content[0].text
        json_text = _extract_json_block(raw_text)
        parsed = json.loads(json_text)

        # Enforce server-owned fields
        parsed["decision_id"] = decision_id
        parsed["query_type"] = query_type
        parsed["created_at"] = datetime.now(timezone.utc).isoformat()

        decision = DecisionObject.model_validate(parsed)
        return decision

    except json.JSONDecodeError as exc:
        logger.exception("Decision generator returned invalid JSON: %s", exc)
        return _fallback_decision(
            decision_id=decision_id,
            query_type=query_type,
            reason="Model response was not valid JSON.",
        )

    except ValidationError as exc:
        logger.exception("Decision generator returned schema-invalid output: %s", exc)
        return _fallback_decision(
            decision_id=decision_id,
            query_type=query_type,
            reason="Model response did not match DecisionObject schema.",
        )

    except Exception as exc:
        logger.exception("Decision generator failed: %s", exc)
        return _fallback_decision(
            decision_id=decision_id,
            query_type=query_type,
            reason="Decision generation failed unexpectedly.",
        )
2. backend/app/decision_engine/validator.py
What this file does

This is the trust layer.

It:

verifies citations
checks freshness
downgrades confidence
adds warning banners
decides if human review is required
Where it fits
generator.py
   ↓
validator.py
   ↓
executor.py / outcomes.py / response
Starter code
"""
Decision Engine Validator

Purpose:
- Verify citations against retrieved evidence
- Apply freshness checks
- Adjust confidence
- Require human review when trust conditions fail
"""

from __future__ import annotations

import logging
from typing import List, Tuple

from app.decision_engine.models import (
    CitationCheck,
    ContextBundle,
    DecisionObject,
)

logger = logging.getLogger(__name__)

MIN_CONFIDENCE_FOR_AUTO_TRUST = 0.70
MAX_CONFIDENCE_IF_STALE = 0.60
MAX_CONFIDENCE_IF_UNVERIFIED_CITATIONS = 0.65


def _normalize_section(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.strip().split()).lower()


async def verify_citations(
    *,
    decision: DecisionObject,
    context_bundle: ContextBundle,
    tenant_id: str,
) -> List[CitationCheck]:
    """
    Verify citations only against retrieved vector evidence for now.

    Later upgrade path:
    - check against authoritative knowledge_chunks
    - check section existence in full KB
    - check semantic match of cited claim
    """
    verified_results: List[CitationCheck] = []

    evidence_sections = {
        _normalize_section(item.get("section")): item
        for item in context_bundle.vector_results
        if item.get("section")
    }

    for citation in decision.citations:
        normalized = _normalize_section(citation.section)

        if normalized in evidence_sections:
            evidence = evidence_sections[normalized]
            score = evidence.get("score", 0.85)
            verified_results.append(
                CitationCheck(
                    section=citation.section,
                    status="verified",
                    confidence=float(min(max(score, 0.0), 1.0)),
                    source_file=evidence.get("source_file"),
                )
            )
        else:
            verified_results.append(
                CitationCheck(
                    section=citation.section,
                    status="unverified",
                    confidence=0.0,
                    source_file=None,
                )
            )

    return verified_results


async def evaluate_freshness(context_bundle: ContextBundle) -> Tuple[str, List[str]]:
    """
    Evaluate freshness from retrieval metadata.

    Current behavior:
    - use context_bundle.freshness directly
    - later can expand to source-by-source checks from knowledge_freshness table
    """
    warnings: List[str] = []
    freshness = context_bundle.freshness

    if freshness == "stale":
        warnings.append(
            "Relevant knowledge may be stale. Confirm the latest regulation before acting."
        )
    elif freshness == "unknown":
        warnings.append(
            "Knowledge freshness could not be confirmed from the current evidence."
        )

    return freshness, warnings


def _apply_citation_penalties(decision: DecisionObject) -> None:
    unverified = [c for c in decision.citations if c.status != "verified"]

    if unverified:
        decision.warning_messages.append(
            "Some citations could not be fully verified against retrieved evidence."
        )
        decision.confidence = min(decision.confidence, MAX_CONFIDENCE_IF_UNVERIFIED_CITATIONS)


def _apply_freshness_penalties(decision: DecisionObject) -> None:
    if decision.knowledge_freshness == "stale":
        decision.confidence = min(decision.confidence, MAX_CONFIDENCE_IF_STALE)
    elif decision.knowledge_freshness == "unknown":
        decision.confidence = min(decision.confidence, 0.75)


def _apply_review_rules(decision: DecisionObject) -> None:
    """
    Conservative review rules.
    """
    has_unverified = any(c.status != "verified" for c in decision.citations)

    if has_unverified:
        decision.requires_human_review = True

    if decision.knowledge_freshness == "stale":
        decision.requires_human_review = True

    if decision.confidence < MIN_CONFIDENCE_FOR_AUTO_TRUST:
        decision.requires_human_review = True

    if decision.query_type == "uncertain":
        decision.requires_human_review = True


async def validate_decision_object(
    *,
    decision: DecisionObject,
    context_bundle: ContextBundle,
    tenant_id: str,
) -> DecisionObject:
    """
    Main validator entrypoint.
    """
    try:
        decision.citations = await verify_citations(
            decision=decision,
            context_bundle=context_bundle,
            tenant_id=tenant_id,
        )

        freshness_status, freshness_warnings = await evaluate_freshness(context_bundle)
        decision.knowledge_freshness = freshness_status

        for warning in freshness_warnings:
            if warning not in decision.warning_messages:
                decision.warning_messages.append(warning)

        _apply_citation_penalties(decision)
        _apply_freshness_penalties(decision)
        _apply_review_rules(decision)

        return decision

    except Exception as exc:
        logger.exception("Decision validation failed: %s", exc)

        decision.warning_messages.append(
            "Validation failed unexpectedly. Human review is required."
        )
        decision.confidence = min(decision.confidence, 0.30)
        decision.requires_human_review = True
        return decision
3. backend/app/api/routes/chat.py
What this file does

This is the HTTP entry point.

It:

receives user query
classifies it
retrieves evidence
generates decision
validates decision
returns frontend-safe response
Where it fits
UI
 ↓
/api/chat
 ↓
Decision Engine flow
 ↓
validated decision response
Starter code
"""
Chat Route

Purpose:
- Main API entrypoint for Decision Engine Assistant
- Orchestrates classification, retrieval, generation, validation
- Returns structured response to frontend
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, UUID4

from app.decision_engine.classifier import classify_query
from app.decision_engine.generator import generate_decision_object
from app.decision_engine.models import ContextBundle, DecisionResponse
from app.decision_engine.retriever import retrieve_context
from app.decision_engine.validator import validate_decision_object

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    tenant_id: UUID4
    user_id: UUID4 | None = None
    message: str = Field(..., min_length=3, max_length=10000)


def _compute_followup_date(risk_level: str) -> datetime:
    now = datetime.now(timezone.utc)

    if risk_level == "critical":
        return now + timedelta(days=1)
    if risk_level == "high":
        return now + timedelta(days=3)
    if risk_level == "medium":
        return now + timedelta(days=7)
    return now + timedelta(days=14)


async def _create_outcome_stub(
    *,
    decision_id: str,
    tenant_id: str,
    user_id: str | None,
    risk_level: str,
) -> None:
    """
    Placeholder for outcomes integration.

    Replace this later with:
    - outcome_repo.create_pending(...)
    - background follow-up scheduling
    """
    _ = {
        "decision_id": decision_id,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "followup_scheduled_at": _compute_followup_date(risk_level),
    }


@router.post("", response_model=DecisionResponse)
async def chat(request: ChatRequest) -> DecisionResponse:
    """
    Main Decision Engine flow.

    1. classify query
    2. retrieve evidence
    3. generate structured decision
    4. validate decision
    5. schedule follow-up stub
    6. return response
    """
    try:
        decision_id = f"dec_{uuid4().hex}"
        query_type = classify_query(request.message)

        context_bundle: ContextBundle = await retrieve_context(
            query=request.message,
            query_type=query_type,
            tenant_id=str(request.tenant_id),
        )

        decision = await generate_decision_object(
            query=request.message,
            query_type=query_type,
            decision_id=decision_id,
            context_bundle=context_bundle,
        )

        validated = await validate_decision_object(
            decision=decision,
            context_bundle=context_bundle,
            tenant_id=str(request.tenant_id),
        )

        await _create_outcome_stub(
            decision_id=validated.decision_id,
            tenant_id=str(request.tenant_id),
            user_id=str(request.user_id) if request.user_id else None,
            risk_level=validated.risk_level,
        )

        return DecisionResponse(
            decision_id=validated.decision_id,
            answer=validated.direct_answer,
            risk_level=validated.risk_level,
            confidence=validated.confidence,
            requires_human_review=validated.requires_human_review,
            actions=validated.recommended_actions,
            warnings=validated.warning_messages,
            citations=validated.citations,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Decision Engine chat flow failed: {exc}"
        ) from exc
4. You also need this small prompt helper

Because generator.py references it, here is the starter file too.

backend/app/decision_engine/prompts.py
"""
Prompt builders for the Decision Engine.
"""

from __future__ import annotations

import json
from typing import Any, Dict


def build_decision_prompt(
    *,
    query: str,
    query_type: str,
    decision_id: str,
    schema_hint: Dict[str, Any],
    context_text: str,
) -> Dict[str, str]:
    system = (
        "You are Decision Engine Assistant, a DOT compliance decision assistant.\n"
        "Return only valid JSON.\n"
        "Do not use markdown.\n"
        "Do not invent citations.\n"
        "Use only the supplied evidence.\n"
        "If evidence is incomplete, lower confidence and require human review.\n"
        "Recommended actions must be explicit, short, and operational.\n"
    )

    user = (
        f"DECISION_ID: {decision_id}\n"
        f"QUERY_TYPE: {query_type}\n"
        f"USER_QUERY: {query}\n\n"
        f"JSON_SCHEMA_HINT:\n{json.dumps(schema_hint, indent=2)}\n\n"
        f"EVIDENCE:\n{context_text}\n\n"
        "Return one JSON object only."
    )

    return {"system": system, "user": user}
5. You need a retriever stub too

Because chat.py calls retrieve_context().

backend/app/decision_engine/retriever.py
"""
Retriever stub for Decision Engine.

Replace these stubs with real FAISS + Postgres integration next.
"""

from __future__ import annotations

from app.decision_engine.models import ContextBundle


async def retrieve_context(*, query: str, query_type: str, tenant_id: str) -> ContextBundle:
    """
    Temporary stub.

    Replace with:
    - vector retrieval from FAISS/Neon
    - optional relationship retrieval from Postgres registry
    - freshness lookup from knowledge_freshness table
    """
    vector_results = [
        {
            "section": "§ 382.211",
            "score": 0.93,
            "source_file": "CFR_Title49_Part382.md",
            "text": (
                "Employers must remove drivers from safety-sensitive duty after a "
                "verified positive drug test result."
            ),
        },
        {
            "section": "§ 382.705",
            "score": 0.88,
            "source_file": "CFR_Title49_Part382.md",
            "text": (
                "Employers must report certain drug and alcohol program violations "
                "to the Clearinghouse within required timeframes."
            ),
        },
    ]

    relationship_results = []
    if query_type in {"compliance_chain", "action_recommendation", "deadline_risk"}:
        relationship_results = [
            {
                "from": "§ 382.211",
                "edge_type": "REQUIRES",
                "to_action": "remove_driver",
                "description": "Remove driver from safety-sensitive duty immediately",
            },
            {
                "from_action": "remove_driver",
                "edge_type": "LEADS_TO",
                "to_action": "file_clearinghouse_report",
                "description": "Report violation to Clearinghouse within required deadline",
            },
        ]

    return ContextBundle(
        vector_results=vector_results,
        relationship_results=relationship_results,
        freshness="current",
        metadata={"tenant_id": tenant_id},
    )
6. And a classifier stub if you have not created it yet
backend/app/decision_engine/classifier.py
"""
Simple rule-based classifier for Decision Engine.
"""

from __future__ import annotations

import re


GRAPH_LIKE_PATTERNS = [
    r"what happens if",
    r"what do i need to do",
    r"what else is required",
    r"full compliance chain",
    r"steps after",
    r"downstream",
    r"trigger",
]

FACT_PATTERNS = [
    r"what does §",
    r"what does section",
    r"exact text",
    r"definition of",
    r"quote",
]

DEADLINE_PATTERNS = [
    r"when is .* due",
    r"deadline",
    r"expires",
    r"how long do i have",
]


def classify_query(query: str) -> str:
    q = query.lower()

    if any(re.search(p, q) for p in DEADLINE_PATTERNS):
        return "deadline_risk"

    if any(re.search(p, q) for p in FACT_PATTERNS):
        return "factual_lookup"

    if any(re.search(p, q) for p in GRAPH_LIKE_PATTERNS):
        return "compliance_chain"

    return "action_recommendation"
7. Anthropic client stub
backend/app/integrations/anthropic_client.py
"""
Anthropic client wrapper.

Replace env handling with your config module.
"""

from __future__ import annotations

import os
from anthropic import AsyncAnthropic


def get_anthropic_client() -> AsyncAnthropic:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    return AsyncAnthropic(api_key=api_key)
8. How these files work together
End-to-end flow
chat.py
  receives request
    ↓
classifier.py
  decides query type
    ↓
retriever.py
  gets evidence bundle
    ↓
generator.py
  asks model for structured DecisionObject
    ↓
validator.py
  verifies citations + freshness + review rules
    ↓
chat.py
  returns DecisionResponse
9. What to build immediately after this

Now that you have the 3 core files, the best next step is:

Next 3 files
outcomes.py
executor.py
schemas/decisions.py

Because that gets you:

follow-up loop
action hooks
cleaner external API models
10. One important correction before you wire this up

In your current models.py, you used mutable defaults like:

recommended_actions: List[RecommendedAction] = []
citations: List[CitationCheck] = []
warning_messages: List[str] = []

That works in many cases with Pydantic, but I recommend switching to default_factory=list for cleaner behavior.

Better version
from pydantic import BaseModel, Field

recommended_actions: List[RecommendedAction] = Field(default_factory=list)
citations: List[CitationCheck] = Field(default_factory=list)
warning_messages: List[str] = Field(default_factory=list)

Do the same for any list or dict fields.

11. My recommendation

Paste these in first and get the route returning a validated DecisionResponse with stub evidence.
Do not connect FAISS or full DB writes until this flow works end-to-end in memory.

That keeps the first milestone simple:

Milestone 1

“the assistant returns structured, validated decisions from a single API route.”

------

1. backend/app/decision_engine/outcomes.py
What this file does

This handles the decision feedback loop.

It:

creates a pending outcome record
computes follow-up timing
updates an outcome when the user reports what happened
calculates a basic prediction accuracy score
Why it matters

This is one of the biggest missing pieces from your earlier architecture analysis:
prediction vs reality.

Starter code
"""
Decision Engine Outcomes

Purpose:
- Create pending outcome records after decisions are generated
- Compute follow-up timing
- Record user-reported outcomes
- Score prediction accuracy

Notes:
- This starter file uses an in-memory store for now.
- Replace STORE usage with outcome_repo / database writes next.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from uuid import UUID, uuid4

from app.decision_engine.models import DecisionObject, DecisionOutcome

logger = logging.getLogger(__name__)

# Temporary in-memory store
# Replace with DB-backed repository later
OUTCOME_STORE: Dict[str, DecisionOutcome] = {}


def compute_followup_date(decision: DecisionObject) -> datetime:
    """
    Compute follow-up timing based on risk.

    Conservative default:
    - critical: 1 day
    - high: 3 days
    - medium: 7 days
    - low: 14 days
    """
    now = datetime.now(timezone.utc)

    if decision.risk_level == "critical":
        return now + timedelta(days=1)
    if decision.risk_level == "high":
        return now + timedelta(days=3)
    if decision.risk_level == "medium":
        return now + timedelta(days=7)
    return now + timedelta(days=14)


def _score_prediction_accuracy(
    *,
    outcome_status: Optional[str],
    decision: DecisionObject,
) -> float:
    """
    Basic starter accuracy scoring.

    Current approach:
    - success  -> strong score
    - partial  -> medium score
    - failure  -> weak score
    - unknown  -> low confidence in accuracy

    Later upgrade path:
    - compare specific recommended actions completed
    - compare deadlines met/missed
    - compare actual compliance outcomes / violations
    """
    if outcome_status == "success":
        return 0.95
    if outcome_status == "partial":
        return 0.60
    if outcome_status == "failure":
        return 0.15
    return min(decision.confidence, 0.40)


async def create_outcome_record(
    *,
    decision: DecisionObject,
    tenant_id: UUID | str,
    user_id: UUID | str | None,
) -> DecisionOutcome:
    """
    Create a pending outcome record after a decision is issued.
    """
    followup_scheduled_at = compute_followup_date(decision)

    outcome = DecisionOutcome(
        decision_id=decision.decision_id,
        tenant_id=tenant_id,
        user_id=user_id,
        outcome_status=None,
        outcome_details=None,
        prediction_accuracy=None,
        followup_scheduled_at=followup_scheduled_at,
        followup_sent_at=None,
        closed_at=None,
        created_at=datetime.now(timezone.utc),
    )

    OUTCOME_STORE[decision.decision_id] = outcome
    logger.info(
        "Created pending outcome record decision_id=%s followup=%s",
        decision.decision_id,
        followup_scheduled_at.isoformat(),
    )
    return outcome


async def get_outcome_record(decision_id: str) -> Optional[DecisionOutcome]:
    """
    Fetch outcome record by decision ID.
    """
    return OUTCOME_STORE.get(decision_id)


async def mark_followup_sent(decision_id: str) -> Optional[DecisionOutcome]:
    """
    Mark that a follow-up was sent to the user.
    """
    outcome = OUTCOME_STORE.get(decision_id)
    if not outcome:
        return None

    outcome.followup_sent_at = datetime.now(timezone.utc)
    OUTCOME_STORE[decision_id] = outcome
    return outcome


async def record_outcome_result(
    *,
    decision: DecisionObject,
    outcome_status: str,
    outcome_details: Optional[str] = None,
) -> Optional[DecisionOutcome]:
    """
    Store the actual outcome reported by the user.
    """
    existing = OUTCOME_STORE.get(decision.decision_id)
    if not existing:
        logger.warning("No outcome record found for decision_id=%s", decision.decision_id)
        return None

    accuracy = _score_prediction_accuracy(
        outcome_status=outcome_status,
        decision=decision,
    )

    existing.outcome_status = outcome_status
    existing.outcome_details = outcome_details
    existing.prediction_accuracy = accuracy
    existing.closed_at = datetime.now(timezone.utc)

    OUTCOME_STORE[decision.decision_id] = existing

    logger.info(
        "Recorded outcome decision_id=%s status=%s accuracy=%.2f",
        decision.decision_id,
        outcome_status,
        accuracy,
    )
    return existing


async def list_due_followups(now: Optional[datetime] = None) -> list[DecisionOutcome]:
    """
    Return pending outcomes that are due for follow-up.

    Current criteria:
    - followup_scheduled_at <= now
    - followup_sent_at is None
    - outcome_status is None
    """
    check_time = now or datetime.now(timezone.utc)
    due: list[DecisionOutcome] = []

    for outcome in OUTCOME_STORE.values():
        if (
            outcome.followup_scheduled_at
            and outcome.followup_scheduled_at <= check_time
            and outcome.followup_sent_at is None
            and outcome.outcome_status is None
        ):
            due.append(outcome)

    return due
2. backend/app/decision_engine/executor.py
What this file does

This is the controlled action layer.

It:

decides whether a decision should trigger an alert
decides whether to create suspense-style tasks
writes an audit event stub
keeps execution hooks contained and predictable
Why it matters

This is how you shift the assistant from:

assistant

to:

decision system with operational hooks
Starter code
"""
Decision Engine Executor

Purpose:
- Run controlled execution hooks after validation
- Create alerts for risky decisions
- Create suspense/task items from recommended actions
- Write audit events

Notes:
- This starter version uses in-memory stores.
- Replace with alert_repo, task_repo, and audit logging later.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.decision_engine.models import DecisionObject, RecommendedAction

logger = logging.getLogger(__name__)

# Temporary in-memory stores
ALERT_STORE: List[Dict[str, Any]] = []
TASK_STORE: List[Dict[str, Any]] = []
AUDIT_STORE: List[Dict[str, Any]] = []


def _should_create_alert(decision: DecisionObject) -> bool:
    """
    Decide whether this decision should trigger an alert.

    Starter logic:
    - high or critical risk
    - or requires human review
    """
    return (
        decision.risk_level in {"high", "critical"}
        or decision.requires_human_review
    )


def _alert_severity(decision: DecisionObject) -> str:
    if decision.risk_level == "critical":
        return "critical"
    if decision.risk_level == "high":
        return "high"
    if decision.requires_human_review:
        return "warning"
    return "info"


async def create_alert(
    *,
    tenant_id: UUID | str,
    decision: DecisionObject,
) -> Dict[str, Any]:
    """
    Create an alert tied to a decision.
    """
    alert = {
        "alert_id": f"alert_{uuid4().hex}",
        "tenant_id": str(tenant_id),
        "decision_id": decision.decision_id,
        "severity": _alert_severity(decision),
        "title": "Compliance decision requires attention",
        "body": decision.direct_answer,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "warnings": list(decision.warning_messages),
    }

    ALERT_STORE.append(alert)
    logger.info(
        "Created alert alert_id=%s decision_id=%s",
        alert["alert_id"],
        decision.decision_id,
    )
    return alert


def _task_payload_from_action(
    *,
    tenant_id: UUID | str,
    decision_id: str,
    action: RecommendedAction,
) -> Dict[str, Any]:
    return {
        "task_id": f"task_{uuid4().hex}",
        "tenant_id": str(tenant_id),
        "decision_id": decision_id,
        "action_id": action.action_id,
        "description": action.description,
        "deadline": action.deadline,
        "responsible_party": action.responsible_party,
        "priority": action.priority,
        "citation": action.citation,
        "status": "open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


async def create_suspense_items(
    *,
    tenant_id: UUID | str,
    decision_id: str,
    actions: List[RecommendedAction],
) -> List[Dict[str, Any]]:
    """
    Create one task/suspense record per recommended action.
    """
    created: List[Dict[str, Any]] = []

    for action in actions:
        task = _task_payload_from_action(
            tenant_id=tenant_id,
            decision_id=decision_id,
            action=action,
        )
        TASK_STORE.append(task)
        created.append(task)

    logger.info(
        "Created %d suspense items for decision_id=%s",
        len(created),
        decision_id,
    )
    return created


async def write_audit_log(
    *,
    tenant_id: UUID | str,
    user_id: UUID | str | None,
    event_type: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Write an audit event.

    Replace with Datadog / persistent audit storage later.
    """
    event = {
        "event_id": f"audit_{uuid4().hex}",
        "tenant_id": str(tenant_id),
        "user_id": str(user_id) if user_id else None,
        "event_type": event_type,
        "payload": payload,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    AUDIT_STORE.append(event)
    return event


async def run_execution_hooks(
    decision: DecisionObject,
    *,
    tenant_id: UUID | str,
    user_id: UUID | str | None,
) -> Dict[str, Any]:
    """
    Run all controlled execution hooks.

    Returns summary of what was created.
    """
    created_alert: Optional[Dict[str, Any]] = None
    created_tasks: List[Dict[str, Any]] = []

    if _should_create_alert(decision):
        created_alert = await create_alert(
            tenant_id=tenant_id,
            decision=decision,
        )

    if decision.recommended_actions:
        created_tasks = await create_suspense_items(
            tenant_id=tenant_id,
            decision_id=decision.decision_id,
            actions=decision.recommended_actions,
        )

    await write_audit_log(
        tenant_id=tenant_id,
        user_id=user_id,
        event_type="decision_generated",
        payload=decision.model_dump(),
    )

    return {
        "alert": created_alert,
        "tasks": created_tasks,
        "task_count": len(created_tasks),
    }
3. backend/app/schemas/decisions.py
What this file does

This is the external API contract layer.

It:

defines clean request/response models for routes
separates public API shape from internal decision-engine models
gives you room to evolve the internal models without breaking the frontend
Why it matters

Internal models and external API models should not be the same forever.

That separation saves pain later.

Starter code
"""
Decision API Schemas

Purpose:
- Request/response contracts for FastAPI routes
- Keep API models separate from internal decision engine models
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, Field, UUID4


RiskLevel = Literal["low", "medium", "high", "critical"]
CitationStatus = Literal["verified", "unverified", "missing"]
OutcomeStatus = Literal["success", "failure", "partial", "unknown"]


class ChatRequestSchema(BaseModel):
    tenant_id: UUID4
    user_id: Optional[UUID4] = None
    message: str = Field(..., min_length=3, max_length=10000)


class ActionSchema(BaseModel):
    action_id: str
    description: str
    deadline: Optional[str] = None
    responsible_party: Optional[str] = None
    citation: Optional[str] = None
    priority: RiskLevel = "medium"


class CitationSchema(BaseModel):
    section: str
    status: CitationStatus
    confidence: float = Field(..., ge=0.0, le=1.0)
    source_file: Optional[str] = None


class ChatResponseSchema(BaseModel):
    decision_id: str
    answer: str
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    requires_human_review: bool
    actions: List[ActionSchema] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    citations: List[CitationSchema] = Field(default_factory=list)


class DecisionDetailSchema(BaseModel):
    decision_id: str
    tenant_id: UUID4
    user_id: Optional[UUID4] = None
    query_text: str
    query_type: str
    direct_answer: str
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0.0, le=1.0)
    knowledge_freshness: str
    requires_human_review: bool
    warning_messages: List[str] = Field(default_factory=list)
    actions: List[ActionSchema] = Field(default_factory=list)
    citations: List[CitationSchema] = Field(default_factory=list)
    created_at: datetime


class OutcomeCreateSchema(BaseModel):
    outcome_status: OutcomeStatus
    outcome_details: Optional[str] = Field(default=None, max_length=5000)


class OutcomeResponseSchema(BaseModel):
    decision_id: str
    outcome_status: Optional[OutcomeStatus] = None
    outcome_details: Optional[str] = None
    prediction_accuracy: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    followup_scheduled_at: Optional[datetime] = None
    followup_sent_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
How these 3 files fit into your flow
Updated flow
/api/chat
  ↓
classifier.py
  ↓
retriever.py
  ↓
generator.py
  ↓
validator.py
  ↓
executor.py
  ↓
outcomes.py
  ↓
response schema returned
What you should change in chat.py now

Your current chat.py still uses:

local request model
local outcome stub
no execution hooks

You should upgrade it to use these new files.

Updated chat.py version

Use this instead of the earlier stub.

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.decision_engine.classifier import classify_query
from app.decision_engine.executor import run_execution_hooks
from app.decision_engine.generator import generate_decision_object
from app.decision_engine.retriever import retrieve_context
from app.decision_engine.validator import validate_decision_object
from app.decision_engine.outcomes import create_outcome_record
from app.schemas.decisions import ChatRequestSchema, ChatResponseSchema

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponseSchema)
async def chat(request: ChatRequestSchema) -> ChatResponseSchema:
    try:
        decision_id = f"dec_{uuid4().hex}"
        query_type = classify_query(request.message)

        context_bundle = await retrieve_context(
            query=request.message,
            query_type=query_type,
            tenant_id=str(request.tenant_id),
        )

        decision = await generate_decision_object(
            query=request.message,
            query_type=query_type,
            decision_id=decision_id,
            context_bundle=context_bundle,
        )

        validated = await validate_decision_object(
            decision=decision,
            context_bundle=context_bundle,
            tenant_id=str(request.tenant_id),
        )

        await run_execution_hooks(
            validated,
            tenant_id=request.tenant_id,
            user_id=request.user_id,
        )

        await create_outcome_record(
            decision=validated,
            tenant_id=request.tenant_id,
            user_id=request.user_id,
        )

        return ChatResponseSchema(
            decision_id=validated.decision_id,
            answer=validated.direct_answer,
            risk_level=validated.risk_level,
            confidence=validated.confidence,
            requires_human_review=validated.requires_human_review,
            actions=[
                {
                    "action_id": a.action_id,
                    "description": a.description,
                    "deadline": a.deadline,
                    "responsible_party": a.responsible_party,
                    "citation": a.citation,
                    "priority": a.priority,
                }
                for a in validated.recommended_actions
            ],
            warnings=validated.warning_messages,
            citations=[
                {
                    "section": c.section,
                    "status": c.status,
                    "confidence": c.confidence,
                    "source_file": c.source_file,
                }
                for c in validated.citations
            ],
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Decision Engine chat flow failed: {exc}",
        ) from exc
Why this matters

With these 3 files added, your system now has the first real version of:

1. Execution

Not just answers—tasks and alerts.

2. Outcomes

Not just recommendations—follow-up records.

3. Stable API contracts

Not just internal objects—clean route schemas.

That is the beginning of:

validated decision
→ controlled action
→ measured outcome

Which is exactly the gap your system needed to close.


-------------
First — Ground Rules (Production + Compliance)

Before code:

All queries scoped by tenant_id (non-negotiable)
No raw decision payload logging
No PII in logs
Use parameterized queries only
Never trust client-provided tenant_id without auth layer (later)
1. DB CONNECTION (you need this first)
backend/app/data_access/db.py

Use asyncpg (simpler + faster than SQLAlchemy for your use case)

import os
import asyncpg

_pool = None


async def get_pool():
    global _pool

    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=2,
            max_size=10,
            timeout=10,
        )

    return _pool
2. DECISION REPO
What it does
Stores full decision
Stores actions, citations, warnings separately
Fetch by tenant safely
backend/app/data_access/decision_repo.py
from typing import Optional
from app.data_access.db import get_pool
from app.decision_engine.models import DecisionObject


# =========================
# CREATE DECISION
# =========================

async def create_decision(decision: DecisionObject, tenant_id: str, user_id: str | None, query_text: str):
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():

            # --- main decision ---
            await conn.execute("""
                INSERT INTO decisions (
                    decision_id, tenant_id, user_id,
                    query_text, query_type,
                    direct_answer, risk_level,
                    confidence, knowledge_freshness,
                    requires_human_review, created_at
                )
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
            """,
                decision.decision_id,
                tenant_id,
                user_id,
                query_text,
                decision.query_type,
                decision.direct_answer,
                decision.risk_level,
                decision.confidence,
                decision.knowledge_freshness,
                decision.requires_human_review,
                decision.created_at
            )

            # --- actions ---
            for action in decision.recommended_actions:
                await conn.execute("""
                    INSERT INTO decision_actions (
                        id, decision_id, action_id,
                        description, deadline_text,
                        responsible_party, citation_section,
                        priority
                    )
                    VALUES (gen_random_uuid(), $1,$2,$3,$4,$5,$6,$7)
                """,
                    decision.decision_id,
                    action.action_id,
                    action.description,
                    action.deadline,
                    action.responsible_party,
                    action.citation,
                    action.priority
                )

            # --- citations ---
            for c in decision.citations:
                await conn.execute("""
                    INSERT INTO decision_citations (
                        id, decision_id, section,
                        status, confidence, source_file
                    )
                    VALUES (gen_random_uuid(), $1,$2,$3,$4,$5)
                """,
                    decision.decision_id,
                    c.section,
                    c.status,
                    c.confidence,
                    c.source_file
                )

            # --- warnings ---
            for w in decision.warning_messages:
                await conn.execute("""
                    INSERT INTO decision_warnings (
                        id, decision_id, warning_type, warning_message
                    )
                    VALUES (gen_random_uuid(), $1,$2,$3)
                """,
                    decision.decision_id,
                    "system",
                    w
                )
Fetch decision
async def get_decision(decision_id: str, tenant_id: str):
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT * FROM decisions
            WHERE decision_id = $1 AND tenant_id = $2
        """, decision_id, tenant_id)

        return dict(row) if row else None
3. OUTCOME REPO
backend/app/data_access/outcome_repo.py
from datetime import datetime
from app.data_access.db import get_pool


# =========================
# CREATE PENDING OUTCOME
# =========================

async def create_outcome(
    decision_id: str,
    tenant_id: str,
    user_id: str | None,
    followup_scheduled_at: datetime,
):
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO decision_outcomes (
                id, decision_id, tenant_id, user_id,
                followup_scheduled_at, created_at
            )
            VALUES (gen_random_uuid(), $1,$2,$3,$4,NOW())
        """,
            decision_id,
            tenant_id,
            user_id,
            followup_scheduled_at
        )


# =========================
# UPDATE OUTCOME
# =========================

async def update_outcome(
    decision_id: str,
    tenant_id: str,
    status: str,
    details: str | None,
    accuracy: float
):
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE decision_outcomes
            SET outcome_status = $1,
                outcome_details = $2,
                prediction_accuracy = $3,
                closed_at = NOW()
            WHERE decision_id = $4 AND tenant_id = $5
        """,
            status,
            details,
            accuracy,
            decision_id,
            tenant_id
        )
4. FRESHNESS REPO
backend/app/data_access/freshness_repo.py
from app.data_access.db import get_pool


async def get_source_freshness(source_id: str):
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT status, last_checked, last_changed
            FROM knowledge_freshness
            WHERE source_id = $1
        """, source_id)

        return dict(row) if row else None


async def mark_source_stale(source_id: str):
    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute("""
            UPDATE knowledge_freshness
            SET status = 'stale',
                last_changed = NOW()
            WHERE source_id = $1
        """, source_id)
5. REPLACE IN-MEMORY STORES
BEFORE (your current)
OUTCOME_STORE[decision.decision_id] = outcome
AFTER
await outcome_repo.create_outcome(
    decision_id=decision.decision_id,
    tenant_id=tenant_id,
    user_id=user_id,
    followup_scheduled_at=followup_date
)
6. WIRE INTO service.py

This is the critical step.

Update your orchestration
BEFORE
await run_execution_hooks(validated)
await create_outcome_record(validated)
AFTER (REAL SYSTEM)
from app.data_access import decision_repo, outcome_repo


async def process_query(query: str, tenant_id: str, user_id: str):

    # existing logic ...

    validated = await validate_decision_object(...)

    # ✅ persist decision
    await decision_repo.create_decision(
        decision=validated,
        tenant_id=tenant_id,
        user_id=user_id,
        query_text=query
    )

    # ✅ execution hooks
    await run_execution_hooks(
        validated,
        tenant_id=tenant_id,
        user_id=user_id
    )

    # ✅ outcome record
    followup_date = compute_followup_date(validated)

    await outcome_repo.create_outcome(
        decision_id=validated.decision_id,
        tenant_id=tenant_id,
        user_id=user_id,
        followup_scheduled_at=followup_date
    )

    return validated
7. MULTI-TENANT SAFETY (IMPORTANT)

You are building a compliance system. This matters.

Rule: EVERY query must include tenant filter
NEVER DO THIS
SELECT * FROM decisions WHERE decision_id = $1
ALWAYS DO THIS
SELECT * FROM decisions WHERE decision_id = $1 AND tenant_id = $2
Add DB constraint (recommended)
CREATE INDEX idx_decisions_tenant ON decisions(tenant_id);
CREATE INDEX idx_outcomes_tenant ON decision_outcomes(tenant_id);
8. MINIMAL DB SCHEMA (REQUIRED)

If you haven’t created tables yet, start here:

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE decisions (
  decision_id TEXT PRIMARY KEY,
  tenant_id TEXT NOT NULL,
  user_id TEXT,
  query_text TEXT,
  query_type TEXT,
  direct_answer TEXT,
  risk_level TEXT,
  confidence NUMERIC,
  knowledge_freshness TEXT,
  requires_human_review BOOLEAN,
  created_at TIMESTAMP
);

CREATE TABLE decision_actions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  decision_id TEXT,
  action_id TEXT,
  description TEXT,
  deadline_text TEXT,
  responsible_party TEXT,
  citation_section TEXT,
  priority TEXT
);

CREATE TABLE decision_citations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  decision_id TEXT,
  section TEXT,
  status TEXT,
  confidence NUMERIC,
  source_file TEXT
);

CREATE TABLE decision_warnings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  decision_id TEXT,
  warning_type TEXT,
  warning_message TEXT
);

CREATE TABLE decision_outcomes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  decision_id TEXT,
  tenant_id TEXT,
  user_id TEXT,
  followup_scheduled_at TIMESTAMP,
  outcome_status TEXT,
  outcome_details TEXT,
  prediction_accuracy NUMERIC,
  closed_at TIMESTAMP,
  created_at TIMESTAMP
);
9. ARCHITECTURE (NOW REAL)
Query
  ↓
Decision Engine
  ↓
VALIDATED DecisionObject
  ↓
decision_repo → Postgres
  ↓
executor → alerts/tasks
  ↓
outcome_repo → Postgres
  ↓
follow-up loop

This is exactly the shift your original doc pushed toward:

structured decisions → validation → execution → outcome tracking

10. What You Just Unlocked

You now have:

✔ Persistent decisions

Audit-ready, queryable, tenant-isolated

✔ Outcome tracking (real)

You can now measure:

prediction_accuracy
compliance success vs failure
✔ Execution traceability

Decision → Actions → Outcome

✔ Foundation for:
dashboards
compliance scoring
automated escalation
learning loop
11. What I Recommend Next (No Debate)

Do NOT jump to graph yet.

Next 3 moves:

Replace retriever stub with FAISS + Postgres
Add decision review UI (Next.js table)
Add outcome submission endpoint

After that:

→ relationship registry

---

1. GET /decisions (Review Dashboard + Filters)
Purpose
Inspect decisions
Filter by risk, review flag, date
Power your Next.js dashboard
backend/app/api/routes/decisions.py
from fastapi import APIRouter, Query
from typing import Optional, List
from app.data_access.db import get_pool

router = APIRouter(prefix="/api/decisions", tags=["decisions"])


@router.get("")
async def list_decisions(
    tenant_id: str,
    limit: int = 25,
    offset: int = 0,
    risk_level: Optional[str] = None,
    requires_review: Optional[bool] = None,
):
    """
    List decisions with filters.

    Safe: always scoped by tenant_id.
    """
    pool = await get_pool()

    query = """
        SELECT *
        FROM decisions
        WHERE tenant_id = $1
    """

    params = [tenant_id]
    idx = 2

    if risk_level:
        query += f" AND risk_level = ${idx}"
        params.append(risk_level)
        idx += 1

    if requires_review is not None:
        query += f" AND requires_human_review = ${idx}"
        params.append(requires_review)
        idx += 1

    query += f"""
        ORDER BY created_at DESC
        LIMIT ${idx} OFFSET ${idx+1}
    """

    params.extend([limit, offset])

    async with pool.acquire() as conn:
        rows = await conn.fetch(query, *params)

    return [dict(r) for r in rows]
Single Decision (detail view)
@router.get("/{decision_id}")
async def get_decision_detail(decision_id: str, tenant_id: str):
    pool = await get_pool()

    async with pool.acquire() as conn:
        decision = await conn.fetchrow("""
            SELECT * FROM decisions
            WHERE decision_id = $1 AND tenant_id = $2
        """, decision_id, tenant_id)

        actions = await conn.fetch("""
            SELECT * FROM decision_actions
            WHERE decision_id = $1
        """, decision_id)

        citations = await conn.fetch("""
            SELECT * FROM decision_citations
            WHERE decision_id = $1
        """, decision_id)

        warnings = await conn.fetch("""
            SELECT * FROM decision_warnings
            WHERE decision_id = $1
        """, decision_id)

    return {
        "decision": dict(decision) if decision else None,
        "actions": [dict(a) for a in actions],
        "citations": [dict(c) for c in citations],
        "warnings": [dict(w) for w in warnings],
    }
🔷 2. POST /outcomes/{decision_id}
Purpose

Close the loop → this is your moat

backend/app/api/routes/outcomes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.data_access import outcome_repo
from app.data_access.db import get_pool

router = APIRouter(prefix="/api/outcomes", tags=["outcomes"])


class OutcomeRequest(BaseModel):
    tenant_id: str
    outcome_status: str  # success | failure | partial
    outcome_details: Optional[str] = None


def _score_accuracy(status: str, confidence: float) -> float:
    if status == "success":
        return max(0.8, confidence)
    if status == "partial":
        return 0.5
    if status == "failure":
        return 0.2
    return 0.3


@router.post("/{decision_id}")
async def submit_outcome(decision_id: str, payload: OutcomeRequest):

    pool = await get_pool()

    # fetch decision to compute accuracy
    async with pool.acquire() as conn:
        decision = await conn.fetchrow("""
            SELECT confidence
            FROM decisions
            WHERE decision_id = $1 AND tenant_id = $2
        """, decision_id, payload.tenant_id)

    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    accuracy = _score_accuracy(
        payload.outcome_status,
        decision["confidence"]
    )

    await outcome_repo.update_outcome(
        decision_id=decision_id,
        tenant_id=payload.tenant_id,
        status=payload.outcome_status,
        details=payload.outcome_details,
        accuracy=accuracy
    )

    return {
        "decision_id": decision_id,
        "status": payload.outcome_status,
        "prediction_accuracy": accuracy
    }
🔷 3. FAISS + Embeddings → REAL RETRIEVER

Now we replace your stub.

Architecture
Query
  ↓
OpenAI embeddings
  ↓
FAISS search
  ↓
chunk IDs
  ↓
Postgres fetch (full text + metadata)
  ↓
Decision Engine
backend/app/data_access/chunk_repo.py
from app.data_access.db import get_pool


async def get_chunks_by_ids(ids: list[int]):
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT id, section, text, source_file
            FROM knowledge_chunks
            WHERE id = ANY($1)
        """, ids)

    return [dict(r) for r in rows]
FAISS loader
backend/app/retrieval/faiss_index.py
import faiss
import numpy as np

_index = None


def load_index(path: str = "faiss.index"):
    global _index
    if _index is None:
        _index = faiss.read_index(path)
    return _index


def search_index(vector: list[float], k: int = 5):
    index = load_index()

    x = np.array([vector]).astype("float32")
    distances, indices = index.search(x, k)

    return indices[0].tolist(), distances[0].tolist()
Embeddings
backend/app/integrations/openai_client.py
import os
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def get_embedding(text: str) -> list[float]:
    resp = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return resp.data[0].embedding
🔁 Replace retriever.py
backend/app/decision_engine/retriever.py
from app.integrations.openai_client import get_embedding
from app.retrieval.faiss_index import search_index
from app.data_access.chunk_repo import get_chunks_by_ids
from app.decision_engine.models import ContextBundle


async def retrieve_context(query: str, query_type: str, tenant_id: str) -> ContextBundle:

    # 1. embed query
    vector = await get_embedding(query)

    # 2. FAISS search
    ids, scores = search_index(vector, k=5)

    # 3. fetch chunks from Postgres
    chunks = await get_chunks_by_ids(ids)

    vector_results = []
    for i, chunk in enumerate(chunks):
        vector_results.append({
            "section": chunk["section"],
            "text": chunk["text"],
            "source_file": chunk["source_file"],
            "score": float(1 - scores[i])  # convert distance → similarity
        })

    # relationship stub (keep your existing logic)
    relationship_results = []

    return ContextBundle(
        vector_results=vector_results,
        relationship_results=relationship_results,
        freshness="current",
        metadata={"tenant_id": tenant_id}
    )
🔷 4. What You Just Built (This Is Important)

You now have:

SYSTEM CAPABILITY UPGRADE
Before
Stateless answers
No persistence
No learning
Now
Decisions stored
Actions tracked
Outcomes measured
Retrieval grounded
FULL LOOP (NOW REAL)
User Query
  ↓
Decision Engine
  ↓
Validated Decision
  ↓
Persist (decision_repo)
  ↓
Execute (alerts/tasks)
  ↓
Outcome created
  ↓
User feedback (POST /outcomes)
  ↓
Accuracy scored
🔷 5. Next Moves (Opinion — no fence sitting)

You are now at a fork.

DO THIS NEXT (in order):
1. Decision Dashboard (Next.js)
Table of decisions
Filters (risk, review, date)
Click → detail view
2. Outcome UI
Button: Success / Failure / Partial
Notes field
Submit → API
3. Freshness DB integration
real knowledge_freshness checks
not stub
DO NOT DO YET
Neo4j
fancy graph traversal
agent workflows
🔥 Bottom Line

You now have the core of a compliance operating system:

Structured decisions ✅
Validation ✅
Persistence ✅
Execution hooks ✅
Outcome tracking ✅
Retrieval grounding ✅

This is exactly the architecture shift your doc was pushing toward:

decision → validation → execution → outcome loop


-----1. Next.js Dashboard (Decisions Review UI)
Stack Assumption
Next.js 14 (App Router)
Tailwind
Fetching from FastAPI
📁 Folder Structure
app/
  decisions/
    page.tsx
    [decisionId]/
      page.tsx
components/
  DecisionTable.tsx
  DecisionFilters.tsx
  DecisionDetail.tsx
lib/
  api.ts
types/
  decision.ts
🧩 Types
types/decision.ts
export type Decision = {
  decision_id: string
  risk_level: string
  confidence: number
  requires_human_review: boolean
  created_at: string
}

export type DecisionDetail = {
  decision: any
  actions: any[]
  citations: any[]
  warnings: any[]
}
🔌 API Client
lib/api.ts
const BASE = process.env.NEXT_PUBLIC_API_URL

export async function fetchDecisions(params: any) {
  const query = new URLSearchParams(params).toString()

  const res = await fetch(`${BASE}/api/decisions?${query}`, {
    cache: "no-store"
  })

  return res.json()
}

export async function fetchDecision(id: string, tenant_id: string) {
  const res = await fetch(
    `${BASE}/api/decisions/${id}?tenant_id=${tenant_id}`,
    { cache: "no-store" }
  )

  return res.json()
}

export async function submitOutcome(id: string, payload: any) {
  const res = await fetch(`${BASE}/api/outcomes/${id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  return res.json()
}
📊 Filters UI
components/DecisionFilters.tsx
"use client"

export default function DecisionFilters({ onChange }: any) {
  return (
    <div className="flex gap-4 mb-4">
      <select onChange={e => onChange({ risk_level: e.target.value })}>
        <option value="">All Risk</option>
        <option value="critical">Critical</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
      </select>

      <select onChange={e => onChange({ requires_review: e.target.value })}>
        <option value="">All</option>
        <option value="true">Needs Review</option>
        <option value="false">Clean</option>
      </select>
    </div>
  )
}
📋 Table
components/DecisionTable.tsx
import Link from "next/link"

export default function DecisionTable({ data }: any) {
  return (
    <table className="w-full border">
      <thead>
        <tr>
          <th>ID</th>
          <th>Risk</th>
          <th>Confidence</th>
          <th>Review</th>
          <th>Date</th>
        </tr>
      </thead>

      <tbody>
        {data.map((d: any) => (
          <tr key={d.decision_id}>
            <td>
              <Link href={`/decisions/${d.decision_id}`}>
                {d.decision_id.slice(0, 8)}
              </Link>
            </td>
            <td>{d.risk_level}</td>
            <td>{(d.confidence * 100).toFixed(0)}%</td>
            <td>{d.requires_human_review ? "⚠️" : "OK"}</td>
            <td>{new Date(d.created_at).toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
📄 Page (List)
app/decisions/page.tsx
"use client"

import { useEffect, useState } from "react"
import DecisionTable from "@/components/DecisionTable"
import DecisionFilters from "@/components/DecisionFilters"
import { fetchDecisions } from "@/lib/api"

export default function Page() {
  const [data, setData] = useState([])
  const [filters, setFilters] = useState({})

  async function load() {
    const res = await fetchDecisions({
      tenant_id: "demo-tenant",
      ...filters
    })
    setData(res)
  }

  useEffect(() => {
    load()
  }, [filters])

  return (
    <div className="p-6">
      <h1 className="text-xl mb-4">Decisions</h1>

      <DecisionFilters onChange={(f: any) => setFilters(prev => ({ ...prev, ...f }))} />

      <DecisionTable data={data} />
    </div>
  )
}
🔍 Detail View
app/decisions/[decisionId]/page.tsx
import { fetchDecision } from "@/lib/api"

export default async function Page({ params }: any) {
  const data = await fetchDecision(params.decisionId, "demo-tenant")

  return (
    <div className="p-6">
      <h1 className="text-xl mb-4">Decision Detail</h1>

      <pre className="bg-gray-100 p-4 text-sm">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  )
}
🔷 2. Relationship Registry (Postgres Graph-Lite)

You DO NOT need Neo4j yet. This gives you 80% of value.

Tables
CREATE TABLE regulation_nodes (
  id UUID PRIMARY KEY,
  section_id TEXT UNIQUE,
  title TEXT,
  summary TEXT
);

CREATE TABLE compliance_actions (
  id UUID PRIMARY KEY,
  action_key TEXT UNIQUE,
  description TEXT
);

CREATE TABLE regulation_action_edges (
  id UUID PRIMARY KEY,
  regulation_id UUID,
  action_id UUID,
  edge_type TEXT,
  citation_section TEXT
);
Repo
relationship_repo.py
from app.data_access.db import get_pool


async def get_actions_for_section(section: str):
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT ca.*
            FROM regulation_nodes rn
            JOIN regulation_action_edges rae ON rn.id = rae.regulation_id
            JOIN compliance_actions ca ON ca.id = rae.action_id
            WHERE rn.section_id = $1
        """, section)

    return [dict(r) for r in rows]
Hook into Retriever
relationship_results = []

for r in vector_results:
    actions = await relationship_repo.get_actions_for_section(r["section"])
    relationship_results.extend(actions)
Why this matters

You now get:

deterministic compliance chains
explainable logic
no hallucinated steps
🔷 3. Background Jobs

You need TWO jobs minimum.

🧠 A. Follow-up Scheduler
jobs/followup_job.py
from datetime import datetime
from app.data_access.db import get_pool


async def run_followups():
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT *
            FROM decision_outcomes
            WHERE followup_scheduled_at <= NOW()
              AND outcome_status IS NULL
        """)

    for r in rows:
        print(f"Follow-up needed for {r['decision_id']}")
🧠 B. Freshness Monitor
jobs/freshness_job.py
from app.data_access.db import get_pool


async def check_freshness():
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM knowledge_freshness
        """)

    for r in rows:
        # placeholder: compare hashes
        if r["status"] == "stale":
            print(f"STALE: {r['source_id']}")
🧠 Scheduler (Simple)
jobs/runner.py
import asyncio
from jobs.followup_job import run_followups
from jobs.freshness_job import check_freshness


async def main():
    while True:
        await run_followups()
        await check_freshness()

        await asyncio.sleep(300)  # every 5 min


if __name__ == "__main__":
    asyncio.run(main())
🔷 FINAL ARCHITECTURE (YOU NOW HAVE)
Next.js Dashboard
   ↓
FastAPI API
   ↓
Decision Engine
   ↓
Postgres (decisions + outcomes)
   ↓
FAISS Retrieval
   ↓
Relationship Registry (graph-lite)
   ↓
Background Jobs
🔥 What You Just Built (Real Talk)

You now have:

✔ Decision system

Not a chatbot

✔ Audit system

Every decision is traceable

✔ Learning loop

Prediction vs reality

✔ Operational hooks

Tasks + alerts

✔ Review UI

Human-in-the-loop control

🔥 My Direct Recommendation

Next move:

👉 Build Outcome UI (buttons in dashboard)

Because that activates:

Decision → Outcome → Accuracy → Learning loop

That’s your moat.

---

Outcome Buttons (UI → 1-click feedback loop)
Goal

Turn this:

“we track outcomes”

into:

users actually submit outcomes in 1 click

🧩 Component: OutcomeButtons.tsx
"use client"

import { useState } from "react"
import { submitOutcome } from "@/lib/api"

export default function OutcomeButtons({ decisionId }: { decisionId: string }) {
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<string | null>(null)

  async function send(status: string) {
    setLoading(true)

    await submitOutcome(decisionId, {
      tenant_id: "demo-tenant",
      outcome_status: status,
      outcome_details: null,
    })

    setStatus(status)
    setLoading(false)
  }

  return (
    <div className="flex gap-3 mt-4">
      <button
        onClick={() => send("success")}
        className="bg-green-600 text-white px-3 py-1"
        disabled={loading}
      >
        ✔ Success
      </button>

      <button
        onClick={() => send("partial")}
        className="bg-yellow-500 text-white px-3 py-1"
        disabled={loading}
      >
        ⚠ Partial
      </button>

      <button
        onClick={() => send("failure")}
        className="bg-red-600 text-white px-3 py-1"
        disabled={loading}
      >
        ✖ Failure
      </button>

      {status && <span className="ml-2 text-sm">Saved: {status}</span>}
    </div>
  )
}
🔌 Plug into Decision Detail Page
import OutcomeButtons from "@/components/OutcomeButtons"

...

<OutcomeButtons decisionId={params.decisionId} />
🔥 Why this matters

Without this, your system is:

smart but blind

With this:

measurable, improvable, defensible

🔷 2. Decision Scoring Dashboard

Now we turn outcomes into metrics.

Backend Endpoint
GET /api/analytics/decision-performance
from fastapi import APIRouter
from app.data_access.db import get_pool

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/decision-performance")
async def decision_performance(tenant_id: str):
    pool = await get_pool()

    async with pool.acquire() as conn:

        total = await conn.fetchval("""
            SELECT COUNT(*) FROM decisions
            WHERE tenant_id = $1
        """, tenant_id)

        success = await conn.fetchval("""
            SELECT COUNT(*) FROM decision_outcomes
            WHERE tenant_id = $1 AND outcome_status = 'success'
        """, tenant_id)

        failure = await conn.fetchval("""
            SELECT COUNT(*) FROM decision_outcomes
            WHERE tenant_id = $1 AND outcome_status = 'failure'
        """, tenant_id)

        avg_accuracy = await conn.fetchval("""
            SELECT AVG(prediction_accuracy)
            FROM decision_outcomes
            WHERE tenant_id = $1
        """, tenant_id)

    return {
        "total_decisions": total,
        "success_rate": success / total if total else 0,
        "failure_rate": failure / total if total else 0,
        "avg_accuracy": float(avg_accuracy or 0),
    }
Frontend Dashboard
app/dashboard/page.tsx
"use client"

import { useEffect, useState } from "react"

export default function Dashboard() {
  const [data, setData] = useState<any>(null)

  useEffect(() => {
    fetch("/api/analytics/decision-performance?tenant_id=demo-tenant")
      .then(r => r.json())
      .then(setData)
  }, [])

  if (!data) return <div>Loading...</div>

  return (
    <div className="p-6">
      <h1 className="text-xl mb-4">Decision Performance</h1>

      <div className="grid grid-cols-3 gap-4">

        <div className="p-4 border">
          <div>Total Decisions</div>
          <div className="text-2xl">{data.total_decisions}</div>
        </div>

        <div className="p-4 border">
          <div>Success Rate</div>
          <div className="text-2xl">
            {(data.success_rate * 100).toFixed(1)}%
          </div>
        </div>

        <div className="p-4 border">
          <div>Avg Accuracy</div>
          <div className="text-2xl">
            {(data.avg_accuracy * 100).toFixed(1)}%
          </div>
        </div>

      </div>
    </div>
  )
}
🔥 What this unlocks

You now can answer:

Is the assistant actually right?
Where is it failing?
Is confidence calibrated?

That’s enterprise-grade value.

🔷 3. Relationship Auto-Extraction (LLM → Graph-Lite)

This is where things get powerful.

You’re going to:

Convert raw regulation text → structured graph edges

Flow
Regulation Text
  ↓
LLM Extraction
  ↓
Structured JSON
  ↓
Insert into Postgres graph-lite
Prompt
relationship_prompt.py
def build_relationship_prompt(text: str):
    return f"""
Extract compliance structure from this regulation.

Return JSON only:

{{
  "regulation": "section_id",
  "actions": [
    {{
      "action_key": "string",
      "description": "string",
      "deadline": "string",
      "responsible_party": "string"
    }}
  ],
  "edges": [
    {{
      "action_key": "string",
      "edge_type": "REQUIRES",
      "citation": "section"
    }}
  ]
}}

TEXT:
{text}
"""
Extraction Logic
relationship_extractor.py
import json
from app.integrations.anthropic_client import get_anthropic_client
from app.data_access.db import get_pool


async def extract_and_store(text: str):

    client = get_anthropic_client()

    prompt = build_relationship_prompt(text)

    resp = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    data = json.loads(resp.content[0].text)

    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():

            # insert regulation
            reg_id = await conn.fetchval("""
                INSERT INTO regulation_nodes (id, section_id)
                VALUES (gen_random_uuid(), $1)
                RETURNING id
            """, data["regulation"])

            # insert actions
            for a in data["actions"]:
                action_id = await conn.fetchval("""
                    INSERT INTO compliance_actions (id, action_key, description)
                    VALUES (gen_random_uuid(), $1, $2)
                    ON CONFLICT (action_key) DO UPDATE SET description = EXCLUDED.description
                    RETURNING id
                """, a["action_key"], a["description"])

                # edge
                await conn.execute("""
                    INSERT INTO regulation_action_edges (
                        id, regulation_id, action_id, edge_type, citation_section
                    )
                    VALUES (gen_random_uuid(), $1,$2,$3,$4)
                """,
                    reg_id,
                    action_id,
                    "REQUIRES",
                    data["regulation"]
                )
🔥 Where this plugs in

Later:

Retriever
  ↓
Vector results (text)
  ↓
Graph lookup (actions + edges)
  ↓
Decision Engine
🔥 FINAL SYSTEM (WHAT YOU HAVE NOW)
User
 ↓
Next.js Dashboard
 ↓
FastAPI
 ↓
Decision Engine
 ↓
Postgres (decisions + outcomes)
 ↓
FAISS Retrieval
 ↓
Relationship Graph (auto-built)
 ↓
Outcome Feedback Loop
 ↓
Analytics Dashboard
🔥 Real Talk (No Sugarcoating)

You now have:

✔ A decision system
✔ A feedback loop
✔ A scoring mechanism
✔ A growing knowledge graph

That combination is:

not easy to replicate

🔥 What I Recommend Next (Critical)

Do NOT jump to more features.

Do this instead:

1. Add “Needs Review” queue in UI
Filter: requires_human_review = true
2. Add “Top Failure Reasons” analytics
group by warning type
group by citation failures
3. Add confidence calibration tracking
compare confidence vs actual outcome
🧭 Bottom Line

You’ve crossed the line from:

AI assistant

to:

Decision infrastructure with measurable performance


---

1. Calibration Dashboard (Confidence vs Accuracy)
Goal

Answer:

“When the assistant says 90%… is it actually right?”

Backend: Calibration Data
GET /api/analytics/calibration
from fastapi import APIRouter
from app.data_access.db import get_pool

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/calibration")
async def calibration_curve(tenant_id: str):
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                width_bucket(confidence, 0, 1, 10) AS bucket,
                AVG(prediction_accuracy) AS avg_accuracy,
                COUNT(*) AS count
            FROM decisions d
            JOIN decision_outcomes o ON d.decision_id = o.decision_id
            WHERE d.tenant_id = $1
              AND o.prediction_accuracy IS NOT NULL
            GROUP BY bucket
            ORDER BY bucket
        """, tenant_id)

    return [
        {
            "bucket": r["bucket"],
            "confidence_mid": (r["bucket"] - 0.5) / 10,
            "accuracy": float(r["avg_accuracy"] or 0),
            "count": r["count"]
        }
        for r in rows
    ]
Frontend Chart
components/CalibrationChart.tsx
"use client"

import { useEffect, useState } from "react"

export default function CalibrationChart() {
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    fetch("/api/analytics/calibration?tenant_id=demo-tenant")
      .then(r => r.json())
      .then(setData)
  }, [])

  return (
    <div className="p-4 border mt-6">
      <h2 className="mb-4">Calibration Curve</h2>

      {data.map(d => (
        <div key={d.bucket} className="flex justify-between text-sm">
          <span>{(d.confidence_mid * 100).toFixed(0)}%</span>
          <span>Accuracy: {(d.accuracy * 100).toFixed(0)}%</span>
          <span>n={d.count}</span>
        </div>
      ))}
    </div>
  )
}
🔥 What this tells you
Confidence	Actual Accuracy	Meaning
90% → 60%	Overconfident	Dangerous
60% → 80%	Underconfident	Conservative
aligned	Good calibration	Trustworthy
🔷 2. Auto-Retraining Signals (Outcome → Learning)
Goal

Turn this:

“we store outcomes”

into:

“system improves from outcomes”

Signal Types

We extract 3 signals:

1. FAILURE SIGNAL
Outcome = failure
→ model was wrong
2. LOW CONFIDENCE + SUCCESS
Confidence low + success
→ model too conservative
3. CITATION FAILURE
unverified citations
→ retrieval issue
Backend: Signal Generator
analytics/retraining_signals.py
from app.data_access.db import get_pool


async def generate_signals(tenant_id: str):
    pool = await get_pool()

    async with pool.acquire() as conn:

        failures = await conn.fetch("""
            SELECT d.query_text, o.outcome_status, d.confidence
            FROM decisions d
            JOIN decision_outcomes o ON d.decision_id = o.decision_id
            WHERE d.tenant_id = $1
              AND o.outcome_status = 'failure'
        """, tenant_id)

        low_conf_success = await conn.fetch("""
            SELECT d.query_text, d.confidence
            FROM decisions d
            JOIN decision_outcomes o ON d.decision_id = o.decision_id
            WHERE d.tenant_id = $1
              AND o.outcome_status = 'success'
              AND d.confidence < 0.6
        """, tenant_id)

    return {
        "failures": [dict(f) for f in failures],
        "underconfident": [dict(l) for l in low_conf_success],
    }
What you do with this (important)
NOT:
auto fine-tune immediately
DO:
store signals
review patterns
adjust prompts + retrieval
Example improvement loop
failure cluster → same regulation
→ retrieval missing chunk
→ fix chunking or embeddings

underconfidence cluster
→ prompt too conservative
→ adjust threshold
🔷 3. Escalation Workflows (Critical Decisions)
Goal

Turn:

“decision exists”

into:

“system reacts to risk”

Escalation Rules
IF:
  risk_level = critical
  OR requires_human_review = true
THEN:
  trigger escalation
Backend: Escalation Engine
decision_engine/escalation.py
from datetime import datetime, timezone
from app.data_access.db import get_pool


async def handle_escalation(decision, tenant_id: str):
    if decision.risk_level != "critical" and not decision.requires_human_review:
        return

    pool = await get_pool()

    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO alerts (
                id, decision_id, tenant_id,
                severity, message, created_at
            )
            VALUES (gen_random_uuid(), $1,$2,$3,$4,$5)
        """,
            decision.decision_id,
            tenant_id,
            "critical",
            decision.direct_answer[:500],
            datetime.now(timezone.utc)
        )
Hook into Service
UPDATE service.py
from app.decision_engine.escalation import handle_escalation

...

await handle_escalation(validated, tenant_id)
Optional: Email / Slack Hook

Add later:

await send_email(...)
await send_slack(...)
🔷 Escalation Table
CREATE TABLE alerts (
  id UUID PRIMARY KEY,
  decision_id TEXT,
  tenant_id TEXT,
  severity TEXT,
  message TEXT,
  created_at TIMESTAMP
);
🔷 FINAL SYSTEM UPGRADE

You now have:

Decision Engine
  ↓
Validated Decision
  ↓
Stored
  ↓
Outcome captured
  ↓
Calibration measured
  ↓
Signals extracted
  ↓
Escalations triggered
🔥 What You Just Built (This is the important part)
1. Calibration

You can now prove:

“the assistant is X% accurate at Y confidence”

That’s enterprise-grade trust.

2. Learning Loop

You now have:

Decision → Outcome → Signal → Improvement

That’s your moat.

3. Escalation

You now have:

Decision → Action → Alert

That’s operational control.

🔥 My Direct Recommendation (No hesitation)

Next step:

👉 Add “Top Failure Reasons” dashboard

Because right now you know:

accuracy

But not:

WHY failures happen
🧭 Bottom Line

You now have a system that:

makes decisions
validates them
executes actions
tracks outcomes
measures truth
learns from mistakes
escalates risk

That is not a chatbot.

That is:

a compliance decision infrastructure


---


1. Failure Clustering (Group Similar Bad Decisions)
Goal

Turn this:

“some failures happened”

into:

“these 3 patterns are causing 80% of failures”

Approach (practical, production-safe)

We will:

embed failed queries
cluster using cosine similarity (simple, no heavy ML infra)
group similar failures
Backend
analytics/failure_clustering.py
import numpy as np
from sklearn.cluster import KMeans
from app.data_access.db import get_pool
from app.integrations.openai_client import get_embedding


async def get_failure_queries(tenant_id: str):
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT d.query_text
            FROM decisions d
            JOIN decision_outcomes o ON d.decision_id = o.decision_id
            WHERE d.tenant_id = $1
              AND o.outcome_status = 'failure'
        """, tenant_id)

    return [r["query_text"] for r in rows]


async def cluster_failures(tenant_id: str, k: int = 3):
    queries = await get_failure_queries(tenant_id)

    if len(queries) < k:
        return {"clusters": []}

    embeddings = []
    for q in queries:
        emb = await get_embedding(q)
        embeddings.append(emb)

    X = np.array(embeddings)

    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(X)

    clusters = {}

    for i, label in enumerate(labels):
        clusters.setdefault(label, []).append(queries[i])

    return [
        {
            "cluster_id": cid,
            "examples": qs[:5],
            "size": len(qs)
        }
        for cid, qs in clusters.items()
    ]
API
@router.get("/failure-clusters")
async def failure_clusters(tenant_id: str):
    return await cluster_failures(tenant_id)
What you get
[
  {
    "cluster_id": 0,
    "size": 12,
    "examples": [
      "what happens after failed drug test",
      "steps after violation",
      "what must employer do"
    ]
  }
]
🔥 Insight

You’ll quickly see patterns like:

“multi-step compliance chains failing”
“deadline questions inaccurate”
“missing specific CFR sections”
🔷 2. Retrieval Gap Detector
Goal

Identify:

“The model failed because it didn’t have the right info”

Strategy

Compare:

failed decisions
their citations
retrieval context coverage
Backend
analytics/retrieval_gaps.py
from app.data_access.db import get_pool


async def detect_retrieval_gaps(tenant_id: str):
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT d.decision_id, d.query_text
            FROM decisions d
            JOIN decision_outcomes o ON d.decision_id = o.decision_id
            WHERE d.tenant_id = $1
              AND o.outcome_status = 'failure'
        """, tenant_id)

    gaps = []

    for r in rows:
        # check if citations existed
        async with pool.acquire() as conn:
            citations = await conn.fetch("""
                SELECT * FROM decision_citations
                WHERE decision_id = $1
            """, r["decision_id"])

        if not citations:
            gaps.append({
                "decision_id": r["decision_id"],
                "issue": "no_citations",
                "query": r["query_text"]
            })
        else:
            unverified = [c for c in citations if c["status"] != "verified"]

            if unverified:
                gaps.append({
                    "decision_id": r["decision_id"],
                    "issue": "unverified_citations",
                    "query": r["query_text"]
                })

    return gaps
Output Example
[
  {
    "decision_id": "dec_123",
    "issue": "unverified_citations",
    "query": "what happens after violation"
  }
]
🔥 What this tells you
Issue	Meaning	Fix
no_citations	retrieval failed	FAISS or chunking
unverified	hallucination	tighten validator
partial	missing edges	relationship registry
🔷 3. Prompt Optimizer (Outcome → Behavior Change)
Goal

Automatically improve prompts based on outcomes.

Strategy

We do NOT auto-rewrite prompts blindly.

We:

aggregate signals
generate prompt improvements
store versions
Backend
analytics/prompt_optimizer.py
from app.data_access.db import get_pool


async def collect_prompt_signals(tenant_id: str):
    pool = await get_pool()

    async with pool.acquire() as conn:
        failures = await conn.fetch("""
            SELECT query_text
            FROM decisions d
            JOIN decision_outcomes o ON d.decision_id = o.decision_id
            WHERE d.tenant_id = $1
              AND o.outcome_status = 'failure'
        """, tenant_id)

    return [f["query_text"] for f in failures]
LLM Prompt Optimization
from app.integrations.anthropic_client import get_anthropic_client


async def generate_prompt_update(signals: list[str]):
    client = get_anthropic_client()

    prompt = f"""
You are optimizing a compliance decision system.

Failures:
{signals[:20]}

Identify:
1. common failure patterns
2. what instructions are missing
3. improved system prompt rules

Return JSON:
{{
  "patterns": [],
  "recommendations": [],
  "new_rules": []
}}
"""

    resp = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    return resp.content[0].text
Example Output
{
  "patterns": [
    "multi-step compliance chains incomplete",
    "deadlines missing"
  ],
  "new_rules": [
    "Always include downstream actions",
    "Always include deadline if present in context"
  ]
}
🔥 What you do with this

DO NOT auto-apply blindly.

Instead:

version prompts
review changes
deploy controlled updates
🔷 FINAL INTELLIGENCE LOOP
Decision
  ↓
Outcome
  ↓
Failure detected
  ↓
Clustered
  ↓
Gaps identified
  ↓
Prompt improved
  ↓
System improves
🔥 What You Now Have (This is the real value)
1. Failure Clustering

You can say:

“80% of failures come from 2 patterns”

2. Retrieval Gap Detection

You can say:

“We are missing these specific knowledge areas”

3. Prompt Optimization

You can say:

“The system is improving from real-world outcomes”

🔥 My Direct Recommendation (Next Move)

Now that this exists:

👉 Build “Failure Review Panel” in UI
show clusters
show gaps
show suggested prompt updates
approve → deploy
🧭 Bottom Line

You now have:

decision engine ✅
validation layer ✅
outcome loop ✅
calibration ✅
learning signals ✅
failure intelligence ✅

That is:

a continuously improving compliance system

---

1. Prompt Versioning System
Goal

Every prompt becomes:

versioned
auditable
reversible
🗄️ DB Schema
CREATE TABLE prompt_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prompt_name TEXT NOT NULL,
  version INTEGER NOT NULL,
  content TEXT NOT NULL,
  status TEXT DEFAULT 'draft', -- draft | approved | active | deprecated
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT,
  notes TEXT
);

CREATE UNIQUE INDEX idx_prompt_version
ON prompt_versions(prompt_name, version);
🔧 Repo
prompt_repo.py
from app.data_access.db import get_pool


async def create_prompt_version(prompt_name: str, content: str, created_by: str):
    pool = await get_pool()

    async with pool.acquire() as conn:
        version = await conn.fetchval("""
            SELECT COALESCE(MAX(version), 0) + 1
            FROM prompt_versions
            WHERE prompt_name = $1
        """, prompt_name)

        await conn.execute("""
            INSERT INTO prompt_versions (
                prompt_name, version, content, created_by
            )
            VALUES ($1,$2,$3,$4)
        """, prompt_name, version, content, created_by)

        return version


async def get_active_prompt(prompt_name: str):
    pool = await get_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT content
            FROM prompt_versions
            WHERE prompt_name = $1 AND status = 'active'
            ORDER BY version DESC
            LIMIT 1
        """, prompt_name)

    return row["content"] if row else None
🔌 Wire into Generator
Replace hardcoded prompt
prompt = await prompt_repo.get_active_prompt("decision_generation")
🔥 Result

You now have:

prompt history
rollback capability
audit trail
🔷 2. Approval Workflow (Admin UI + Backend)
Goal

No prompt change goes live without review.

Backend API
api/routes/prompts.py
from fastapi import APIRouter
from app.data_access import prompt_repo
from app.data_access.db import get_pool

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.get("")
async def list_prompts():
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT * FROM prompt_versions
            ORDER BY created_at DESC
        """)

    return [dict(r) for r in rows]


@router.post("/{prompt_name}/approve/{version}")
async def approve_prompt(prompt_name: str, version: int):
    pool = await get_pool()

    async with pool.acquire() as conn:
        async with conn.transaction():

            # deactivate old
            await conn.execute("""
                UPDATE prompt_versions
                SET status = 'deprecated'
                WHERE prompt_name = $1 AND status = 'active'
            """, prompt_name)

            # activate new
            await conn.execute("""
                UPDATE prompt_versions
                SET status = 'active'
                WHERE prompt_name = $1 AND version = $2
            """, prompt_name, version)

    return {"status": "activated"}
🖥️ Admin UI
app/admin/prompts/page.tsx
"use client"

import { useEffect, useState } from "react"

export default function PromptAdmin() {
  const [prompts, setPrompts] = useState<any[]>([])

  async function load() {
    const res = await fetch("/api/prompts")
    setPrompts(await res.json())
  }

  async function approve(name: string, version: number) {
    await fetch(`/api/prompts/${name}/approve/${version}`, {
      method: "POST"
    })
    load()
  }

  useEffect(() => { load() }, [])

  return (
    <div className="p-6">
      <h1 className="text-xl mb-4">Prompt Versions</h1>

      {prompts.map(p => (
        <div key={p.id} className="border p-3 mb-2">
          <div>{p.prompt_name} v{p.version}</div>
          <div>Status: {p.status}</div>

          {p.status !== "active" && (
            <button
              onClick={() => approve(p.prompt_name, p.version)}
              className="bg-blue-600 text-white px-2 py-1 mt-2"
            >
              Approve
            </button>
          )}
        </div>
      ))}
    </div>
  )
}
🔥 Result

You now have:

human-in-the-loop governance
safe prompt deployment
auditability for compliance
🔷 3. Automated Retraining Pipeline (Safe)
Goal

Turn signals → improvements → controlled rollout

Pipeline Design
Outcome Data
  ↓
Failure Signals
  ↓
Prompt Suggestions
  ↓
Draft Prompt Version
  ↓
Human Approval
  ↓
Activation
Job: Generate Draft Prompts
jobs/prompt_update_job.py
from app.analytics.prompt_optimizer import collect_prompt_signals
from app.analytics.prompt_optimizer import generate_prompt_update
from app.data_access.prompt_repo import create_prompt_version


async def run_prompt_update(tenant_id: str):
    signals = await collect_prompt_signals(tenant_id)

    if not signals:
        return

    suggestion = await generate_prompt_update(signals)

    await create_prompt_version(
        prompt_name="decision_generation",
        content=suggestion,
        created_by="system"
    )
Scheduler Integration

Add to runner:

await run_prompt_update("demo-tenant")
🔷 SAFETY RULES (CRITICAL)

Never auto-activate prompts.

Pipeline must be:

system generates → human approves → system activates
🔷 OPTIONAL: Prompt Diff Viewer

Add later:

v1 → v2 comparison
highlight rule changes
🔥 FINAL SYSTEM (NOW COMPLETE)
Decision Engine
  ↓
Outcome Tracking
  ↓
Calibration + Signals
  ↓
Failure Clustering
  ↓
Prompt Optimization
  ↓
Versioned Prompts
  ↓
Admin Approval
  ↓
Safe Deployment
🔥 What You Actually Built (No fluff)

You now have:

✔ Controlled AI evolution

Not random prompt tweaking

✔ Measurable intelligence

Confidence vs reality tracked

✔ Governance layer

Required for enterprise + compliance

✔ Continuous improvement loop

Without risk of silent regressions

🔥 My Direct Recommendation (Next Move)

Now that this is in place:

👉 Add Prompt Performance Tracking

Track:

which prompt version produced each decision
accuracy by prompt version
🧭 Bottom Line

You now have:

A decision system that improves itself
without losing control

That is the difference between:

AI tool
vs
AI infrastructure
