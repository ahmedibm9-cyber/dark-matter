# Pipeline Specification

> **Status:** Draft v0.1 — Not yet ratified
> **Part of:** Aether Intelligence Platform
> **Scope:** Collector → Evidence → Inference → Verification → Compilation, stage contracts, confidence mathematics

---

## 1. Pipeline Overview

```
┌────────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ Filesystem │   │   Git    │   │   AST    │   │ Runtime  │   │   API    │   │   Tests  │   │  Docker  │
│ Collector  │   │ Collector │   │ Collector│   │ Collector│   │ Collector│   │ Collector│   │ Collector│
└─────┬──────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
      │               │              │              │              │              │              │
      └───────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
                                            │
                                      Evidence[]
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │    Ingest    │──→ Evidence Store (immutable)
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │  Deduplicate  │──→ Hash-based dedup, discard duplicates
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │   Normalize   │──→ Convert to canonical evidence format
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │    Merge     │──→ Merge with existing graph state
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │    Infer     │──→ Rule Engine → derived facts
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │   Validate   │──→ Consistency checks, constraints
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │  Materialize │──→ Graph events → knowledge graph update
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │    Compile   │──→ Markdown, .ai, JSON, dashboard
                                    └──────────────┘
```

### 1.1 Full Pipeline vs. Incremental Pipeline

| Mode | Trigger | Scope | Cost |
|------|---------|-------|------|
| **Full** | `aether scan --full` or first init | Whole repository | Minutes (one-time) |
| **Incremental** | Git commit, file change, timer | Changed paths only | Milliseconds (steady-state) |

---

## 2. Stage Contracts

### 2.1 Collection Stage

**Input:** Repository path, optional scope filter (paths, patterns, commit range)

**Output:** `list[RawEvidence]`

**Contract:**

```python
@dataclass
class CollectorInput:
    repo_path: Path
    scope: CollectorScope       # ALL, PATHS, COMMIT_RANGE
    paths: list[str] = None    # If scope == PATHS
    from_commit: str = None    # If scope == COMMIT_RANGE
    to_commit: str = None      # If scope == COMMIT_RANGE
    config: dict = None        # Collector-specific configuration

@dataclass
class CollectorScope:
    ALL = "all"
    PATHS = "paths"
    COMMIT_RANGE = "commit_range"

@dataclass
class RawEvidence:
    collector: str             # Collector name
    collector_version: str     # Collector version
    kind: str                  # Evidence kind
    payload: dict              # Collected data
    source_path: str           # Origin file path (if applicable)
    source_commit: str         # Git commit (if applicable)
    timestamp: datetime        # Collection timestamp
    tags: list[str]            # Collector-assigned tags
    confidence_weight: float   # How definitive this evidence type is [0, 1]
```

**Rules:**
- Collectors run independently (parallelizable)
- One collector failure never blocks others
- Collectors are resource-bounded (max files, max depth, max time)
- Each collector reports its own version for reproducibility

### 2.2 Ingestion Stage

**Input:** `list[RawEvidence]`

**Output:** `list[StoredEvidence]`

**Contract:**

```python
@dataclass
class StoredEvidence:
    id: str                    # EVID-XXXX
    collector: str
    collector_version: str
    kind: str
    payload: dict
    source_path: str
    source_commit: str
    collected_at: datetime
    ingested_at: datetime
    hash: str                  # SHA-256 of payload + collector + timestamp
    tags: list[str]
    confidence_weight: float
    deduplicated: bool         # True if this was a duplicate
```

**Rules:**
- Evidence is hashed on ingestion (SHA-256 of `collector + kind + payload`)
- Duplicate hash → marked as duplicate, not re-stored
- Evidence is immutable once stored
- Evidence has no foreign key to nodes — nodes reference evidence, not vice versa

### 2.3 Deduplication Stage

**Input:** `list[StoredEvidence]`

**Output:** `list[StoredEvidence]` (duplicates removed)

**Dedup Strategy:**

```python
def deduplicate(evidence_list: list[StoredEvidence],
                existing_hashes: set[str]) -> list[StoredEvidence]:
    """Remove evidence whose hash already exists in the store."""
    return [e for e in evidence_list if e.hash not in existing_hashes]
```

**Special cases:**
- Same hash, different timestamp → still duplicate (payload determines identity)
- Same hash, different collector → still duplicate (evidence is content-addressed)

### 2.4 Normalization Stage

**Input:** `list[StoredEvidence]`

**Output:** `list[NormalizedEvidence]`

**Contract:**

```python
@dataclass
class NormalizedEvidence:
    stored: StoredEvidence
    node_candidates: list[NodeCandidate]     # Nodes this evidence might create/update
    edge_candidates: list[EdgeCandidate]     # Edges this evidence might create/update
    fact_candidates: list[FactCandidate]     # Facts this evidence supports

@dataclass
class NodeCandidate:
    kind: str
    name: str
    properties: dict
    confidence_weight: float

@dataclass
class EdgeCandidate:
    source_candidate: str    # Node kind + name (resolved to ID later)
    target_candidate: str    # Node kind + name
    kind: str
    properties: dict
    confidence_weight: float

@dataclass
class FactCandidate:
    statement: str
    category: str
    confidence_weight: float
```

**Rules:**
- Normalization is collector-specific (each collector knows what it produces)
- Node/edge candidates are resolved to IDs in the Merge stage
- A single evidence item can produce multiple candidates

### 2.5 Merge Stage

**Input:** `list[NormalizedEvidence]`, existing `KnowledgeGraph`

**Output:** `list[GraphMutation]`

**Contract:**

```python
@dataclass
class GraphMutation:
    kind: str                  # NODE_CREATE, NODE_UPDATE, NODE_DEPRECATE,
                               # EDGE_CREATE, EDGE_DELETE
    entity_id: str             # Node or edge ID
    entity_kind: str
    properties: dict           # New or updated properties
    evidence_ref: str          # Evidence ID that justifies this mutation
    confidence_delta: float    # How this changes confidence
```

**Resolution Rules:**

1. **Identity resolution:** Node candidates are matched to existing nodes by:
   - `File`, `Directory`: matched by absolute path
   - `Class`, `Function`, `Interface`: matched by fully qualified name + file path
   - `Dependency`: matched by name + source
   - `API`, `Endpoint`: matched by method + path

2. **Conflict resolution:**
   - Same node, conflicting properties → higher confidence weight wins
   - Same node, same confidence weight → later timestamp wins
   - Same edge, conflict → higher confidence wins

3. **Deprecation:**
   - Evidence of deletion → mark node as deprecated
   - Node re-observed after deprecation → reactivate

### 2.6 Inference Stage

**Input:** `list[GraphMutation]`, existing `KnowledgeGraph`

**Output:** `list[DerivedFact]`, `list[Unknown]`, `list[GraphMutation]`

**Contract:**

```python
@dataclass
class DerivedFact:
    statement: str
    category: str
    confidence: float
    evidence_refs: list[str]      # Evidence that supports this fact
    rule_id: str                  # Rule that produced this fact
    dependencies: list[str]       # IDs of evidence/nodes this fact depends on

@dataclass
class Unknown:
    topic: str
    reason: str
    evidence_gap: str
    required_collector: str
    priority: str                 # critical, high, medium, low
    blocks: list[str]
    estimated_confidence_gain: float
```

**Inference Types:**

| Type | Description | Example |
|------|-------------|---------|
| **Structural** | Architecture from file layout | "This is a layered architecture" |
| **Semantic** | Business meaning from code patterns | "This function validates payment" |
| **Relational** | Implicit dependencies | "Feature X depends on Service Y" |
| **Temporal** | Patterns over time | "This module changes every sprint" |
| **Qualitative** | Health, risk, quality metrics | "Test coverage is low" |
| **Predictive** | Likely future states | "This dependency is likely to be deprecated" |

### 2.7 Rule Engine Contract

```python
@dataclass
class Rule:
    id: str                    # RULE-XXXX
    name: str
    description: str
    category: str              # structural, semantic, relational, temporal, qualitative, predictive
    inputs: list[RuleInput]    # Required evidence/node types
    outputs: list[RuleOutput]  # Produced fact types
    confidence_formula: str    # Expression for computing confidence
    version: str
    enabled: bool = True
    weight: float = 1.0        # Relative importance

@dataclass
class RuleInput:
    kind: str                  # Evidence kind or node kind
    required: bool             # Must be present for rule to fire
    min_count: int = 1

@dataclass
class RuleOutput:
    kind: str                  # Fact kind or node kind
    description: str
```

#### 2.7.1 Rule Definition Format

```yaml
Rules are defined in .aether/rules/ as YAML:

# detect-layered-architecture.yaml
id: RULE-0001
name: Detect Layered Architecture
category: structural
description: >
  If the repository has folders like controllers/, services/, repositories/,
  infer a layered architecture pattern.
inputs:
  - kind: DIRECTORY
    required: true
    min_count: 3
  - kind: FILE
    required: false
outputs:
  - kind: ARCHITECTURE_PATTERN
    description: "Detected architectural pattern"
confidence_formula: "folder_count / 5 * layout_score"
```

#### 2.7.2 Built-in Rules

| Rule | Category | Produces |
|------|----------|----------|
| Detect MVC | structural | Architecture pattern |
| Detect microservices | structural | Architecture pattern |
| Detect monorepo | structural | Repository structure |
| Detect framework | semantic | Framework detection |
| Map API to handlers | relational | API-Function mapping |
| Detect authentication pattern | semantic | Auth method |
| Orphan file detection | structural | Risk |
| Dead code detection | temporal | Risk |
| High churn detection | temporal | Risk |
| Test coverage assessor | qualitative | Health metric |
| Dependency freshness | qualitative | Health metric |
| Bus factor estimator | qualitative | Risk |

### 2.8 Validation Stage

**Input:** `list[GraphMutation]`, `list[DerivedFact]`

**Output:** `list[VerifiedMutation]`, `list[RejectedMutation]`, `list[Verification]`

**Contract:**

```python
@dataclass
class VerifiedMutation:
    mutation: GraphMutation
    verification: Verification

@dataclass
class RejectedMutation:
    mutation: GraphMutation
    reason: str
    verification: Verification

@dataclass
class Verification:
    id: str                    # VERIFY-XXXX
    claim: str
    claim_id: str
    evidence_refs: list[str]
    method: str                # automated, rule_based, pattern_match, cross_reference
    result: str                # verified, rejected, inconclusive
    confidence: float
    verifier: str              # Which verifier component
    timestamp: datetime
```

**Validation Checks:**

1. **Structural integrity:** Every edge references existing nodes
2. **Schema compliance:** Every node matches its kind's schema
3. **Evidence sufficiency:** Every mutation has enough evidence to justify its confidence
4. **Conflict detection:** Mutations don't contradict established facts without higher confidence
5. **Constraint enforcement:** Business rules, security rules, naming conventions

### 2.9 Materialization Stage

**Input:** `list[VerifiedMutation]`

**Output:** Graph events applied to store

**Flow:**

```python
def materialize(mutations: list[VerifiedMutation], store: Store, tx: Transaction):
    events = []
    for mutation in mutations:
        if mutation.kind == "NODE_CREATE":
            event = Event(kind="NODE_CREATED",
                          entity_id=mutation.entity_id,
                          payload=mutation.properties)
            store.node_create(tx, mutation.to_node())
        elif mutation.kind == "NODE_UPDATE":
            event = Event(kind="NODE_UPDATED",
                          entity_id=mutation.entity_id,
                          payload=mutation.properties)
            store.node_update(tx, mutation.to_node())
        # ... other kinds
        event.sequence = store.event_append(tx, event)
        events.append(event)
    return events
```

**After materialization:**
- Knowledge graph is up to date
- Verification ledger is updated
- Unknowns database is checked for resolutions
- Health metrics are flagged for re-computation

### 2.10 Compilation Stage

**Input:** Knowledge graph state

**Output:** Multiple target artifacts

**Contract:**

```python
@dataclass
class CompilerTarget:
    kind: str                  # "markdown", "ai_package", "json", "dashboard", "html", "graphml"
    output_path: Path
    config: dict               # Target-specific options

@dataclass
class CompilationArtifact:
    target: CompilerTarget
    path: Path
    size_bytes: int
    checksum: str
    generated_at: datetime
    graph_version: str
```

#### 2.10.1 Target Specifications

**repository.ai (AI Package):**
```
Binary format optimized for AI model consumption.
Contains:
- Compressed knowledge graph (nodes + edges + properties)
- Evidence ledger (immutable, verifiable)
- Confidence index (every node and edge scored)
- Genome summary (compressed to <50KB)
- Knowledge graph (serialized, <200KB)
- Verification ledger (all claims, evidence, results)
- Decision history (compressed ADRs)
- Statistics (health, coverage, risk)
- Schema version
- Graph checksum
- Timestamp

Format: CBOR (Concise Binary Object Representation) or MessagePack
Structure:
  header: {magic: "AETHER", version, timestamp, checksum}
  genome: {compressed identity, architecture}
  graph: {nodes[], edges[], confidence_index}
  ledger: {claims[], verifications[]}
  decisions: {adrs[], scores[]}
  metrics: {health[], coverage[], risk[]}
  index: {by_kind, by_tag, by_name}
  footer: {checksum, signature}
```

**Markdown:**
```
Renders graph subsets to human-readable documentation:
- FileMap (tree from Directory + File nodes)
- Architecture (from Module + Class + Function + Edge)
- Feature registry (from Feature nodes)
- API catalog (from API + Endpoint nodes)
- Database schema (from Database + Table + Column)
- Workflow map (from Workflow nodes)
- Decision log (from Decision nodes)
- Risk register (from Risk nodes)
- Unknowns report (from Unknown nodes)
- Health dashboard (from metrics)

Each markdown file includes:
- Generated timestamp
- Graph version
- Confidence indicators
- Last verified date
- Links to evidence
```

**JSON Export:**
```
Complete graph dump in structured JSON:
{
  "version": "...",
  "generated_at": "...",
  "statistics": {...},
  "nodes": [...],
  "edges": [...],
  "evidence": {...},
  "unknowns": [...],
  "health": {...}
}
```

**Dashboard JSON:**
```
Compact stats for visualization:
{
  "health": { "architecture": 89, "security": 91, ... },
  "coverage": { "authentication": 100, "business_rules": 54, ... },
  "counts": { "files": 1832, "classes": 92, "tests": 442, ... },
  "unknowns": { "total": 7, "critical": 2 },
  "risks": { "high": 3, "medium": 8 },
  "timeline": { "last_audit": "...", "last_change": "..." }
}
```

---

## 3. Incremental Pipeline

### 3.1 Trigger Sources

| Trigger | Detection | Action |
|---------|-----------|--------|
| Git commit | `git diff HEAD~1` | Scan changed files |
| File watcher | Filesystem events | Scan changed files |
| Timer | Cron every N hours | Full scan (for runtime evidence) |
| Manual | CLI command | User-specified scope |

### 3.2 Incremental Flow

```
Trigger
    │
    ▼
Determine changed paths
    │
    ▼
For each changed path:
    │
    ├── File added    → FilesystemCollector.collect(path)
    ├── File modified → FilesystemCollector.collect(path)
    └── File deleted  → Evidence(file_deleted, path) → deprecate node
    │
    ▼
New Evidence[] (subset of full pipeline)
    │
    ▼
Graph mutations scoped to affected subgraph
    │
    ▼
Rules re-fired only for affected subgraph
    │
    ▼
Only affected compiler targets re-generated
```

### 3.3 Impact Analysis

When a file changes, the system determines:

```
File changed: src/auth/login.ts
    │
    ├──→ Node: FILE-1832 (updated)
    ├──→ Node: CLASS-0092 (updated) [if class in file]
    ├──→ Edge: CONTAINS (DIR-0031 → FILE-1832) (unchanged)
    ├──→ Edge: IMPLEMENTS (CLASS-0092 → IFACE-0007) (re-verified)
    ├──→ Fact: "Authentication uses JWT" (confidence recalculated)
    ├──→ Rule: DetectMVC (re-fired for auth subgraph)
    ├──→ Unknown: "Session management" (checked for resolution)
    └──→ Views affected: FileMap, Architecture, Feature-Auth
```

---

## 4. Confidence Mathematics

### 4.1 Base Confidence

Every piece of evidence has a `confidence_weight` [0.0, 1.0]:

| Evidence Kind | Weight | Rationale |
|---------------|--------|-----------|
| AST analysis | 0.95 | Definitive, structural |
| Compiled type info | 0.95 | Type system is authoritative |
| Runtime test pass | 0.90 | Behavioral confirmation |
| Integration test | 0.85 | Multi-component validation |
| Migration file | 0.85 | Declarative schema definition |
| Configuration file | 0.80 | Explicit declaration |
| Package manifest | 0.80 | Declared dependency |
| Import statement | 0.75 | Strong signal |
| Docstring/comment | 0.50 | May be stale |
| Git history pattern | 0.60 | Statistical, not definitive |
| Log analysis | 0.55 | Observational |
| Naming convention | 0.40 | Heuristic |
| File path pattern | 0.35 | Weak structural signal |
| LLM inference | 0.30 | AI-generated, needs verification |
| Human statement | 0.70 | Domain knowledge, but fallible |

### 4.2 Composite Confidence

For a node, edge, or fact supported by multiple evidence items:

```python
def composite_confidence(evidence_list: list[Evidence]) -> float:
    """
    Combine multiple evidence weights into a single confidence score.

    Formula:
        confidence = 1 - Π(1 - wi × fi × ti × ai)

    Where:
        wi = evidence weight
        fi = freshness factor (1.0 if recent, decays to 0.5 over time)
        ti = source trust factor (1.0 for trusted collectors, 0.5 for LLM)
        ai = agreement factor (1.0 if all agree, 0.5 if conflicting)
    """
    if not evidence_list:
        return 0.0

    product = 1.0
    for e in evidence_list:
        adjusted_weight = (e.confidence_weight *
                           freshness_factor(e) *
                           source_trust_factor(e) *
                           agreement_factor(e, evidence_list))
        product *= (1.0 - adjusted_weight)

    return 1.0 - product
```

### 4.3 Freshness Decay

```python
def freshness_factor(evidence: Evidence, now: datetime = None) -> float:
    """
    Evidence freshness decays over time.

    - Static evidence (AST, config, manifest): decays to 0.9 after 30 days
    - Dynamic evidence (test, runtime): decays to 0.5 after 30 days
    - Human evidence: decays to 0.5 after 90 days
    - Git evidence: decays to 0.7 after 7 days
    """
    if now is None:
        now = datetime.utcnow()

    age_days = (now - evidence.collected_at).total_seconds() / 86400.0

    decay_rates = {
        "static":   0.90,   # Retains 90% after 30 days
        "dynamic":  0.50,   # Retains 50% after 30 days
        "human":    0.50,   # Retains 50% after 90 days
        "git":      0.70,   # Retains 70% after 7 days
    }

    half_lives = {
        "static":   30,
        "dynamic":  30,
        "human":    90,
        "git":      7,
    }

    kind = evidence.kind
    half_life = half_lives.get(kind, 30)
    decay_rate = decay_rates.get(kind, 0.80)

    return decay_rate ** (age_days / half_life)
```

### 4.4 Source Trust

```python
def source_trust_factor(evidence: Evidence) -> float:
    """
    Trust score based on evidence source.

    - AST parser: 1.0 (definitive)
    - Test runner: 1.0 (definitive)
    - Package manager: 0.95
    - Git: 0.90
    - Runtime probe: 0.85
    - Log parser: 0.70
    - LLM: 0.40 (AI-generated, requires verification)
    - Human input: 0.75 (domain expert, but fallible)
    - Web API: 0.60 (external dependency)
    """
    trust_scores = {
        "ast_parser": 1.0,
        "test_runner": 1.0,
        "package_manager": 0.95,
        "git": 0.90,
        "runtime_probe": 0.85,
        "log_parser": 0.70,
        "type_checker": 1.0,
        "migration_parser": 0.95,
        "config_parser": 0.95,
        "llm": 0.40,
        "human": 0.75,
        "web_api": 0.60,
        "mcp_server": 0.70,
    }
    return trust_scores.get(evidence.collector, 0.50)
```

### 4.5 Agreement Factor

```python
def agreement_factor(evidence: Evidence,
                     all_evidence: list[Evidence]) -> float:
    """
    How much this evidence agrees with others supporting the same claim.

    - All agree: 1.0
    - Majority agree: 0.9
    - Split: 0.7
    - Minority: 0.5
    - Alone: 0.8 (no conflict, but no corroboration)
    """
    if len(all_evidence) == 1:
        return 0.8  # Lone witness

    # Same claim, same direction
    agreeing = sum(1 for e in all_evidence
                   if e.confidence_weight >= 0.5 == evidence.confidence_weight >= 0.5)
    ratio = agreeing / len(all_evidence)

    if ratio >= 0.9:
        return 1.0
    elif ratio >= 0.66:
        return 0.9
    elif ratio >= 0.33:
        return 0.7
    else:
        return 0.5
```

### 4.6 Verification Boost

```python
def verification_boost(verification: Verification) -> float:
    """
    Independent verification adds a multiplier.

    - Verified by test: 1.5x
    - Verified by manual review: 1.3x
    - Cross-referenced: 1.2x
    - Verified by runtime: 1.4x
    - Unverified: 1.0x
    - Contradicted: 0.0x
    """
    multipliers = {
        "test": 1.5,
        "manual_review": 1.3,
        "cross_reference": 1.2,
        "runtime": 1.4,
        "unverified": 1.0,
        "contradicted": 0.0,
    }
    return multipliers.get(verification.method, 1.0)
```

### 4.7 Final Confidence

```python
def final_confidence(node: Node,
                     evidence_list: list[Evidence],
                     verification: Verification = None) -> float:
    """Compute final confidence for a node, edge, or fact."""
    base = composite_confidence(evidence_list)

    if verification:
        base *= verification_boost(verification)

    return min(max(base, 0.0), 1.0)  # Clamp to [0, 1]
```

### 4.8 Confidence Tiers

| Range | Label | Meaning |
|-------|-------|---------|
| 0.95 - 1.00 | **Verified** | Multiple definitive evidence sources, independently verified |
| 0.85 - 0.94 | **High Confidence** | Strong evidence, consistent across sources |
| 0.70 - 0.84 | **Medium Confidence** | Good evidence, some inference involved |
| 0.50 - 0.69 | **Low Confidence** | Heuristic or limited evidence |
| 0.25 - 0.49 | **Speculative** | AI-generated or inferred without direct evidence |
| 0.00 - 0.24 | **Unknown** | Insufficient evidence to make any claim |

---

## 5. Collector SDK Contract

### 5.1 Collector Base

```python
class BaseCollector(ABC):
    """Every collector implements this interface."""

    @abstractmethod
    def name(self) -> str: ...
    @abstractmethod
    def version(self) -> str: ...
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def capabilities(self) -> list[CollectorCapability]: ...

    @abstractmethod
    def collect(self, input: CollectorInput) -> list[RawEvidence]:
        """
        Main collection method.
        - Must be safe to call concurrently
        - Must handle partial failures gracefully
        - Must respect resource bounds (max_files, max_depth, timeout)
        - Returns empty list if nothing to collect
        """

    @abstractmethod
    def can_handle(self, input: CollectorInput) -> bool:
        """Can this collector process the given input?"""

    def dependencies(self) -> list[str]:
        """Other collector names this depends on (optional)."""
        return []
```

### 5.2 Collector Discovery

```python
# Collectors are discovered via:
# 1. Built-in: Registered in aether.collectors.builtin
# 2. Plugin: Entry points (aether.collectors) in installed packages
# 3. Config: Explicit paths in .aether/config.yaml

class CollectorRegistry:
    def register(self, collector: BaseCollector) -> None: ...
    def get(self, name: str) -> BaseCollector: ...
    def all(self) -> list[BaseCollector]: ...
    def for_input(self, input: CollectorInput) -> list[BaseCollector]: ...
```

### 5.3 Resource Bounds

```python
@dataclass
class CollectorBounds:
    max_files: int = 10000
    max_depth: int = 20
    max_size_mb: int = 100
    timeout_seconds: int = 300
    max_evidence_per_run: int = 50000
```

---

## 6. Orchestration

### 6.1 Pipeline Runner

```python
class PipelineRunner:
    """
    Orchestrates the full or incremental pipeline.
    """

    def __init__(self, store: Store, registry: CollectorRegistry,
                 rule_engine: RuleEngine, compiler: Compiler):
        ...

    def run_full(self, repo_path: Path) -> PipelineResult:
        """Full pipeline: all collectors, all rules, all targets."""

    def run_incremental(self, repo_path: Path,
                        changed_paths: list[str]) -> PipelineResult:
        """Incremental pipeline: affected collectors, subgraph, targets."""

    def run_collectors(self, input: CollectorInput) -> list[RawEvidence]:
        """Run all applicable collectors."""

    def run_inference(self, evidence: list[StoredEvidence]) -> PipelineResult:
        """Run inference on new evidence without full collection."""

    def run_verification(self, mutations: list[GraphMutation]) -> list[VerifiedMutation]:
        """Verify pending mutations before materialization."""

    def run_compile(self, targets: list[CompilerTarget]) -> list[CompilationArtifact]:
        """Compile current graph state to targets."""
```

### 6.2 Pipeline Result

```python
@dataclass
class PipelineResult:
    success: bool
    events_appended: int
    nodes_created: int
    nodes_updated: int
    nodes_deprecated: int
    edges_created: int
    edges_deleted: int
    facts_derived: int
    unknowns_identified: int
    unknowns_resolved: int
    verifications_recorded: int
    artifacts_generated: list[CompilationArtifact]
    warnings: list[str]
    errors: list[str]
    duration_ms: int
```

### 6.3 Error Recovery

- Stage failures are non-fatal unless they involve data corruption
- Collectors retry up to 3 times on transient errors
- Pipeline state is checkpointed after each stage
- On crash recovery: resume from last checkpoint
- Events are idempotent (same event applied twice → same result)

---

## 7. CI Integration

### 7.1 GitHub Action

```yaml
name: Aether Intelligence Update
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  aether:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for git collector
      - uses: aether/setup@v1
      - run: aether scan --incremental
      - run: aether compile --target markdown --output docs/
      - run: aether compile --target ai-package --output .aether/
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "auto: update repository intelligence"
```

### 7.2 Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: aether-scan
        name: Aether incremental scan
        entry: aether scan --incremental --staged
        language: system
        pass_filenames: true
```

---

## 8. Verification Pipeline (for AI Claims)

When an AI model proposes a change to the knowledge graph:

```
AI Model
    │
    ├── Claim: "This repo uses Stripe for payments"
    │
    ▼
Claim Store (untrusted)
    │
    ├── Evidence needed: ["stripe" in package.json, "Stripe" in imports,
    │                      "stripe" in config files, API routes matching Stripe patterns]
    │
    ▼
Evidence Collector (trusted)
    │
    ├── Evidence gathered:
    │     ├── package.json has "stripe": "^12.0.0"  ← EVID-0991 (weight: 0.80)
    │     ├── src/payment/stripe.ts exists            ← EVID-0992 (weight: 0.95)
    │     ├── stripe webhook routes found             ← EVID-0993 (weight: 0.85)
    │     └── Stripe API key pattern in config        ← EVID-0994 (weight: 0.75)
    │
    ▼
Verifier
    │
    ├── Composite confidence: 0.97
    ├── Verification: "verified" (all evidence supports claim)
    │
    ▼
Graph Event: FACT-2882 created
    │
    ▼
Knowledge Graph updated
    │
    ▼
Compiler generates updated documentation
```

If the AI claim is wrong:

```
AI Claim: "This repo uses Braintree for payments"
    │
    ▼
Evidence Collector: No Braintree evidence found
    │
    ▼
Verifier: "rejected" (no supporting evidence)
    │
    ▼
Unknown: "payment processor" created
    │
    ▼
Claim is logged with AI metadata for review
```
