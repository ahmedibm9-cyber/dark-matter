# Event Model Specification v1

> **Status:** Draft
> **Part of:** Aether Intelligence Platform
> **Scope:** Event types, sourcing, replay, time travel, provenance

---

## 1. Rationale

Currently, Aether stores state directly. When a file is discovered, a node
is created. When a fact is inferred, it is recorded. There is no record of
*why* the state changed — only that it changed.

An event model changes this. Every state change becomes an immutable event.
The current graph state is derived by replaying events. This gives Aether:
- **Auditability:** Every state change has a cause
- **Replayability:** The graph can be reconstructed from scratch
- **Time travel:** Query the graph as it existed at any point
- **Incremental updates:** Only new events need processing
- **Provenance:** Every node, edge, and fact traces to its creating event
- **Debugging:** Errors can be traced to the exact event that caused them

---

## 2. Design Principle

> **Events are the source of truth. The graph is a derived view.**

This means:
- The graph is never edited directly (enforced by GraphService)
- Every mutation produces an event first
- The event log is append-only and immutable
- The graph is reconstructed by replaying events
- Events never change — only new events are appended

---

## 3. Event Structure

```python
@dataclass
class Event:
    sequence: int                # Monotonically increasing, gapless
    kind: str                    # Event type (see §4)
    entity_id: str               # Affected entity ID
    entity_kind: str             # Kind of affected entity
    payload: dict                # Event-specific data
    evidence_ref: Optional[str]  # Evidence that triggered this event
    capability_id: Optional[str] # Capability that produced this event
    parent_sequence: Optional[int]  # Previous event in causal chain
    timestamp: datetime          # When the event occurred
    checksum: str                # SHA-256 of all fields above
```

---

## 4. Event Types

### 4.1 Evidence Events

| Event | Payload | Triggered By |
|-------|---------|--------------|
| `EVIDENCE_INGESTED` | `{kind, source, hash, size}` | Collector produces new evidence |
| `EVIDENCE_EXPIRED` | `{evidence_id, reason}` | TTL-based expiry check |

### 4.2 Node Events

| Event | Payload | Triggered By |
|-------|---------|--------------|
| `NODE_CREATED` | `{kind, name, properties_summary}` | Collector or rule detects new entity |
| `NODE_UPDATED` | `{changed_fields, old_values, new_values}` | New evidence modifies node |
| `NODE_DEPRECATED` | `{reason, replacement_id?}` | Entity no longer observed |
| `NODE_REACTIVATED` | `{reason}` | Entity re-observed after deprecation |
| `NODE_MERGED` | `{surviving_id, absorbed_ids}` | Two nodes identified as same entity |

### 4.3 Edge Events

| Event | Payload | Triggered By |
|-------|---------|--------------|
| `EDGE_CREATED` | `{source_id, target_id, kind}` | Relationship detected |
| `EDGE_DELETED` | `{source_id, target_id, kind, reason}` | Relationship no longer valid |
| `EDGE_REPLACED` | `{source_id, target_id, old_kind, new_kind}` | Relationship nature changed |

### 4.4 Inference Events

| Event | Payload | Triggered By |
|-------|---------|--------------|
| `FACT_RECORDED` | `{statement, category, rule_id, confidence}` | Rule infers new fact |
| `FACT_INVALIDATED` | `{fact_id, reason, replacement_id?}` | Contradictory evidence |
| `FACT_CONFIDENCE_CHANGED` | `{fact_id, old_confidence, new_confidence, reason}` | Evidence freshness decay |
| `RULE_EXECUTED` | `{rule_id, input_count, output_count, duration_ms}` | Rule engine runs |

### 4.5 Verification Events

| Event | Payload | Triggered By |
|-------|---------|--------------|
| `VERIFICATION_RECORDED` | `{claim, result, confidence, method}` | Verifier processes claim |
| `VERIFICATION_SUPERSEDED` | `{old_verification_id, new_verification_id}` | New verification replaces old |

### 4.6 Unknown Events

| Event | Payload | Triggered By |
|-------|---------|--------------|
| `UNKNOWN_IDENTIFIED` | `{topic, reason, priority, required_capability?}` | Inference detects gap |
| `UNKNOWN_RESOLVED` | `{unknown_id, resolution_evidence}` | Gap filled by new evidence |
| `UNKNOWN_PRIORITY_CHANGED` | `{unknown_id, old_priority, new_priority}` | Manual or automated priority adjustment |

### 4.7 Pipeline Events

| Event | Payload | Triggered By |
|-------|---------|--------------|
| `COLLECTOR_STARTED` | `{capability_id, scope}` | Pipeline begins collection |
| `COLLECTOR_COMPLETED` | `{capability_id, evidence_count, duration_ms}` | Collector finishes |
| `COLLECTOR_FAILED` | `{capability_id, error, partial_results}` | Collector errors |
| `INFERENCE_STARTED` | `{evidence_range}` | Inference phase begins |
| `INFERENCE_COMPLETED` | `{fact_count, unknown_count, duration_ms}` | Inference phase ends |
| `COMPILER_STARTED` | `{capability_id, target}` | Compiler begins |
| `COMPILER_COMPLETED` | `{capability_id, target, output_path, size_bytes}` | Compiler finishes |
| `PIPELINE_COMPLETED` | `{summary}` | Full pipeline run completes |

### 4.8 Lifecycle Events

| Event | Payload | Triggered By |
|-------|---------|--------------|
| `CAPABILITY_REGISTERED` | `{capability_id, version, type}` | New capability added |
| `CAPABILITY_DEPRECATED` | `{capability_id, replacement_id?}` | Capability marked deprecated |
| `CAPABILITY_REMOVED` | `{capability_id}` | Capability removed |
| `SCHEMA_MIGRATED` | `{from_version, to_version, changes}` | Schema migration applied |
| `STORE_INITIALIZED` | `{schema_version, event_count, node_count}` | Store opened or created |
| `STORE_CORRUPTION_DETECTED` | `{details, affected_entities}` | Integrity check fails |

---

## 5. Event Log

The event log is an append-only sequence of events.

### 5.1 Structure

```python
class EventLog:
    """
    Append-only log of all events in a repository's lifetime.
    """

    def append(self, event: Event) -> int:
        """Append event. Returns sequence number. Thread-safe."""

    def read(self, sequence: int) -> Optional[Event]:
        """Read event by sequence number."""

    def stream(self, after_sequence: int = 0,
               limit: int = 1000,
               kinds: list[str] = None) -> Iterable[Event]:
        """Stream events after a given sequence number."""

    def count(self) -> int:
        """Total events in the log."""

    def last_sequence(self) -> int:
        """Highest sequence number."""

    def range(self, from_seq: int, to_seq: int) -> list[Event]:
        """Read a contiguous range of events."""
```

### 5.2 Sequence Guarantees

- Sequences are **monotonically increasing and gapless**
- Sequence 0 is always `STORE_INITIALIZED`
- Sequences never wrap or reset
- Two events cannot have the same sequence number

### 5.3 Storage

In the JSON store, events are stored as individual files:

```
.aether/events/
    0000001.json
    0000002.json
    ...
```

In SQLite, events are stored in an `events` table with an auto-incrementing
primary key. In Neo4j, events are stored as nodes with `:Event` labels.

---

## 6. Graph Reconstruction

The current graph state is derived by replaying events:

```python
def reconstruct_graph(event_log: EventLog) -> GraphState:
    """
    Replay all events in sequence to produce the current graph state.
    """
    state = GraphState()
    for event in event_log.stream(after_sequence=0):
        apply_event(state, event)
    return state

def apply_event(state: GraphState, event: Event):
    if event.kind == "NODE_CREATED":
        state.nodes[event.entity_id] = Node(id=event.entity_id, ...)
    elif event.kind == "NODE_UPDATED":
        state.nodes[event.entity_id].properties.update(event.payload["changed_fields"])
    elif event.kind == "NODE_DEPRECATED":
        state.nodes[event.entity_id].expired = event.timestamp
    elif event.kind == "EDGE_CREATED":
        ...
    elif event.kind == "FACT_RECORDED":
        ...
```

### 6.1 Incremental Reconstruction

Instead of replaying all events, the system maintains a snapshot and
applies only new events:

```python
def incremental_update(state: GraphState, new_events: list[Event]):
    """Apply new events to an existing graph state."""
    for event in new_events:
        apply_event(state, event)
```

This is how incremental scans work: only events from the latest scan
are applied to the existing graph.

---

## 7. Time Travel

Point-in-time queries use event replay with a cutoff:

```python
def state_at(event_log: EventLog, timestamp: datetime) -> GraphState:
    """
    Return graph state as it existed at the given timestamp.
    """
    state = GraphState()
    for event in event_log.stream(after_sequence=0):
        if event.timestamp > timestamp:
            break
        apply_event(state, event)
    return state
```

Optimization: store periodic snapshots (every 1000 events) and replay
only events after the nearest snapshot.

---

## 8. Provenance via Events

Every entity can be traced to its creating event, and from there to
the evidence and capability that produced it:

```
Node: FILE-1832
    │
    ▼
Event: NODE_CREATED (sequence: 442)
    │
    ├── capability_id: "collector.filesystem"
    │
    └── evidence_ref: "EVID-0991"
            │
            ▼
        Evidence: file "/src/auth/login.ts"
            │
            ├── source: "filesystem"
            ├── collected_at: 2026-06-26T10:00:00Z
            └── hash: "a1b2c3d4..."
```

This chain is returned by `GraphService.explain()`.

---

## 9. Event Sourcing vs. Current State

The store maintains both:

```
Event Log (append-only, immutable)
    │
    ├──→ [Replay] → Current State (derived, regenerable)
    │
    ├──→ [Replay + cutoff] → Historical State
    │
    └──→ [Audit] → Provenance Chain
```

The current state is cached for performance. The event log is the
authoritative source. If the cache is corrupted, it can be rebuilt
from the event log.

---

## 10. Migration Strategy

Phase 1 (Current): State-based store with event recording
- Every mutation records an event
- Graph is stored as materialized state
- Events are not yet used for reconstruction

Phase 2: Event-sourced with snapshot
- Graph is reconstructed from events on startup
- Periodic snapshots for performance
- Events are the primary store; state is cache

Phase 3: Fully event-sourced
- No materialized state
- Everything derived from events
- Snapshots are purely performance optimization

Each phase is backward-compatible. Phase 1 implementations can coexist
with Phase 3 implementations by sharing the same event log format.

---

## 11. Event Schema Versioning

Events themselves have a schema version:

```python
@dataclass
class Event:
    schema_version: str = "1.0.0"  # Event schema version
    ...
```

If the event schema needs to change (new fields, deprecated fields),
a new schema version is introduced. Old events retain their original
schema. The event reader handles multiple schema versions transparently.

```python
EVENT_SCHEMA_REGISTRY = {
    "1.0.0": EventSchemaV1,
    "1.1.0": EventSchemaV1_1,
    "2.0.0": EventSchemaV2,
}
```

---

## 12. Event Size Budget

Individual events should be small (under 1KB typical, under 10KB max).
Large payloads (file content, diff data) are stored in the evidence store
and referenced by the event, not included inline.

```python
# GOOD - small event, large data referenced
event = Event(
    kind="EVIDENCE_INGESTED",
    entity_id="EVID-0991",
    payload={
        "kind": "file",
        "source": "filesystem",
        "hash": "a1b2c3d4...",
        "size_bytes": 12345,
        # NO content payload here
    },
)

# Evidence payload is stored separately in the evidence store
evidence = store.get_evidence("EVID-0991")  # contains full payload
```
