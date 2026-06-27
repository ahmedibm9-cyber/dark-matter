# Dark Matter — Roadmap v1

> **Status:** Ratified
> **Purpose:** Phased implementation plan from vertical slice to production platform

---

## Phase 1 — Freeze the Platform

Lock down the abstractions that every future feature depends on.

| Task | Artifact | Priority | Est. Effort |
|------|----------|----------|-------------|
| Capability/Plugin System | CAPABILITY-SYSTEM.md | P0 | Spec complete |
| Canonical GraphService API | GRAPHSERVICE-API.md | P0 | Spec complete |
| Event Model | EVENT-MODEL.md | P0 | Spec complete |
| Knowledge Reasoner | REASONER.md | P1 | Spec complete |
| Implement Capability Registry | `src/aether/capabilities/` | P0 | 2-3 sessions |
| Implement GraphService | `src/aether/graph/service.py` | P0 | 2-3 sessions |
| Wire events into GraphService | `src/aether/graph/events.py` | P0 | 1 session |
| Migrate existing collectors to plugins | Refactor | P0 | 1 session |

**Definition of done:** No component imports the store directly. Everything goes through GraphService. Capabilities are registered and discovered.

**Important:** The CLI is now `dm` (not `aether`). Store directory is `.darkmatter` (not `.aether`).

---

## Phase 2 — Harden the Vertical Slice

Strengthen the existing prototype to be re-runnable and deterministic.

| Task | Artifact | Priority | Est. Effort |
|------|----------|----------|-------------|
| Persistent ID counters | `store/counters.py` | P0 | 1 session |
| YAML rule packs (replace hardcoded) | `src/aether/inference/rules/` | P0 | 1 session |
| YAML pattern packs (reasoner) | `src/aether/reasoner/patterns/` | P1 | 1 session |
| Schema validation | `src/aether/graph/schema.py` | P0 | 1 session |
| Transaction support in JSON store | `src/aether/store/json_store.py` | P0 | 1 session |
| Incremental scan mode | `pipeline.py:run_incremental()` | P0 | 2 sessions |
| Determinism tests | `tests/test_determinism.py` | P0 | 1 session |
| Integration tests for acceptance criteria | `tests/test_acceptance.py` | P0 | 1 session |

**Definition of done:** `python src/run_pipeline.py --input repo` produces identical output on re-runs. Evidence deduplicates. IDs persist across runs. Rules are loaded from YAML.

**Important:** The CLI is now `dm` (not `aether`). Store directory is `.darkmatter` (not `.aether`).

---

## Phase 3 — Build the User Experience

Transform from a library into a CLI tool.

| Task | Artifact | Priority | Est. Effort |
|------|----------|----------|-------------|
| `aether init` | CLI | P0 | 1 session |
| `aether scan` | CLI | P0 | 1 session |
| `aether verify` | CLI | P1 | 1 session |
| `aether compile` | CLI | P0 | 1 session |
| `aether query` | CLI | P1 | 2 sessions |
| `aether graph` | CLI | P1 | 1 session |
| `aether explain` | CLI | P1 | 1 session |
| `aether doctor` | CLI | P2 | 1 session |
| `aether diff` | CLI | P2 | 2 sessions |
| `aether stats` | CLI | P1 | 1 session |
| Tab completion | CLI | P2 | 1 session |
| `.aether/config.yaml` | Configuration | P0 | 1 session |

**Definition of done:** Aether is installable via pip and has a complete CLI with help, tab completion, and configuration.

---

## Phase 4 — Scale

Add production capabilities.

| Task | Artifact | Priority | Est. Effort |
|------|----------|----------|-------------|
| Git collector | `collectors/git.py` | P0 | 2 sessions |
| AST collector (Python) | `collectors/ast_python.py` | P0 | 3 sessions |
| AST collector (TypeScript) | `collectors/ast_typescript.py` | P1 | 3 sessions |
| Dependency collector | `collectors/dependencies.py` | P0 | 2 sessions |
| Security scanner pack | `rules/security/` | P1 | 3 sessions |
| Rule pack: Docker | `rules/docker/` | P2 | 1 session |
| Rule pack: Next.js | `rules/nextjs/` | P2 | 1 session |
| Rule pack: React | `rules/react/` | P2 | 1 session |
| CI integration (GitHub Actions) | `.github/workflows/aether.yml` | P1 | 1 session |
| IDE integration (VS Code) | `extensions/vscode/` | P2 | 3 sessions |
| SQLite store | `store/sqlite_store.py` | P1 | 3 sessions |

**Definition of done:** Aether can scan real-world repositories with Git history, AST analysis, and dependency resolution. Outputs include architecture reports, security findings, and dependency health.

---

## Phase 5 — Ecosystem

Expand beyond single-repository intelligence.

| Task | Artifact | Priority | Est. Effort |
|------|----------|----------|-------------|
| Cross-repo queries | `query/` | P2 | 3 sessions |
| Reasoner pack: architecture | `patterns/architecture/` | P1 | 2 sessions |
| Reasoner pack: quality | `patterns/quality/` | P1 | 2 sessions |
| Reasoner pack: evolution | `patterns/evolution/` | P2 | 2 sessions |
| Query language (AetherQL) | `query/language/` | P2 | 4 sessions |
| Dashboard (web) | `dashboard/` | P2 | 4 sessions |
| Remote capability registry | `capabilities/remote/` | P3 | 4 sessions |
| Neo4j store | `store/neo4j_store.py` | P3 | 3 sessions |
| Model benchmark suite | `benchmarks/` | P2 | 2 sessions |

**Definition of done:** Aether can analyze multi-repository systems, provides a web dashboard, and includes a query language.

---

## Current Status (June 2026)

| Phase | Progress |
|-------|----------|
| Phase 1 (Freeze) | Specs complete. Implementation not started. |
| Phase 2 (Harden) | Not started. |
| Phase 3 (CLI) | Not started. |
| Phase 4 (Scale) | Not started. |
| Phase 5 (Ecosystem) | Not started. |

**Next milestone:** Phase 1 implementation — Capability Registry + GraphService + Event wiring.

---

## Appendix: Vertical Slice Accepted Limitations

The existing v0.1 prototype (`src/aether/`) has these known limitations,
all of which are addressed in Phases 1-2:

| Limitation | Resolution |
|------------|------------|
| ID counters reset on restart | Phase 2: Persistent counters |
| Rules hardcoded in Python | Phase 2: YAML rule packs |
| No GraphService (direct store access) | Phase 1: GraphService |
| No capability system | Phase 1: Capability registry |
| No event recording | Phase 1: Event model |
| No incremental mode | Phase 2: Incremental scan |
| No schema validation | Phase 2: Schema registry |
| Single-writer JSON store | Phase 2: File locking |
