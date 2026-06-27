# Self-Audit Protocol

> Defines how the Project Intelligence Layer audits itself. All audit results
> are recorded in `ops/audits/reports/` and tracked in the improvement log.

---

## 1. Schedule

| Audit Type | Frequency | When | Owner |
|------------|-----------|------|-------|
| Full system audit | Weekly | Monday 06:00 UTC | Automation |
| Docs freshness scan | Weekly | Monday 06:00 UTC | Automation |
| SOP compliance check | Bi-weekly | Every other Monday | Process Lead |
| Template conformance | Monthly | 1st of month | Process Lead |
| Constitution violation scan | Monthly | 1st of month | Process Lead |
| Ad-hoc / triggered | On demand | Any PR or major change | Reviewer |

### Weekly Flow
1. Auto-audit script runs (Monday 06:00 UTC)
2. Results posted to `#audits` channel / committed to `ops/audits/reports/`
3. Any score below threshold triggers a review issue
4. Improvement log updated with findings

---

## 2. What to Check

### 2.1 Docs Freshness

| Check | Detail | Method |
|-------|--------|--------|
| Last-modified dates | Every `.md` file must be touched within 90 days | `find ... -mtime +90` |
| Stale content markers | Files with `<!-- STALE -->` comment must have review date | grep for STALE comments |
| Broken internal links | All markdown links within `docs/` resolve | `markdown-link-check` or `lychee` |
| Orphaned docs | Files in `docs/` not linked from any index | Custom script (find unlinked files) |

### 2.2 Template Usage

| Check | Detail | Method |
|-------|--------|--------|
| SPEC uses current template | `docs/specs/*.md` match `ops/templates/SPEC-template.md` | Diff against template |
| ADR uses current template | `docs/adr/*.md` match `ops/templates/ADR-template.md` | Diff against template |
| SOP uses current template | `ops/sops/*.md` match `ops/templates/SOP-template.md` | Diff against template |
| Placeholder completeness | No `TODO`, `FIXME`, or `TBD` in published docs | grep count |

### 2.3 SOP Compliance

| Check | Detail | Method |
|-------|--------|--------|
| SOPs present for all processes | Every recurring process has an SOP | Check manifest against process list |
| SOPs up to date | Last reviewed within 6 months | `git log` for SOP files |
| SOPs followed in practice | Random sample of 3 recent PRs checked against each SOP | Manual review |
| Exception log maintained | All SOP deviations logged in `ops/sops/exceptions/` | Check directory exists and populated |

### 2.4 Constitution Violations

| Check | Detail | Method |
|-------|--------|--------|
| Decisions align with principles | Cross-reference decisions with constitution principles | Automated keyword + manual review |
| No contradictory rules | Constitution rules conflict detection | Script that cross-references rule IDs |
| Required reviews completed | All significant changes had required review types | git log + PR metadata analysis |
| Escalation path followed | Escalations documented when threshold exceeded | Check ops/audits/escalations/ |

---

## 3. Scoring Methodology

Each component is scored 0–100. The overall health score is a weighted average.

### 3.1 Weight Distribution

| Component | Weight | Max Points |
|-----------|--------|------------|
| Docs Freshness | 15% | 100 |
| Template Usage | 15% | 100 |
| SOP Compliance | 25% | 100 |
| Constitution Adherence | 25% | 100 |
| Technical Health | 20% | 100 |

### 3.2 Scoring Rules per Component

**Docs Freshness:**
- Start at 100
- −5 per stale doc (over 90 days since modification)
- −10 per broken internal link
- −5 per orphaned doc
- Minimum: 0

**Template Usage:**
- Start at 100
- −15 per spec/adr/sop deviating from template
- −5 per placeholder (TODO/FIXME/TBD) in published doc
- Minimum: 0

**SOP Compliance:**
- Start at 100
- −10 per missing SOP
- −5 per SOP not reviewed in 6 months
- −20 per evidence of process violation (per instance)
- Minimum: 0

**Constitution Adherence:**
- Start at 100
- −15 per decision violating a constitutional principle
- −10 per missing required review type
- −5 per undocumented escalation
- Minimum: 0

**Technical Health:**
- Mapped from auto-audit script score (see below)

### 3.3 Auto-Audit Score Calculation

The auto-audit script generates a technical score:

```
Score = (Checks_Passed / Total_Checks) × 100
```

Where:
- Total_Checks = 8 (deps, tests, coverage, todos, secrets, lint, build, docs)
- Checks_Passed = Total_Checks - FAILURES

| Technical Score | Rating |
|----------------|--------|
| 90–100 | ✅ Healthy |
| 75–89  | ⚠️ Warning |
| 50–74  | 🔴 Critical |
| 0–49   | 🚨 Emergency |

---

## 4. Improvement Tracking

### 4.1 Improvement Log

Every audit finding that requires action is logged in `ops/audits/improvements.md`:

```markdown
## YYYY-MM-DD — [Category] Breif Description

- **Severity:** Critical / High / Medium / Low
- **Source:** Weekly audit / PR review / Incident
- **Symptom:** What was observed
- **Root Cause:** Why it happened
- **Action:** What was done
- **Resolution Date:** YYYY-MM-DD
- **Prevention:** How to avoid recurrence
- **Trend:** Worsening / Stable / Improving
```

### 4.2 Measuring Progress

| Metric | Baseline | Target | Current | Trend |
|--------|----------|--------|---------|-------|
| Overall Health Score | — | ≥85 | — | — |
| Docs Freshness | — | ≥90 | — | — |
| Template Compliance | — | ≥95 | — | — |
| SOP Compliance | — | ≥80 | — | — |
| Constitution Adherence | — | ≥95 | — | — |
| Technical Health | — | ≥85 | — | — |
| Open Improvements | — | ≤5 | — | — |
| Avg. Resolution Time | — | ≤14 days | — | — |

---

## 5. Audit Report Template

Reports are generated automatically and stored at `ops/audits/reports/audit_YYYYMMDD_HHMMSS.md`.

```markdown
# Self-Audit Report — YYYY-MM-DD

**Type:** Weekly / Monthly / Ad-hoc
**Run by:** Automated / [Name]
**Duration:** X min

## Component Scores

| Component | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Docs Freshness | XX/100 | 15% | X.X |
| Template Usage | XX/100 | 15% | X.X |
| SOP Compliance | XX/100 | 25% | X.X |
| Constitution Adherence | XX/100 | 25% | X.X |
| Technical Health | XX/100 | 20% | X.X |
| **Overall** | **—** | **100%** | **X.X/100** |

## Findings

### 🔴 Critical (Score < 50)
- ...

### 🟡 Warning (Score 50–74)
- ...

### ✅ Passing (Score ≥ 75)
- ...

## Action Items

| Priority | Item | Owner | Deadline |
|----------|------|-------|----------|
| P0 | ... | @person | YYYY-MM-DD |
| P1 | ... | @person | YYYY-MM-DD |
| P2 | ... | @person | YYYY-MM-DD |

## Trend

- **Previous score:** X.X
- **Current score:** X.X
- **Change:** +X.X / -X.X
- **Direction:** Improving / Stable / Declining
```

---

## 6. Minimum Acceptable Scores

| Category | Minimum | Below Minimum Action |
|----------|---------|----------------------|
| Overall Health | 75 | Emergency review; halt non-critical work |
| Docs Freshness | 70 | Assign docs rotation; block doc-related PRs |
| Template Usage | 80 | Schedule template remediation sprint |
| SOP Compliance | 70 | Process review; mandatory SOP training |
| Constitution Adherence | 85 | Convene architecture council; annotate violations |
| Technical Health | 75 | Trigger incident response; fix critical items |
| Open Improvements | ≤10 if any | Triage and assign; close stale items |

---

## 7. Escalation

If any minimum score is breached:

1. **Auto-create** a GitHub issue with label `audit-critical`
2. **Notify** the process lead and engineering manager
3. **Schedule** a remediation review within 48 hours
4. **Block** all non-critical changes until score recovers above minimum
5. **Document** root cause and preventative measures in the improvement log

---

## 8. Tooling

| Tool | Purpose | Run Command |
|------|---------|-------------|
| `auto-audit-script.sh` | Full technical audit | `bash ops/automation/auto-audit-script.sh` |
| `find + stat` | Docs freshness | `find docs/ -name '*.md' -mtime +90` |
| `markdown-link-check` | Link validation | `npx markdown-link-check 'docs/**/*.md'` |
| `git log` | Review history | `git log --since="6 months ago" -- ops/sops/` |
| Template diff | Conformance check | `diff -u ops/templates/SPEC-template.md docs/specs/latest.md` |
| grep | Placeholder scan | `grep -rn 'TODO|FIXME|TBD' docs/ \| wc -l` |

---

*Last reviewed: YYYY-MM-DD*
*Review frequency: Monthly*
*Owner: Process Lead*
