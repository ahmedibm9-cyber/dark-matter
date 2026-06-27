# Graph Schema Specification

> **Status:** Draft v0.1 — Not yet ratified
> **Part of:** Aether Intelligence Platform
> **Scope:** Node types, edge types, properties, lifecycle, identity, versioning

---

## 1. Identity System

### 1.1 ID Format

Every entity has a stable, never-recycled identifier.

```
Format: <KIND>-<SEQUENCE>
Example: FILE-0042, CLASS-0091, API-0183

Rules:
- KIND is a 2-8 character uppercase mnemonic
- SEQUENCE is zero-padded to minimum 4 digits
- IDs are never deleted — only deprecated or superseded
- An ID's kind never changes over its lifetime
- Sequence assignment: monotonically increasing per-kind counter
```

### 1.2 Kind Mnemonics

| Kind | Mnemonic | Example |
|------|----------|---------|
| Project | `PROJ` | PROJ-0001 |
| Repository | `REPO` | REPO-0001 |
| Directory | `DIR` | DIR-0042 |
| File | `FILE` | FILE-1832 |
| Class | `CLASS` | CLASS-0092 |
| Interface | `IFACE` | IFACE-0007 |
| Function | `FUNC` | FUNC-0822 |
| Method | `METH` | METH-0044 |
| Variable | `VAR` | VAR-0017 |
| Module | `MOD` | MOD-0003 |
| API | `API` | API-0183 |
| API Endpoint | `ENDPT` | ENDPT-0051 |
| Database | `DB` | DB-0001 |
| Table | `TABLE` | TABLE-0033 |
| Column | `COL` | COL-0184 |
| Index | `IDX` | IDX-0009 |
| Constraint | `CONSTR` | CONSTR-0002 |
| Workflow | `WF` | WF-0007 |
| Business Rule | `BR` | BR-0012 |
| Feature | `FEAT` | FEAT-0001 |
| Test | `TEST` | TEST-0442 |
| Test Suite | `TSUITE` | TSUITE-0011 |
| Bug | `BUG` | BUG-0317 |
| Issue | `ISSUE` | ISSUE-0142 |
| Decision | `DEC` | DEC-0031 |
| ADR | `ADR` | ADR-0005 |
| Requirement | `REQ` | REQ-0088 |
| Risk | `RISK` | RISK-0019 |
| Dependency | `DEP` | DEP-0092 |
| External Service | `EXT` | EXT-0004 |
| Configuration | `CFG` | CFG-0013 |
| Build | `BUILD` | BUILD-0047 |
| Release | `REL` | REL-0009 |
| Deployment | `DEPLOY` | DEPLOY-0012 |
| Pipeline | `PIPE` | PIPE-0003 |
| Task | `TASK` | TASK-0055 |
| Document | `DOC` | DOC-0022 |
| Prompt | `PROMPT` | PROMPT-0008 |
| Agent | `AGENT` | AGENT-0001 |
| Model (LLM) | `MODEL` | MODEL-0003 |
| MCP Server | `MCP` | MCP-0001 |
| Metric | `METRIC` | METRIC-0017 |
| Evidence | `EVID` | EVID-0991 |
| Event | `EVENT` | EVENT-0301 |
| Fact | `FACT` | FACT-2882 |
| Unknown | `UNK` | UNK-0007 |
| Assumption | `ASSUME` | ASSUME-0004 |
| Verification | `VERIFY` | VERIFY-0011 |
| Claim | `CLAIM` | CLAIM-0006 |

---

## 2. Node Types

Every node follows this base structure:

```yaml
BaseNode:
  id: str                # Stable identifier (KIND-XXXX)
  kind: str              # Node kind (matches ID prefix)
  name: str              # Human-readable name
  properties: dict       # Kind-specific properties (schema-validated)
  created: timestamp     # First observed
  modified: timestamp    # Last property change
  observed: timestamp    # Last confirmed to exist
  verified: timestamp    # Last independently verified
  expired: timestamp     # Null until deprecated
  evidence_refs: str[]   # IDs of supporting evidence
  confidence: float      # Computed [0.0, 1.0] — never stored directly
  tags: str[]            # Arbitrary classification labels
  checksum: str          # Hash of (kind + properties + evidence_refs)
```

### 2.1 Project

```yaml
Project:
  id: PROJ-XXXX
  properties:
    description: str
    language: str          # Primary programming language
    frameworks: str[]      # Detected frameworks
    domain: str            # Business domain
    created_date: timestamp
    version: str
  validation:
    required: [description, language]
```

### 2.2 Repository

```yaml
Repository:
  id: REPO-XXXX
  properties:
    url: str              # Remote URL
    default_branch: str
    git_sha: str          # HEAD commit
    root_path: path
    languages: dict       # Language -> bytes
    total_files: int
    total_lines: int
  validation:
    required: [url, root_path]
```

### 2.3 Directory

```yaml
Directory:
  id: DIR-XXXX
  properties:
    path: path             # Absolute path
    relative_path: str     # Relative to repo root
    depth: int
    file_count: int
    purpose: str           # Inferred category (src, test, docs, config, etc.)
  validation:
    required: [path]
```

### 2.4 File

```yaml
File:
  id: FILE-XXXX
  properties:
    path: path
    relative_path: str
    extension: str
    size_bytes: int
    line_count: int
    language: str          # Detected
    encoding: str
    created: timestamp     # Git history
    last_modified: timestamp
    hash: str              # Content hash
    purpose: str           # Code, test, config, docs, data, etc.
    classification: str    # Source, generated, vendored, ignored
  validation:
    required: [path, hash]
```

### 2.5 Module

```yaml
Module:
  id: MOD-XXXX
  properties:
    name: str
    path: path
    language: str
    type: str              # Package, namespace, library
    exports: str[]         # Public API symbols
  validation:
    required: [name, path]
```

### 2.6 Class

```yaml
Class:
  id: CLASS-XXXX
  properties:
    name: str
    full_name: str         # Qualified name
    visibility: str        # public, private, internal, protected
    kind: str              # class, abstract, static, singleton, data, mixin
    superclasses: str[]    # Direct parent classes
    interfaces: str[]      # Implemented interfaces
    mixins: str[]
    methods: int
    properties: int        # Class-level attributes
    lines: int
    complexity: float      # Cyclomatic complexity
  validation:
    required: [name, full_name]
```

### 2.7 Interface

```yaml
Interface:
  id: IFACE-XXXX
  properties:
    name: str
    full_name: str
    visibility: str
    methods: str[]
    properties: str[]
    implementations: int   # Count of known implementors
    lines: int
  validation:
    required: [name, full_name]
```

### 2.8 Function

```yaml
Function:
  id: FUNC-XXXX
  properties:
    name: str
    full_name: str
    visibility: str
    kind: str              # function, method, lambda, async, generator
    parameters: param[]
    return_type: str
    lines: int
    complexity: float
    is_async: bool
    is_generator: bool
    has_side_effects: bool
    docstring: str
  validation:
    required: [name, full_name]
```

### 2.9 API

```yaml
API:
  id: API-XXXX
  properties:
    name: str
    version: str
    base_url: str
    protocol: str          # REST, GraphQL, gRPC, WebSocket, SOAP
    authentication: str[]  # Detected auth methods
    endpoints: int
    documentation: str
    spec_file: str         # OpenAPI, GraphQL schema, etc.
  validation:
    required: [name, protocol]
```

### 2.10 API Endpoint

```yaml
APIEndpoint:
  id: ENDPT-XXXX
  properties:
    path: str
    method: str            # GET, POST, PUT, DELETE, PATCH, etc.
    operation_id: str
    summary: str
    parameters: param[]
    request_body: schema
    responses: response[]
    authentication: str
    rate_limit: str
    deprecated: bool
  validation:
    required: [path, method]
```

### 2.11 Database

```yaml
Database:
  id: DB-XXXX
  properties:
    name: str
    kind: str              # PostgreSQL, MySQL, SQLite, MongoDB, Redis, etc.
    version: str
    connection_string: str  # URI format (redacted)
    tables: int
    size_bytes: int
    host: str              # inference target, not literal
    purpose: str           # Primary, cache, queue, analytics, etc.
  validation:
    required: [name, kind]
```

### 2.12 Table

```yaml
Table:
  id: TABLE-XXXX
  properties:
    name: str
    schema: str
    columns: int
    row_estimate: int
    primary_key: str
    foreign_keys: str[]
    indexes: str[]
    engine: str            # InnoDB, MyISAM, etc.
    charset: str
    purpose: str
  validation:
    required: [name]
```

### 2.13 Column

```yaml
Column:
  id: COL-XXXX
  properties:
    name: str
    data_type: str
    nullable: bool
    default: str
    is_primary_key: bool
    is_foreign_key: bool
    is_unique: bool
    is_indexed: bool
    max_length: int
    enum_values: str[]
    description: str
  validation:
    required: [name, data_type]
```

### 2.14 Workflow

```yaml
Workflow:
  id: WF-XXXX
  properties:
    name: str
    description: str
    trigger: str           # Event, schedule, manual, webhook
    steps: int
    critical: bool
    failure_impact: str
    sla: str
    owner: str
    documentation: str
  validation:
    required: [name, trigger]
```

### 2.15 Business Rule

```yaml
BusinessRule:
  id: BR-XXXX
  properties:
    name: str
    description: str
    category: str          # Validation, calculation, workflow, access, compliance
    expression: str        # The rule logic in pseudo-code
    source: str            # Where it originates (legal, product, domain)
    priority: str          # Critical, high, medium, low
    test_coverage: bool
    last_reviewed: timestamp
    violations: str[]      # Known violation scenarios
  validation:
    required: [name, category]
```

### 2.16 Feature

```yaml
Feature:
  id: FEAT-XXXX
  properties:
    name: str
    description: str
    category: str
    status: str            # active, deprecated, planned, removed
    owner: str
    launch_date: timestamp
    deprecated_date: timestamp
    dependencies: str[]    # Feature IDs
    documentation: str[]
  validation:
    required: [name, status]
```

### 2.17 Dependency

```yaml
Dependency:
  id: DEP-XXXX
  properties:
    name: str
    version: str
    latest_version: str
    kind: str              # runtime, dev, build, test, optional, peer
    source: str            # npm, pip, cargo, maven, go, nuget, gem, etc.
    license: str
    security_advisories: str[]
    is_direct: bool
    is_outdated: bool
    deprecation_status: str
    health: str            # Maintained, archived, unmaintained, unknown
  validation:
    required: [name, kind, source]
```

### 2.18 Test

```yaml
Test:
  id: TEST-XXXX
  properties:
    name: str
    file: path
    kind: str              # unit, integration, e2e, snapshot, property, smoke
    framework: str
    coverage_target: str
    status: str            # passing, failing, skipped, flaky
    last_run: timestamp
    duration_ms: int
    flakiness_score: float
  validation:
    required: [name, file, kind]
```

### 2.19 Decision

```yaml
Decision:
  id: DEC-XXXX
  properties:
    title: str
    context: str           # Why this decision was needed
    options: str[]         # Alternatives considered
    selected: str          # Option chosen
    rationale: str         # Why this option won
    rejected_reasons: str[] # Why other options lost
    predicted_impact: str  # Expected consequences
    actual_impact: str     # Actual consequences (filled later)
    status: str            # proposed, accepted, superseded, rejected
    confidence: str        # predicted vs actual assessment
    revisit_date: timestamp
    category: str          # architecture, technology, process, product
  validation:
    required: [title, context, selected]
```

### 2.20 Risk

```yaml
Risk:
  id: RISK-XXXX
  properties:
    description: str
    category: str          # security, performance, reliability, compliance, cost, bus factor
    probability: float     # 0.0 - 1.0
    impact: str            # critical, high, medium, low
    score: float           # probability × impact
    mitigation: str
    owner: str
    status: str            # open, mitigated, accepted, resolved
    discovered: timestamp
  validation:
    required: [description, category]
```

### 2.21 Unknown

```yaml
Unknown:
  id: UNK-XXXX
  properties:
    topic: str             # What is unknown
    reason: str            # Why it's unknown
    evidence_gap: str      # What evidence is missing
    required_collector: str # What collector could fill the gap
    priority: str          # Critical, high, medium, low
    blocks: str[]          # What this unknown blocks
    confidence_gain: float # Estimated improvement if resolved
    status: str            # open, collecting, resolved, stale
    created: timestamp
    resolved: timestamp
  validation:
    required: [topic, reason, priority]
```

### 2.22 Assumption

```yaml
Assumption:
  id: ASSUME-XXXX
  properties:
    statement: str
    evidence_found: str[]
    evidence_missing: str[]
    confidence: float
    status: str            # unverified, confirmed, contradicted, pending
    created: timestamp
    verified: timestamp
    source: str            # What generated this assumption (audit, AI, human)
  validation:
    required: [statement, status]
```

### 2.23 Evidence

```yaml
Evidence:
  id: EVID-XXXX
  properties:
    kind: str              # file, test, config, log, runtime, git, document, claim
    source: str            # Collector or method that produced it
    source_id: str         # Collector-specific identifier
    payload: dict          # Collected data
    confidence_weight: float # How definitive this evidence type is
    observed: timestamp
    hash: str              # Payload hash
    expires: timestamp     # Null if permanent
    tags: str[]
  validation:
    required: [kind, source, payload, hash]
  lifecycle:
    - Immutable once committed
    - Never deleted, only superseded by newer evidence
    - Hash-addressable for deduplication
```

### 2.24 Verification

```yaml
Verification:
  id: VERIFY-XXXX
  properties:
    claim: str             # What was verified
    claim_id: str          # Reference to claim/assertion
    evidence_refs: str[]   # Evidence supporting the claim
    method: str            # test, review, measure, artifact, runtime, human
    result: str            # verified, rejected, inconclusive, pending
    confidence: float
    verifier: str          # Who/what performed the verification
    timestamp: timestamp
    notes: str
  validation:
    required: [claim, method, result]
```

### 2.25 Event

```yaml
Event:
  id: EVENT-XXXX
  properties:
    kind: str              # EVIDENCE_INGESTED, NODE_CREATED, NODE_UPDATED, etc.
    entity_id: str         # Affected entity
    entity_kind: str       # Node kind affected
    evidence_ref: str      # Evidence that triggered the event
    payload: dict          # Event-specific data
    timestamp: timestamp
    sequence: int          # Monotonically increasing per-repository
    parent_id: str         # Previous event in chain (for replay ordering)
  validation:
    required: [kind, entity_id, timestamp, sequence]
  lifecycle:
    - Append-only
    - Never mutated or deleted
    - Source of truth for graph state
```

---

## 3. Edge Types

Every edge follows this structure:

```yaml
BaseEdge:
  source_id: str         # Source node ID
  target_id: str         # Target node ID
  kind: str              # Relationship kind
  properties: dict       # Edge-specific properties
  evidence_refs: str[]   # Supporting evidence
  confidence: float      # Computed
  created: timestamp
  modified: timestamp
  checksum: str
```

### 3.1 Containment Edges

| Edge | Source | Target | Meaning | Properties |
|------|--------|--------|---------|------------|
| `CONTAINS` | Directory | Directory | Nested directory | depth |
| `CONTAINS` | Directory | File | File in directory | |
| `CONTAINS` | Module | Class | Class belongs to module | |
| `CONTAINS` | Module | Function | Function belongs to module | |
| `CONTAINS` | Module | Interface | Interface belongs to module | |
| `CONTAINS` | Class | Function | Method in class | visibility |
| `CONTAINS` | Class | Variable | Class attribute | visibility |
| `CONTAINS` | Database | Table | Table in database | |
| `CONTAINS` | Table | Column | Column in table | ordinal |
| `CONTAINS` | Feature | BusinessRule | Feature has business rule | |
| `CONTAINS` | TestSuite | Test | Test belongs to suite | |
| `CONTAINS` | Repository | Directory | Root directories | |
| `CONTAINS` | Repository | Module | Top-level modules | |
| `CONTAINS` | API | APIEndpoint | Endpoint belongs to API | |

### 3.2 Dependency Edges

| Edge | Source | Target | Meaning | Properties |
|------|--------|--------|---------|------------|
| `IMPORTS` | File | File | File imports another | symbol, line |
| `IMPORTS` | File | Module | File imports module | symbol |
| `IMPORTS` | File | Dependency | File uses external dep | symbol, line |
| `DEPENDS_ON` | Feature | Feature | Feature depends on another | kind (hard, soft, optional) |
| `DEPENDS_ON` | Module | Module | Module coupling | kind, strength |
| `DEPENDS_ON` | Class | Class | Class uses another | kind, line |
| `DEPENDS_ON` | Workflow | Workflow | Workflow sequence | order |
| `DEPENDS_ON` | Repository | Dependency | Project dependency | scope |

### 3.3 Ownership Edges

| Edge | Source | Target | Meaning | Properties |
|------|--------|--------|---------|------------|
| `OWNS` | Module | File | Module owns file | |
| `OWNS` | Feature | File | Feature owns file | |
| `OWNS` | Team | Module | Team owns module | (future) |
| `OWNS` | Person | Module | Person owns module | (future) |

### 3.4 Implementation Edges

| Edge | Source | Target | Meaning | Properties |
|------|--------|--------|---------|------------|
| `IMPLEMENTS` | Class | Interface | Class implements interface | |
| `IMPLEMENTS` | Class | Class | Class extends superclass | |
| `IMPLEMENTS` | Function | APIEndpoint | Function handles endpoint | |
| `IMPLEMENTS` | Function | BusinessRule | Function implements rule | |
| `IMPLEMENTS` | Feature | BusinessRule | Feature implements rule | |
| `IMPLEMENTS` | Test | Feature | Test covers feature | |
| `IMPLEMENTS` | Test | Function | Test covers function | |
| `IMPLEMENTS` | Test | APIEndpoint | Test covers endpoint | |

### 3.5 Evidence Edges

| Edge | Source | Target | Meaning | Properties |
|------|--------|--------|---------|------------|
| `EVIDENCE_FOR` | Evidence | Node | Evidence supports node existence | weight |
| `EVIDENCE_FOR` | Evidence | Edge | Evidence supports edge | weight |
| `EVIDENCE_FOR` | Evidence | Fact | Evidence supports fact | weight |
| `EVIDENCE_AGAINST` | Evidence | Node | Evidence contradicts node | weight |
| `VERIFIED_BY` | Claim | Verification | Claim has verification | result |

### 3.6 Knowledge Edges

| Edge | Source | Target | Meaning | Properties |
|------|--------|--------|---------|------------|
| `REFERENCES` | Node | Node | Generic reference | context |
| `DOCUMENTS` | Document | Node | Document describes node | |
| `DOCUMENTS` | Prompt | Node | Prompt operationalizes node | |
| `GENERATES` | Node | Node | One generates another | context |
| `SUPERSEDES` | Node | Node | Replaces another | |
| `BLOCKS` | Unknown | Node | Unknown blocks knowledge of node | |
| `RELATES_TO` | Node | Node | Arbitrary semantic relationship | relationship_type, context |

### 3.7 Change Edges

| Edge | Source | Target | Meaning | Properties |
|------|--------|--------|---------|------------|
| `CREATED_BY` | Node | Event | Node created by event | |
| `MODIFIED_BY` | Node | Event | Node modified by event | |
| `CAUSED_BY` | Event | Evidence | Event triggered by evidence | |
| `TRIGGERED_BY` | Workflow | Event | Workflow triggered by event | |

### 3.8 Temporal Edges

| Edge | Source | Target | Meaning | Properties |
|------|--------|--------|---------|------------|
| `PRECEDES` | Event | Event | Event order | |
| `PRECEDES` | Decision | Decision | Decision chronology | |
| `PRECEDES` | Release | Release | Release sequence | |
| `CAUSES` | Decision | Node | Decision led to node | impact |

---

## 4. Schema Validation Rules

### 4.1 Required Fields

Every node kind has a set of required fields that must be present to create or update a node. If required evidence is missing, the node is created with an associated `Unknown` entry.

### 4.2 Field Constraints

| Constraint | Applies To | Behavior |
|------------|------------|----------|
| `required` | Any field | Node creation fails without it |
| `immutable` | id, kind, created, checksum | Cannot change after creation |
| `computed` | confidence, health, trust | Never stored, calculated on query |
| `versioned` | Any field | History preserved in event log |
| `indexed` | Any field | Query engine builds index |
| `unique` | name, path, hash | Enforced within kind |

### 4.3 Type Constraints

- `str`: UTF-8 string
- `int`: 64-bit signed integer
- `float`: 64-bit IEEE 754
- `bool`: true/false
- `timestamp`: ISO 8601 with timezone
- `path`: Absolute or relative filesystem path
- `str[]`: Array of strings
- `dict`: Key-value map (schema may specify sub-fields)
- `schema`: Nested object with its own validation

---

## 5. Lifecycle

### 5.1 Node Lifecycle

```
Unknown (Evidence Gap)
    │
    ▼
Discovered (First evidence observed)
    │
    ▼
Active (Regularly observed and verified)
    │
    ├──→ Modified (Properties change)
    │       │
    │       ▼
    │   Active (re-verified)
    │
    ├──→ Stale (Not observed recently)
    │       │
    │       ├──→ Active (re-observed)
    │       └──→ Deprecated (expired + no re-observation)
    │
    └──→ Deprecated (Explicitly superseded or removed)
            │
            └──→ Archived (After retention period)
```

### 5.2 Evidence Lifecycle

```
Collected
    │
    ▼
Ingested (Immutably stored)
    │
    ├──→ Superseded (Newer evidence replaces)
    └──→ Expired (Temporary evidence type times out)
```

### 5.3 Event Lifecycle

```
Created (Append-only)
    │
    ▼
Committed (Part of event log)
    │
    └──→ Replayed (Used in graph reconstruction)
```

---

## 6. Versioning

### 6.1 Graph Version

The entire knowledge graph has a version:

```
Format: <epoch>.<sequence>
Example: 1.442

- Epoch: Incremented on breaking schema changes
- Sequence: Incremented on every event
```

### 6.2 Schema Version

```
Format: <MAJOR>.<MINOR>.<PATCH>
Example: 1.3.0

MAJOR: Breaking node/edge schema changes
MINOR: Non-breaking additions (new fields, new node kinds)
PATCH: Validation rules, metadata changes
```

### 6.3 Node Versioning

Nodes are not versioned individually. Instead, the event log captures every state change. To reconstruct a node at a point in time:

```
node_state(id, timestamp) =
    fold events_before(timestamp) over base_state
```

---

## 7. Graph Constraints

### 7.1 Structural Constraints

- Every node must have at least one evidence reference to exist
- Every edge must reference a valid source and target node
- No dangling edges (edges removed if either endpoint is deprecated)
- IDs are globally unique across all node kinds
- Path-based nodes (File, Directory) are unique per path

### 7.2 Integrity Constraints

- Event CRDT: commutative, idempotent, conflict-free across concurrent collectors
- Checksum verification on every read
- Evidence immutability: once committed, evidence payloads are never modified
- Replay must produce identical graph state given same events

---

## 8. Query Model

The graph supports these query primitives:

```
1. Get node by ID
2. Get neighbors (inbound, outbound, depth-limited)
3. Path between two nodes (with edge kind filter)
4. Subgraph (nodes of given kinds within N hops)
5. Pattern match (source -[edge]-> target with property filters)
6. Time-travel (state at given timestamp)
7. Confidence filter (nodes/edges with confidence >= threshold)
8. Unknowns blocking a subgraph
9. Verification coverage for a feature
10. Evidence trail for a fact
```

These primitives are exposed through:
- A Python query API in the core library
- A CLI (`aether query "..."`)
- Eventually a dedicated query language
