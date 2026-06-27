# RFC 0004: Rule Engine

**Status:** Accepted  
**Date:** 2026-06-26  
**Author:** Architecture specification  

## Summary

Define the rule engine: a declarative, data-driven system for inferring
knowledge from evidence. Rules are defined in YAML, not code, and can
be added, removed, or modified without changing the engine.

## Motivation

Rules represent the intelligence of the system. If rules are hardcoded,
adding new knowledge requires changing the engine. By making rules
declarative and externally defined, the system becomes extensible
without modifying its core.

## Design

### Rule Definition
Rules are YAML files stored in `.aether/rules/`:

```yaml
id: 0001
name: Detect Framework
category: semantic
inputs:
  - kind: FILE
    required: true
    min_count: 1
confidence_formula: "match_count / expected_count * evidence_weight"
```

### Rule Execution
- Rules are deterministic (same inputs → same outputs)
- Rules produce facts, unknowns, and confidence updates
- Rules never modify evidence or the graph directly
- Rules can be enabled/disabled independently

### Built-in Rules
The v1 engine ships with rules for: architecture detection, framework
detection, dependency analysis, orphan detection, test coverage
assessment, and API mapping.

## Alternatives Considered
- **Hardcoded rules in Python**: Rejected — requires engine changes for new rules
- **Rules as plugins**: Deferred to v2 — YAML is simpler for v1
- **Machine-learned rules**: Deferred to v3 — requires training data

## Consequences
- Rules are auditable (YAML can be version-controlled)
- Non-developers can write rules
- Rule execution is slower than hardcoded logic
- Complex rules may require escaping YAML limitations

## Status
This design is implemented in PIPELINE.md §2.7.
