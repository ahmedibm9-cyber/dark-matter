# Storage Interface Specification

> **Status:** Draft v0.1 — Not yet ratified
> **Part of:** Aether Intelligence Platform
> **Scope:** Abstract store contract, CRUD, queries, transactions, migrations, JSON v1 implementation

---

## 1. Design Principles

1. **The engine never touches storage directly.** Every persistence operation goes through the interface.
2. **The store is a detail.** JSON, SQLite, Neo4j, DuckDB are implementations of the same contract.
3. **Transactions are mandatory for consistency.** Even the JSON store simulates them.
4. **Migrations are versioned and reversible.** Schema changes are explicit operations.
5. **The event log is append-only.** Evidence and events are never mutated.

---

## 2. Store Interface

### 2.1 Abstract Contract

```python
class Store(ABC):
    """
    Abstract persistence layer for the Aether knowledge graph.
    Every implementation must satisfy this contract.
    """

    # --- Lifecycle ---

    @abstractmethod
    def initialize(self, config: StoreConfig) -> None:
        """Create or open the store at the given path/config."""

    @abstractmethod
    def close(self) -> None:
        """Flush and release resources."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all data (for testing). Never used in production."""

    # --- Schema & Migration ---

    @abstractmethod
    def schema_version(self) -> str:
        """Return current schema version (semver)."""

    @abstractmethod
    def migrate(self, target_version: str) -> MigrationResult:
        """Migrate from current version to target version."""

    # --- Transactions ---

    @abstractmethod
    @contextmanager
    def transaction(self) -> Generator[Transaction, None, None]:
        """
        Atomic unit of work.
        All mutations within a transaction are committed or rolled back together.
        Nested transactions are flattened (savepoints optional).
        """

    # --- Node CRUD ---

    @abstractmethod
    def node_create(self, tx: Transaction, node: Node) -> NodeResult:
        """Create a node. Fails if ID or unique constraint violated."""

    @abstractmethod
    def node_read(self, node_id: str) -> Optional[Node]:
        """Read node by ID. Returns None if not found."""

    @abstractmethod
    def node_update(self, tx: Transaction, node: Node) -> NodeResult:
        """Update node properties. Merges with existing; only provided fields change."""

    @abstractmethod
    def node_deprecate(self, tx: Transaction, node_id: str, reason: str) -> NodeResult:
        """Mark node as deprecated. Sets expired timestamp."""

    @abstractmethod
    def node_delete(self, tx: Transaction, node_id: str) -> NodeResult:
        """Hard delete. Only for rollback/undo. Not used in normal operation."""

    # --- Edge CRUD ---

    @abstractmethod
    def edge_create(self, tx: Transaction, edge: Edge) -> EdgeResult:
        """Create edge. Fails if source or target don't exist."""

    @abstractmethod
    def edge_read(self, source_id: str, target_id: str, kind: str) -> Optional[Edge]:
        """Read specific edge by its composite key."""

    @abstractmethod
    def edge_update(self, tx: Transaction, edge: Edge) -> EdgeResult:
        """Update edge properties."""

    @abstractmethod
    def edge_delete(self, tx: Transaction, source_id: str, target_id: str, kind: str) -> EdgeResult:
        """Remove edge."""

    # --- Event Log ---

    @abstractmethod
    def event_append(self, tx: Transaction, event: Event) -> EventResult:
        """Append event to immutable log. Returns sequence number."""

    @abstractmethod
    def event_read(self, sequence: int) -> Optional[Event]:
        """Read event by sequence number."""

    @abstractmethod
    def event_stream(self, after_sequence: int = 0, limit: int = 1000) -> Iterable[Event]:
        """Stream events after a given sequence number (for replay)."""

    @abstractmethod
    def event_count(self) -> int:
        """Total events in the log."""

    # --- Evidence Store ---

    @abstractmethod
    def evidence_store(self, tx: Transaction, evidence: Evidence) -> EvidenceResult:
        """Store evidence immutably. Deduplicates by hash."""

    @abstractmethod
    def evidence_read(self, evidence_id: str) -> Optional[Evidence]:
        """Read evidence by ID."""

    @abstractmethod
    def evidence_find(self, query: EvidenceQuery) -> list[Evidence]:
        """Query evidence by kind, source, time range, tags."""

    # --- Query ---

    @abstractmethod
    def query_nodes(self, query: NodeQuery) -> list[Node]:
        """Query nodes by kind, properties, tags, time window."""

    @abstractmethod
    def query_edges(self, query: EdgeQuery) -> list[Edge]:
        """Query edges by kind, source/target kinds, properties."""

    @abstractmethod
    def get_neighbors(self, node_id: str, direction: str = "both",
                      edge_kinds: list[str] = None,
                      max_depth: int = 1) -> list[NeighborResult]:
        """Traverse graph from node_id."""

    @abstractmethod
    def find_path(self, source_id: str, target_id: str,
                  edge_kinds: list[str] = None,
                  max_depth: int = 10) -> Optional[list[PathStep]]:
        """Shortest path between two nodes."""

    @abstractmethod
    def subgraph(self, root_id: str,
                 node_kinds: list[str] = None,
                 max_depth: int = 3) -> Subgraph:
        """Extract subgraph around root node."""

    # --- Point-in-Time ---

    @abstractmethod
    def state_at(self, timestamp: datetime) -> StoreSnapshot:
        """Return graph state as it existed at given timestamp."""
```

### 2.2 Transaction Contract

```python
class Transaction(ABC):
    @abstractmethod
    def commit(self) -> None:
        """Persist all changes atomically."""

    @abstractmethod
    def rollback(self) -> None:
        """Discard all changes since transaction start."""

    @abstractmethod
    def is_active(self) -> bool:
        """Is the transaction still open?"""
```

### 2.3 Configuration Contract

```python
@dataclass
class StoreConfig:
    path: str                    # Filesystem path or connection string
    store_type: str              # "json", "sqlite", "neo4j", "duckdb", "memory"
    schema_version: str          # Requested schema version
    read_only: bool = False
    cache_size_mb: int = 64
    journal_mode: str = "wal"    # For SQLite: "wal", "delete", "memory"
    encryption_key: Optional[str] = None
    extra: dict = field(default_factory=dict)  # Store-specific options
```

---

## 3. Query Model

### 3.1 NodeQuery

```python
@dataclass
class NodeQuery:
    kinds: list[str] = None
    ids: list[str] = None
    tags: list[str] = None         # AND within list
    tags_any: list[str] = None     # OR within list
    properties: dict = None        # Exact match key-value pairs
    property_filters: list[PropertyFilter] = None  # Range, prefix, regex
    confidence_min: float = 0.0
    confidence_max: float = 1.0
    created_after: datetime = None
    created_before: datetime = None
    modified_after: datetime = None
    observed_after: datetime = None
    include_deprecated: bool = False
    limit: int = 100
    offset: int = 0
    sort_by: str = "name"         # name, created, modified, confidence
    sort_order: str = "asc"       # asc, desc
```

### 3.2 EdgeQuery

```python
@dataclass
class EdgeQuery:
    kinds: list[str] = None
    source_ids: list[str] = None
    target_ids: list[str] = None
    source_kinds: list[str] = None
    target_kinds: list[str] = None
    properties: dict = None
    confidence_min: float = 0.0
    limit: int = 100
    offset: int = 0
```

### 3.3 EvidenceQuery

```python
@dataclass
class EvidenceQuery:
    kinds: list[str] = None
    sources: list[str] = None          # Collector names
    tags: list[str] = None
    observed_after: datetime = None
    observed_before: datetime = None
    hash: str = None                   # Exact hash lookup
    limit: int = 100
    offset: int = 0
```

### 3.4 PathStep

```python
@dataclass
class PathStep:
    source_id: str
    edge_kind: str
    target_id: str
    depth: int
```

### 3.5 NeighborResult

```python
@dataclass
class NeighborResult:
    node: Node
    edge: Edge
    direction: str       # "inbound", "outbound"
    depth: int
```

### 3.6 Subgraph

```python
@dataclass
class Subgraph:
    nodes: list[Node]
    edges: list[Edge]
    root_id: str
    depth: int
```

### 3.7 PropertyFilter

```python
@dataclass
class PropertyFilter:
    key: str
    operator: str         # eq, neq, gt, gte, lt, lte, prefix, suffix, contains, regex, exists, not_exists
    value: Any = None     # None for exists/not_exists
```

---

## 4. Result Types

```python
@dataclass
class NodeResult:
    success: bool
    node: Optional[Node]
    error: Optional[str]
    sequence: Optional[int]      # Event sequence that produced this change

@dataclass
class EdgeResult:
    success: bool
    edge: Optional[Edge]
    error: Optional[str]

@dataclass
class EventResult:
    success: bool
    event: Optional[Event]
    sequence: Optional[int]

@dataclass
class EvidenceResult:
    success: bool
    evidence: Optional[Evidence]
    deduplicated: bool           # True if hash already existed

@dataclass
class MigrationResult:
    success: bool
    from_version: str
    to_version: str
    steps_applied: list[str]
    error: Optional[str]

@dataclass
class StoreSnapshot:
    nodes: list[Node]
    edges: list[Edge]
    timestamp: datetime
    event_sequence: int
```

---

## 5. Migration Contract

### 5.1 Migration Interface

```python
class Migration(ABC):
    @abstractmethod
    def version(self) -> str:
        """Target version after migration."""

    @abstractmethod
    def description(self) -> str:
        """What this migration changes."""

    @abstractmethod
    def up(self, store: Store, tx: Transaction) -> None:
        """Apply migration forward."""

    @abstractmethod
    def down(self, store: Store, tx: Transaction) -> None:
        """Revert migration (if supported)."""

    @abstractmethod
    def requires(self) -> list[str]:
        """Required previous version(s)."""
```

### 5.2 Migration Registry

```python
class MigrationRegistry:
    def register(self, migration: Migration) -> None: ...
    def resolve(self, from_version: str, to_version: str) -> list[Migration]: ...
    def available_versions(self) -> list[str]: ...
```

### 5.3 Migration Rules

- Migrations are ordered by version (semver comparison)
- Each migration has `up` and `down`
- `down` is optional for destructive changes (data loss warning)
- Migrations run within a transaction
- Schema version is stored in the store itself (`_meta` collection)
- Migration history is logged as events

---

## 6. Error Handling

### 6.1 Store Exceptions

```python
class StoreError(Exception): ...
class StoreConnectionError(StoreError): ...
class StoreIntegrityError(StoreError): pass       # Constraint violation
class StoreNotFoundError(StoreError): pass         # Node/edge not found
class StoreConflictError(StoreError): pass         # Unique constraint violation
class StoreTransactionError(StoreError): pass      # Transaction failure
class StoreMigrationError(StoreError): pass        # Migration failure
class StoreSchemaError(StoreError): pass           # Schema version mismatch
class StoreReadOnlyError(StoreError): pass         # Write on read-only store
class StoreTimeoutError(StoreError): pass          # Operation timed out
```

---

## 7. JSON Store (v1 Implementation)

### 7.1 Storage Layout

```
.aether/
    schema_version      # Plain text: "1.0.0"
    meta.json           # Store metadata
    events/             # Append-only event log
        0000001.json    # Event file (one per sequence)
        0000002.json
        ...
    nodes/              # Node directory
        FILE/           # One subdirectory per node kind
            FILE-0001.json
            FILE-0002.json
        CLASS/
            CLASS-0001.json
        ...
    edges/              # Edge directory
        CONTAINS/       # One subdirectory per edge kind
            edges.jsonl # JSON Lines file
        IMPORTS/
            edges.jsonl
        ...
    evidence/           # Evidence directory (immutable)
        EVID-0001.json
        ...
    indices/            # Query indexes
        by_kind.json
        by_name.json
        by_path.json
        by_tag.json
        ...
    locks/              # Transaction locks
        tx-001.lock
        ...
```

### 7.2 Event as Files

```
Rationale:
- Events are append-only by nature
- Each event as a file avoids file-level contention
- Sequence number = filename
- For high-volume repos, batch events into sequence-range files:
  0000001-0001000.jsonl
```

### 7.3 Transaction Implementation

The JSON store simulates transactions:

1. Acquire write lock (file-based mutex)
2. Write pending changes to `_pending/` directory
3. On `commit()`: atomically rename `_pending/*` → final location
4. On `rollback()`: delete `_pending/*`
5. Release write lock

Limitations:
- No concurrent writes (single-writer)
- Reads are lock-free (eventual consistency within single process)
- Suitable for single-repository use
- Not suitable for multi-process or server deployment

### 7.4 Performance Notes

| Operation | Estimated Cost | Note |
|-----------|---------------|------|
| Node read by ID | O(1) | Direct file lookup |
| Node read by kind+name | O(log n) | Index lookup |
| Edge read | O(1) | Direct line in JSONL |
| Neighbor traversal (1 hop) | O(k) | k = edge count for node |
| Neighbor traversal (N hops) | O(k^N) | Exponential — use depth limit |
| Event stream | O(n) | Sequential read |
| Evidence write | O(1) | Append file |
| Full graph reconstruction | O(e) | All events replayed |

### 7.5 Limitations vs. Future Stores

| Capability | JSON (v1) | SQLite (v2) | Neo4j (v3) |
|------------|-----------|-------------|------------|
| Concurrent writers | No | Yes | Yes |
| ACID transactions | Simulated | Full | Full |
| Graph traversal | In-memory | Recursive CTEs | Native |
| Query performance | O(n) scans | Indexed | Indexed |
| Multi-repository | No | Yes | Yes |
| Remote access | No | No | Yes |
| Max nodes | ~10K | ~10M | ~100M+ |
| Setup | Zero config | File-based | Server required |

---

## 8. SQLite Store (v2 — Future)

Key considerations for when SQLite becomes the default:

- Each repository gets its own `.aether.db` file
- WAL mode for concurrent reads + single writer
- Foreign keys enabled
- JSON columns for flexible properties
- Full-text search on node names, descriptions, evidence payloads
- Recursive CTEs for graph traversal
- Attach multiple `.aether.db` files for cross-repo queries

---

## 9. Concurrency Model

```
┌──────────────────────────────────────────────┐
│              Write Transaction                │
│  ┌────────┐  ┌────────┐  ┌────────┐          │
│  │Collector│  │Inference│  │ CLI    │          │
│  └───┬────┘  └───┬────┘  └───┬────┘          │
│      │           │           │                 │
│      └─────┬─────┴─────┬─────┘                 │
│            │           │                       │
│            ▼           ▼                       │
│      Store.mutex (write lock)                  │
│            │                                    │
│            ▼                                    │
│      Transaction → Commit/Rollback             │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐
│                Read Queries                   │
│  ┌────────┐  ┌────────┐  ┌────────┐          │
│  │Compiler│  │CLI     │  │Dashboard│          │
│  └───┬────┘  └───┬────┘  └───┬────┘          │
│      │           │           │                 │
│      └─────┬─────┴─────┬─────┘                 │
│            │           │                       │
│            ▼           ▼                       │
│      Lock-free reads (snapshot isolation)      │
│      Event log + materialized graph           │
└──────────────────────────────────────────────┘
```
