# Model Replacement Test

> **Purpose:** Assess project resilience against AI model changes.  
> **Last Updated:** 2026-06-25  
> **Owner:** Project Lead

---

## 1. Critical Knowledge Audit

### 1.1 Architecture Decisions and Their Rationale

| Decision | Rationale | Documented? | Risk |
|---|---|---|---|
| Monorepo structure | Simplified dependency management, atomic commits across packages | `project-brain/architecture.md` | Medium |
| React + TypeScript frontend | Team expertise, type safety, ecosystem maturity | `project-brain/architecture.md` | Low |
| Node.js/Express backend | Rapid development, unified language with frontend | `project-brain/architecture.md` | Low |
| PostgreSQL database | ACID compliance, JSON support, strong ecosystem | `decisions/why-postgres.md` | Low |
| Redis for caching | In-memory performance, pub/sub capabilities | `decisions/why-redis.md` | Low |
| JWT authentication | Stateless auth, microservice-friendly | `intelligence/decision-log.md` | Low |
| Microservices split | Independent deployability, team scaling | `intelligence/decision-log.md` | Medium |
| GraphQL gateway | Flexible queries, reduced over-fetching | `project-brain/architecture.md` | High |
| Docker Compose local dev | Environment parity, easy onboarding | `intelligence/decision-log.md` | Low |

**Undocumented decisions (HIGH RISK):**
- Why `csv-parser` v3 was chosen over v2 (specific bug workaround)
- Why the notification system uses polling instead of WebSockets
- Why the payment flow is synchronous (compliance requirement)
- Why the legacy v1 API endpoints were retained (migration timeline)
- Why `lodash` is pinned to 4.17.x (breaking change in 4.18)

### 1.2 Business Rules and Implementation Details

| Business Rule | Location | Documented? | Risk |
|---|---|---|---|
| Trial period = 14 days from signup | `services/billing/src/rules/trial.ts` | `intelligence/domain-knowledge.md` | Low |
| Discount cap = 50% max | `services/billing/src/rules/discounts.ts` | `intelligence/domain-knowledge.md` | Low |
| Password min 12 chars, 3 of 4 types | `services/auth/src/validation.ts` | `intelligence/domain-knowledge.md` | Low |
| Order cancellation window = 1 hour | `services/orders/src/rules/cancellation.ts` | Not documented | **Critical** |
| Refund requires admin approval over $500 | `services/billing/src/rules/refunds.ts` | Not documented | **Critical** |
| Export limit = 10,000 rows per request | `services/reports/src/export.ts` | Not documented | **High** |
| Rate limit = 100 req/min per user | `middleware/rateLimiter.ts` | Not documented | **High** |
| Session timeout = 30 min inactivity | `services/auth/src/session.ts` | Not documented | **High** |
| Max concurrent logins = 3 per user | `services/auth/src/rules/concurrent.ts` | Not documented | **Critical** |
| Data retention = 90 days for logs | `services/logging/src/retention.ts` | Not documented | **Critical** |

### 1.3 Codebase Navigation Knowledge

| Knowledge | Value | Documented? | Risk |
|---|---|---|---|
| Entry points by service | Fast onboarding | `project-brain/architecture.md` | Low |
| Module dependency graph | Safe refactoring | `project-brain/architecture.md` | Medium |
| Test file mirror structure | Quick test location | Not documented | **High** |
| Shared utility locations | Avoid duplication | Not documented | **High** |
| Type definition locations | Correct imports | Not documented | **Medium** |
| Configuration file hierarchy | Correct env setup | Not documented | **High** |
| Migration file naming convention | DB schema understanding | Not documented | **Medium** |
| Storybook/component locations | UI development | Not documented | **High** |

### 1.4 Workflow Understanding

| Workflow | End-to-End Path | Documented? | Risk |
|---|---|---|---|
| User Registration | Signup form -> API -> Auth -> Email -> DB | Not documented | **Critical** |
| Checkout Flow | Cart -> API -> Validation -> Payment -> Email | Not documented | **Critical** |
| Password Reset | Request form -> Auth -> Email -> Token -> Reset | Not documented | **High** |
| Report Generation | UI -> API -> Query Builder -> Export -> Email | Not documented | High |
| Multi-tenant Onboarding | Admin UI -> Provisioning -> DNS -> Config | Not documented | **Critical** |
| Backup/Restore | Cron -> Dump -> S3 -> Verification | Not documented | High |
| CI/CD Pipeline | Push -> Build -> Test -> Deploy -> Smoke | `ops/ci-cd.md` | Low |

### 1.5 Bug Knowledge

| Bug ID | Issue | Root Cause | Fix Location | Documented? | Risk |
|---|---|---|---|---|---|
| BUG-001 | Emails not sent on signup | Race condition in email queue | `services/email/src/queue.ts:45` | Not documented | **Critical** |
| BUG-002 | Session expires early | Clock skew between services | `services/auth/src/session.ts:120` | Not documented | **Critical** |
| BUG-003 | Report export times out | Missing index on `reports.created_at` | Migration V20240501 | Not documented | **High** |
| BUG-004 | Double charge on retry | Idempotency key not checked | `services/billing/src/payment.ts:210` | Not documented | **Critical** |
| BUG-005 | Search returns stale results | Cache invalidation missing on update | `services/search/src/cache.ts:88` | Not documented | **High** |
| BUG-006 | File upload fails >10MB | Missing nginx body size config | `infra/nginx/nginx.conf` | Not documented | **Medium** |

### 1.6 Dependency Knowledge

| Dependency | Purpose | Why Chosen | Documented? | Risk |
|---|---|---|---|---|
| express | HTTP framework | Defacto standard, middleware ecosystem | Not documented | Medium |
| sequelize | ORM | Migration support, active community | Not documented | Medium |
| bull | Job queue | Redis-backed, retries, scheduling | Not documented | Medium |
| winston | Logging | Transports, levels, production-ready | Not documented | Low |
| axios | HTTP client | Interceptors, cancelation, wide use | Not documented | Low |
| zod | Validation | TypeScript-first, inferred types | Not documented | Medium |
| vitest | Testing | Fast, compatible with Jest API | Not documented | Low |
| playwright | E2E testing | Multi-browser, auto-wait, trace viewer | Not documented | Low |
| dayjs (not moment) | Date handling | Tree-shakeable, immutable API | Not documented | **High** |
| sharp | Image processing | Performance, streaming support | Not documented | Medium |

**At-risk undocumentation:**
- Why `moment` was replaced with `dayjs` (bundle size + license issue)
- Why `node-fetch` was replaced with `undici` (performance)
- Why `redux` was chosen over `zustand` (team familiarity at time)
- Why specific patch versions are pinned in `package.json`

### 1.7 Historical Context

| Context | Relevance | Documented? | Risk |
|---|---|---|---|
| Why v1 was monolithic | Started as MVP, time-to-market priority | Not documented | **High** |
| Why v2 split services | Team grew from 2 to 15 engineers | Not documented | **High** |
| Why we migrated from MySQL | Scaling issues, JSONB needs | Not documented | **High** |
| Previous CEO's pet feature (legacy) | Still maintained, no one knows why | Not documented | **Critical** |
| Abandoned GraphQL migration halfway | 50% endpoints migrated, rest legacy REST | Not documented | **Critical** |

### 1.8 Testing Knowledge

| Knowledge | Value | Documented? | Risk |
|---|---|---|---|
| Test naming conventions | Find tests quickly | Not documented | Medium |
| Mock vs fixture conventions | Consistent testing patterns | Not documented | High |
| Test coverage expectations | Quality bar | Not documented | **Critical** |
| E2E test environment setup | Run integration tests | Not documented | High |
| Snapshot update procedure | Maintain UI tests | Not documented | High |
| Test data factories | Create test fixtures | Not documented | High |
| Performance test thresholds | Regression detection | Not documented | **Critical** |

### 1.9 Deployment Knowledge

| Aspect | Details | Documented? | Risk |
|---|---|---|---|
| Deploy order | Auth -> API -> Workers -> Frontend | Not documented | **Critical** |
| Database migration procedure | Run migrations BEFORE code deploy | Not documented | **Critical** |
| Blue-green cutover steps | DNS change, connection draining | Not documented | **High** |
| Rollback procedure | Steps to revert safely | Not documented | **Critical** |
| Feature flag check required | Disable flag BEFORE deploy | Not documented | **High** |
| Secrets rotation process | Regular key rotation | Not documented | **High** |
| Health check endpoints | Verify deploy success | Not documented | Medium |

### 1.10 Operational Knowledge

| Aspect | Details | Documented? | Risk |
|---|---|---|---|
| Monitoring dashboards | Grafana URLs, key metrics per service | Not documented | **Critical** |
| Alert thresholds | PagerDuty config, severity levels | Not documented | **Critical** |
| On-call runbooks | What to do for each alert type | Not documented | **Critical** |
| Log aggregation | Loki/Kibana query patterns | Not documented | **High** |
| Backup verification | How to test backup integrity | Not documented | **High** |
| Capacity planning | When to scale, historical trends | Not documented | **High** |
| Incident response | Steps for severity classification | Not documented | **Critical** |

---

## 2. Context Survival Analysis

### 2.1 Lost Context If Conversation History Is Gone

| Context Type | Impact | Survives In |
|---|---|---|
| Current bug being investigated | Dev time wasted re-diagnosing | Issue tracker |
| In-progress feature context | Wrong implementation | PR description |
| Recent refactoring decisions | Inconsistent changes | Commit messages |
| Testing setup state | Flaky test debugging | Test config |
| Environment-specific issues | Repeated investigation | Not captured |
| Colleague conversations | Lost tribal knowledge | Not captured |
| Code review feedback on current PR | Repeat review cycles | PR review history |
| Current sprint specifics | Misaligned priorities | Jira/Linear |

### 2.2 Task-Specific Context That Must Be Preserved

| Task | Essential Context | Where to Save |
|---|---|---|
| Payment integration | PCI compliance requirements, test card numbers | `intelligence/domain-knowledge.md` |
| GDPR compliance | Data retention rules, right-to-erasure flow | `intelligence/domain-knowledge.md` |
| Performance optimization | Current bottlenecks, benchmarks | `project-brain/performance.md` |
| Security audit | Known vulnerabilities, mitigation status | `project-brain/security.md` |
| API versioning | Deprecated endpoints, migration timeline | `intelligence/decision-log.md` |

### 2.3 Minimum Viable Context (MVC) Document Template

```markdown
# Minimum Viable Context — [Project Name]

## 1. Project Identity
- **Name:** [Project Name]
- **Domain:** [Brief description]
- **Stack:** Node.js, TypeScript, React, PostgreSQL, Redis, Docker
- **Repository:** [URL]

## 2. Architecture (5-minute overview)
- [ ] Monorepo with packages/services structure
- [ ] Frontend: React + TypeScript, Vite, Tailwind
- [ ] Backend: Express.js microservices
- [ ] Database: PostgreSQL (primary), Redis (cache/queue)
- [ ] API Gateway: GraphQL + REST
- [ ] Auth: JWT-based, multi-tenant
- [ ] Deployment: Docker -> Kubernetes (staging/prod)

## 3. Critical Conventions
- [ ] Naming: camelCase for code, kebab-case for files
- [ ] Branching: feature/<ticket-id>-<description>
- [ ] Commit style: Conventional Commits (feat:, fix:, chore:)
- [ ] Testing: Unit (vitest) + Integration + E2E (Playwright)
- [ ] Types: Strict TypeScript, no `any` without justification
- [ ] Error handling: Custom error classes, centralized handler

## 4. Must-Know Before Touching Code
- [ ] NEVER run migrations directly on production
- [ ] ALWAYS update the FileMap.txt when adding files
- [ ] ALWAYS run `npm run typecheck` before pushing
- [ ] Environment variables are in `infra/env/` — never commit .env
- [ ] The `legacy` folder contains v1 API — do not modify, only remove
- [ ] Payment processing MUST go through the audit service
- [ ] All external API calls MUST have circuit breakers

## 5. Current State
- **Active branch:** [branch-name]
- **Current sprint focus:** [sprint-goal]
- **Known breaking changes in progress:** [list]
- **Pending decisions:** [list]

## 6. Where Things Live
| What | Where |
|---|---|
| Frontend app | `apps/web/` |
| Backend services | `services/*/` |
| Shared types | `packages/shared/` |
| Database migrations | `packages/db/migrations/` |
| Infrastructure | `infra/` |
| Documentation | `docs/` + this directory |
| CI/CD pipelines | `.github/workflows/` |
| Test fixtures | `packages/test-utils/` |

## 7. Quick Start
```bash
git clone [repo]
npm install
npm run dev        # starts all services via Docker
npm run db:migrate  # runs latest migrations
npm test           # runs unit tests
```

## 8. Critical Contacts
- **Tech Lead:** [Name] — architecture decisions
- **Product Owner:** [Name] — feature priorities
- **DevOps:** [Name] — deployment issues
- **Security:** [Name] — vulnerability reports
```

---

## 3. Reasoning Preservation

### 3.1 Required Reasoning Patterns

| Pattern | Why Needed | Preserved In |
|---|---|---|
| Security-first | Financial data, user privacy | `project-brain/security.md` |
| Cost-aware | Cloud costs, scaling economics | Need to create |
| Migration-compatible | Partial GraphQL migration | `intelligence/decision-log.md` |
| Backwards-compatible | v1 API still in use | Need to create |
| Fail-safe | Payment processing, async jobs | Need to create |
| Incremental delivery | Feature flags, gradual rollout | Need to create |

### 3.2 Decision-Making Frameworks

| Framework | Context | Documented |
|---|---|---|
| RFC Process | Proposing architecture changes | `docs/rfc-process.md` |
| Cost-Benefit Analysis | Library/dependency choices | Not documented |
| Security Review Checklist | Pre-merge security verification | `project-brain/security.md` |
| Performance Budget | Acceptable latency thresholds | Need to create |
| Accessibility Checklist | a11y compliance requirements | Need to create |

### 3.3 Reasoning Seeds

#### Seed 1: How to Think About Architecture Changes

```
When evaluating an architecture change for this project:

1. COMPATIBILITY: Does this break the v1 API? If yes, can we version it?
2. MIGRATION PATH: Can we run old + new side-by-side?
3. TEAM IMPACT: How many engineers need to learn this?
4. OPERATIONAL COST: Does this increase deploy complexity?
5. SECURITY IMPACT: Does this change the attack surface?
6. TEST EFFORT: Can we test this in isolation?

The project has a LOW tolerance for:
- Breaking changes without migration guides
- Single-point-of-failure additions
- Untestable abstractions
```

#### Seed 2: How to Think About Dependencies

```
When adding or replacing a dependency:

1. IS IT NEEDED? Can we do it with what we have? (stdlib, existing utils)
2. IS IT MAINTAINED? Check: last commit < 6 months, open issues, release cadence
3. BUNDLE SIZE IMPACT: Check with bundlephobia. Target < 5KB gzipped.
4. TYPES: Does it have TypeScript types? (definitelytyped or built-in)
5. LICENSE: Must be MIT, Apache 2.0, or BSD. NO GPL/AGPL.
6. WHY THIS ONE: Short justification to add to `intelligence/decision-log.md`

Prohibited: Libraries with known CVEs, unmaintained > 2 years, AGPL.
```

#### Seed 3: How to Think About Database Changes

```
When making database changes:

1. ARE MIGRATIONS REVERSIBLE? Each migration must have a down migration.
2. ZERO-DOWNTIME: Can we deploy without locking tables?
3. DATA BACKFILL: Is there existing data to migrate? Plan in batches.
4. INDEX IMPACT: New index? Check for existing similar indexes. Test query plans.
5. ROLLBACK PLAN: What happens if we need to revert the migration?

Golden rule: New columns must be nullable or have defaults. 
Never add NOT NULL columns to existing tables without defaults.
```

#### Seed 4: How to Think About API Design

```
When designing or modifying an API:

1. CONSISTENCY: Does this match existing API patterns? (naming, error format, pagination)
2. VERSIONING: Is this a breaking change? If yes, version the endpoint.
3. PAGINATION: Does the response need pagination? Use cursor-based for lists.
4. ERROR FORMAT: Return consistent error shape: { error: { code, message, details } }
5. RATE LIMITING: Should this endpoint have a different rate limit?
6. IDEMPOTENCY: Can the client safely retry? If payment-related, YES.
7. VALIDATION: Validate EVERYTHING at the boundary. Zod schemas required.
```

#### Seed 5: How to Think About Security

```
When making ANY code change:

1. Is user input involved? If yes, validate, sanitize, escape.
2. Is sensitive data involved? Never log PII, tokens, or secrets.
3. Is this an auth-related change? Pair review required.
4. Is this payment-related? Full audit trail required. Must trigger audit event.
5. Is this a dependency update? Check for CVEs first (npm audit).
6. Is this an API change? Rate limiting, auth, CORS configured?
7. Is this a file upload? Validate type, size, scan content.

Never: Store secrets in code, disable CSRF, disable Helmet headers,
log passwords/tokens, use eval(), trust user-provided URLs.
```

---

## 4. Model Transition Procedure

### Step-by-Step Handoff Checklist

```markdown
# AI Model Transition Checklist

## Phase 1: Load Context

- [ ] Read `agent-handoff-template.md` — understand the handoff process
- [ ] Read `repository-dna.md` — understand project identity and conventions
- [ ] Read `project-brain/project-overview.md` — 30,000-foot view
- [ ] Read `intelligence/decision-log.md` — all architectural decisions
- [ ] Read `intelligence/domain-knowledge.md` — business rules and domain model
- [ ] Read `project-brain/architecture.md` — technical architecture
- [ ] Read `knowledge-graph.md` — entity relationships and dependency chains

## Phase 2: Explore

- [ ] Run `FileMap.txt` review — understand file structure
- [ ] Review active tasks in task tracker
- [ ] Review known issues / bug tracker
- [ ] Clone repo and run `npm install && npm run dev` — verify working setup
- [ ] Run test suite: `npm test` — understand test results

## Phase 3: Verify

- [ ] Start with a small verification task:
   - Fix a trivial bug (typo, styling, test fix)
   - Add a small unit test
   - Update documentation
- [ ] Push the verification change via a PR
- [ ] Get feedback from human reviewer

## Phase 4: Ramp Up

- [ ] Take on a small feature (< 3 files changed)
- [ ] Take on a medium feature (1 module, full stack)
- [ ] Take on a large feature (cross-service, coordination needed)

## Phase 5: Full Context Acquisition (First Week)

### Day 1
- [ ] Read all documentation files
- [ ] Set up local development environment
- [ ] Run test suite and understand test structure

### Day 2
- [ ] Review last 50 commits — understand recent changes and patterns
- [ ] Review open PRs — understand current work in progress
- [ ] Review top 10 open issues — understand known problems

### Day 3
- [ ] Trace one complete workflow (Registration as first)
   - Frontend pages -> API calls -> Service chain -> DB interactions
   - Draw a sequence diagram
- [ ] Review deployment pipeline and infrastructure

### Day 4
- [ ] Complete one small fix (documentation, simple bug)
- [ ] Submit for review to validate understanding

### Day 5
- [ ] Review monitoring and alerting
- [ ] Understand operational runbooks
- [ ] Pair with team member for knowledge transfer

## Sign-Off

- [ ] Can explain the full Registration workflow from UI to DB
- [ ] Can set up the project from scratch without assistance
- [ ] Can locate any file by describing its purpose
- [ ] Knows the deploy procedure and rollback steps
- [ ] Knows which decisions are documented and which are not
```

---

## 5. Knowledge Gap Analysis

### 5.1 Documentation Status

| Category | Documented (Safe) | Undocumented (At Risk) | AI Training Only (Unreliable) |
|---|---|---|---|
| Architecture | Core structure, service split | Rationale for specific technology choices | General web dev knowledge |
| Business Rules | Trial period, discounts, passwords | Cancellation window, refund thresholds, rate limits | Common SaaS practices |
| Development Setup | Docker compose setup | Local env troubleshooting, specific tool versions | General Node.js knowledge |
| Testing | CI pipeline config | Coverage expectations, test patterns | Testing best practices |
| Deployment | CI/CD pipeline steps | Ordering constraints, rollback procedure | Container deployment patterns |
| Security | Auth mechanism overview | PCI compliance, specific threat models | Security fundamentals |
| Operations | — | Monitoring dashboards, runbooks | Cloud operations |
| Bug Knowledge | — | Known bugs, workarounds, root causes | General debugging |
| Historical | — | Past decisions, abandoned features | Common industry history |
| Dependencies | — | Why each dep was chosen, alternatives considered | Library popularity |

### 5.2 Prioritization of What to Document Next

| Priority | Item | Reason | Effort |
|---|---|---|---|
| 🔴 P0 | Business rules (cancellation, refund, sessions) | Legal/compliance risk | 2 days |
| 🔴 P0 | Deployment rollback procedure | Production safety | 1 day |
| 🔴 P0 | Known bugs and workarounds | Prevent repeated debugging | 2 days |
| 🔴 P0 | Operational runbooks (monitoring, alerts) | Operations safety | 3 days |
| 🟡 P1 | Reasoning seeds (architecture, design) | Correct decision-making | 1 day |
| 🟡 P1 | Minimum viable context template | Faster onboarding | 1 day |
| 🟡 P1 | Testing conventions and patterns | Consistent quality | 2 days |
| 🟢 P2 | Dependency rationale | Informed choices | 1 day |
| 🟢 P2 | Historical context | Avoid repeated mistakes | 1 day |
| 🔵 P3 | Codebase navigation map | Faster development | 0.5 day |

### 5.3 Documentation Health Metrics

| Metric | Current | Target |
|---|---|---|
| Architecture decisions documented | 40% | 90% |
| Business rules documented | 25% | 100% |
| Bug knowledge captured | 0% | 80% |
| Dependency rationale documented | 10% | 80% |
| Operational runbooks documented | 0% | 90% |
| Testing patterns documented | 15% | 80% |
| Workflow documentation | 10% | 85% |

---

## 6. Continuity Score

### Score Breakdown

| Category | Score | Justification |
|---|---|---|
| Architecture knowledge preservation | 45% | Core structure documented; rationale for many decisions missing |
| Business rules preservation | 25% | Only obvious rules captured; critical rules undocumented |
| Decision rationale preservation | 20% | Some decisions in decision log; most rationale is unrecorded |
| Operational knowledge preservation | 5% | Almost entirely undocumented — highest risk area |
| Code navigation knowledge preservation | 30% | File structure understood but conventions not documented |
| Testing knowledge preservation | 20% | CI exists but patterns, conventions, coverage targets undocumented |
| Deployment knowledge preservation | 15% | CI/CD pipeline documented; rollback, ordering, gotchas missing |
| Dependency knowledge preservation | 10% | No systematic documentation of dependency choices |
| Historical context preservation | 5% | Almost entirely tribal knowledge |
| Bug knowledge preservation | 0% | Nothing documented — every bug is tribal knowledge |

### Overall Continuity Score

```
Architecture:       ████████░░░░░░░░░░░░  45%
Business Rules:     █████░░░░░░░░░░░░░░░  25%
Decision Rationale: ████░░░░░░░░░░░░░░░░  20%
Operations:         █░░░░░░░░░░░░░░░░░░░   5%
Code Navigation:    ██████░░░░░░░░░░░░░░  30%
Testing:            ████░░░░░░░░░░░░░░░░  20%
Deployment:         ███░░░░░░░░░░░░░░░░░  15%
Dependencies:       ██░░░░░░░░░░░░░░░░░░  10%
Historical Context: █░░░░░░░░░░░░░░░░░░░   5%
Bug Knowledge:      ░░░░░░░░░░░░░░░░░░░░   0%
────────────────────────────────────────
OVERALL:            18%
```

### Status: 🔴 CRITICAL

An AI model replacement today would lose approximately **82% of project knowledge**. Immediate action required on P0 items identified in Section 5.2.

### Path to Green (80%+)

| Milestone | Target Score | Estimated Timeline |
|---|---|---|
| Document all business rules | 35% | 1 week |
| Capture bug knowledge + runbooks | 50% | 2 weeks |
| Document deployment + operations | 60% | 3 weeks |
| Create reasoning seeds + MVC template | 65% | 1 month |
| Complete dependency + historical docs | 75% | 6 weeks |
| Achieve target | 80%+ | 2 months |
