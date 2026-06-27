# Engineering Memory

> Living document capturing why we built things the way we did, what we learned, and what we'd do differently.

---

## Entry Format

```
Date       | Decision | Context | Alternatives Considered | Rationale | Outcome | Lessons
```

---

## Entries

### 1. TypeScript Migration from JavaScript
2025-01-15 | TS-001 | Monorepo migration from JS to TS | Gradual JSDoc, Flow, full rewrite | JSDoc too verbose, Flow deprecated, full rewrite too risky. Used `ts-migrate` with per-package rollout. | 6-week migration completed with zero regressions. | Migrate incrementally by package, not all at once. Lock dependency versions during migration.

### 2. Monorepo with Turborepo
2025-02-01 | INFRA-001 | Single repo growing to 15 packages | Nx, Lerna, Bazel, separate repos | Turborepo had best DX, fastest cache, simpler config. Nx overly complex, Bazel too heavy. | Build times dropped from 12m to 2.5m. | Pick tooling that your team can understand without dedicated infra engineers.

### 3. GraphQL over REST for API Gateway
2025-02-20 | API-001 | Need unified API for mobile/web | REST with BFF, gRPC, tRPC | REST BFF required per-client endpoints. gRPC poor browser support. GraphQL gave declarative fetching. | 40% less data transferred, 60% fewer endpoints. | Schema-first design prevents most breaking changes. Version your schema, not your API.

### 4. PostgreSQL as Primary Database
2025-03-01 | DB-001 | Need ACID, JSON, full-text search | MongoDB, MySQL, CockroachDB | MongoDB lacks joins/transactions. MySQL weaker JSON/extension support. CockroachDB too immature. | Handles 10M+ rows with sub-50ms queries. | Use JSONB sparingly — normalized tables outperform at scale.

### 5. Event-Driven Architecture with Kafka
2025-03-15 | ARCH-001 | Need async processing for billing, notifications, search indexing | RabbitMQ, Redis Streams, SQS | RabbitMQ lacks replay. Redis Streams no long-term retention. SQS vendor lock-in. Kafka gave replay, retention, exactly-once. | Processing 500k events/day with 99.9% reliability. | Never commit to event schema without schema registry. Avro with Schema Registry is non-negotiable.

### 6. Feature Flags with Unleash
2025-04-01 | FF-001 | Need gradual rollout, A/B testing, kill switches | LaunchDarkly, custom solution, Flagsmith | LaunchDarkly too expensive. Custom solution too slow to build. Unleash open-source, self-hosted, meets all needs. | Rolled out 47 features with flags, 3 emergency kill-switch activations. | Flag cleanup must be a checklist item in the Definition of Done. Orphaned flags accumulate fast.

### 7. React Query over Redux for Server State
2025-04-10 | FE-001 | Complex server state management | Redux Toolkit, Zustand, Apollo Client | Redux too much boilerplate. Zustand too unopinionated for caching. React Query handled caching, refetching, optimistic updates out of the box. | 70% less state code. Cache invalidation bugs dropped to near zero. | Not a full Redux replacement — use Zustand for client-only UI state alongside React Query.

### 8. Tailwind CSS over Styled Components
2025-04-20 | FE-002 | Design system consistency in React | Styled Components, CSS Modules, vanilla CSS | Styled Components runtime cost. CSS Modules no design-token system. Tailwind with custom config gave token-based design, zero runtime cost. | Bundle size reduced 85KB. Design audits pass 100%. | Invest in custom Tailwind config early. Default Tailwind is generic; branded config makes it a design system.

### 9. Auth0 for Authentication
2025-05-01 | SEC-001 | Need SSO, MFA, social login | Firebase Auth, Keycloak, custom auth | Firebase Auth limited enterprise SSO. Keycloak too complex to operate. Custom auth too risky. AuthO gave 50+ SSO providers, MFA, breached-password detection. | 3-week integration vs estimated 8-week custom build. | AuthO costs scale with MAU — monitor billing monthly. Set up spending alerts on day one.

### 10. Vitest over Jest
2025-05-10 | TEST-001 | Need faster test runner | Jest, Mocha, Ava | Jest slow with ESM. Mocha too barebones. Ava lacking ecosystem. Vitest Jest-compatible API, native ESM, 3x faster. | 12m test suite -> 4m. ESM issues eliminated. | For Vite-based projects, Vitest is strictly superior. No reason to use Jest.

### 11. Indexing Strategy — Partial Indexes for Soft-Deleted Rows
2025-05-15 | PERF-001 | Queries scanning soft-deleted rows (30% of table) | Full table scan, application-level filtering, partial indexes | Full scan too slow. App filtering doesn't help. Partial index `WHERE deleted_at IS NULL` cut index size by 40%. | Query time 800ms -> 45ms. | Profile first, index second. Index without data is cargo-culting.

### 12. Image Optimization Pipeline
2025-05-20 | PERF-002 | Large user-uploaded images (5MB avg) killing page load | Client-side resize, accept originals, serve via CDN | Client-side resize unreliable. Originals too slow. CDN alone insufficient. Pipeline: resize to 3 sizes (thumb, web, full) + WebP conversion + CDN. | 5MB -> 120KB avg. LCP improved 4.2s -> 1.1s. | AVIF is better compression but WebP has broader support. Serve both with `<picture>`.

### 13. Rate Limiting — Token Bucket vs Sliding Window
2025-06-01 | SEC-002 | API abuse during launch | Token bucket, sliding window, fixed window | Fixed window allows burst at boundaries. Token bucket simpler. Sliding window more accurate but more complex. Chose Hybrid: token bucket per-IP, sliding window per-user. | Blocked 12k abusive requests in first month. | Rate limit at the gateway, not the app. Never rate limit health checks.

### 14. Architecture Decision: Microservices over Modular Monolith
2025-06-10 | ARCH-002 | Team growing from 5 to 25 engineers | Modular monolith, serverless, nanoservices | Modular monolith good for small team but coupling grows. Serverless cold starts too slow for core API. Nanoservices too granular. Microservices with clear bounded contexts struck balance. | 12 services, 6 teams, independent deploys. | Start modular monolith. Extract services only when team boundaries demand it. Premature microservices are distributed monoliths.

### 15. Error Tracking — Sentry Self-Hosted
2025-06-20 | OBS-001 | Error tracking across services | DataDog, Rollbar, self-built, Sentry cloud | DataDog too expensive. Rollbar less powerful. Self-built too much effort. Sentry cloud costly at scale. Self-hosted Sentry saved 60%. | Processing 2M events/month for $200 infra cost. | Self-hosting Sentry is operationally heavy. Use cloud until 1M+ events/month.

### 16. Finite State Machine for Order Workflow
2025-07-01 | BIZ-001 | 15+ order states, complex transitions | State machine library, manual if/else, event sourcing | Manual if/else unmaintainable. Event sourcing overkill. State machine library gave visual transitions, guards, side effects. Used XState with generated workflow diagrams. | Order bugs dropped 90%. New state additions are safe. | Put state machines in their own package. Diagram generation catches invalid transitions in code review.

### 17. Database Migration Strategy — Sqitch over Knex Migrations
2025-07-10 | DB-002 | Need reversible, reviewable migrations | Knex migrations, Flyway, Alembic, Sqitch | Knex migrations not reversible easily. Flyway Java dependency. Alembic Python-only. Sqitch: language-agnostic, revert/test/deploy per change, VCS-aware. | Deploy/rollback 100+ migrations without incident. | Test migration rollback as part of CI. A migration that can't revert is a hostage.

### 18. Caching Layer — Redis + CDN
2025-07-20 | PERF-003 | API p95 latency > 2s, database at 80% CPU | Varnish, Memcached, nothing, Redis | Varnish HTTP-only. Memcached limited data structures. Redis: multi-purpose cache (API, session, rate-limit). CDN for static + cacheable API responses. | p95 latency 250ms. DB CPU 25%. Infra cost unchanged. | Cache invalidation is the hardest problem. Use cache tags for pattern-based invalidation.

### 19. Dependency Management — Renovate over Dependabot
2025-08-01 | DEVX-001 | Managing 200+ dependencies across monorepo | Dependabot, manual updates, Renovate | Dependabot PR-per-dep creates noise. Manual updates too slow. Renovate: group updates, automerge, schedule, monorepo-aware. | 95% of dependency updates automated. Zero breaking-change incidents from automated updates. | Configure automerge only for patch updates. Require manual review for major. Pin exact versions in libraries.

### 20. Incident Retrospective — Search Index Outage (2025-08-15)
2025-08-15 | INC-001 | Full-text search down 45 minutes | N/A | Kafka consumer lagged 2M events due to schema incompatibility between producer and consumer. | Hotfix: restarted consumer with updated schema. Long-term: Schema Registry enforcement + consumer lag alerts. | Always enforce schema compatibility. Never deploy schema changes without consumer validation. Add consumer lag alerting.

### 21. Incident Retrospective — Payment Double Charge (2025-09-01)
2025-09-01 | INC-002 | 47 users double-charged ($12k total) | N/A | Idempotency key missing on payment retry. Retry logic sent duplicate charge to Stripe. | Fixed: added idempotency key to all payment mutations. Refunded all duplicates. | Every payment mutation MUST be idempotent. Idempotency keys should be required, not optional. Add integration test for retry flow.

### 22. Frontend State — Recoil to Zustand Migration
2025-09-10 | FE-003 | Recoil experimental, performance issues at scale | Jotai, Zustand, Redux, Valtio | Recoil unstable API, concurrency bugs. Jotai similar issues. Zustand: simple, proven, no boilerplate. Chose Zustand for client state + React Query for server state. | Migration completed in 2 weeks. Bundle size reduced 30KB. | Avoid experimental libraries for core infrastructure. Zustand's simplicity made migration trivial.

### 23. CI/CD — GitHub Actions over Jenkins
2025-09-20 | DEVOPS-001 | Jenkins too slow, complex pipeline maintenance | CircleCI, GitLab CI, Buildkite, GHA | CircleCI costly. GitLab CI not our platform. Buildkite required self-hosted agents. GHA: good free tier, native GitHub integration, matrix builds. | CI time 18m -> 6m. Maintenance effort halved. | GHA is excellent for standard workflows. For complex pipeline orchestration, consider external orchestrator like Dagster.

### 24. API Versioning — URL Path vs Header vs Query
2025-10-01 | API-002 | Need to version APIs for breaking changes | URL path (/v1/), header (Accept-Version), query (?v=1) | URL path simplest, most visible, cacheable. Query ugly. Header invisible in logs. Chose URL path versioning. | Clean, discoverable API. Clients clearly pinned. | Avoid versioning by never breaking v1. Add fields, don't remove them. Version only when unavoidable.

### 25. Testing Strategy — Testing Trophy over Pyramid
2025-10-10 | TEST-002 | Low confidence in releases despite test coverage | Testing pyramid, honeycomb, trophy | Pyramid overemphasizes unit tests. Honeycomb doesn't guide where to invest. Trophy: integration tests > static analysis > unit > E2E. | Moved from 300 unit / 50 integration to 100 unit / 400 integration / 20 E2E. | Integration tests catch bugs units miss. E2E tests the critical paths only. Test business logic, not framework code.

### 26. Tailwind CSS Pro Build Optimization
2025-10-20 | PERF-004 | Tailwind build time 45s in CI | JIT mode, purge optimization, webpack esbuild | JIT already enabled. Purge scanning slow. Used esbuild for CSS processing instead of webpack. | Build time 45s -> 5s. | esbuild is dramatically faster than webpack for CSS. Use it as a dedicated CSS processor.

### 27. UX Decision — Optimistic Updates
2025-11-01 | UX-001 | UI felt slow after mutations | Loading spinners, skeleton screens, optimistic updates | Spinners poor UX. Skeletons only for initial load. Optimistic updates: show result immediately, rollback on error. | Perceived latency dropped from 1.2s to 50ms. Support tickets about slowness eliminated. | Optimistic updates require robust error handling. Always save a rollback snapshot. Always show error state clearly.

### 28. Observability — OpenTelemetry over DataDog Agent
2025-11-10 | OBS-002 | Vendor lock-in, high DataDog costs | DataDog agent, OpenTelemetry + Grafana, SigNoz | DataDog agent vendor-locked. OpenTelemetry standard, multi-backend. Grafana Tempo for traces, Mimir for metrics, Loki for logs. | Infra monitoring cost reduced 70%. Migrated to self-hosted Grafana stack. | OpenTelemetry is the right abstraction. Pick it regardless of backend. Instrument with OTel SDK, export anywhere.

### 29. Soft Deletes Implementation
2025-11-20 | DB-003 | Need recovery from accidental deletes | Hard delete with backup, soft delete, deleted_at table | Hard delete unrecoverable without DBA. Separate table complex queries. Soft delete with `deleted_at` filter simplest. | Recovered 3 accidental deletes in first month. | Partial indexes on `WHERE deleted_at IS NULL` are mandatory. Add unique partial indexes too.

### 30. Documentation — ADRs over Wiki
2025-12-01 | DOC-001 | Decision context lost, wiki outdated | ADR files, Notion/wiki, Confluence | Wiki/Confluence quickly stale. ADRs in repo, reviewed in PRs, always current. | 45 ADRs written and maintained. Onboarding time reduced 40%. | ADRs are the single source of truth for decisions. Require ADR for any significant architectural choice.

### 31. Database Sharding Strategy — Citus over Manual Sharding
2025-12-05 | DB-004 | Orders table growing beyond 50M rows, need horizontal scaling | Manual sharding by org_id, Citus, Vitess, NoSQL migration | Manual sharding complex to maintain. Vitess operationally heavy. NoSQL migration too risky. Citus gave PostgreSQL-compatible distributed tables with minimal code changes. | Orders table distributed across 4 nodes. Query performance unchanged. Migration took 2 weeks. | Start with Citus for PostgreSQL sharding. It's the least invasive option. Monitor shard balance and rebalance quarterly.

### 32. Error Boundary Strategy — React Error Boundaries + Sentry
2025-12-10 | FE-004 | Unhandled React errors crashing entire page | Global error handler, per-component boundary, route-level boundary | Global handler too coarse. Per-component too granular (200+ components). Route-level balanced granularity with manageable surface area. Each route wrapped with boundary reporting to Sentry. | Zero full-page crashes in production since implementation. 95% of errors caught with context. | Use route-level error boundaries. Include enough context (route, user ID, action) for debugging. Always show a recovery button.

### 33. Container Strategy — Docker Compose for Dev, Kubernetes for Prod
2025-12-15 | DEVOPS-002 | Consistent dev/prod environments, scaling needs | Docker Compose everywhere, K8s everywhere, Nomad, PaaS (Heroku/Railway) | K8s everywhere too heavy for dev. Nomad less ecosystem support. PaaS costly at scale. Docker Compose for local dev, K8s for prod with Skaffold bridging the gap. | Zero "works on my machine" bugs in 6 months. Dev onboarding from 2 days to 2 hours. | Invest in dev/prod parity. Skaffold makes K8s local dev bearable. Don't force K8s on developers for daily work.

### 34. Log Aggregation — Loki over ELK Stack
2026-01-05 | OBS-003 | Log storage costs growing 30% MoM with ELK | ELK, Loki + Grafana, CloudWatch, DataDog logs | ELK storage too expensive (3x compression). CloudWatch vendor lock-in. DataDog logs too costly. Loki: cheaper storage, native Grafana integration, no indexing overhead. | Log storage costs reduced 80%. Query speed comparable. | Loki trades indexing speed for storage cost. Acceptable for logs. Traces belong in Tempo, metrics in Mimir, logs in Loki — use the right tool.

### 35. Code Formatting — Biome over Prettier + ESLint
2026-01-15 | DEVX-002 | Prettier + ESLint slow (12s), config duplication, plugin conflicts | Biome, Prettier + ESLint, dprint, Oxc | Prettier + ESLint slow with 200+ files. Plugin conflicts monthly. dprint less ecosystem. Oxc alpha-stage. Biome: Rust-based, 10x faster, unified formatting + linting. | Lint + format from 12s to 1.2s for full codebase. Zero config conflicts. | Rust-based tools are the future. Biome is production-ready for most projects. Keep ESLint for a few plugins Biome doesn't support yet.

### 36. API Pagination — Cursor-Based over Offset-Based
2026-01-20 | API-003 | Offset pagination slow on large datasets, inconsistent when data changes | Cursor-based, offset-based, keyset pagination | Offset pagination slow with OFFSET on large tables. Inconsistent results when rows inserted/deleted between pages. Cursor-based: stable, fast, works with real-time data. Used base64-encoded composite cursors. | API response time stable regardless of page depth. No duplicate/missing items in paginated results. | Always use cursor-based pagination for lists that change frequently. Offset is fine only for static/admin lists under 10k rows.

### 37. WebSocket Strategy — Socket.IO over Raw WebSocket
2026-02-01 | REALTIME-001 | Need real-time updates for orders, notifications, chat | Socket.IO, raw WebSocket, SSE, Pusher | Raw WebSocket lacks auto-reconnect, rooms, fallback transport. SSE unidirectional. Pusher costly at scale. Socket.IO: auto-reconnect, rooms, namespaces, fallback to long-polling, 10x less code. | Real-time order updates working with 50ms latency. Auto-reconnect handles 99% of connection drops. | Socket.IO is the right choice for most real-time needs. Only drop to raw WebSocket if you need maximum throughput and can build reconnect/room logic yourself.

### 38. Migration: Stripe API Version Upgrade (2024-12 to 2025-02)
2026-02-10 | MIG-001 | Stripe API version upgrade required 3 breaking changes | Staged rollout per endpoint, test mode dry-run, shadow traffic | Staged rollout: upgrade one endpoint at a time, validate in test mode. Shadow traffic: duplicate requests to new version, compare responses. | Zero customer-facing incidents. All 12 Stripe endpoints migrated over 3 weeks. Shadow traffic caught 2 response format mismatches. | Test mode + shadow traffic is the safest migration pattern. Never upgrade all endpoints at once. Compare responses programmatically.

### 39. Migration: PostgreSQL Major Version Upgrade (15 to 16)
2026-02-20 | MIG-002 | Need PostgreSQL 16 features (pg_stat_io, improved parallel query) | In-place upgrade, logical replication, blue-green with pgcat | In-place upgrade too risky (downtime, no rollback). Logical replication: minimal downtime, full rollback. Blue-green with pgcat: instant cutover, complex setup. Chose logical replication with pglogical. | 2-minute cutover window. Zero data loss. Rollback tested successfully. | Logical replication is the safest upgrade path. Always test rollback on staging. Have a manual failback plan.

### 40. Decision: Protobuf over JSON for Internal Service Communication
2026-03-01 | ARCH-003 | Internal gRPC calls slower than expected, large payloads | JSON over HTTP, Protobuf, MessagePack, Cap'n Proto | JSON parsing slow at scale. MessagePack less tooling support. Cap'n Proto immature. Protobuf: fast, strongly typed, great gRPC integration, code generation. | Payload size reduced 60%. Deserialization 5x faster. Type errors caught at compile time. | Protobuf is worth the schema overhead for internal services. Use buf.build for schema management. Keep JSON for external APIs.

### 41. Decision: E2E Testing with Playwright over Cypress
2026-03-10 | TEST-003 | Flaky E2E tests, slow CI, limited browser support | Playwright, Cypress, Puppeteer, Selenium | Cypress flaky, limited to Chromium, slow. Puppeteer Chromium-only. Selenium slow, complex. Playwright: multi-browser, fast, auto-wait, network interception. | E2E flakiness dropped from 15% to 1%. Test execution 3x faster. Cross-browser tests in same CI run. | Playwright is strictly superior to Cypress for most use cases. Auto-wait eliminates most flakiness. Network interception is a superpower for testing edge cases.

### 42. Decision: Code Generation with Plop for Feature Scaffolding
2026-03-20 | DEVX-003 | New features require 8+ files manually created, boilerplate errors | Plop, Hygen, Yeoman, manual | Yeoman heavy. Hygen less template flexibility. Manual error-prone. Plop: lightweight, in-repo templates, prompts for feature name/files. | New feature scaffolding time from 15m to 30s. Zero missing file bugs. Consistent file structure across teams. | Invest in scaffolding early. Every time a developer manually copies files, you're wasting money. Templates should be in the repo.

### 43. Decision: Environment Variable Management — 1Password CLI over .env Files
2026-04-01 | SEC-003 | .env files committed to repo 3 times, secrets leaked | .env files, 1Password CLI, Vault, Doppler, SOPS | .env files unsafe (committed 3x). Vault operationally heavy. Doppler costly. SOPS requires key management. 1Password CLI: developer-friendly, audit trail, auto-injects into shell. | Zero secret leaks since migration. Developer onboarding simplified. Audit trail for all secret access. | 1Password CLI is the right balance of security and developer experience. Don't over-engineer secret management. Make it easy to do the right thing.

### 44. Decision: Alerting Strategy — Burn Rate Alerts over Static Thresholds
2026-04-10 | OBS-004 | Static threshold alerts too noisy (100+ alerts/day), too many false positives | Burn rate alerts, static thresholds, anomaly detection, no alerts | Static thresholds: noisy, miss gradual degradation. Anomaly detection: complex, black-box. No alerts: unacceptable. Burn rate: alert based on how fast error budget is consumed. | Alert volume dropped from 100+/day to 8/day. All 8 were real incidents. Mean time to detect improved 4x. | Burn rate alerts are the gold standard for SLO-based alerting. Configure at 1x, 5x, 10x burn rates. Always measure MTTD.

### 45. Decision: Database Backups — WAL-G over pg_dump
2026-04-20 | DB-005 | pg_dump backups too slow (4h for 500GB DB), no PITR support | WAL-G, pg_dump, pgBackRest, Barman | pg_dump slow, no point-in-time recovery. pgBackRest powerful but complex config. Barman solid but Python dependency. WAL-G: simple, fast, S3-native, PITR support. | Backup time from 4h to 15min. PITR enabled with 1-minute granularity. Restore tested monthly. | WAL-G is the simplest PITR solution for PostgreSQL on cloud storage. Test restores monthly, not just backups. No backup is real until you've restored it.

### 46. Decision: API Documentation — GraphQL Hive + Publishing Workflow
2026-05-01 | DOC-002 | GraphQL API docs out of date, no changelog for consumers | GraphQL Hive, Apollo Studio, manual docs, Stoplight | Apollo Studio costly for self-hosted. Manual docs always stale. Stoplight no native GraphQL support. Hive: schema registry, changelog, cost analysis, operation registry. | API docs always up to date. Consumers get changelog on schema changes. Breaking changes caught in CI. | Schema registry with changelog is essential for GraphQL at scale. Hive is the best open-source option. Operation registry prevents undocumented queries.

### 47. Decision: Mobile Push Notifications — Firebase over Custom Push Service
2026-05-15 | MOBILE-001 | Push notification delivery unreliable, inconsistency between iOS/Android | Firebase Cloud Messaging, custom push service, AWS SNS, OneSignal | Custom push: need to maintain APNs + FCM connections, complex. SNS costly at scale. OneSignal costly. Firebase: free, reliable, handles APNs/FCM abstraction. | Push delivery rate improved from 92% to 99.5%. One code path for both platforms. | Firebase FCM is the standard for a reason. It handles the hard parts (device token management, delivery guarantees). Use Firebase Functions for sending logic.

### 48. Decision: Component Library — Radix UI over Material UI
2026-06-01 | FE-005 | MUI too opinionated, heavy bundle, customization painful | Radix UI, Material UI, Chakra UI, Headless UI, Ant Design | MUI heavy (120KB+), customization requires theme overrides, brand feel limited. Chakra bundle larger. Headless UI few components. Ant Design not React-native friendly. Radix: unstyled, accessible, composable, small bundle. | Bundle size reduced 90KB. Design system implemented in 2 weeks vs estimated 6 weeks with MUI. Full WCAG 2.1 AA compliance. | Unstyled component libraries give you full design control without rebuilding accessibility. Radix + Tailwind is the ideal combination.

### 49. Decision: Authentication Pattern — BFF (Backend for Frontend) over Direct Auth
2026-06-15 | SEC-004 | Access tokens exposed to browser, token theft via XSS | BFF pattern, direct Auth0 SDK, token in iframe, PKCE alone | Direct Auth0 SDK exposes tokens in browser. Iframe approach complex, cross-browser issues. PKCE alone doesn't prevent XSS token theft. BFF: tokens stored in HTTP-only cookies, never exposed to JavaScript. | Zero token theft incidents since BFF migration. All tokens server-side. CSRF protected. | BFF is the gold standard for browser-based auth. Never expose access tokens to JavaScript. HTTP-only cookies + CSRF tokens are the way.

### 50. Decision: GraphQL Federation over Schema Stitching
2026-07-01 | GRAPHQL-001 | Single GraphQL gateway becoming bottleneck, 15 services to compose | Federation (Apollo), schema stitching, no gateway (client-side stitching) | Schema stitching requires manual resolver wiring. Client-side stitching complex, no shared cache. Federation: declarative, type-safe, managed composition. | Gateway composition scales to 15 services. Adding new service is 3 files. Schema coordination automated. | Federation is worth the complexity for 5+ services. Under 5 services, schema stitching is simpler. Always use @key directives for entity resolution.

### 51. Decision: Feature Branch Workflow over Trunk-Based Development
2026-07-10 | DEV-001 | Merge conflicts frequent, CI takes 15min, trunk-based too risky | Feature branches, trunk-based, GitHub Flow, Git Flow | Trunk-based requires ultra-fast CI (<5min) and high discipline. Git Flow too complex. GitHub Flow simple but no staging branch. Feature branches with short-lived branches (<2 days) and squash merges. | Merge conflicts reduced 80%. CI still 15min but acceptable with feature branches. | Feature branches work well when CI is 5-15min. If CI were <5min, trunk-based would be better. Squash merges keep history clean.

### 52. Decision: Graceful Degradation over Strict Error Handling
2026-07-20 | UX-002 | Third-party API outages cascading to complete page failures | Graceful degradation, circuit breaker, fail-fast, caching | Fail-fast caused cascading failures. Circuit breaker handled downstream timeouts. Graceful degradation: show stale data + "last updated" banner instead of error screen. | Page load success rate improved from 97% to 99.9%. Support tickets about "site down" dropped 90%. | Graceful degradation builds trust. Show something useful even when data is stale. Always show data freshness indicator.

### 53. Decision: UUIDs over Auto-Increment IDs
2026-08-01 | DB-006 | Sequential IDs exposing business metrics (order count), migration issues with sharding | UUID v4, UUID v7, auto-increment, Snowflake-style IDs, ULID | Auto-increment exposes growth rate, conflicts with sharding. UUID v4 random, bad for B-tree index performance. Snowflake requires coordination service. UUID v7: time-sorted, good index performance, no coordination needed. | Index performance within 5% of auto-increment. No conflicts during sharding. Business metrics not exposed. | UUID v7 is the best ID format for new applications. Time-sorted, shard-friendly, performant. Never use UUID v4 for primary keys.

### 54. Decision: Server-Side Rendering with Next.js over Client-Side Rendering
2026-08-10 | FE-006 | Poor SEO, slow initial page load (4.2s FCP), poor Core Web Vitals | Next.js SSR, Create React App (client-only), Gatsby, Remix, Qwik | CRA: poor SEO, slow FCP. Gatsby: static-only, not suitable for dynamic app. Remix: good but smaller ecosystem. Qwik: too early. Next.js: SSR, ISR, great DX, large ecosystem. | FCP 4.2s -> 1.1s. Core Web Vitals all green. SEO traffic up 150%. | Next.js is the standard for React SSR. Use ISR for content pages, SSR for user-specific pages. Avoid getServerSideProps for data that can be cached.

### 55. Decision: Zod for Validation over Joi/Yup
2026-08-20 | API-004 | Validation code duplicated across frontend and backend, runtime type errors | Zod, Joi, Yup, io-ts, TypeScript types only | Joi backend-only. Yup good but TypeScript inference limited. io-ts powerful but complex. Zod: TypeScript-first, inferred types, works frontend + backend, small bundle. | Shared validation schemas between frontend + backend. Zero type/runtime mismatch bugs. 30% less validation code. | Zod is the standard for TypeScript validation. Share schemas between frontend and backend. Beware of Zod's pipe() for complex transformations — test thoroughly.

### 56. Decision: Incremental Static Regeneration for Product Pages
2026-09-01 | FE-007 | Product pages need near-real-time inventory + price updates | ISR (Next.js), SSR every request, full SSG rebuild, client-side fetch | Full SSG rebuild too slow (10k product pages, 30min build). SSR every request too slow (200ms each). Client-side fetch after static load (good but initial stale ISR: stale while revalidate, always fresh within cache window. | Product pages served from CDN (instant), stale-while-revalidate for freshness. Build time unchanged. | ISR is ideal for catalog/content pages. Use on-demand revalidation when inventory/prices change. Avoid ISR for user-specific pages.

### 57. Decision: PNPM over NPM/Yarn
2026-09-10 | DEVX-004 | Disk space growing (node_modules 5GB+ per project), install times slow, dependency inconsistencies | pnpm, npm, Yarn PnP, Yarn Berry | npm slow installs, no disk dedup. Yarn PnP strict mode too many compatibility issues. Yarn Berry better but migration complex. pnpm: content-addressable storage, strict, fast. | Disk usage from 5GB to 1.2GB per project. Install time 60s -> 15s. Zero phantom dependency bugs. | pnpm is the best package manager for monorepos. Strict mode catches missing dependencies. Content-addressable storage saves significant disk space.

### 58. Decision: Structured Logging with pino over Winston
2026-09-20 | OBS-005 | Logging overhead 10% of CPU, JSON parsing expensive, slow | pino, Winston, Bunyan, console.log | Winston slow (string interpolation + JSON.stringify). Bunyan unmaintained. console.log unstructured. pino: fastest Node.js logger, structured by default, child loggers, low overhead. | Logging CPU overhead from 10% to 1%. Log ingestion in Loki 3x faster. Structured queries easier. | pino is the fastest Node.js logger by a wide margin. Use child loggers for request-scoped context. Never use console.log in production.

### 59. Decision: T3 Stack for New Projects
2026-10-01 | ARCH-004 | Inconsistent tech choices across new microservices (some Express, some Fastify, some Hono) | T3 Stack (tRPC, Prisma, Next.js, Tailwind), Express + REST, Fastify + REST, Hono + REST | Express mature but slow. Fastify faster but fewer libraries. Hono Edge-compatible but young. T3: opinionated, type-safe, full-stack, great DX for CRUD services. | New services built in 1/3 the time. Consistent patterns across all services. Type safety end-to-end. | T3 stack is ideal for new CRUD-heavy services. Not suitable for compute-heavy or streaming services (use Go/Rust for those).

### 60. Decision: Database Change Data Capture for Event Bus
2026-10-15 | DB-007 | Need reliable event sourcing from database changes without dual-write problem | Debezium + Kafka Connect, dual-write in app, outbox pattern, transactional outbox | Dual-write risks inconsistency. Manual outbox requires app changes. Transactional outbox reliable but more code. Debezium captures CDC from WAL — no dual-write, no app changes. | All database changes reliably streamed to Kafka. Zero dual-write inconsistency incidents. | Debezium CDC is the most reliable way to get events from database changes. Use for search indexing, cache invalidation, analytics. Don't use for commands — use Kafka directly for commands.

### 61. Decision: AWS ECS Fargate over EKS/EKS for Container Orchestration
2026-11-01 | INFRA-002 | K8s operation overhead too high for 12-person team | ECS Fargate, EKS (K8s managed), EKS self-managed, Nomad, Lambda | EKS managed: 3 FTE cluster maintenance overhead. EKS self-managed: 5 FTE. Nomad: smaller ecosystem. Lambda: cold starts, 15min timeout. ECS Fargate: no cluster management, serverless containers. | Zero cluster management overhead. Deploy times from 10m (K8s) to 2m (ECS). Cost 20% lower than EKS. | ECS Fargate is the best option for teams under 20 engineers. EKS only makes sense with dedicated infrastructure team. Use Copilot CLI for ECS deployment.

### 62. Decision: Design Tokens as Code over Design Tool Export
2026-11-15 | FE-008 | Design tokens manually copied from Figma, always out of sync | Design tokens as code (Style Dictionary), Figma API export, manually copy, shared Figma plugin | Manual copy: always stale. Figma export via plugin: good but requires designers to trigger. Design tokens as code: Style Dictionary generates CSS, TS, Swift, Kotlin from a single source of truth. | Token sync automated. Platform builds from single token source. Design audits pass 100%. | Design tokens as code with Style Dictionary is the right approach. Automate token generation in CI. Designers edit tokens via PR, creating audit trail.

### 63. Decision: Dependency Injection — No DI Framework over NestJS/Inversify
2026-12-01 | ARCH-005 | DI framework overhead for Node.js microservices not worth the complexity | No DI (manual), NestJS, Inversify, TSyringe, Awilix | NestJS opinionated, heavy. Inversify verbose, decorator-heavy. TSyringe simple but adds abstraction. Awilix good but unfamiliar. Manual DI: factory functions + dependency modules. Simple, no magic. | Zero DI-related bugs or debugging time. Code is explicit about dependencies. Easy to test (just pass mocks). | DI frameworks solve problems you don't have in Node.js. Manual DI with factory functions is simpler, more explicit, and easier to debug. Use it for 2 years before considering a framework.

---

## Patterns That Worked

| Pattern | Context | Why It Worked |
|---------|---------|---------------|
| Feature flags in every PR | Gradual rollout, A/B testing, kill switch | Decoupled deploy from release |
| Integration-test-heavy strategy | Finding regressions early | Caught 90% of bugs before staging |
| ADRs in repository | Decision documentation | Always up to date, reviewed in PRs |
| Monorepo with Turborepo | Sharing code across teams | Easy refactoring, atomic commits |
| OpenTelemetry instrumentation | Observability | Backend-agnostic, no lock-in |
| Route-level error boundaries | React error handling | Full page crashes eliminated |
| Cursor-based pagination | API list endpoints | Consistent results, stable performance |
| BFF auth pattern | Token security | Zero token theft incidents |
| Burn rate alerts | Incident detection | 90% fewer false positives |
| Plop scaffolding | New feature creation | 30s vs 15m, zero missing files |
| Playwright for E2E | Cross-browser testing | 15% flakiness -> 1% |
| Unstyled component libraries (Radix) | Design system | Full control + accessibility built-in |

## Patterns That Failed

| Pattern | Context | Why It Failed |
|---------|---------|---------------|
| Recoil for state management | Frontend state | Experimental API, concurrency bugs |
| Manual dependency updates | 200+ deps, monorepo | Consumed 20% of dev time |
| Premature microservices | Team of 5 | Massive overhead, no benefit |
| Testing pyramid approach | Test suite confidence | Too many brittle unit tests |
| Wiki for docs | Documentation | Instant staleness, no ownership |
| Offset-based pagination | Large list endpoints | Slow on deep pages, inconsistent |
| Static threshold alerts | Monitoring | 100+ noisy alerts/day, missed gradual issues |
| Cypress for E2E | Cross-browser testing | Chromium-only, flaky, slow CI |
| .env files for secrets | Environment configuration | Committed to repo 3 times |
| MUI for design system | React components | Heavy bundle, customization complexity |
| Schema stitching | GraphQL gateway | Manual resolver wiring, doesn't scale past 5 services |
| pg_dump for backups | Database backups | 4h backup time, no PITR support |

## Performance Learnings

| What Was Slow | What Fixed It | Improvement |
|---------------|---------------|-------------|
| DB queries scanning soft-deleted rows | Partial indexes | 800ms -> 45ms |
| Large image uploads (5MB avg) | Multi-size + WebP pipeline | 4.2s LCP -> 1.1s |
| Tailwind CSS build in CI | esbuild CSS processor | 45s -> 5s |
| No cache layer | Redis + CDN | p95 2s -> 250ms |
| Jest test suite | Vitest migration | 12m -> 4m |
| Offset pagination on 1M+ rows | Cursor-based pagination | 3s -> 50ms on page 100 |
| JSON parsing in gRPC | Protobuf serialization | 5x faster deserialization |
| Prettier + ESLint on 200+ files | Biome unified tool | 12s -> 1.2s |
| pg_dump 500GB database | WAL-G incremental backups | 4h -> 15min |
| MUI bundle size (120KB) | Radix UI migration | 120KB -> 30KB |
| ELK log storage costs | Loki + Grafana | 80% cost reduction |

## Security Learnings

| Vulnerability | Fix | Detection Method |
|---------------|-----|------------------|
| No rate limiting on auth endpoints | Token bucket + sliding window | Load test found 100% CPU at 5k req/s |
| Missing idempotency keys on payments | Required key on all mutations | Incident: 47 users double-charged |
| No schema validation on Kafka events | Schema Registry enforcement | Incident: 45m search outage |
| Auth tokens in client logs | PII scrubbing in log pipeline | Security audit |
| No CSRF on mutation endpoints | Double-submit cookie pattern | Penetration test |
| .env files committed to repo (3x) | 1Password CLI integration | Code review caught third occurrence |
| Access tokens exposed to browser JS | BFF pattern with HTTP-only cookies | Architecture review |
| No webhook HMAC signatures | HMAC-SHA256 on all outgoing webhooks | Security audit |
| Stored XSS via user name in email templates | Input sanitization + Handlebars auto-escape | Penetration test |
| Cross-tenant data via shared cache | Tenant-scoped Redis keys | Bug report from customer |

## Migration Learnings

| Migration | What Went Wrong | What Went Right | Lessons |
|-----------|-----------------|-----------------|---------|
| JS to TypeScript | Initial `any` overload | Per-package migration plan | Use `ts-migrate`, allow `any` debt, pay down gradually |
| Jest to Vitest | ESM module resolution | Jest-compatible API | Enable `vi` globals, avoid `jest.` calls |
| Recoil to Zustand | Migration middleware complexity | Simple store-per-domain pattern | Zustand's simplicity made migration trivial |
| Monolith to Microservices | Distributed monolith anti-pattern | Clear bounded contexts | Extract by team boundary, not technical boundary |
| DataDog to Grafana | Dashboard migration effort | OTel made backend swap possible | Use OpenTelemetry from day one |
| Elasticsearch to Meilisearch | Index format incompatible | Schema re-index with zero downtime | Run old + new in parallel, validate results |
| Stripe API version upgrade | 3 breaking endpoint changes | Shadow traffic caught 2 mismatches | Test mode + shadow traffic is safest pattern |
| PostgreSQL 15 to 16 | Logical replication setup complexity | 2-minute cutover, zero data loss | Always test rollback on staging |
| Material UI to Radix | Component-by-component migration needed | No regressions with visual regression tests | Visual regression tests are mandatory for UI migrations |
| Prettier+ESLint to Biome | Biome missing 3 ESLint plugins | 10x speedup, kept ESLint for 3 rules | Don't wait for 100% parity; 90% is good enough for migration |

---

*Last updated: 2025-12-01*
