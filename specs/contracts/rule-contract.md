# Rule Contract v1

## Inputs
- `evidence: list[Evidence]` — evidence relevant to this rule's domain
- `graph: KnowledgeGraph` — current graph state (for context-dependent rules)

## Outputs
- `facts: list[DerivedFact]` — statements inferred from evidence
- `unknowns: list[Unknown]` — knowledge gaps detected
- `confidence_results: dict` — recomputed confidence for affected nodes/edges

## Invariants
1. Rules never modify evidence or the graph directly — they produce candidates
2. Rules are deterministic: same inputs → same outputs
3. Rule definitions are declarative (YAML), not imperative (code)
4. Rules are independently versioned
5. A rule can be disabled without affecting other rules
6. Rules must declare their input dependencies explicitly
7. Rules do not have side effects beyond producing facts and unknowns
8. Empty output is valid — means rule found nothing to infer

## Failure Modes
| Mode | Cause | Behavior |
|------|-------|----------|
| Missing input | Required evidence absent | Rule doesn't fire, no error |
| Malformed rule | YAML parse failure | Rule disabled, logged |
| Circular dependency | Rule A depends on Rule B depends on A | Detected at registration, rejected |
| Infinite loop | Rule produces same fact repeatedly | Dedup filter catches it |
| Confidence > 1.0 | Formula error | Clamp to 1.0 |
