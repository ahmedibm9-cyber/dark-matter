# Architecture Review Checklist

> Review against architecture decisions and overall system design. Run before
> major feature implementation and at milestone boundaries. Each item includes
> the concern, verification method, and severity (BLOCKER / RECOMMENDED).

---

## MODULARITY — Clear boundaries, single responsibility, explicit interfaces

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | Each module has one clearly defined responsibility | Read module README or docstring; does it describe one concern? | BLOCKER |
| 2 | Module boundaries align with business domain boundaries | Map modules to bounded contexts; no split domains | BLOCKER |
| 3 | Public API is explicit (index.ts, __init__.py, re-exports) | Consumers import from index, not internal paths | BLOCKER |
| 4 | Internal implementation details are hidden | Check `_` prefix, `private` keyword, non-exported symbols | RECOMMENDED |
| 5 | No god objects or utility classes doing everything | Check files >400 lines for extraction opportunities | RECOMMENDED |
| 6 | Each module is independently testable in isolation | Can you instantiate the module's primary class without 10 mocks? | RECOMMENDED |
| 7 | Plugin/extension points exist for future variation | Strategy pattern, plug-in interface, or hook system | RECOMMENDED |
| 8 | Module dependencies are explicit (DI, imports, config) | Scan for hidden global dependencies | RECOMMENDED |

---

## COUPLING — Dependency direction, circular deps, appropriate intimacy

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | Dependency direction follows layering (UI → Domain → Data) | Run `madge` or `dependency-cruiser` to verify direction | BLOCKER |
| 2 | No circular dependencies between modules | `madge --circular src/` must return empty | BLOCKER |
| 3 | High-level modules do not depend on low-level details | DIP — abstractions owned by high-level modules | BLOCKER |
| 4 | Shared kernel is minimal and stable | Common/types/domain code should change rarely | RECOMMENDED |
| 5 | Modules communicate through well-defined interfaces, not shared state | Check for direct imports of sibling internals | RECOMMENDED |
| 6 | No inappropriate intimacy (accessing internals of other modules) | Code review for `private` member access, internal API calls | RECOMMENDED |
| 7 | Dependency count per module is bounded (<10 direct deps) | Count imports from other project modules | RECOMMENDED |
| 8 | Frameworks are behind abstractions, not leaking into domain | Check for React/Express imports in domain/service files | BLOCKER |

---

## COHESION — Related functionality grouped, unrelated separated

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | Files/classes contain only related functionality | Does the file name match the content? | RECOMMENDED |
| 2 | Unrelated concerns are in separate modules | Auth logic not in user profile service | BLOCKER |
| 3 | Functions in a module operate at the same abstraction level | No SQL queries mixed with UI formatting | RECOMMENDED |
| 4 | Helper/util modules don't become catch-alls | Check `utils/`, `helpers/` for unrelated functions | RECOMMENDED |
| 5 | Constants/enums defined near their usage domain | Not all enums in a single `constants.ts` | RECOMMENDED |
| 6 | Interface segregation — clients not forced to depend on unused methods | Check interface sizes; split if >5 methods | RECOMMENDED |
| 7 | Exceptions/errors specific to module domain | Not all errors in a single `errors.ts` | RECOMMENDED |

---

## SCALABILITY — Stateless design, caching strategy, async processing

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | Services are stateless (horizontal scaling ready) | Check for in-memory state, local file storage | BLOCKER |
| 2 | Caching strategy defined with TTL and invalidation | Cache keys, eviction policy, stale-while-revalidate | RECOMMENDED |
| 3 | Database queries have appropriate indexes | Review slow query log, explain plans | RECOMMENDED |
| 4 | Read/write workloads separated (CQRS readiness) | Separate read models from write models | RECOMMENDED |
| 5 | Background jobs use queues, not inline processing | Check for Bull, Sidekiq, Celery, SQS integration | RECOMMENDED |
| 6 | Rate limiting and throttling for external integrations | Check API gateway, middleware rate limiter | RECOMMENDED |
| 7 | Pagination for all list endpoints (cursor or offset) | Default page size, max page size, cursor-based in high-volume | RECOMMENDED |
| 8 | Connection pooling for database | Verify pool size configuration | RECOMMENDED |
| 9 | Static assets served via CDN, not application server | Check asset URL configuration | RECOMMENDED |
| 10 | Database read replicas for read-heavy workloads | Architecture diagram review | RECOMMENDED |

---

## RESILIENCE — Fault isolation, graceful degradation, circuit breakers

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | Single service failure does not cascade | Use bulkhead pattern, separate thread pools | BLOCKER |
| 2 | External service failures have circuit breakers | Check for `opossum`, `resilience4j`, `hystrix` | RECOMMENDED |
| 3 | Graceful degradation on dependency failure | Feature works with reduced functionality, not crash | BLOCKER |
| 4 | Retry with exponential backoff for transient failures | Look for retry library, custom retry logic | RECOMMENDED |
| 5 | Timeouts configured for all external calls | HTTP client, DB query, queue read timeouts | BLOCKER |
| 6 | Fallback responses when data unavailable | Cached/static fallback, stale cache | RECOMMENDED |
| 7 | Health check endpoints for each service | `/health`, `/ready`, `/live` endpoints | RECOMMENDED |
| 8 | Graceful shutdown handling (SIGTERM) | Check process signal handlers | RECOMMENDED |
| 9 | Data consistency after partial failures | Saga pattern, transactional outbox, compensating transactions | RECOMMENDED |
| 10 | Self-healing capabilities (auto-restart, crash recovery) | Deployment config (K8s restartPolicy, PM2) | RECOMMENDED |

---

## SECURITY — Least privilege, defense in depth, secure defaults

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | Least privilege for service accounts and API keys | Check IAM roles, RBAC, token scopes | BLOCKER |
| 2 | Defense in depth — multiple security layers | WAF + Auth + Input validation + Output encoding | BLOCKER |
| 3 | Secure defaults (opt-in to less secure options) | Configs default to secure values, require explicit override | BLOCKER |
| 4 | Network segmentation (public/private subnets) | Architecture diagram: DMZ, VPC, private subnets | RECOMMENDED |
| 5 | Secrets managed via vault/secret store, not env files | HashiCorp Vault, AWS Secrets Manager, Azure Key Vault | BLOCKER |
| 6 | Audit logging for security-relevant events | Login, permission changes, data deletion logged | RECOMMENDED |
| 7 | Data encryption at rest and in transit | TLS, database encryption, S3 server-side encryption | BLOCKER |
| 8 | Authentication is centralized (SSO, OIDC) | Not custom auth per service | RECOMMENDED |
| 9 | API keys are rotatable and revocable individually | Key management strategy, rotation schedule | RECOMMENDED |
| 10 | PII data minimized and anonymized where possible | Data flow review for PII collection/storage | RECOMMENDED |

---

## TESTABILITY — Dependency injection, mock boundaries, seam identification

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | Dependencies injected via constructor or parameter | Check for new() inside methods, static calls | BLOCKER |
| 2 | I/O boundaries are mockable (interfaces/abstractions) | External calls behind interfaces, not concrete classes | BLOCKER |
| 3 | Global/static state minimized | Check for singletons, static variables, module-level state | BLOCKER |
| 4 | Seams exist for testing without changing production code | Can you inject a test double without modifying the class? | RECOMMENDED |
| 5 | Time abstraction for time-dependent logic | Use `Date.now()` wrapper, not direct calls | RECOMMENDED |
| 6 | Randomness is seeded or mockable | Random generators behind interface | RECOMMENDED |
| 7 | Configuration overridable in tests | Config from env/DI, not hardcoded | RECOMMENDED |
| 8 | File system access abstracted | `fs` operations behind interface | RECOMMENDED |
| 9 | Side effects are explicit (return values preferred) | Pure functions preferred; side effects at edges | RECOMMENDED |
| 10 | Test fixtures are simple and composable | Factory functions, builders, not huge JSON files | RECOMMENDED |

---

## DEPLOYABILITY — Configuration externalization, migration strategy, feature flags

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | Configuration externalized from code (env/secret store) | No hardcoded URLs, credentials, environment names | BLOCKER |
| 2 | Database migrations are reversible (down migrations) | Check for `down` or `rollback` migration files | BLOCKER |
| 3 | Feature flags allow gradual rollout | LaunchDarkly, Unleash, flag schema in code | RECOMMENDED |
| 4 | Zero-downtime deployment strategy (blue-green, rolling) | Deployment config review | RECOMMENDED |
| 5 | Health check for deployment orchestration | `/health` returns 200 before traffic routing | RECOMMENDED |
| 6 | Containerization with immutable tags (not `:latest`) | Docker image tagging strategy | RECOMMENDED |
| 7 | Infrastructure as Code (Terraform, Pulumi, CDK) | No manual infrastructure changes | RECOMMENDED |
| 8 | Environment parity (dev/staging/prod as similar as possible) | Check Docker Compose vs production setup | RECOMMENDED |
| 9 | Database versioning and schema history tracked | Migration files, not manual DDL | RECOMMENDED |
| 10 | Rollback plan documented for each deploy | Playbook for quick revert | RECOMMENDED |

---

## Decision

- [ ] **APPROVED** — Architecture meets all BLOCKER requirements
- [ ] **CONDITIONAL** — Approved with noted RECOMMENDED items to address in next milestone
- [ ] **REWORK** — One or more architectural BLOCKER items must be addressed

**Architect:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ **Date:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
