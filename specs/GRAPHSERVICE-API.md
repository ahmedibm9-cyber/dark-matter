# GraphService API Specification v1

> **Status:** Draft
> **Part of:** Aether Intelligence Platform
> **Scope:** Canonical interface for all graph mutations and queries

---

## 1. Rationale

Currently, the pipeline and store have no clear boundary. Collectors,
inference engines, and compilers all reach into storage directly.
This coupling prevents independent evolution of any layer.

The GraphService is the single canonical API through which all graph
mutations and queries must pass. No component — collector, rule, reasoner,
verifier, compiler, or CLI — accesses storage directly.

---

## 2. Design Principle

> **Everything goes through GraphService. Nothing goes around it.**

This means:
- No component imports the store
- No component writes files in `.aether/`
- No component reads raw JSON from disk
- Every state change is recorded as an event
- Every query is a method call, not a file read

---

## 3. GraphService Interface

```python
class GraphService:
    """
    Single canonical interface for graph operations.
    Every mutation, query, and verification goes through this service.
    The service wraps the store, enforces contracts, records events,
    and maintains invariants.
    """
```

### 3.1 Lifecycle

```python
def initialize(self, config: ServiceConfig) -> None:
    """
    Initialize the graph service.
    Opens or creates the store, verifies schema version,
    replays events if recovery is needed.
    """

def close(self) -> None:
    """Flush and release resources."""

@contextmanager
def transaction(self) -> Generator[Transaction, None, None]:
    """
    Begin a transactional scope.
    All mutations within the scope commit or roll back atomically.
    """
```

### 3.2 Node Operations

```python
def create_node(self, kind: str, name: str, properties: dict,
                evidence_refs: list[str], tags: list[str] = None) -> NodeResult:
    """
    Create a new node.
    - Assigns stable ID (KIND-XXXXX)
    - Validates kind against schema registry
    - Validates required properties
    - Records NODE_CREATED event
    - Returns created node or error
    """

def update_node(self, node_id: str, properties: dict = None,
                evidence_refs: list[str] = None,
                tags: list[str] = None) -> NodeResult:
    """
    Update node properties.
    - Merges provided properties with existing
    - Validates against schema
    - Records NODE_UPDATED event
    - Updates modified and observed timestamps
    """

def deprecate_node(self, node_id: str, reason: str,
                   replacement_id: str = None) -> NodeResult:
    """
    Mark a node as deprecated.
    - Sets expired timestamp
    - Links to replacement node if provided
    - Does NOT delete the node
    - Records NODE_DEPRECATED event
    """

def reactivate_node(self, node_id: str, evidence_refs: list[str]) -> NodeResult:
    """
    Reactivate a previously deprecated node.
    - Clears expired timestamp
    - Requires new evidence
    - Records NODE_REACTIVATED event
    """

def get_node(self, node_id: str) -> Optional[Node]:
    """Retrieve node by ID. Returns None if not found."""

def find_nodes(self, query: NodeQuery) -> list[Node]:
    """Search nodes by kind, properties, tags, confidence, time window."""
```

### 3.3 Edge Operations

```python
def create_edge(self, source_id: str, target_id: str, kind: str,
                properties: dict = None,
                evidence_refs: list[str] = None) -> EdgeResult:
    """
    Create an edge between two nodes.
    - Validates source and target exist
    - Validates edge kind against schema
    - Checks for duplicate (source, target, kind)
    - Records EDGE_CREATED event
    """

def delete_edge(self, source_id: str, target_id: str, kind: str,
                reason: str = None) -> EdgeResult:
    """
    Remove an edge.
    - Does not delete the nodes
    - Records EDGE_DELETED event
    """

def get_edges(self, query: EdgeQuery) -> list[Edge]:
    """Search edges by kind, source, target, properties."""

def replace_edges(self, source_id: str, target_id: str,
                  old_kind: str, new_kind: str,
                  properties: dict = None,
                  evidence_refs: list[str] = None) -> EdgeResult:
    """
    Atomically replace an edge: delete old kind, create new kind.
    Used when a relationship's nature changes (e.g., depends_on -> implements).
    Records both EDGE_DELETED and EDGE_CREATED in one transaction.
    """
```

### 3.4 Evidence Operations

```python
def store_evidence(self, evidence: EvidenceInput) -> EvidenceResult:
    """
    Store evidence immutably.
    - Computes content hash
    - Deduplicates by hash
    - Returns existing ID if duplicate
    - Records EVIDENCE_INGESTED event (on first occurrence)
    - Evidence is immutable once stored
    """

def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
    """Retrieve evidence by ID."""

def find_evidence(self, query: EvidenceQuery) -> list[Evidence]:
    """Search evidence by kind, source, time range, tags."""
```

### 3.5 Fact Operations

```python
def record_fact(self, statement: str, category: str,
                rule_id: str, evidence_refs: list[str],
                confidence: float) -> FactResult:
    """
    Record an inferred fact.
    - Links fact to deriving rule and supporting evidence
    - Does NOT deduplicate facts (same statement from new evidence is new fact)
    - Records FACT_RECORDED event
    """

def get_facts(self, query: FactQuery) -> list[Fact]:
    """Search facts by statement, category, rule, confidence range."""

def invalidate_fact(self, fact_id: str, reason: str,
                    replacement_fact_id: str = None) -> FactResult:
    """
    Mark a fact as invalid (contradicted by newer evidence).
    Does not delete — preserves history.
    Records FACT_INVALIDATED event.
    """
```

### 3.6 Verification Operations

```python
def record_verification(self, claim: str, evidence_refs: list[str],
                        method: str, result: str,
                        confidence: float) -> VerificationResult:
    """
    Record a verification result.
    - Every verification is immutable once recorded
    - Records VERIFICATION_RECORDED event
    """

def get_verifications(self, query: VerificationQuery) -> list[Verification]:
    """Search verifications by claim, result, method, time."""
```

### 3.7 Unknown Operations

```python
def record_unknown(self, topic: str, reason: str,
                   required_capability: str = None,
                   priority: str = "medium") -> UnknownResult:
    """
    Record a knowledge gap.
    - Unknowns are first-class entities
    - Can be resolved when new evidence arrives
    - Records UNKNOWN_IDENTIFIED event
    """

def resolve_unknown(self, unknown_id: str,
                    resolution_evidence: str) -> UnknownResult:
    """
    Mark an unknown as resolved.
    - Links resolution to evidence
    - Records UNKNOWN_RESOLVED event
    """

def get_unknowns(self, query: UnknownQuery) -> list[Unknown]:
    """Search unknowns by topic, priority, status."""
```

### 3.8 Query Operations

```python
def query(self, request: GraphQuery) -> QueryResult:
    """
    General graph query interface.
    Supports:
    - Get node by ID
    - Get neighbors (depth-limited, kind-filtered)
    - Path finding (shortest path, all paths, bounded depth)
    - Subgraph extraction (root node + N hops + kind filters)
    - Pattern matching (source -[edge]-> target with property filters)
    """

def explain(self, node_id: str) -> Explanation:
    """
    Return the complete provenance chain for a node:
    - Evidence that created it
    - Rules that inferred facts about it
    - Verifications that confirmed it
    - Events that modified it
    - Confidence decomposition
    """

def state_at(self, timestamp: datetime) -> GraphSnapshot:
    """
    Return the graph state as it existed at a given timestamp.
    Requires event-sourced store.
    """
```

### 3.9 Bulk Operations

```python
def import_snapshot(self, snapshot: dict, source: str) -> BulkResult:
    """
    Import a pre-built graph snapshot.
    - Validates every node, edge, and evidence
    - Records one BULK_IMPORT event
    - Returns counts of imported/rejected/skipped entities
    """

def export_snapshot(self) -> dict:
    """
    Export entire graph state as a portable snapshot.
    Includes all nodes, edges, evidence, facts, verifications.
    """
```

---

## 4. Contract Enforcement

The GraphService enforces these invariants:

### 4.1 Before Every Mutation

- [ ] Node/edge kind exists in schema registry
- [ ] Required properties present and typed correctly
- [ ] Evidence references point to existing evidence
- [ ] Node references point to existing nodes (for edges)
- [ ] No duplicate IDs (for creation)
- [ ] No duplicate composite keys (for edges)

### 4.2 After Every Mutation

- [ ] Event recorded in event log
- [ ] Checksum updated on modified nodes
- [ ] Timestamps updated (modified, observed)
- [ ] Confidence flagged for recomputation

---

## 5. Event Recording

Every mutating method records an event before returning:

```python
def _record_event(self, kind: str, entity_id: str,
                  entity_kind: str, payload: dict):
    event = Event(
        kind=kind,
        entity_id=entity_id,
        entity_kind=entity_kind,
        payload=payload,
        timestamp=datetime.utcnow(),
        sequence=self._next_sequence(),
    )
    self.store.append_event(event)
```

The event sequence is guaranteed to be monotonically increasing and
gapless within a single repository's lifetime.

---

## 6. Error Handling

```python
class GraphServiceError(Exception): pass
class NodeNotFoundError(GraphServiceError): pass
class EdgeNotFoundError(GraphServiceError): pass
class DuplicateNodeError(GraphServiceError): pass
class DuplicateEdgeError(GraphServiceError): pass
class SchemaValidationError(GraphServiceError): pass
class EvidenceNotFoundError(GraphServiceError): pass
class InvariantViolationError(GraphServiceError): pass
```

Every method returns structured results:

```python
@dataclass
class NodeResult:
    success: bool
    node: Optional[Node]
    event_id: Optional[str]
    error: Optional[str]

@dataclass
class EdgeResult:
    success: bool
    edge: Optional[Edge]
    event_id: Optional[str]
    error: Optional[str]

@dataclass
class EvidenceResult:
    success: bool
    evidence_id: Optional[str]
    deduplicated: bool
    error: Optional[str]
```

---

## 7. Transactional Guarantees

```
┌──────────────────────────────────────────┐
│  with graph.transaction() as tx:         │
│      graph.create_node(..., tx=tx)       │
│      graph.create_edge(..., tx=tx)       │
│      graph.record_fact(..., tx=tx)       │
│      # All or nothing                    │
│      tx.commit()                         │
└──────────────────────────────────────────┘
```

Rules:
- Every mutation must occur within a transaction
- Transactions are serialized (one at a time)
- Reads can occur outside transactions
- Events are committed with the transaction
- On rollback, no events are recorded

---

## 8. Implementation Note

The GraphService wraps the Store. It does not replace it.

```
Pipeline Component
    │
    ▼
GraphService (canonical API)
    │
    ├── Schema validation
    ├── Contract enforcement
    ├── Event recording
    ├── Business logic (dedup, merge, deprecation)
    │
    ▼
Store (persistence)
    │
    └── JSON / SQLite / Neo4j
```

The GraphService is what components import and use.
The Store is what the GraphService imports and uses.
Nothing else imports the Store.
