# Architecture Decision Record Template

> **Purpose:** Capture architectural decisions with their context, rationale, and consequences. Every significant architectural choice MUST be recorded as an ADR.
> **Version:** 1.0.0
> **Based on:** Michael Nygard's ADR pattern

---

## ADR Format

Each ADR is a single file following this naming convention:

```
adr-{NNNN}-{short-description-with-dashes}.md
```

Where `NNNN` is a zero-padded sequential number (e.g., `0001`, `0002`, `0042`).

**Example:** `adr-0001-use-postgresql-for-primary-database.md`

---

## ADR Template

```markdown
# ADR-{NNNN}: {Title}

> **A short, descriptive title of the decision.**

---

## Status

**{proposed | accepted | deprecated | superseded}**

- **Proposed:** Suggested but not yet agreed upon
- **Accepted:** Formally agreed upon and in effect
- **Deprecated:** No longer recommended but still in use
- **Superseded by [ADR-{MMMM}](adr-{MMMM}-new-decision.md):** Replaced by a newer decision

---

## Date

{YYYY-MM-DD} (date of decision or date of last status change)

---

## Context

### Problem Statement

What problem are we solving? What forces are at play? What is the situation that demands a decision?

### Background

Provide enough context so that someone unfamiliar with the project can understand the decision. Include:

- Current system architecture and relevant components
- Business requirements or constraints driving this decision
- Technical constraints (platform, language, ecosystem, team skills)
- Timeline constraints or release dependencies
- Regulatory or compliance requirements
- Known future requirements that may influence the decision

### Forces

List the competing forces that must be balanced:

- **Performance:** Response time, throughput, scalability requirements
- **Cost:** Development cost, operational cost, licensing cost
- **Complexity:** Learning curve, maintenance burden, debugging difficulty
- **Time:** Development time, time-to-market pressure
- **Reliability:** Uptime requirements, fault tolerance needs
- **Security:** Threat model, compliance requirements, data sensitivity
- **Evolvability:** Expected future changes, extensibility requirements
- **Team:** Existing expertise, team size, hiring constraints
- **Ecosystem:** Library support, community size, vendor lock-in risk

---

## Decision

What did we decide? State the decision clearly and unambiguously.

**We have decided to use {Technology / Approach / Pattern} for {Component / System} because {primary reason}.**

### Detailed Description

Provide a detailed description of what was decided. Include:

- The specific technology, version, and configuration
- The architectural pattern or design approach
- How this decision manifests in the codebase
- What components are affected and how
- Any configuration or operational changes required

### Architecture Diagram (if applicable)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Component A   │────▶│   Component B   │────▶│   Component C   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Code Example (if applicable)

```typescript
// Example of how this decision looks in code
const db = new Database({
  host: process.env.DB_HOST,
  port: 5432,
  ssl: true
});
```

---

## Rationale

### Why This Decision Was Made

Explain the reasoning behind the decision. Connect back to the forces and context.

1. **Primary reason:** [The most compelling reason for this decision]
2. **Secondary reason:** [Another supporting reason]
3. **Tertiary reason:** [An additional supporting reason]

### Evidence and Data

Provide any evidence that supports this decision:

- Benchmark results showing performance comparison
- Community adoption trends and ecosystem health
- Team experience and familiarity with the technology
- Vendor stability and support quality
- Security audit results or compliance certification
- Case studies from similar projects or organizations

### Constraints Satisfied

List which constraints from the Context section are satisfied by this decision:

- ✅ [Constraint 1] — [How it is satisfied]
- ✅ [Constraint 2] — [How it is satisfied]
- ❌ [Constraint 3] — [Why it is not satisfied, and why that is acceptable]

---

## Consequences

### Positive Consequences (Pros)

1. **[Pro 1]:** [Description of positive outcome]
2. **[Pro 2]:** [Description of positive outcome]
3. **[Pro 3]:** [Description of positive outcome]

### Negative Consequences (Cons / Tradeoffs)

1. **[Con 1]:** [Description of negative outcome, with mitigation if applicable]
   - **Mitigation:** [How we will address this negative consequence]
2. **[Con 2]:** [Description of negative outcome, with mitigation if applicable]
   - **Mitigation:** [How we will address this negative consequence]
3. **[Con 3]:** [Description of negative outcome, with mitigation if applicable]
   - **Mitigation:** [How we will address this negative consequence]

### Risks Introduced

1. **[Risk 1]:** [Description of risk] (Severity: {Low | Medium | High | Critical})
   - **Mitigation:** [How we will mitigate or monitor this risk]
2. **[Risk 2]:** [Description of risk] (Severity: {Low | Medium | High | Critical})
   - **Mitigation:** [How we will mitigate or monitor this risk]

### Migration (if applicable)

If this decision represents a change from a previous decision, describe the migration path:

1. **Phase 1:** [Interim state or parallel run]
2. **Phase 2:** [Cut-over to new system]
3. **Phase 3:** [Decommission old system]
4. **Rollback:** [How to revert if migration fails]

---

## Alternatives Considered

Each alternative must include: what it was, why it was considered, and why it was rejected.

### Alternative 1: {Alternative Name}

- **Description:** [Brief description of the alternative]
- **Why considered:** [What made this option attractive]
- **Evaluation:**
  - **Performance:** [Good / Fair / Poor]
  - **Cost:** [Good / Fair / Poor]
  - **Complexity:** [Good / Fair / Poor]
  - **Evolvability:** [Good / Fair / Poor]
  - **Security:** [Good / Fair / Poor]
  - **Team fit:** [Good / Fair / Poor]
- **Why rejected:** [Specific technical or operational reason]
- **Closing argument:** [One-sentence summary of why this alternative was not chosen]

### Alternative 2: {Alternative Name}

- **Description:** [Brief description of the alternative]
- **Why considered:** [What made this option attractive]
- **Evaluation:**
  - **Performance:** [Good / Fair / Poor]
  - **Cost:** [Good / Fair / Poor]
  - **Complexity:** [Good / Fair / Poor]
  - **Evolvability:** [Good / Fair / Poor]
  - **Security:** [Good / Fair / Poor]
  - **Team fit:** [Good / Fair / Poor]
- **Why rejected:** [Specific technical or operational reason]
- **Closing argument:** [One-sentence summary of why this alternative was not chosen]

### Alternative 3: {Alternative Name}

- **Description:** [Brief description of the alternative]
- **Why considered:** [What made this option attractive]
- **Evaluation:**
  - **Performance:** [Good / Fair / Poor]
  - **Cost:** [Good / Fair / Poor]
  - **Complexity:** [Good / Fair / Poor]
  - **Evolvability:** [Good / Fair / Poor]
  - **Security:** [Good / Fair / Poor]
  - **Team fit:** [Good / Fair / Poor]
- **Why rejected:** [Specific technical or operational reason]
- **Closing argument:** [One-sentence summary of why this alternative was not chosen]

---

## Related Decisions

- **[ADR-{NNNN}](adr-{NNNN}-title.md):** [Relationship description]
- **[ADR-{MMMM}](adr-{MMMM}-title.md):** [Relationship description]
- **[ADR-{OOOO}](adr-{OOOO}-title.md):** [Relationship description]

### Decision Tree

```
ADR-0001 (Use PostgreSQL)
└── ADR-0003 (Use Prisma ORM) ── depends on ADR-0001
    └── ADR-0004 (Use PostgreSQL migrations) ── depends on ADR-0003
├── ADR-0002 (Use Redis for caching) ── independent of ADR-0001
```

---

## Implementation Notes

### Implementation Lead
{Name or Agent ID}

### Estimated Effort
{X person-days or X agent-hours}

### Key Implementation Files
- `src/path/to/implementation/file1.ts` — Primary implementation
- `src/path/to/implementation/file2.ts` — Supporting implementation
- `src/path/to/config/file.yaml` — Configuration changes

### Key Test Files
- `tests/path/to/test/file1.test.ts` — Tests for the implementation
- `tests/path/to/test/file2.test.ts` — Integration tests

### Documentation Files
- `docs/architecture/{topic}.md` — Architecture documentation
- `docs/operations/{topic}.md` — Operations documentation
- `CHANGELOG.md` — User-facing change description

### Migration Scripts
- `migrations/{timestamp}_description.up.sql` — Up migration
- `migrations/{timestamp}_description.down.sql` — Down migration

---

## Change History

| Date | Status | Changed By | Description |
|---|---|---|---|
| YYYY-MM-DD | Proposed | {Name} | Initial proposal |
| YYYY-MM-DD | Accepted | {Name} | Decision accepted |
| YYYY-MM-DD | Deprecated | {Name} | Marked as deprecated |
| YYYY-MM-DD | Superseded | {Name} | Superseded by ADR-{MMMM} |

---

## Review Checklist

- [ ] Problem statement is clear and specific
- [ ] All competing forces are identified
- [ ] Decision is stated clearly and unambiguously
- [ ] Rationale connects back to context and forces
- [ ] Consequences include both pros and cons
- [ ] At least 3 alternatives were considered and evaluated
- [ ] Rejected alternatives have specific, technical rejection reasons
- [ ] Risks are identified with mitigations
- [ ] Related decisions are cross-referenced
- [ ] Implementation notes are complete and actionable
- [ ] Migration path is defined (if applicable)
- [ ] Rollback plan is defined (if applicable)

---

> *"Every decision is a tradeoff. Good ADRs make the tradeoffs explicit."*
```
