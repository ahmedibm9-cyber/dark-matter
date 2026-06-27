# Decision Framework

> A structured, repeatable system for making software engineering decisions. Every decision must be justified, documented, and traceable.

---

## 1. Architecture Decisions

### 1.1 Trigger Conditions

An architecture decision is required when any of the following conditions are met:

| Condition | Example |
|-----------|---------|
| New system or service introduction | Adding a new microservice, worker, or bounded context |
| Technology substitution | Replacing a database, message broker, or runtime |
| Cross-cutting concern emerges | Observability, caching strategy, auth model |
| Constraint violation detected | Current approach cannot meet SLA, cost, or compliance |
| Team scaling requires it | Monolith splitting, module extraction, ownership boundary |
| External dependency changes | Deprecation, license change, security advisory |
| Requirement fundamentally conflicts with current architecture | A feature that changes data flow, trust model, or deployment topology |

### 1.2 Required Inputs

Before any architecture decision, the following must be gathered:

- **Current Architecture**: As-is state, including ADRs, diagrams, and dependency graph
- **Requirements**: Functional and non-functional (SLAs, scale, compliance, budget)
- **Constraints**: Time, cost, team capability, regulatory, infrastructure
- **Tradeoffs**: Known tradeoffs of the current approach and the proposed change
- **Context**: Business drivers, timeline, stakeholder priorities

### 1.3 Evaluation Criteria

Every architecture decision must be scored against these criteria:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Scalability | High | Can this handle 10x current load without redesign? |
| Maintainability | High | How many people can understand and change this? |
| Cost | Medium | Infrastructure, licensing, engineering hours |
| Team Expertise | Medium | Can the current team operate this effectively? |
| Ecosystem | Low | Community health, library support, hiring pool |
| Security | Critical | Does this introduce attack surface or compliance gaps? |
| Operability | High | Monitoring, debugging, deploy, rollback complexity |

### 1.4 Decision Process

Every architecture decision follows this 8-step process:

**Step 1: Define the Problem**
- State the problem in one sentence
- Identify the decision scope
- Define success criteria

**Step 2: Gather Context**
- Collect all required inputs (section 1.2)
- Interview stakeholders
- Review relevant ADRs and past decisions

**Step 3: Identify Options**
- Generate at least 2 viable options (including "do nothing")
- Research industry patterns
- Consult team experience

**Step 4: Evaluate**
- Score each option against evaluation criteria (section 1.3)
- Build a comparison table
- Identify risks per option

**Step 5: Decide**
- Select the option that best meets weighted criteria
- Document the rationale
- Identify what this decision deprioritizes

**Step 6: Document ADR**
- Write an Architecture Decision Record using the template (section 1.5)
- Store in `docs/adr/` with sequential numbering

**Step 7: Communicate**
- Present to affected teams
- Update architectural diagrams
- Tag relevant stakeholders in the ADR

**Step 8: Implement**
- Break into executable tickets
- Define verification criteria
- Schedule follow-up review (3-6 months)

### 1.5 Decision Template (ADR)

```markdown
# ADR-NNN: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[What is the problem? What forces are at play?]

## Decision
[What was decided and why?]

## Consequences
[What becomes easier? What becomes harder?]

## Alternatives Considered
| Option | Pros | Cons |
|--------|------|------|
| Option A | ... | ... |
| Option B | ... | ... |

## Compliance
[How will compliance be verified?]

## Notes
[References, discussions, links]
```

### 1.6 Examples

**Example: Choosing between Postgres and MongoDB for a new service**
- Problem: Product catalog service needs flexible schema for varying product types
- Options: Postgres with JSONB, MongoDB, DynamoDB
- Decision: Postgres with JSONB — team expertise, transactional consistency, one fewer infra component
- ADR: docs/adr/0014-catalog-storage.md

---

## 2. Database Decisions

### 2.1 Schema Change Decision Process

Every schema change must pass through this process:

1. **Identify impact**: Which tables, indexes, views, functions, and applications are affected?
2. **Classify change**:
   - Additive (new column, nullable) → Safe, can be backward-compatible
   - Modifying (type change, constraint add) → Needs migration plan
   - Destructive (drop column, drop table) → Requires deprecation period + migration
3. **Write migration**: Forward migration + rollback migration
4. **Review migration**: Peer review focusing on data loss and performance
5. **Stage migration**:
   - < 10GB table: run in transaction
   - 10GB-100GB: use online migration tooling (gh-ost, pt-online-schema-change)
   - > 100GB: requires downtime planning or sharding
6. **Verify**: Run migration against staging with production-sized data

### 2.2 Migration Strategy Decision Tree

```
Is the change backward-compatible (read-only safe with old code)?
├── YES → Canary deploy migration, then deploy new code
└── NO
    ├── Can we make it backward-compatible?
    │   ├── YES → Add intermediate state, deploy in phases
    │   └── NO
    │       ├── Is zero-downtime required?
    │       │   ├── YES → Use expand-migrate-contract pattern:
    │       │   │           1. Add new schema alongside old
    │       │   │           2. Dual-write until safe
    │       │   │           3. Migrate data
    │       │   │           4. Remove old schema
    │       │   └── NO → Schedule downtime window
    │       └── [END]
    └── [END]
```

### 2.3 Normalization vs Denormalization Decision Framework

| Consideration | Favor Normalization | Favor Denormalization |
|---------------|-------------------|----------------------|
| Write volume | High | Low |
| Read volume | Low | High |
| Consistency requirements | Strong | Eventually consistent OK |
| Query complexity | Simple joins | Complex or cross-aggregate |
| Data relationships | Many-to-many | Document-style nested |
| Team maturity | High (can manage complex schema) | Lower (simpler query surface) |
| Change velocity | Low (schema changes expensive) | High (schema denormalized to queries) |

**Rule**: Start normalized. Denormalize when — and only when — a measured performance problem exists and normalization is proven to be the cause.

### 2.4 Indexing Decision Framework

```
Is this index for a primary key, unique constraint, or foreign key?
├── YES → Create immediately (these are structural)
└── NO
    ├── Is this for a query that runs more than 100 times/day?
    │   ├── YES → Consider index
    │   └── NO → Skip (index maintenance cost > benefit)
    └── [Evaluate]
        ├── What is the selectivity of the column(s)?
        │   ├── High (>20% unique) → Good candidate
        │   └── Low (<1% unique) → Poor candidate, consider alternative
        ├── What is the write-to-read ratio?
        │   ├── Heavy writes → Index adds overhead, measure carefully
        │   └── Heavy reads → Index likely beneficial
        └── Composite index needed?
            ├── YES → Order columns by selectivity (highest first)
            └── NO → Single-column index sufficient
```

---

## 3. API Decisions

### 3.1 REST vs GraphQL vs gRPC Decision Tree

```
Primary client type?
├── Public web/mobile (third-party or external)
│   ├── Simple CRUD, cacheable, widespread adoption → REST
│   ├── Complex data requirements, multiple client types → GraphQL
│   └── Real-time, binary, high-throughput → gRPC + gRPC-Web
├── Internal service-to-service
│   ├── Low latency, high throughput → gRPC
│   ├── Polyglot environment, simple operations → REST
│   └── Streaming, bidirectional → gRPC
└── Event-driven / async
    └── Async messaging (choose message format, not RPC style)
```

**Decision Considerations**:

| Factor | REST | GraphQL | gRPC |
|--------|------|---------|------|
| Caching | Excellent (HTTP caching) | Limited (post requests) | Not built-in |
| Human readability | Yes | Yes | No (proto) |
| Schema enforcement | OpenAPI | Schema-first | Proto IDL |
| Tooling ecosystem | Mature | Growing | Good |
| Learning curve | Low | Medium | Medium-high |
| Performance (latency) | Good | Good | Excellent |
| Payload size | Large (verbose) | Tailored | Small (binary) |
| Versioning | URL/Header | Field deprecation | Proto package |

### 3.2 API Versioning Strategy

```
Is the API public (external-facing)?
├── YES → Use URL versioning (e.g., /v1/orders)
│   ├── Why: Explicit, easy to route, no content negotiation complexity
│   └── Deprecation: Announce 6+ months before removal, sunset header
└── NO → Internal API
    ├── Monorepo / single deploy → No versioning needed (rolling deploy)
    └── Separate deploys → Use header versioning (Accept: application/vnd.company.v2+json)
```

### 3.3 Authentication Method Decision Tree

```
Is this a public API (no user context)?
├── YES → API key (service-level auth)
└── NO → User context required
    ├── Is this a first-party client (our web app, mobile app)?
    │   ├── YES → OAuth 2.0 with PKCE (Authorization Code flow)
    │   └── NO → Third-party client
    │       ├── Machine-to-machine → OAuth 2.0 Client Credentials
    │       └── User delegation → OAuth 2.0 Authorization Code
    └── [END]
├── Does the auth flow need to be stateless?
│   ├── YES → JWT (short-lived access + refresh token rotation)
│   └── NO → Session-based (server-side session store)
└── [END]
```

### 3.4 Error Handling Strategy

| Error Category | HTTP Status | Response Shape | Handling |
|----------------|-------------|----------------|----------|
| Validation | 400 | `{ error: "VALIDATION_ERROR", details: [...] }` | User action |
| Authentication | 401 | `{ error: "UNAUTHENTICATED" }` | Re-auth |
| Authorization | 403 | `{ error: "FORBIDDEN" }` | Log + alert |
| Not Found | 404 | `{ error: "NOT_FOUND" }` | Graceful handling |
| Conflict | 409 | `{ error: "CONFLICT", details: [...] }` | Retry or user decision |
| Rate Limited | 429 | `{ error: "RATE_LIMITED", retryAfter: 60 }` | Backoff + retry |
| Server Error | 500 | `{ error: "INTERNAL_ERROR", requestId: "..." }` | Retry + report |
| Unavailable | 503 | `{ error: "SERVICE_UNAVAILABLE" }` | Circuit break + retry |

**Rule**: Every endpoint must return structured errors in the same format. Never expose stack traces or internal details.

---

## 4. UI Decisions

### 4.1 Component Composition vs Inheritance

```
Do you need to customize behavior at runtime?
├── YES → Composition (pass behavior via props/slots)
└── NO → Does the component share state/behavior?
    ├── YES → Composition (hooks, custom hooks, render props)
    └── NO → Composition (always prefer composition over inheritance)
```

**Rule**: Inheritance is never the right choice for UI components. Use composition exclusively.

### 4.2 State Management Decision Tree

```
Is the state server-driven (data from API)?
├── YES → Server state management (React Query, SWR, RTK Query)
└── NO → Client-only state
    ├── Is the state local (single component or small subtree)?
    │   ├── YES → useState / useReducer
    │   └── NO → Global state needed
    │       ├── Small-medium app → Context + useReducer
    │       ├── Large app, complex interactions → Zustand, Jotai, or Redux
    │       └── URL-shareable state → URL params
    └── [END]
├── Is there real-time or collaborative state?
│   └── YES → Consider dedicated sync engine (Liveblocks, Yjs, PartyKit)
└── [END]
```

### 4.3 Server-Side vs Client-Side Rendering

| Factor | SSR | CSR | SSG |
|--------|-----|-----|-----|
| SEO required | Essential | Poor (improves with hydration) | Best |
| First paint matters | Good | Slower | Excellent |
| Interactivity | Form-based | Rich | Limited |
| Data freshness | Per request | Per request | Built at deploy |
| Cost (compute) | Higher | Lower (CDN) | Lowest (static) |
| Auth required | Yes | Yes | No (pre-built) |

**Decision**: Start with SSG for marketing/content pages, CSR for authenticated app pages. Add SSR/SSR streaming only when SEO or perceived performance requires it.

### 4.4 Design System vs Custom Approach

```
Do you have 3+ engineers working on UI?
├── NO → Custom approach (build what you need, no overhead)
└── YES
    ├── Do you need consistency across products?
    │   ├── YES → Design system investment
    │   └── NO → Do you have a dedicated designer?
    │       ├── YES → Design system
    │       └── NO → Start with a UI library (shadcn/ui, MUI, Chakra)
    └── [END]
├── Is accessibility compliance required (WCAG)?
│   ├── YES → Design system with a11y built in
│   └── NO → Can defer but should still consider
└── [END]
```

---

## 5. Security Decisions

### 5.1 Encryption Approach Decision Tree

```
Is data at rest or in transit?
├── In transit → TLS 1.2+ (mandatory for all external communication)
└── At rest
    ├── Database-level → Transparent Data Encryption (TDE)
    ├── Column-level → Application-level encryption (field-by-field)
    ├── File-level → Server-side encryption (SSE-S3, SSE-KMS)
    └── Client-side → End-to-end encryption (user holds keys)
├── Do you need to search encrypted data?
│   ├── YES → Consider deterministic encryption or searchable encryption
│   │   └── Risk: Deterministic = less secure (same plaintext = same ciphertext)
│   └── NO → Random IV per encryption (most secure)
└── [END]
```

### 5.2 Auth Provider Decision Framework

| Factor | Self-Hosted (Keycloak, Authentik) | Managed (Auth0, Cognito, Clerk) | Build In-House |
|--------|----------------------------------|--------------------------------|----------------|
| Team size | > 10 eng | Any | > 20 eng + security team |
| Compliance | Full control | SOC2, HIPAA via vendor | Full custom |
| Maintenance cost | High | Low (SaaS) | Very High |
| Customization | Full | Limited to vendor | Full |
| Time to integrate | Weeks | Days | Months |
| Vendor lock-in | Low | Medium | None (but high build cost) |

**Recommendation**: Use managed auth provider until you outgrow it. Building auth in-house is almost never justified.

### 5.3 Secret Management Approach

```
Where does the secret live?
├── Source code → NEVER. Block via pre-commit hooks + git-secrets scan
├── Environment variables → Acceptable for dev, NOT for production
├── CI/CD pipeline variables → Acceptable for non-prod
├── Secret manager (Vault, AWS Secrets Manager, GCP Secret Manager) → CORRECT
└── Encrypted in database (for user secrets) → Acceptable if using KMS + envelope encryption

Rotation policy:
├── Database credentials → Every 90 days (auto-rotate)
├── API keys → On compromise or every 180 days
└── TLS certificates → 90 days (auto-renew via ACME)
```

**Rule**: No secret may ever be committed to version control. Any leaked secret triggers an incident response.

### 5.4 Compliance Requirement Decision Tree

```
What compliance framework applies?
├── SOC2 → Audit logging, access control, change management, encryption
├── HIPAA → BAAs, PHI encryption, access logging, audit trail, BCDR
├── GDPR → Data minimization, consent, right to deletion, DPA with subprocessors
├── PCI-DSS → Network segmentation, encryption, logging, quarterly scans
├── FedRAMP → NIST 800-53 controls, third-party assessment
└── Internal/Startup → Minimum: encryption, access control, logging

For each framework, verify:
├── Data classification implemented
├── Access controls enforced (least privilege)
├── Audit trail exists
├── Encryption configured correctly
├── Incident response plan documented
└── Training completed
```

---

## 6. Decision Log

Every decision made using this framework must be recorded:

| # | Date | Category | Decision | Author | ADR Link |
|---|------|----------|----------|--------|----------|
| 1 | | | | | |
| 2 | | | | | |

---

## 7. Decision Review Cadence

- **Monthly**: Team reviews pending decisions older than 2 weeks
- **Quarterly**: Audit decisions made in the quarter — are the expected outcomes materializing?
- **Annually**: Full framework review and update based on lessons learned

---

## 8. Escalation

If a decision affects:
- **Data safety** → Escalate to CISO / security lead
- **Customer-facing SLA** → Escalate to engineering director
- **Cost > $10k/month** → Escalate to engineering director + finance
- **Team restructuring** → Escalate to VP Engineering

---

*Every decision is a bet. This framework ensures the bet is informed, documented, and reversible.*
