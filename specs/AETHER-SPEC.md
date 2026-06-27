# Dark Matter Specification v1.0

> **Status:** Proposed
> **Constitutional document for the Dark Matter Intelligence Platform.**

---

## 0. Preamble

Dark Matter is an intelligence operating system for software repositories.
Its purpose is to continuously extract, verify, organize, compile, and distribute
repository knowledge so that any human or AI can make high-confidence engineering
decisions with minimal context and maximal traceability.

Dark Matter observes repositories. It never modifies them.

---

## 1. Philosophy

### 1.1 Purpose
Observe repositories. Never modify them. Infer knowledge. Never invent facts.
Preserve evidence. Explain every conclusion. Produce deterministic outputs.
Remain model-independent.

### 1.2 Principles
1. **Evidence is sacred.** Evidence is the only source of truth. Everything else is derived.
2. **Facts must be earned.** Every fact must trace back to evidence.
3. **Inference is not invention.** Inference generalizes from evidence; it does not fabricate.
4. **Confidence must be explainable.** Every confidence score decomposes into its contributing factors.
5. **Determinism is required.** Same evidence + same graph + same rules → same output.
6. **Model independence is axiomatic.** No AI model writes to the graph directly.
7. **Storage is a detail.** The core engine never touches storage directly.
8. **Views are ephemeral.** Markdown, JSON, dashboards are generated; they are never sources of truth.

---

## 2. Immutable Rules

### 2.1 Evidence Rules
| Rule | Contract |
|------|----------|
| Evidence SHALL be immutable | evidence-contract.md §Invariants |
| Evidence SHALL NOT be deleted | evidence-contract.md §Invariants |
| Evidence SHALL be content-addressed | evidence-contract.md §Invariants |
| Evidence SHALL NOT reference nodes | evidence-contract.md §Invariants |

### 2.2 Node Rules
| Rule | Contract |
|------|----------|
| Nodes SHALL have stable identity | node-contract.md §Invariants |
| Nodes SHALL reference evidence | node-contract.md §Invariants |
| Node kind SHALL NOT change | node-contract.md §Invariants |
| Node properties SHALL satisfy schema | node-contract.md §Invariants |

### 2.3 Edge Rules
| Rule | Contract |
|------|----------|
| Edges SHALL reference valid nodes | edge-contract.md §Invariants |
| Edges SHALL reference evidence | edge-contract.md §Invariants |
| Edge composite key SHALL be unique | edge-contract.md §Invariants |

### 2.4 Collector Rules
| Rule | Contract |
|------|----------|
| Collectors SHALL NOT modify repositories | collector-contract.md §Invariants |
| Collectors SHALL be resource-bounded | collector-contract.md §Invariants |
| Collector failures SHALL be isolated | collector-contract.md §Invariants |

### 2.5 Inference Rules
| Rule | Contract |
|------|----------|
| Rules SHALL NOT modify evidence or graph | rule-contract.md §Invariants |
| Rules SHALL be deterministic | rule-contract.md §Invariants |
| Rules SHALL be declarative | rule-contract.md §Invariants |

### 2.6 Compiler Rules
| Rule | Contract |
|------|----------|
| Compilers SHALL be deterministic | compiler-contract.md §Invariants |
| Compilers SHALL NOT modify graph or evidence | compiler-contract.md §Invariants |
| Compilers SHALL include graph version in output | compiler-contract.md §Invariants |

### 2.7 Query Rules
| Rule | Contract |
|------|----------|
| Queries SHALL NOT modify the graph | query-contract.md §Invariants |
| Queries SHALL be deterministic | query-contract.md §Invariants |

### 2.8 Verification Rules
| Rule | Contract |
|------|----------|
| Verifiers SHALL NOT modify the graph | verifier-contract.md §Invariants |
| Verification SHALL be evidence-based | verifier-contract.md §Invariants |
| Verification SHALL NOT trust claim sources | verifier-contract.md §Invariants |

### 2.9 Architecture Rules
| Rule | Source |
|------|--------|
| AI SHALL NOT write to the graph directly | ARCHITECTURE.md §3.2 |
| Storage SHALL satisfy the store interface | STORAGE-IFACE.md §2 |
| The graph SHALL be event-sourced | ARCHITECTURE.md §1 #1 |
| Evidence SHALL be separated from knowledge | ARCHITECTURE.md §1 #5 |

---

## 3. Contracts

All implementations of Dark Matter MUST satisfy the following contracts:

| Contract | Version | Status |
|----------|---------|--------|
| contracts/node-contract.md | v1 | Proposed |
| contracts/edge-contract.md | v1 | Proposed |
| contracts/evidence-contract.md | v1 | Proposed |
| contracts/collector-contract.md | v1 | Proposed |
| contracts/rule-contract.md | v1 | Proposed |
| contracts/compiler-contract.md | v1 | Proposed |
| contracts/query-contract.md | v1 | Proposed |
| contracts/verifier-contract.md | v1 | Proposed |

These contracts SHALL NOT be violated. If a contract must change, it requires
an RFC and a new version number. The old contract remains valid for
implementations targeting the previous version.

---

## 4. Architecture

The architecture SHALL follow the subsystem boundaries defined in
`ARCHITECTURE.md`. The following layers are mandatory:

1. **Collector Layer** — produces evidence
2. **Evidence Layer** — stores evidence immutably
3. **Inference Layer** — applies rules to produce facts
4. **Knowledge Layer** — materializes the knowledge graph
5. **Compiler Layer** — generates output artifacts
6. **Storage Layer** — provides persistence

Each layer SHALL communicate through the defined contracts.
No layer SHALL bypass a contract to access another layer's internals.

---

## 5. Governance

### 5.1 RFC Process
Changes to the specification, contracts, or architecture SHALL follow the RFC
process defined in `/rfcs/`. Key rules:

- Every RFC has a unique numeric identifier
- RFCs are never deleted — only superseded
- RFCs document the decision, rationale, and alternatives considered

### 5.2 Versioning
The specification uses semantic versioning:

- MAJOR: Breaking contract changes
- MINOR: Non-breaking additions (new node kinds, new contracts)
- PATCH: Clarifications, corrections, metadata

### 5.3 Scope
Explicit non-goals are defined in `NON-GOALS.md`.
Features that fall into non-goal categories SHALL be rejected without RFC.

---

## 6. Compliance

An implementation MAY claim compliance with Dark Matter Specification v1 only if:

1. It satisfies all contracts listed in §3
2. It implements all mandatory layers in §4
3. It follows all immutable rules in §2
4. It does not violate any non-goal in `NON-GOALS.md`
5. It passes the acceptance criteria in `ACCEPTANCE-CRITERIA.md`

Partial compliance SHALL be explicitly declared as "Dark Matter Specification v1 — Partial"
with the missing contracts listed.
