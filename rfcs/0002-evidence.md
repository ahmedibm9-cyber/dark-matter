# RFC 0002: Evidence Model

**Status:** Accepted  
**Date:** 2026-06-26  
**Author:** Architecture specification  

## Summary

Define the evidence model: how raw observations from collectors become
immutable, content-addressed evidence records that form the foundation
of all knowledge in the graph.

## Motivation

Knowledge is only as reliable as its evidence. Without a first-class
evidence model, there is no way to distinguish verified facts from
inferences, heuristics, or guesses. Evidence must be:
- Immutable (never modified after collection)
- Traceable (every fact links to its evidence)
- Verifiable (evidence can be re-collected and compared)

## Design

Evidence is the atomic unit of observation.

### Structure
- Evidence has a kind (file, test, config, log, runtime, git, document, claim)
- Evidence has a source (which collector produced it)
- Evidence has a payload (the actual data collected)
- Evidence has a hash (SHA-256 of kind + source + payload)
- Evidence has a confidence_weight (how definitive this evidence type is)

### Key Rules
- Evidence is immutable once stored
- Evidence is content-addressed (same hash = same evidence)
- Evidence never references nodes — nodes reference evidence
- Evidence is never deleted

### Evidence vs. Knowledge
Evidence is raw observation. Knowledge is derived from evidence through
inference rules. This separation is axiomatic.

## Alternatives Considered
- **Mutable evidence**: Rejected — destroys traceability
- **Evidence without hashing**: Rejected — allows duplicates without detection
- **Bidirectional evidence/nodes**: Rejected — creates circular dependencies

## Consequences
- Evidence grows monotonically (append-only)
- Deduplication is free (hash-based)
- Provenance is always traceable
- Storage requirements grow with repo activity

## Status
This design is implemented in GRAPH-SCHEMA.md §2.23 and PIPELINE.md §2.2.
