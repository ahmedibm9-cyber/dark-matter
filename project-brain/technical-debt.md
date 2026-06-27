# Technical Debt Register

## Overview

This document tracks all known technical debt across the project. Each item is assigned a unique identifier, categorized by type, assessed for cost and effort, and assigned a priority based on the ratio of cost-of-not-fixing to effort-to-fix. The register is reviewed quarterly and updated as part of the planning process.

## Debt Classification Framework

### Types of Technical Debt

| Type | Definition | Examples |
|------|------------|----------|
| **Code Smell** | Poor code structure that violates design principles | God classes, long methods, excessive nesting, magic numbers |
| **Architectural** | Structural decisions that limit evolution | Missing abstraction layer, tight coupling, improper separation of concerns |
| **Test** | Gaps or deficiencies in test coverage | Missing unit tests, inadequate integration tests, flaky tests |
| **Documentation** | Missing, outdated, or incorrect documentation | Stale API docs, missing README sections, no ADRs |
| **Dependency** | Outdated, deprecated, or vulnerable dependencies | Abandoned packages, security CVEs, unsupported versions |
| **Configuration** | Manual configuration, hardcoded values, config drift | Environment-specific branches, manual deployment steps |
| **Knowledge** | Information siloed in individuals' heads | Undocumented tribal knowledge, no onboarding materials |
| **Process** | Inefficient or manual processes that could be automated | Manual release steps, manual database migrations |

### Priority Matrix

| Priority | Cost-to-Fix Ratio | Action |
|----------|------------------|--------|
| **Critical** | Cost > 5x Effort | Fix current sprint |
| **High** | 3x - 5x Effort | Fix within 2 sprints |
| **Medium** | 1x - 3x Effort | Fix within current quarter |
| **Low** | < 1x Effort | Fix when in area, or backlog |

## Debt Register

### Critical

| ID | Area | Description | Cost of Not Fixing | Effort | Age | Opened |
|----|------|-------------|-------------------|--------|-----|--------|
| TD-001 | Auth | JWT secret key is hardcoded in `config/auth.php` and committed to git history. Key has been rotated but old key remains in git history accessible to anyone with repo access. | Security breach: anyone with repo access can sign arbitrary JWTs. Rotating keys invalidates all sessions. | 2 days | 14 months | 2025-04-12 |
| TD-002 | Database | Single PostgreSQL table `events` stores all event types (audit, notifications, webhooks) with a `type` discriminator column. No partitioning. Table has 400M rows and growing 50M/month. | Query performance degrading exponentially. Full table scans for all queries. Estimated query time will exceed 30s by Q3 2026. | 3 weeks | 18 months | 2025-01-05 |
| TD-003 | Security | Password hashing uses bcrypt with cost factor 8 (minimum recommended is 12). No automatic rehashing on login. | User passwords are 4x faster to brute force than current best practices. Regulatory non-compliance (GDPR Art. 32). | 3 days | 10 months | 2025-09-02 |
| TD-004 | API | REST API has no versioning strategy. All endpoints are at `/api/v1/` with no path for v2. Breaking changes are deployed without migration period. | Cannot evolve API without breaking existing integrations. Third-party integrations fragile. | 2 weeks | 20 months | 2024-10-15 |

### High

| ID | Area | Description | Cost of Not Fixing | Effort | Age | Opened |
|----|------|-------------|-------------------|--------|-----|--------|
| TD-005 | Backend | Monolithic `UserService` class handles authentication, profile management, preferences, notifications, and billing logic. 4,200 lines. 35 public methods. | Any change to one concern risks breaking others. Development velocity reduced by estimated 40% in user-related features. | 2 weeks | 16 months | 2025-03-01 |
| TD-006 | Frontend | State management uses a mix of React Context (6 contexts), Redux (legacy), and local state. No consistent pattern. | Developers must understand 3 state systems. Data flow is unpredictable. Bugs from state synchronization are common (avg 2/month). | 3 weeks | 22 months | 2024-09-20 |
| TD-007 | Testing | Test suite has 847 tests but CI run time is 28 minutes. 34 tests are flaky (non-deterministic). | Developers skip running tests locally. Flaky tests erode trust in CI. Estimated 12 developer-hours/week lost to flaky test reruns. | 4 weeks | 12 months | 2025-07-01 |
| TD-008 | Database | Database migrations are not version-controlled. Developers apply changes directly to staging and production via SQL scripts stored in a shared Drive folder. | No audit trail of schema changes. Rollback requires manual reverse engineering. Onboarding new developers requires tribal knowledge transfer. | 1 week | 8 months | 2025-10-20 |
| TD-009 | Frontend | Legacy jQuery-based components coexist with React in the same application. jQuery modifies DOM that React manages, causing unpredictable re-renders. | Hard console errors on 5% of page loads. Feature development in affected areas is avoided by team. Loss of 1 developer-week/month to debugging. | 4 weeks | 24 months | 2024-07-10 |
| TD-010 | CI/CD | Deployment requires manual SSH into production server, pulling latest code, running migrations, and restarting services. No automated rollback. | Average deployment time: 45 minutes. Deployment errors: 1 in 5. Mean time to recovery: 2 hours. No deployments after 2 PM to allow error recovery time. | 2 weeks | 30 months | 2024-01-15 |

### Medium

| ID | Area | Description | Cost of Not Fixing | Effort | Age | Opened |
|----|------|-------------|-------------------|--------|-----|--------|
| TD-011 | Frontend | CSS is a single 4,500-line `styles.css` file with no preprocessor, no BEM naming, and 200+ `!important` declarations. | Adding new styles risks breaking existing ones. Style debugging takes 2-3x longer than feature implementation. | 2 weeks | 26 months | 2024-05-01 |
| TD-012 | Backend | Error handling is inconsistent: 40% of API endpoints return RFC 7807 problem details, 35% return custom error shapes, 25% return generic 500 with no body. | API consumers must handle 3 error formats. Integration development takes 30% longer. Debugging production issues is harder. | 1 week | 14 months | 2025-05-10 |
| TD-013 | Backend | Configuration is spread across YAML files, environment variables, a database table, and a hardcoded constants file. No single source of truth. | Configuration changes require updating 2-4 locations. Incorrect configuration caused 3 production incidents in past 6 months. | 1 week | 18 months | 2025-01-20 |
| TD-014 | Data | Logging uses `console.log` in production code (12 occurrences), mixed with structured logging via Winston (most services), and syslog (legacy services). | Cannot centralize log analysis. Production logs contain unstructured noise. Debugging production issues takes 2x longer. | 3 days | 16 months | 2025-03-15 |
| TD-015 | Frontend | Images served without WebP conversion, responsive sizes, or lazy loading. Average page weight of images: 3.2MB. | Lighthouse performance score: 62 (target: >90). Bounce rate increases by 12% per second of load time. Mobile data costs for users are high. | 5 days | 10 months | 2025-09-10 |
| TD-016 | Backend | File uploads are stored on local disk (`/var/uploads/`) instead of S3-compatible object storage. | No durability guarantees. Uploads lost on server restart. Cannot scale horizontally without NAS/PVC. | 3 days | 20 months | 2024-11-01 |
| TD-017 | Testing | Integration tests use a shared test database without isolation between test runs. Tests are order-dependent. | Random test failures on CI (~15% of runs). Developers trust CI less. Bug escapes to production (3 in last quarter attributed to test gaps). | 1 week | 14 months | 2025-05-05 |
| TD-018 | API | Rate limiting is implemented in application middleware instead of API gateway. Rate limiter state is in-memory (not shared across instances). | Rate limits reset per-instance behind load balancer. Users can exceed intended limits by hitting different instances. | 2 days | 16 months | 2025-03-20 |

### Low

| ID | Area | Description | Cost of Not Fixing | Effort | Age | Opened |
|----|------|-------------|-------------------|--------|-----|--------|
| TD-019 | Frontend | Deprecated vendor bundle includes `moment.js` (120KB) — only 3 usages remain, replaceable with `date-fns` (4KB). | 116KB unnecessary bundle size. Adds ~300ms to load time on 3G. | 1 day | 18 months | 2025-01-10 |
| TD-020 | Backend | Null checks are inconsistent: some methods return `null`, some return `Optional<T>`, some throw `NullPointerException`/`NullReferenceException`. | Occasional NPE in production (~2/month). Each takes ~30min to debug and fix. | 5 days | 22 months | 2024-09-15 |
| TD-021 | Documentation | API documentation is on a Confluence page last updated 14 months ago. 8 endpoints documented, 42 exist. | New team members spend 2-3 days discovering API endpoints. External API consumers given outdated docs. | 3 days | 14 months | 2025-05-01 |
| TD-022 | Backend | Legacy database view `user_summary_v` uses `SELECT *` and joins 12 tables. Used by 3 reports and 2 API endpoints. | Adding a column to any joined table may break the view. Query takes 8-12 seconds. Lock contention on underlying tables. | 2 days | 16 months | 2025-03-25 |
| TD-023 | Infrastructure | SSL certificates are manually renewed every 3 months via a calendar reminder. | Alert fatigue from expiring-certificate monitoring. Human error risk: certificate expired for 4 hours in January 2026. | 2 days | 30 months | 2024-01-10 |
| TD-024 | Frontend | No automated visual regression testing. UI changes are reviewed manually. | Visual bugs reach production approximately twice per sprint. Average fix time: 30 minutes. | 3 days | 12 months | 2025-07-15 |
| TD-025 | Backend | Webhook delivery uses synchronous HTTP calls. If webhook consumer is slow (<30s), the request thread blocks. | Webhook delivery failures under load. API latency p95 increased to 4s when webhooks are active. | 4 days | 8 months | 2025-11-01 |

## Code Smells Inventory

### Detected via Static Analysis (SonarQube)

| Rule Violation | Count | Files | Severity |
|----------------|-------|-------|----------|
| Cognitive Complexity > 15 | 47 | src/services/*.ts | High |
| Duplicated Blocks (3+ lines) | 23 | src/utils/*.ts, src/helpers/*.ts | Medium |
| Function > 100 lines | 31 | src/services/*.ts | High |
| Class > 500 lines | 8 | src/models/*.ts, src/services/*.ts | High |
| Too Many Parameters (> 4) | 56 | src/**/*.ts | Medium |
| Nested Control Flow (depth > 4) | 19 | src/services/*.ts | High |
| Magic Numbers | 134 | src/**/*.ts | Low |
| Empty Catch Block | 12 | src/services/*.ts, src/api/*.ts | High |

### Manual Audit Findings

1. **Global Mutable State in API Client**: The HTTP client module has a mutable base URL that gets overwritten by test setup, causing race conditions in parallel tests.
2. **Copy-Pasted Pagination Logic**: Pagination logic is duplicated across 7 different query methods with minor variations. Extracting a shared pagination utility would eliminate 200+ lines.
3. **Mixed Abstraction Levels in `OrderProcessor`**: The class handles everything from HTTP request parsing to database writes to email composition, violating the Single Responsibility Principle.
4. **Primitive Obsession**: User IDs passed as raw strings throughout the codebase instead of a `UserId` value type. No type safety on ID usage.
5. **Shotgun Surgery**: Changing the user model schema requires updates to 14 files across 3 packages. No centralized schema definition.

## Architectural Debt

### Identified Issues

1. **No Clear Bounded Contexts**: Domain logic is organized by technical layer (controllers, services, repositories) rather than by domain context. This means billing logic sits next to user notification logic, making it impossible to extract microservices in the future without a full rewrite.

2. **Circular Module Dependencies**: The `auth` module imports from `user`, which imports from `notification`, which imports from `auth`. This circular dependency causes unpredictable initialization order and makes it impossible to tree-shake unused modules.

3. **Missing Anticorruption Layer**: External API integrations directly use domain models as DTOs. When a third-party API changes its response format (Stripe, SendGrid), the change propagates through the entire domain layer.

4. **Event Bus Without Contracts**: Pub/sub events are emitted and consumed without typed contracts. Event names are magic strings, payloads are `Record<string, any>`, and there is no subscriber validation at compile time.

5. **Repository Pattern Leakage**: The repository abstraction layer is inconsistent. Some repositories return domain models, others return ORM entities. Some use the Unit of Work pattern, others auto-commit.

## Test Debt

### Coverage Gaps

| Module | Line Coverage | Branch Coverage | Critical Paths Untested |
|--------|-------------|----------------|------------------------|
| Auth (login, registration, MFA) | 72% | 58% | MFA backup codes, rate limiting, brute force detection |
| Billing (invoicing, subscriptions) | 45% | 32% | Failed payment handling, proration, downgrade edge cases |
| Reporting (export, aggregation) | 38% | 25% | Large dataset handling, concurrent export requests, format conversion |
| Webhook delivery | 52% | 40% | Retry with backoff, signature validation, idempotency |
| Search indexing | 30% | 18% | Special characters, Unicode, very long documents |

### Flaky Tests

| Test | Failure Rate | Root Cause | Fix Status |
|------|-------------|------------|------------|
| `OrderService.shouldProcessRefund` | 25% (4 of 16) | Shared mutable date mock; test passes only before noon | In progress |
| `SearchResults.shouldPaginateCorrectly` | 18% (3 of 16) | Race condition in async indexing fixture | Triaged |
| `NotificationService.shouldBatchEmails` | 12% (2 of 16) | Elasticsearch index refresh latency | Fix scheduled |
| `RateLimiter.shouldResetAfterWindow` | 30% (5 of 16) | Test depends on `Date.now()` with no mock | Known |
| `DataExport.shouldGenerateCSV` | 15% (2 of 16) | Temporary file cleanup race | Fixed (pr #1284) |

### Missing Test Levels

- **No contract tests** for API consumers
- **No visual regression tests** for UI components
- **No performance/load tests** for critical endpoints
- **No chaos tests** for infrastructure resilience
- **No security tests** beyond basic SAST scanning

## Documentation Debt

| Document | Last Updated | Status | Owner |
|----------|-------------|--------|-------|
| API Reference | 2025-04-10 (14 months stale) | 8 of 42 endpoints doc'd | Needs reassignment |
| Architecture Overview | 2025-06-01 (12 months stale) | Outdated; references deprecated services | Engineering lead |
| Onboarding Guide | 2026-01-15 (5 months stale) | Missing new dev environment setup | DevEx team |
| Disaster Recovery Plan | 2025-03-01 (15 months stale) | Dr tested but docs not updated | SRE team |
| Security Policies | 2025-11-01 (7 months stale) | Missing new SSO integration | Security team |
| Deployment Runbook | 2026-02-01 (4 months stale) | Updated but missing rollback section | DevOps |
| User Help Center | 2025-08-01 (10 months stale) | New features not documented | Product team |

## Dependency Debt

### Outdated Dependencies

| Package | Current | Latest | Age | Risk |
|---------|---------|--------|-----|------|
| express | 4.17.1 | 4.21.0 | 4 years | 3 known CVEs (2 high) |
| lodash | 4.17.20 | 4.17.21 | 3 years | 1 known CVE |
| axios | 0.21.4 | 1.7.2 | 3 years | Breaking change (ESM) |
| moment | 2.29.1 | 2.30.1 | 3 years | Deprecated; no new features |
| passport | 0.6.0 | 0.7.0 | 2 years | Minor breaking changes |
| mongoose | 6.12.0 | 8.8.0 | 2 years | Major version jump |
| eslint | 8.57.0 | 9.x | 1 year | Breaking config format change |

### Deprecated Dependencies

| Package | Replacement | Migration Status |
|---------|-------------|-----------------|
| request (deprecated) | got / undici | 4 files still use it |
| react-helmet (unmaintained) | @unhead/react / react-helmet-async | Pending migration |
| @types/bluebird (unused) | Remove | Can be safely removed |
| gulp (legacy build) | Vite / esbuild | Build migration in progress |

### Vulnerable Dependencies

| Package | Version | CVE | Severity | Fix Available |
|---------|---------|-----|----------|---------------|
| braces | <3.0.3 | CVE-2024-4068 | High | Update to ^3.0.3 |
| tar | <6.2.1 | CVE-2024-28849 | Medium | Update to ^6.2.1 |
| tough-cookie | <4.1.3 | CVE-2023-26136 | Medium | Update to ^4.1.3 |
| qs | <6.11.1 | CVE-2024-27980 | High | Update to ^6.11.1 |

## Configuration Debt

| Issue | Details | Impact | Fix |
|-------|---------|--------|-----|
| Environment variable naming inconsistency | `DB_HOST`, `DATABASE_HOST`, `DB_URL` all used in different services | Confusion during setup; startup failures for new environments | Standardize on `DATABASE_*` prefix |
| Hardcoded staging API keys in source | Skip. Config in `.env.example` but listed in source for 3 services | Security risk; staging credentials leak | Move to environment variables, add to vault |
| Missing default values | 15 config keys have no defaults; services fail if env var not set | Brittle startup; unclear what's required | Add sensible defaults with validation |
| Config validation duplication | 4 separate YAML files validate the same database config | Drift between validations | Centralized config schema |
| Feature flags in database | Feature flags stored in a config table but accessed via in-memory cache with 5-minute TTL | Feature toggle changes take 5 minutes to propagate | Add pub/sub invalidation or reduce TTL |

## Debt Repayment Roadmap

### Q3 2026 (Current Quarter)

| Quarter | Items | Estimated Cost | Expected Benefit |
|---------|-------|---------------|------------------|
| Q3 2026 | TD-001 (JWT secret), TD-003 (bcrypt cost), TD-010 (CI/CD), TD-023 (SSL auto-renew) | 4 weeks | Security baseline met; deployment time reduced from 45min to 10min |
| Q4 2026 | TD-002 (table partitioning), TD-005 (UserService refactor), TD-009 (jQuery removal) | 8 weeks | Query time back under 1s; dev velocity +40% in user features |
| Q1 2027 | TD-006 (state management), TD-007 (flaky tests), TD-011 (CSS refactor) | 8 weeks | CI time reduced to 12min; UI bugs reduced by 60% |
| Q2 2027 | TD-004 (API versioning), TD-012 (error handling), TD-014 (logging) | 6 weeks | API evolution unblocked; production debugging time halved |

## Prevention Strategies

### Development Process

1. **Three Strike Policy**: If the same workaround is applied three times, the underlying debt must be scheduled for repayment.
2. **Boy Scout Rule**: Always leave code slightly cleaner than you found it. Spend 10% of task time on nearby debt reduction.
3. **Debt Awareness in Code Review**: Every PR must include a "Technical Debt Impact" section in the description, noting any debt introduced or repaid.
4. **Automated Quality Gates**: CI fails if: SonarQube quality gate fails, test coverage delta < -2%, or new code introduces cognitive complexity > 15.

### Debt Budget Policy

| Metric | Threshold | Action |
|--------|-----------|--------|
| Critical debt items | > 3 | Freeze feature work; allocate sprint to debt |
| High debt items | > 10 | Allocate 20% of capacity to debt repayment |
| Test coverage (overall) | < 70% | No new feature merges without equivalent tests |
| Flaky test rate | > 5% | Freeze merges until flaky rate reduced |
| Dependency age (critical) | > 2 years behind | Auto-create P2 ticket for upgrade |
| CI pipeline duration | > 20 minutes | Investigate and optimize within 1 week |
| SonarQube rating | < B (6.5/10) | Block release; improve to B or better |

### New Feature Debt Cap

When implementing new features, no more than 1 "High" debt item or 3 "Medium" debt items may be introduced per feature. If this cap is exceeded, the feature must include a debt repayment plan as part of its definition of done.
