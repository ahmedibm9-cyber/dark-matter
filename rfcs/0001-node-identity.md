# RFC 0001: Node Identity Model

**Status:** Accepted  
**Date:** 2026-06-26  
**Author:** Architecture specification  

## Summary

Define how nodes in the knowledge graph are identified, ensuring stable,
never-recycled identifiers that survive across graph versions.

## Motivation

Without stable identity, merging evidence from multiple collectors or
reconstructing graph state over time becomes impossible. IDs must be
predictable, kind-scoped, and permanent.

## Design

Every node gets an ID in format: K-XXXXX where K is a kind mnemonic.

Examples:
- PROJ-0001 (Project)
- FILE-1832 (File)
- CLASS-0092 (Class)
- API-0183 (API)

### Rules
- IDs are immutable once assigned
- IDs are never recycled or deleted
- Sequence numbers use monotonically increasing counters (one per kind)
- IDs are globally unique across all kinds

### Alternatives Considered
- **UUIDs**: Rejected — not human-readable, no kind information, no ordering
- **Path-based IDs**: Rejected — paths change; ID must be stable
- **Semantic IDs**: Rejected — any semantic component can become inaccurate

## Consequences
- Stable references for evidence, edges, and queries
- Human-readable identifiers in logs and output
- Simple counter-based allocation (trivially implementable in any store)
- No ID reuse means IDs grow monotonically over time

## Status
This design is implemented in GRAPH-SCHEMA.md §1.
