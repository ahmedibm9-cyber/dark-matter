# User Journey — A Developer's Day with Aether

> **Status:** Draft
> **Purpose:** Define every interaction a developer has with Aether, from project creation to shipping. No architecture. No nodes. No edges. Just commands, outputs, and what happens.

---

## The 10 Commands

```
aether init      — Start a new project with Aether
aether start     — Begin a work session
aether work      — Load context for a task
aether scan      — Update intelligence from changes
aether verify    — Check facts against evidence
aether compile   — Generate outputs
aether review    — Get pre-commit/pre-PR analysis
aether doctor    — Diagnose and fix issues
aether search    — Find anything in project knowledge
aether explain   — Understand why Aether thinks something
```

That's it. A developer never needs more than these.

---

## Scenario 1 — Starting a New Project

**What the user does:**

```bash
cd my-new-project
aether init
```

**What they see:**

```
Aether initialized.

Scanning project structure...
  ✓ 47 files found
  ✓ Languages: TypeScript, CSS, JSON
  ✓ Dependencies: 23 direct, 81 transitive
  ✓ Git history: 142 commits, 4 contributors

Repository intelligence ready.

Next: aether start
```

**What happened internally (user never sees this):**
- `aether init` created `.aether/` directory structure
- Filesystem collector ran: 47 evidence records
- Dependency collector ran: 104 evidence records  
- Git collector ran: 142 commits analyzed
- Inference engine detected: Next.js, React, Tailwind
- Knowledge graph built: 62 nodes, 89 edges
- Confidence computed for all initial facts
- `repository.ai` compiled
- Health baseline established

**Subsystems involved:** All of them. For the first and only time.

---

## Scenario 2 — Morning Session Start

**What the user does:**

```bash
aether start
```

**What they see:**

```
Good morning.

─── Today's Focus ──────────────────────────────
  TASK-044   Fix scoring algorithm overflow
  SAT        Practice session (30 min)
  USRA-071   Authentication bug

─── Project Health ─────────────────────────────
  sat-tool       87  (stable)
  usra-plus      71  (declining)

─── Overnight Changes ──────────────────────────
  • 3 new commits (auth module)
  • 1 dependency updated (express 4.18→4.19)
  • Confidence dropped in scoring module (92→84)

─── Recommended ────────────────────────────────
  aether work TASK-044
```

**What happened internally:**
- Checked `.aether/` for existing intelligence
- Compared last-known graph state with current filesystem
- Detected 3 new git commits
- Re-ran dependency collector for changed package.json
- Updated confidence for affected facts
- Computed delta report
- Loaded task registry (from `.aether/tasks/` or external tracker)
- Selected recommended next action

---

## Scenario 3 — Loading Task Context

**What the user does:**

```bash
aether work TASK-044
```

**What they see:**

```
Loading task: Fix scoring algorithm overflow

─── Context ────────────────────────────────────
  Description: Math.floor overflow in large group
  scoring produces negative results above 2^31

─── Known Architecture ─────────────────────────
  src/scoring/math.ts  (confidence: 98%)
  src/scoring/group.ts (confidence: 95%)

─── Related Facts ──────────────────────────────
  Scoring uses 32-bit integer (confidence: 92%)
  Max group size 10,000 (confidence: 87%)

─── Affected by Change ─────────────────────────
  Decision DEC-0031: "Use fixed-point arithmetic"
  (confidence: 78% — 6 months old)

─── Suggested First File ───────────────────────
  src/scoring/math.ts

─── Tests ──────────────────────────────────────
  tests/scoring/math.test.ts  (coverage: 83%)
  tests/scoring/group.test.ts (coverage: 71%)

─── Previous Attempts ──────────────────────────
  Branch fix/overflow-v1 (merged, incomplete)
  Branch fix/overflow-v2 (abandoned)
```

**What happened internally:**
- Queried knowledge graph for task-relevant nodes
- Found FILE nodes: math.ts, group.ts
- Found DECISION node: DEC-0031 with evidence chain
- Found FACTS: integer size, max group size
- Found TEST nodes with coverage metrics
- Checked git history for related branches
- Computed confidence for all displayed facts
- Retrieved evidence freshness for age indicator

---

## Scenario 4 — During Development

**What the user does:** Saves a file.

**What they see:** Nothing. Aether watches silently.

**What happened internally:**
- File watcher detected change
- Evidence collected: FILE_MODIFIED
- Affected subgraph identified: math.ts node + edges
- Re-ran only rules that depend on this file
- Updated confidence for affected facts
- Checked for regressions (no new unknowns)
- Updated health metrics incrementally
- Total elapsed: ~300ms (no visible output)

---

## Scenario 5 — Manual Intelligence Update

**What the user does:**

```bash
aether scan
```

**What they see:**

```
Scanning...

  ── Collected ─────────────────────────────────
  Filesystem:    12 files changed
  Dependencies:  1 added, 0 removed
  Git:           5 new commits

  ── Inference ─────────────────────────────────
  2 facts promoted (confidence increased)
  1 fact deprecated (no longer supported)
  1 unknown resolved (new evidence found)

  ── Health ────────────────────────────────────
  Architecture:  unchanged
  Security:      unchanged
  Testing:       unchanged
  Confidence:    +2% (scoring module)

  Scan complete (1.2s)
```

**What happened internally:**
- Incremental pipeline: only changed files processed
- Evidence deduplicated against existing store
- Graph updated: nodes updated, edges re-verified
- Inference re-ran only on affected subgraph
- Confidence recomputed for affected entities
- Unknowns checked for resolution
- Health metrics recalculated
- No re-compile (user didn't request it)

---

## Scenario 6 — Verifying Work

**What the user does:**

```bash
aether verify
```

**What they see:**

```
Verification Results

  ── Claims Made ───────────────────────────────
  "Uses BigInt for scoring" → VERIFIED (0.94)
    evidence: src/scoring/math.ts (0.92)
              src/scoring/group.ts (0.89)
              test/scoring/bigint.test.ts (0.95)

  "Eliminated integer overflow" → VERIFIED (0.91)
    evidence: test/scoring/overflow.test.ts (0.93)
              test run 2026-06-26 (0.88)

  ── Unknowns ──────────────────────────────────
  "Performance impact at 100k groups"
  Requires: benchmark test (missing collector)

  ── Summary ───────────────────────────────────
  7 verified     (confidence ≥ 0.70)
  2 inconclusive (need more evidence)
  0 rejected
  1 unknown detected
```

**What happened internally:**
- Collected new evidence from changed files
- Ran inference rules on new evidence
- Cross-referenced new facts with existing knowledge
- Compared new evidence against existing verification records
- Computed composite confidence using the full formula
- Identified gaps as new Unknowns
- Recorded all verifications in the ledger

---

## Scenario 7 — Pre-Commit Review

**What the user does:**

```bash
aether review
```

**What they see:**

```
Review Ready

  ── What Changed ──────────────────────────────
  4 files modified
  2 features affected: scoring, reporting
  1 decision impacted: DEC-0031 (fixed-point)

  ── Risks ─────────────────────────────────────
  LOW    Reporting module uses old math API
         → test still passes, but check output

  ── Documentation ─────────────────────────────
  ⚠ Architecture diagram is stale
    → run aether compile to update

  ── Recommendation ────────────────────────────
  ✓ No blocking issues found.
  ✓ All affected tests pass.
  ✓ Confidence increased for scoring facts.

  Run aether compile before commit.
```

**What happened internally:**
- Compared pre-scan graph state with current
- Identified affected feature nodes via edge traversal
- Checked impact on decision nodes
- Scanned for known risk patterns
- Checked documentation freshness (last compile timestamp vs. last change)
- Queried test results for affected files
- Generated risk assessment

---

## Scenario 8 — Compiling Intelligence

**What the user does:**

```bash
aether compile
```

**What they see:**

```
Compiling...

  ── Outputs ───────────────────────────────────
  ✓ .aether/repository.ai          (12 KB)
  ✓ .aether/intelligence.md        (24 KB)
  ✓ .aether/architecture.svg       (updated)
  ✓ .aether/change-log.md          (updated)

  Compilation complete (0.4s)
```

**What happened internally:**
- Read current graph state (via GraphService)
- Ran each registered compiler capability:
  - AI package compiler: serialized graph to CBOR/MessagePack
  - Markdown compiler: rendered FileMap, facts, decisions
  - Architecture compiler: rendered graphviz/d2 diagram
  - Changelog compiler: diffed event log for new events
- Each compiler produced deterministic output
- All artifacts written to `.aether/`
- Compilation event recorded

---

## Scenario 9 — Before Opening a PR

**What the user does:**

```bash
aether review --pr
```

**What they see:**

```
PR Review: feature/scoring-overflow-fix

  ── Summary ───────────────────────────────────
  Base: main (abc1234)
  Branch: feature/scoring-overflow-fix (def5678)
  12 commits, 8 files changed

  ── Intelligence Delta ────────────────────────
  +3 facts added
  +1 unknown resolved
  +1 confidence increased (scoring: 84→94)
  ~0 decisions changed
  !0 regressions detected

  ── Affected Features ─────────────────────────
  Scoring        ─── impact: HIGH
  Reporting      ─── impact: LOW (compatible)

  ── Verification ──────────────────────────────
  ✓ All new claims have supporting evidence
  ✓ No contradictory evidence found
  ✓ Tests pass for affected features

  ── Recommendation ────────────────────────────
  ✓ Ready for PR.
  ── 2 reviewers suggested (auth, scoring owners)
```

---

## Scenario 10 — Before a Release

**What the user does:**

```bash
aether review --release v2.1.0
```

**What they see:**

```
Release Review: v2.1.0

  ── Since v2.0.0 ─────────────────────────────
  47 commits
  23 files changed
  3 features added
  2 bugs fixed
  1 dependency updated
  0 breaking changes detected

  ── Intelligence Health ───────────────────────
  Architecture:          87  (stable)
  Testing:               82  (+5 since v2.0.0)
  Security:              91  (unchanged)
  Documentation:         78  (-3, needs update)
  Confidence:            89  (unchanged)

  ── Risks ─────────────────────────────────────
  MEDIUM   New auth dependency (passport v0.7)
           → 1 CVE in transitive dep
  LOW      Deprecated API used in 2 places

  ── Recommendation ────────────────────────────
  ✓ Release-blocking: NO
  ⚠ Address MEDIUM risk before shipping
  ── Run: aether doctor --fix
```

---

## Scenario 11 — After a Production Bug

**What the user does:**

```bash
aether search "payment timeout"
```

**What they see:**

```
Search Results: "payment timeout"

  ── Files ─────────────────────────────────────
  src/payment/process.ts        (confidence: 95%)
  src/payment/webhook.ts        (confidence: 92%)

  ── Facts ─────────────────────────────────────
  "Payment processing uses Stripe" (verified)
  "Webhook timeout is 30s"         (confidence: 87%)

  ── Decisions ────────────────────────────────
  DEC-0021: "Use Stripe for payments" (2025-11)
  DEC-0044: "Set webhook timeout to 30s" (2026-01)

  ── Unknowns ─────────────────────────────────
  "Timeout behavior in high-load"
  ⚠ Marked as unknown — missing load test evidence

  ── Recent Changes ───────────────────────────
  payment/webhook.ts modified 2 days ago
  by @ahmed (commit a1b2c3d)
```

---

## Scenario 12 — Diagnosing Issues

**What the user does:**

```bash
aether doctor
```

**What they see:**

```
Aether Diagnostic

  ── Store Health ──────────────────────────────
  ✓ Event log: 1,442 events, no gaps
  ✓ Evidence store: 891 records, all hashes valid
  ✓ Knowledge graph: 312 nodes, 487 edges
  ✓ No schema version drift

  ── Capability Health ─────────────────────────
  ✓ 12 capabilities registered
  ✓ 0 stale capabilities
  ✓ All dependencies resolved

  ── Recommended Actions ───────────────────────
  • Run aether scan (last scan was 3 days ago)
  • 2 unknowns can be resolved by adding a test collector
  • Confidence decay detected in auth module
    → re-verify with aether verify
```

---

## Scenario 13 — Explaining a Fact

**What the user does:**

```bash
aether explain "uses Stripe for payments"
```

**What they see:**

```
Explanation: "Uses Stripe for payments"

  Confidence: 97% (VERIFIED)

  ── Evidence Chain ────────────────────────────
  1. package.json → stripe: ^12.0.0
     collector: filesystem (0.80)
     freshness: 12 days (0.97)

  2. src/payment/stripe.ts
     collector: filesystem (0.95)
     freshness: 12 days (0.97)

  3. src/payment/stripe.test.ts (passing)
     collector: test_runner (0.90)
     freshness: 7 days (0.98)

  ── Composite ─────────────────────────────────
  0.80×0.97 + 0.95×0.97 + 0.90×0.98
  = 0.97 (VERIFIED)

  ── Verification ──────────────────────────────
  VERIFY-0042 | 2026-06-20 | automated
  Result: All evidence supports claim
```

---

## Scenario 14 — Switching AI Models

**What the user does:**

```bash
# User switches from Claude to GPT-5
# No Aether command needed.

# New AI reads:
cat .aether/repository.ai
```

**What happens:**
- The `repository.ai` package contains the complete knowledge graph
- The new AI loads it in under 2 seconds
- It has all nodes, edges, facts, evidence, decisions, and confidence scores
- It can answer questions immediately without scanning the repository
- It knows what's verified, what's inferred, and what's unknown
- Model replacement is invisible to the user

---

## The Three Products

```
┌─────────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (10 commands)                      │
│                                                                     │
│  aether init | start | work | scan | verify | compile               │
│  aether review | doctor | search | explain                          │
│                                                                     │
│  The developer never thinks about nodes, edges, or confidence.      │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AETHER KERNEL (invisible)                         │
│                                                                     │
│  Collectors → Evidence → GraphService → Inference → Reasoner        │
│  → Verification → Compiler → Event Log → Capability Registry       │
│                                                                     │
│  The kernel you've already specified in detail.                      │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    INTELLIGENCE PACKAGE (portable)                   │
│                                                                     │
│  repository.ai                                                      │
│                                                                     │
│  Consumed by: Claude, GPT, Gemini, Cursor, OpenCode, MCP servers    │
│  Zero setup. Instant expertise.                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Summary

| Scenario | Command | User sees | Hidden subsystems |
|----------|---------|-----------|-------------------|
| New project | `aether init` | Project summary | All collectors, inference, graph build |
| Morning | `aether start` | Focus, health, changes | Delta detection, task loading |
| Task context | `aether work TASK` | Architecture, facts, tests | Graph queries, confidence lookup |
| Save file | (automatic) | Nothing | Incremental pipeline (~300ms) |
| Manual update | `aether scan` | Changes, facts, health | Incremental pipeline |
| Verify work | `aether verify` | Claim verification | Evidence collection, inference, verification |
| Pre-commit | `aether review` | Risks, recommendations | Graph diff, impact analysis |
| Compile | `aether compile` | Output artifacts | All compilers run |
| Pre-PR | `aether review --pr` | Full delta | Cross-branch graph comparison |
| Pre-release | `aether review --release` | Health, risks, recommendation | Full graph audit |
| Debug | `aether search` | Files, facts, decisions | Graph search, provenance |
| Diagnose | `aether doctor` | Store health, recommendations | Integrity checks |
| Understand | `aether explain` | Evidence chain | Provenance traversal |
| Switch AI | (none needed) | Instant expertise | `repository.ai` loading |
