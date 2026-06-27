# RFC 0005: Storage Abstraction

**Status:** Accepted  
**Date:** 2026-06-26  
**Author:** Architecture specification  

## Summary

Define the storage abstraction: the engine never touches persistence
directly. All storage operations go through a defined interface,
allowing JSON, SQLite, Neo4j, or any future store to be swapped
without changing the engine.

## Motivation

Early-stage projects often hardcode storage, making migration painful
when scale demands it. By defining the storage contract on day one,
the engine remains storage-agnostic and the data can outlive any
single storage backend.

## Design

### Store Interface
The Store contract defines:
- Lifecycle: initialize, close, clear
- Schema: version tracking, migration
- Transactions: atomic commit/rollback
- Node CRUD: create, read, update, deprecate, delete
- Edge CRUD: create, read, update, delete
- Event log: append, read, stream, count
- Evidence: store, read, find
- Query: nodes, edges, neighbors, path, subgraph, state_at

### Store Implementations
| Store | Status | Use Case |
|-------|--------|----------|
| JSON v1 | Immediate | Single-repo, zero-config |
| SQLite v2 | Future | Multi-repo, concurrent readers |
| Neo4j v3 | Future | Enterprise, 100M+ nodes |

### Key Design Decisions
1. Transactions are mandatory for writes (even JSON store simulates them)
2. Event log is append-only (all state changes are events)
3. Queries are lock-free (snapshot isolation for reads)
4. Store config is passed at initialization (engine is configuration-agnostic)

## Alternatives Considered
- **Direct SQLite**: Rejected — couples engine to SQL schema
- **JSON as a "temporary" solution**: Accepted with explicit interface — avoids rewrites
- **Document store (MongoDB)**: Deferred — not needed until multi-repo coordination

## Consequences
- Engine remains storage-agnostic
- JSON v1 is limited to single-writer, small repositories
- Migration tooling required for backend changes
- Each store implementation must satisfy the full contract

## Status
This design is implemented in STORAGE-IFACE.md.
