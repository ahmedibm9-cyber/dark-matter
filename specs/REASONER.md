# Knowledge Reasoner Specification v1

> **Status:** Draft
> **Part of:** Aether Intelligence Platform
> **Scope:** Higher-order reasoning from graph patterns, cross-cutting insights, architecture-level analysis

---

## 1. Rationale

Inference rules extract facts from evidence: "package.json contains stripe →
this project uses Stripe." But many important insights cannot be derived from
a single evidence source. They emerge from patterns across the entire graph:

- "This is a microservices architecture" (requires seeing service boundaries,
  API gateways, inter-service communication patterns)
- "Authentication is duplicated" (requires seeing the same pattern in
  multiple service boundaries)
- "Test coverage for payments is critically low" (requires correlating
  business rule importance with test existence)
- "Three architectural decisions conflict" (requires comparing ADR outcomes)

These are not inferences. They are **reasoning** — higher-order insights
that require graph-wide pattern detection, not evidence-to-fact deduction.

---

## 2. Reasoner vs. Inference Engine

| Aspect | Inference Engine | Reasoner |
|--------|-----------------|----------|
| Input | Evidence | Graph state + verified facts |
| Output | Facts, Unknowns | Insights, Warnings, Recommendations |
| Scope | Single evidence or small evidence set | Full graph or large subgraph |
| Certainty | Confidence score | Confidence score + supporting pattern |
| Trigger | Evidence arrives | Graph state changes, periodic, or on-demand |
| Examples | "Uses Stripe" | "Auth is duplicated across 4 services" |

The Reasoner operates **after** inference and verification. It assumes the
graph is consistent and verified. It does not re-verify facts — it discovers
patterns among them.

---

## 3. Reasoner Model

```python
@dataclass
class ReasoningPattern:
    id: str                    # e.g., "pattern.microservice-detection"
    version: str
    name: str
    description: str
    category: str              # architectural, quality, security, consistency, evolution
    severity: str              # info, warning, critical
    inputs: list[PatternInput] # Graph patterns to detect
    outputs: list[InsightKind] # What the pattern produces
    confidence_formula: str    # How to compute insight confidence
    remediation: str           # Suggested action

@dataclass
class PatternInput:
    type: str                  # "node_pattern", "edge_pattern", "subgraph_pattern",
                               # "metric_threshold", "temporal_pattern"
    query: str                 # Graph query or metric expression
    threshold: float = None    # For metric-based patterns

@dataclass
class Insight:
    id: str                    # INSIGHT-XXXX
    pattern_id: str            # Which pattern produced this
    statement: str             # Human-readable insight
    category: str
    severity: str
    confidence: float
    supporting_nodes: list[str]  # Node IDs involved
    supporting_edges: list[str]  # Edge IDs involved
    supporting_pattern: dict     # The matched pattern data
    remediation: str
    created: datetime
    expires: datetime            # Re-check after this
    status: str                  # active, acknowledged, resolved, dismissed
```

---

## 4. Reasoning Pattern Categories

### 4.1 Architectural Patterns

Detect system-level architectural properties:

| Pattern | Description | Example Insight |
|---------|-------------|-----------------|
| `pattern.microservice-detection` | Detect microservice boundaries | "Repository contains 4 distinct service boundaries" |
| `pattern.layered-architecture` | Detect layering violations | "Service layer directly accesses database (violates layering)" |
| `pattern.monolith-identification` | Detect monolithic tendencies | "Single deployment unit with 200+ modules" |
| `pattern.circular-dependency` | Detect circular deps between modules | "Module A → B → C → A forms a cycle" |
| `pattern.event-driven` | Detect event/message patterns | "Event bus pattern detected with 3 producers, 12 consumers" |

### 4.2 Quality Patterns

Detect quality-related patterns:

| Pattern | Description | Example Insight |
|---------|-------------|-----------------|
| `pattern.duplicate-code` | Detect similar implementations | "Authentication logic duplicated in 4 files" |
| `pattern.unused-api` | Detect APIs without callers | "3 API endpoints have zero callers" |
| `pattern.low-test-coverage` | Low coverage on critical paths | "Payment flow has 18% test coverage (critical)" |
| `pattern.high-complexity` | High cyclomatic complexity | "Function validateOrder() has complexity 47 (threshold: 15)" |

### 4.3 Security Patterns

Detect security-relevant patterns:

| Pattern | Description | Example Insight |
|---------|-------------|-----------------|
| `pattern.hardcoded-secret` | Detect potential secrets | "Potential API key in config/credentials.json" |
| `pattern.deprecated-dependency` | Outdated or vulnerable deps | "lodash v4.17.20 has 3 known CVEs" |
| `pattern.unauthenticated-endpoint` | Missing auth on sensitive endpoint | "POST /api/admin/users has no auth middleware" |
| `pattern.permission-escalation` | Privilege issues | "User service can access payment database directly" |

### 4.4 Consistency Patterns

Detect inconsistencies across the codebase:

| Pattern | Description | Example Insight |
|---------|-------------|-----------------|
| `pattern.contradictory-decisions` | ADRs that conflict | "ADR-0012 (use SQLite) contradicts ADR-0007 (use PostgreSQL)" |
| `pattern.naming-inconsistency` | Naming convention violations | "3 modules use snake_case, 7 use camelCase" |
| `pattern.duplicate-business-rule` | Same rule implemented differently | "Tax calculation implemented in 3 places with different rates" |
| `pattern.schema-drift` | Schema vs. code mismatch | "Database has column 'email', but code uses 'email_address'" |

### 4.5 Evolution Patterns

Detect trends and changes over time:

| Pattern | Description | Example Insight |
|---------|-------------|-----------------|
| `pattern.high-churn` | Files that change frequently | "src/auth/login.ts changed 47 times in 30 days" |
| `pattern.decreasing-coverage` | Test coverage trending down | "Coverage dropped from 72% to 58% over 3 months" |
| `pattern.increasing-complexity` | Complexity trending up | "Module complexity increased 140% in 2 releases" |
| `pattern.bus-factor` | Knowledge concentration risk | "Only 1 author for 80% of payment module" |

---

## 5. Reasoner Pipeline

The Reasoner is a capability like any other, registered in the capability
system and executed by the pipeline.

```
Graph state change (evidence ingested, facts updated)
    │
    ▼
Trigger reasoner patterns
    │
    ├── Immediate patterns (cheap, fast): circular deps, naming inconsistency
    ├── Deferred patterns (expensive, slow): duplicate code, unused API
    └── Scheduled patterns (periodic): coverage trends, evolution
    │
    ▼
Execute pattern queries against graph
    │
    ▼
Compute confidence for each candidate insight
    │
    ▼
Filter by confidence threshold (default: 0.6)
    │
    ▼
Deduplicate against existing insights
    │
    ▼
Record new insights via GraphService
    │
    ▼
Update insight status (new, existing_confirmed, existing_contradicted)
```

### 5.1 Execution Cost Tiers

| Tier | Cost | Frequency | Examples |
|------|------|-----------|---------|
| T1 | Very cheap (sub-ms) | On every event | Naming patterns, edge count thresholds |
| T2 | Cheap (ms) | On every scan | Circular deps, API callers |
| T3 | Moderate (100ms) | On full scan | Duplicate code, architecture detection |
| T4 | Expensive (seconds) | On demand | Full graph analysis, evolution trends |
| T5 | Very expensive (minutes) | Scheduled | Cross-repository pattern detection |

Tiers T4 and T5 are never executed automatically. They require explicit
user request or scheduled maintenance windows.

---

## 6. Insight Lifecycle

```
New (detected by reasoner)
    │
    ├──→ Active (confidence above threshold)
    │       │
    │       ├──→ Acknowledged (human reviewed)
    │       │       │
    │       │       ├──→ Addressed (action taken, awaiting re-check)
    │       │       │       │
    │       │       │       └──→ Resolved (re-check confirms fix)
    │       │       │
    │       │       └──→ Dismissed (false positive or acceptable)
    │       │
    │       └──→ Superseded (replaced by newer insight)
    │
    └──→ Low Confidence (below threshold, logged but not surfaced)
```

Insights are stored as nodes in the graph (`kind: INSIGHT`) with edges
to the nodes and facts that support them.

---

## 7. Confidence for Insights

Insight confidence is computed differently from fact confidence:

```python
def insight_confidence(pattern_match: dict, graph: GraphState) -> float:
    """
    Insight confidence depends on:
    1. Pattern specificity (how precise the pattern is)
    2. Evidence quality of supporting nodes
    3. Number of independent supporting subgraph matches
    4. Age of supporting evidence
    5. Human confirmation if available
    """
    specificity = pattern_match["pattern_specificity"]  # [0, 1]
    evidence_quality = avg_confidence(supporting_nodes)
    match_count_factor = min(match_count / expected_count, 1.0)
    freshness = compute_freshness(supporting_evidence_ages)
    human_boost = 1.2 if confirmed_by_human else 1.0

    return (specificity * 0.3 +
            evidence_quality * 0.3 +
            match_count_factor * 0.2 +
            freshness * 0.2) * human_boost
```

---

## 8. Pattern Definition Format

```yaml
# Example: .aether/patterns/circular-dependency.yaml
id: pattern.circular-dependency
version: 1.0.0
name: Circular Dependency Detection
category: architectural
severity: critical
description: >
  Detect circular dependencies between modules.
  Circular dependencies increase coupling and make independent
  testing and deployment difficult.

inputs:
  - type: edge_pattern
    query: >
      MATCH (a:MODULE)-[:DEPENDS_ON]->(b:MODULE)-[:DEPENDS_ON]->(c:MODULE)
      WHERE c.id = a.id
      RETURN a, b, c
  - type: metric_threshold
    query: "module.circular_dependency_count"
    threshold: 0

outputs:
  - INSIGHT

confidence_formula: >
  0.8 * (1 - 1/(match_count + 1)) * evidence_quality

remediation: >
  Refactor the circular dependency by extracting shared code into
  a new module, or by inverting the dependency direction.
```

---

## 9. Reasoner as a Capability

The Reasoner is registered in the capability system:

```yaml
id: reasoner.graph-patterns
version: 1.0.0
type: REASONER
entrypoint: aether.reasoner.patterns
permissions:
  - resource: graph.read
    scope: "all"
    reason: "Analyze graph structure for patterns"
  - resource: graph.write
    scope: "kind:insight"
    reason: "Record detected insights"
dependencies:
  - capability: graph.service
    version: ">=1.0.0"
resource_limits:
  timeout_seconds: 30
  max_memory_mb: 256
tags: [reasoning, patterns, architecture]
```

---

## 10. Relationship to Other Subsystems

```
Collectors → Evidence → Inference → Facts
                                          │
                                    Knowledge Graph
                                          │
                                    Reasoner (new)
                                          │
                                    Insights
                                          │
                                    Verification
                                          │
                                    Compiler → Outputs
```

The Reasoner:
- **Reads** from the verified knowledge graph
- **Writes** insights (a new node kind)
- **Does not** create facts (facts come from evidence + rules)
- **Does not** modify nodes or edges created by collectors
- **Does not** re-run inference

This separation ensures that even if the Reasoner produces a wrong insight,
it cannot corrupt the underlying fact graph. Insights are advisory;
facts are foundational.
