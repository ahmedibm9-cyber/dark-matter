# Architecture Specification

> **Status:** Draft v0.1 — Not yet ratified
> **Project:** Dark Matter Intelligence Platform
> **Scope:** Subsystem boundaries, data flow, trust model, design requirements

---

## 0. Naming

The current project uses "brain" as its central metaphor. This is overloaded (project brain, repository brain, AI brain, knowledge brain) and conflates the platform with one of its outputs.

Proposed names for discussion:

| Name | Rationale |
|------|-----------|
| **Aether** | The medium through which knowledge propagates — neutral, precise, unused |
| **Kernel** | The intelligence core of a repository — evokes OS architecture |
| **Nexus** | The connection point where facts, evidence, and inference converge |
| **Loom** | Weaves raw evidence into structured knowledge |

This document uses **Dark Matter** as the project name.

---

## 1. Design Requirements

The following 15 requirements are architectural invariants. Every subsystem decision must satisfy them.

| # | Requirement | Implication |
|---|-------------|-------------|
| 1 | **Event-sourced, not state-based** | Graph is never edited directly. Only events modify state. Full replayability. |
| 2 | **Every fact needs provenance** | No node, edge, or property exists without traceable evidence. |
| 3 | **Separate facts from inferences** | Computed metrics (health, risk, trust) are derived views, not stored data. |
| 4 | **Real type system** | Every node kind has a schema — required fields, optional fields, validation, identity rules. |
| 5 | **Separate evidence from knowledge** | Evidence is immutable and preserved forever. Knowledge is regenerable from evidence. |
| 6 | **Rule engine** | Inference is data-driven. Adding a new rule never requires changing the engine. |
| 7 | **Everything needs IDs** | Stable, kind-scoped, never-recycled identifiers for every entity. |
| 8 | **Incremental intelligence** | Only re-process what changed. Milliseconds per commit, not minutes. |
| 9 | **Confidence mathematics** | Confidence is computed from evidence quality, count, source trust, freshness, agreement, and verification. |
| 10 | **Unknown is first-class** | Unknowns are tracked with reason, missing collector, priority, and estimated confidence gain. |
| 11 | **Collectors are plug-ins** | Every collector implements `collect() -> Evidence[]`. No hardcoded scanners. |
| 12 | **Compiler with multiple targets** | One intelligence source compiles to `.ai`, Markdown, JSON, dashboards, etc. |
| 13 | **Query language** | Structured queries over the knowledge graph (not just file grep). |
| 14 | **Time is first-class** | Every entity has created/modified/observed/verified/expired timestamps. Point-in-time queries. |
| 15 | **AI-replaceable** | AI never writes to the graph directly. AI produces claims → evidence → verifier → graph. |

---

## 2. Subsystem Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            COLLECTOR LAYER                                  │
│                                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Filesystem│ │   Git    │ │   AST    │ │ Runtime  │ │   API    │  ...      │
│  │ Collector│ │ Collector│ │ Collector│ │ Collector│ │ Collector│          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘          │
│       │            │            │            │            │                  │
│       └────────────┴────────────┴────────────┴────────────┘                  │
│                                │                                             │
│                         Evidence[]                                           │
└────────────────────────────────┼─────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            EVIDENCE LAYER                                   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Evidence Store                                │  │
│  │  Immutable append-only log. Every evidence item has source,          │  │
│  │  timestamp, hash, collector_id, and payload.                         │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                 │                                           │
│                          Evidence Events                                    │
└────────────────────────────────┼─────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            INFERENCE LAYER                                  │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────────┐  │
│  │ Ingest      │→ │ Merge &     │→ │ Deduplicate  │→ │ Inferred Facts   │  │
│  │ Evidence    │  │ Normalize   │  │ & Resolve    │  │ & Relationships  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────┬─────────┘  │
│                                                              │             │
│                                     ┌────────────────────────┘             │
│                                     ▼                                     │
│                          ┌─────────────────────┐                          │
│                          │    Rule Engine       │                          │
│                          │  Data-driven rules   │                          │
│                          │  produce derived     │                          │
│                          │  facts, confidence   │                          │
│                          │  scores, unknowns    │                          │
│                          └─────────────────────┘                          │
│                                     │                                       │
│                            Graph Events                                     │
└────────────────────────────────┼─────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            KNOWLEDGE LAYER                                  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Knowledge Graph                              │  │
│  │  Materialized view of facts + relationships. Nodes, edges,          │  │
│  │  properties with evidence pointers, confidence, and timestamps.     │  │
│  │  Never edited directly — only via event replay.                     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     Verification Ledger                             │  │
│  │  Every claim maps to evidence. Every verification maps to a         │  │
│  │  confidence score. Trust is computed, not stated.                   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     Unknowns Database                               │  │
│  │  Tracked gaps: missing evidence, unobserved collectors, low          │  │
│  │  confidence areas. Priority-ranked for automated resolution.        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┼─────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            COMPILER LAYER                                   │
│                                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │.ai Pkg   │ │ Markdown │ │ Dashboard│ │   JSON   │ │ Neo4j    │  ...    │
│  │ Compiler │ │ Compiler │ │ Compiler │ │ Compiler │ │ Compiler │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘

         ┌──────────────────────────────────────────────────────┐
         │                    STORAGE LAYER                     │
         │                                                      │
         │  ┌─────────────────────────────────────────────────┐ │
         │  │           Store Interface (Abstract)            │ │
         │  │  CRUD · Query · Transaction · Migration         │ │
         │  └─────────────────────────────────────────────────┘ │
         │           ▲              ▲              ▲            │
         │           │              │              │            │
         │  ┌────────┴──┐   ┌──────┴──────┐   ┌───┴───────┐   │
         │  │ JSONStore │   │ SQLiteStore  │   │ Neo4jStore│   │
         │  │   (v1)    │   │   (v2)      │   │   (v3)    │   │
         │  └───────────┘   └─────────────┘   └───────────┘   │
         └──────────────────────────────────────────────────────┘
```

---

## 3. Trust Model

### 3.1 Trust Boundaries

```
┌─────────────────────────────────────────────────────┐
│                     TRUSTED                          │
│  ┌───────────────────────────────────────────────┐  │
│  │         Store Layer (persistence)             │  │
│  │   Events are cryptographically chainable.     │  │
│  │   Store is append-only for evidence.          │  │
│  └───────────────────────────────────────────────┘  │
│                         │                            │
│                         ▼                            │
│  ┌───────────────────────────────────────────────┐  │
│  │         Inference Layer (rules engine)        │  │
│  │   Rules are versioned, tested, reviewed.      │  │
│  │   Rule outputs are traceable to evidence.     │  │
│  └───────────────────────────────────────────────┘  │
│                         │                            │
│                         ▼                            │
│  ┌───────────────────────────────────────────────┐  │
│  │         Knowledge Layer (graph + ledger)      │  │
│  │   Never written directly. Only via events.    │  │
│  │   Immutable evidence trail for every node.    │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌────────┐    ┌──────────┐    ┌──────────┐
    │Collector│   │   CLI    │    │   AI     │
    │Plug-ins │   │  Tools   │    │  Models  │
    └────────┘    └──────────┘    └──────────┘
     UNTRUSTED      TRUSTED         UNTRUSTED
     (external)     (human)         (external)
```

### 3.2 AI Trust Boundary

The most important trust rule: **AI never writes to the graph directly.**

```
AI Model (untrusted)
    │
    │ Produces claim + evidence
    ▼
Claim Store (untrusted, reviewable)
    │
    │ Passes through verifier
    ▼
Verifier (trusted)
    │
    │ Applies rules, checks evidence
    ▼
Approved? ──No──→ Rejected (logged)
    │
    Yes
    ▼
Graph Event (trusted, immutably recorded)
    │
    ▼
Knowledge Graph updated
```

This means:
- Swapping one LLM for another never corrupts the knowledge base
- Every AI-generated claim is reviewable before it enters the graph
- The verifier is the gatekeeper, not the AI
- The system degrades gracefully: if the AI is unavailable, existing knowledge persists

---

## 4. Data Flow

### 4.1 Full Pipeline

```
Git Push / File Change / Timer
              │
              ▼
[Collector Plug-in] ──→ Evidence[]
              │
              ▼
[Evidence Store] ──→ events.log (append-only)
              │
              ▼
[Ingest Engine] ──→ Normalized Evidence
              │
              ▼
[Rule Engine] ──→ Facts, Relationships, Unknowns
              │
              ▼
[Graph Materializer] ──→ Graph Events
              │
              ▼
[Knowledge Graph] ──→ Verified, timestamped state
              │
              ├──→ [Compiler] ──→ repository.ai
              ├──→ [Compiler] ──→ Markdown
              ├──→ [Compiler] ──→ Dashboard
              └──→ [Query Engine]
```

### 4.2 Incremental Flow

```
Git Commit
    │
    ▼
Affected files identified
    │
    ▼
Only these files → Collectors → New Evidence
    │
    ▼
Only affected subgraph → Inference → Updated Facts
    │
    ▼
Only affected views → Compiler → Updated Outputs
```

### 4.3 Event Types

Every state change is an event:

| Event | Trigger | Payload |
|-------|---------|---------|
| `EVIDENCE_INGESTED` | Collector produces evidence | Evidence payload + source metadata |
| `NODE_CREATED` | Inference detects new entity | Node kind, properties, evidence ref |
| `NODE_UPDATED` | New evidence modifies properties | Diff + evidence ref |
| `NODE_DEPRECATED` | Evidence indicates removal or superseding | Deprecation reason + replacement ref |
| `EDGE_CREATED` | New relationship inferred | Source, target, kind, evidence ref |
| `EDGE_REMOVED` | Relationship no longer supported | Edge ref + evidence ref |
| `VERIFICATION_RECORDED` | Verifier processes claim | Claim ref, result, confidence |
| `UNKNOWN_IDENTIFIED` | Inference detects knowledge gap | Unknown record |
| `UNKNOWN_RESOLVED` | New evidence fills a gap | Unknown ref + resolution |

---

## 5. ID System

Every entity gets a stable, never-recycled ID.

```
Format: <KIND>-<SEQUENCE>

Examples:
FILE-0001
CLASS-0042
API-0183
RULE-0017
DECISION-0031
FACT-2882
EVIDENCE-0991
UNKNOWN-0007
```

- KIND is a 2-8 character uppercase mnemonic
- SEQUENCE is zero-padded to 4+ digits
- IDs are never deleted, only deprecated
- An ID's kind never changes over its lifetime
- Sequence assignment uses monotonically increasing counters (one per kind)

---

## 6. Time Model

Every entity carries timestamps:

| Field | Meaning | Mutable? |
|-------|---------|----------|
| `created` | When first observed | Immutable |
| `modified` | When properties last changed | Updated on event |
| `observed` | When last confirmed to exist | Updated on evidence |
| `verified` | When last verified against evidence | Updated on verification |
| `expired` | When entity becomes invalid | Set at deprecation |

This enables:
- Point-in-time graph queries ("show repository at commit X")
- Temporal drift detection ("architecture vs. three months ago")
- Staleness-aware confidence decay

---

## 7. Subsystem Responsibilities

| Subsystem | Owns | Does Not Own |
|-----------|------|--------------|
| **Collectors** | Evidence production, source metadata | Graph structure, inference, storage |
| **Evidence Store** | Immutable event log, evidence dedup | Knowledge semantics, rules |
| **Inference Engine** | Evidence→Facts transformation, rule execution | Persistence, collectors, views |
| **Rule Engine** | Rule definitions, confidence computation | Data storage, UI, collectors |
| **Knowledge Graph** | Materialized entity state, relationships | Direct mutation, inference logic |
| **Verification Ledger** | Claim→Evidence mapping, trust scores | Graph structure, rule definitions |
| **Unknowns DB** | Knowledge gap tracking, priority scoring | Evidence collection, graph queries |
| **Compiler** | Multi-target output generation | Graph state, inference, verification |
| **Query Engine** | Graph traversal, search, analysis | Persistence, output formatting |
| **Store** | Persistence, transactions, migration | Business logic, inference, views |

---

## 8. Collector Architecture

```
Collector Interface
━━━━━━━━━━━━━━━━━
collect(target: Path) → Evidence[]
name() → str
version() → str
dependencies() → str[]
capabilities() → CollectorCapability[]

CollectorCapability
━━━━━━━━━━━━━━━━━
id: str
description: str
evidence_kinds: EvidenceKind[]
```

Collectors are:
- Independently versioned
- Discoverable via plugin registry
- Isolated (one collector failure never blocks others)
- Resource-bounded (quota for file count, depth, time)

Built-in collector categories:
- Static: filesystem, git, AST, dependencies, docs
- Dynamic: runtime, tests, API probes, telemetry
- External: GitHub, Jira, Figma, Notion, MCP servers, Postman

---

## 9. Confidence Model

Confidence is computed, never stored directly.

```
Confidence =
    EvidenceQuality ×
    EvidenceCount ×
    SourceTrust ×
    Freshness ×
    Agreement ×
    VerificationState
```

Each factor is a float [0.0, 1.0]:

| Factor | Basis |
|--------|-------|
| EvidenceQuality | How definitive the evidence type is (AST > grep > comment) |
| EvidenceCount | Number of independent sources supporting the claim |
| SourceTrust | Trust score of the collector or source that produced the evidence |
| Freshness | Decay function based on time since last observation |
| Agreement | Proportion of evidence sources that agree on the claim |
| VerificationState | 1.0 if independently verified, 0.5 if inferred, 0.0 if unverified |

---

## 10. Scalability Principles

- **Collection**: Parallelizable per collector plugin. No cross-collector coordination.
- **Inference**: Scoped to affected subgraph. Not a full rebuild.
- **Storage**: Store abstraction allows swap from JSON (single-repo) to SQLite (multi-repo) to Neo4j (enterprise).
- **Compiler**: Independent per target. Can be parallelized or distributed.
- **Query**: Graph traversal is bounded by edge hops. Default max depth = 5.
