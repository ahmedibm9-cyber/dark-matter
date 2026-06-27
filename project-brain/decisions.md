# Architecture Decision Records

## Decision-Making Process

### How Decisions Are Made

1. **Proposal**: Anyone on the team can propose a decision by writing a draft ADR and submitting it as a pull request to this file.
2. **Review**: The ADR is reviewed by at least two team members with relevant expertise. The review window is a minimum of 3 business days unless the decision is time-sensitive.
3. **Approval**: Decision is approved by the engineering lead or architect. For decisions with cross-team impact, a broader RFC process is used (see below).
4. **Status Update**: The ADR status is updated to Accepted, and a link to the implementation PR is added.
5. **Implementation**: The decision is implemented following the guidance in the ADR. If significant deviations arise during implementation, the ADR must be updated or a new ADR must supersede it.

### RFC Process (Cross-Team Decisions)

For decisions affecting multiple teams or with significant architectural impact:

1. RFC document created in `docs/rfcs/` with the format `RFC-YYYY-MM-DD-title.md`
2. RFC announced in #architecture Slack channel with a 1-week comment period
3. RFC reviewed in the bi-weekly architecture review meeting
4. Decision documented as ADR with link to RFC discussion

### How to Propose New Decisions

1. Copy the ADR template below
2. Assign the next available ADR ID (check this file for the highest used ID)
3. Create a branch and PR adding the ADR to this file
4. Set status to "Proposed"
5. Notify the team in #architecture Slack channel
6. Address feedback in PR comments
7. Once approved, update status to "Accepted"

### ADR Template

```markdown
## ADR-{ID}: {Title}

- **Date**: {YYYY-MM-DD}
- **Status**: {Proposed | Accepted | Deprecated | Superseded}
- **Supersedes**: {ADR-ID if applicable}
- **Superseded by**: {ADR-ID if applicable}
- **Decision Maker**: {Name}
- **Domain**: {Architecture | Database | API | UI | Security | Process}

### Context

{What is the issue motivating this decision? What constraints exist? What is the current state of the system?}

### Decision

{What is the change being proposed or implemented? Be specific and concrete.}

### Consequences

{What are the trade-offs? What becomes easier? What becomes harder? What risks are introduced?}

### Alternatives Considered

{What other options were evaluated? Why were they rejected? Include pros/cons for each.}

### Implementation Notes

{Link to implementation PRs, affected files, migration guides. Any follow-up work required.}
```

---

## Decisions by Domain

### Architecture

## ADR-001: Use Monorepo with Turborepo

- **Date**: 2024-09-15
- **Status**: Accepted
- **Decision Maker**: Engineering Lead
- **Domain**: Architecture

### Context

The project consists of a Next.js frontend, Express API backend, shared TypeScript types, and a shared UI component library. These were previously in separate repositories, causing coordination overhead, version mismatch issues, and slow cross-repo refactoring.

### Decision

Adopt a single monorepo managed by Turborepo with npm workspaces. All packages live under `packages/`:
- `packages/web` — Next.js frontend
- `packages/api` — Express API
- `packages/shared` — Shared TypeScript types and utilities
- `packages/ui` — React component library (consumed by web)

### Consequences

- Positive: Single version for all dependencies, atomic cross-package commits, shared build cache
- Positive: Simplified CI (one pipeline, one build)
- Negative: Larger clone size, longer initial install time
- Negative: Requires team discipline to maintain package boundaries

### Alternatives Considered

- **Separate repos**: Rejected due to version sync overhead and slow refactoring
- **Single repo with no workspaces**: Rejected due to lack of package isolation

### Implementation Notes

PR: https://github.com/ourcompany/app/pull/1
Migration guide: `docs/monorepo-migration.md`

---

## ADR-002: React with Next.js (App Router)

- **Date**: 2024-10-01
- **Status**: Accepted
- **Decision Maker**: Frontend Lead
- **Domain**: Architecture

### Context

The existing frontend was a Create React App (CRA) application with client-side rendering. Performance issues (slow FCP, poor SEO), routing complexity, and lack of server-side rendering capabilities drove the need for a modern framework.

### Decision

Migrate to Next.js 14 with the App Router. Use React Server Components for data-fetching pages and client components for interactive features. Deploy as a Docker container on EKS (not Vercel) to maintain infrastructure consistency.

### Consequences

- Positive: Server-side rendering improves FCP by 60%, SEO is now possible
- Positive: App Router provides nested layouts, loading states, error boundaries
- Positive: Server Components reduce client bundle size
- Negative: Learning curve for Server Components vs Client Components
- Negative: Cannot use Vercel's optimized deployment; must manage our own infrastructure
- Negative: Some npm packages are not yet compatible with React 18 Server Components

### Alternatives Considered

- **Remix**: Rejected due to smaller ecosystem and team familiarity with Next.js
- **Vite + React Router**: Rejected — no SSR, would need separate solution
- **Stay with CRA**: Rejected — CRA is effectively unmaintained

### Implementation Notes

PR: https://github.com/ourcompany/app/pull/45
Migration strategy: Incremental — pages migrated one at a time using Next.js rewrites

---

## ADR-003: Event-Driven Architecture for Cross-Service Communication

- **Date**: 2025-02-10
- **Status**: Accepted
- **Decision Maker**: Engineering Lead
- **Domain**: Architecture

### Context

As the monolith grew, synchronous HTTP calls between internal modules created tight coupling, cascading failures, and performance bottlenecks. The billing module calling the notification module directly during payment processing is a primary example — if notifications are slow, payments are slow.

### Decision

Adopt an event-driven architecture using Redis Pub/Sub for internal events and Kafka for domain events that need persistence and replay. Events are defined as typed TypeScript interfaces in the `shared` package.

- Internal events (Redis Pub/Sub): Cache invalidation, user status change, ephemeral notifications
- Domain events (Kafka): Order placed, payment completed, user registered, report generated

### Consequences

- Positive: Decoupled services can evolve independently
- Positive: Failed consumers don't block producers (async fire-and-forget)
- Positive: Event log enables auditing and replay
- Negative: Eventual consistency — consumers may see stale data
- Negative: Debugging async flows is harder than sync calls
- Negative: Operational complexity of running Redis + Kafka

### Alternatives Considered

- **RabbitMQ**: Rejected — Kafka has better replay capabilities for audit logging
- **gRPC bidirectional streaming**: Rejected — more complex, overkill for current scale
- **AWS SQS/SNS**: Rejected — vendor lock-in, harder to test locally

### Implementation Notes

PR: https://github.com/ourcompany/app/pull/234
Event catalog: `packages/shared/src/events/`

---

## ADR-004: Feature Flags via LaunchDarkly

- **Date**: 2025-04-20
- **Status**: Accepted
- **Decision Maker**: Engineering Lead
- **Domain**: Architecture

### Context

Deploying unfinished features to production required long-lived feature branches, causing merge conflicts, integration issues, and delayed releases. We needed a way to deploy code continuously while controlling feature visibility.

### Decision

Adopt LaunchDarkly for feature flag management. All new features are developed behind feature flags. Flags are evaluated server-side (API) and passed to the frontend as initial props.

### Consequences

- Positive: Continuous deployment to production with zero-downtime releases
- Positive: Canary releases and targeted rollouts (by user, org, plan)
- Positive: Kill switches for problematic features without redeployment
- Negative: Ongoing cost (LaunchDarkly is not free)
- Negative: Flag management debt if flags are not cleaned up after release
- Negative: Added code complexity from conditional branching

### Alternatives Considered

- **Self-hosted Unleash**: Rejected — additional operational overhead
- **Environment variables**: Rejected — require redeployment to change
- **Database flags**: Rejected — latency, no targeting capabilities

### Implementation Notes

PR: https://github.com/ourcompany/app/pull/312
Flag cleanup policy: Flags must be removed within 2 sprints of full rollout

---

### Database

## ADR-005: PostgreSQL as Primary Database

- **Date**: 2024-08-01
- **Status**: Accepted
- **Decision Maker**: Engineering Lead
- **Domain**: Database

### Context

The initial prototype used MongoDB for schema flexibility. As the data model matured, the lack of relational integrity, ad-hoc querying challenges, and transaction support became bottlenecks.

### Decision

Migrate from MongoDB to PostgreSQL 15 as the primary database. Use Prisma as the ORM for type-safe database access.

### Consequences

- Positive: Strong schema enforcement, referential integrity, ACID transactions
- Positive: Rich querying capabilities (JSONB, full-text search, window functions)
- Positive: Prisma provides auto-generated TypeScript types
- Negative: Schema changes require migrations (less flexible than MongoDB)
- Negative: Migration from MongoDB required significant data transformation
- Negative: Prisma has some performance limitations on complex queries (use raw SQL when needed)

### Alternatives Considered

- **MySQL 8**: Rejected — PostgreSQL has better JSON support, extensions, and performance characteristics
- **CockroachDB**: Considered for future multi-region, overkill for current scale
- **Stay with MongoDB**: Rejected — transaction support was insufficient for billing workflows

### Implementation Notes

PR: https://github.com/ourcompany/app/pull/2
Migration guide: `docs/mongodb-to-postgresql-migration.md`

---

## ADR-006: Database Migrations with Flyway

- **Date**: 2024-08-15
- **Status**: Accepted
- **Decision Maker**: Backend Lead
- **Domain**: Database

### Context

Database schema changes were applied manually, leading to drift between environments and incidents from unapplied or incorrectly applied migrations.

### Decision

Adopt Flyway for database migrations. Migration scripts live in `packages/api/src/main/resources/db/migration/` and are automatically applied during deployment.

### Consequences

- Positive: Version-controlled, repeatable, auditable schema changes
- Positive: Flyway checksums detect tampered migration scripts
- Positive: Works with the existing Java-based data pipeline as well as Node.js API
- Negative: Adds a step to the deployment process
- Negative: Rollbacks require explicit undo scripts

### Alternatives Considered

- **Prisma Migrate**: Rejected — team wanted database-agnostic migration tool; Prisma Migrate has had reliability issues
- **Knex.js migrations**: Rejected — JavaScript-based, no checksum verification
- **Liquibase**: Rejected — XML/JSON format is verbose; Flyway is simpler

### Implementation Notes

PR: https://github.com/ourcompany/app/pull/15
Naming convention: V{number}__{description}.sql

---

## ADR-007: Redis for Caching and Session Storage

- **Date**: 2024-09-01
- **Status**: Accepted
- **Decision Maker**: Backend Lead
- **Domain**: Database

### Context

The application needed a fast, shared cache for API responses, database query results, and user sessions. In-memory caching per-instance was causing inconsistency behind the load balancer.

### Decision

Deploy ElastiCache Redis (cluster mode) for shared caching and session storage. Redis is accessed via ioredis with a connection pool.

### Consequences

- Positive: Consistent cache across all application instances
- Positive: Sub-millisecond read latency for cached data
- Positive: Session persistence across pod restarts
- Negative: Additional infrastructure cost and operational complexity
- Negative: Cache invalidation requires careful design
- Negative: Network round-trip adds ~1ms compared to in-memory cache

### Alternatives Considered

- **Memcached**: Rejected — no data persistence, no pub/sub, no data structures
- **In-memory cache**: Rejected — inconsistent across instances, lost on restart
- **DynamoDB DAX**: Rejected — vendor lock-in, higher cost

### Implementation Notes

PR: https://github.com/ourcompany/app/pull/67
Cache key naming convention: `{service}:{entity}:{id}:{field}`

---

### API

## ADR-008: RESTful API Design

- **Date**: 2024-08-01
- **Status**: Accepted
- **Decision Maker**: Backend Lead
- **Domain**: API

### Context

The initial API used a mix of REST, RPC-style endpoints, and GraphQL (Apollo Server). This inconsistency confused API consumers and increased maintenance burden.

### Decision

Standardize on RESTful API design with JSON request/response bodies. Use Express with a layered architecture (routes -> controllers -> services -> repositories). Resource naming follows the plural convention: `/api/v1/users`, `/api/v1/reports`.

### Consequences

- Positive: Familiar, predictable API surface
- Positive: Wide ecosystem of tooling and client libraries
- Positive: HTTP caching, status codes, and methods are well-understood
- Negative: Over-fetching and under-fetching common (addressed by including sparse fieldsets)
- Negative: Version management required for breaking changes

### Alternatives Considered

- **GraphQL only**: Rejected — complexity for simple CRUD operations; caching is harder
- **gRPC**: Rejected — needs HTTP/2 everywhere; harder for frontend consumption
- **Mixed REST + GraphQL**: Rejected — inconsistent; API consumers confused

### Implementation Notes

API documentation: https://api.ourcompany.com/docs (OpenAPI 3.1)
Postman collection: `docs/api/postman-collection.json`

---

## ADR-009: API Versioning via URL Path

- **Date**: 2025-03-01
- **Status**: Proposed
- **Decision Maker**: Backend Lead
- **Domain**: API

### Context

The current API has no versioning strategy. All endpoints are at `/api/v1/`. As we need to make breaking changes, we need a mechanism to support multiple API versions simultaneously.

### Decision

Use URL path versioning (`/api/v1/`, `/api/v2/`) with a minimum support window of 6 months for deprecated versions. Version deprecation communicated via the `Sunset` HTTP header and documented in the changelog.

### Consequences

- Positive: Clear, explicit version selection
- Positive: Easy to route in the load balancer and monitor usage per version
- Positive: Works well with infrastructure caching (different URLs = different cache keys)
- Negative: URL pollution — every endpoint carries version prefix
- Negative: Encourages copy-paste version maintenance instead of careful API design

### Alternatives Considered

- **Header-based versioning** (Accept header): Rejected — harder to test, less visible in logs
- **Query parameter versioning** (`?v=2`): Rejected — cached as same URL by some proxies
- **No versioning (always backward compatible)**: Rejected — impossible to evolve API

### Implementation Notes

Implementation PR: TBD
Migration guide: TBD

---

### UI

## ADR-010: Tailwind CSS for Styling

- **Date**: 2024-10-15
- **Status**: Accepted
- **Decision Maker**: Frontend Lead
- **Domain**: UI

### Context

The existing CSS was a mess — a single 4,500-line stylesheet with 200+ `!important` declarations, no naming convention, and no design tokens. Adding new styles was risky and slow.

### Decision

Adopt Tailwind CSS v3 with a custom design token configuration. All colors, spacing, typography, and shadows are defined in `tailwind.config.js` as design tokens. No custom CSS is written unless absolutely necessary (custom animations, complex responsive layouts).

### Consequences

- Positive: Rapid prototyping without context-switching between HTML and CSS files
- Positive: Zero dead CSS via PurgeCSS (average bundle: 12KB gzipped for utilities)
- Positive: Design token system enforced through configuration
- Negative: HTML can become verbose with many utility classes
- Negative: Learning curve for developers accustomed to semantic CSS
- Negative: Component abstractions needed to avoid repeating utility classes

### Alternatives Considered

- **CSS Modules**: Rejected — no built-in design token system, dead CSS possible
- **Styled Components**: Rejected — runtime cost, larger bundle size, harder theming
- **SCSS with BEM**: Rejected — manual naming, no design token enforcement
- **Vanilla CSS**: Rejected — unmaintainable at scale (proven by existing codebase)

### Implementation Notes

PR: https://github.com/ourcompany/app/pull/89
Component library migration: In progress (40% of components migrated to Tailwind)

---

## ADR-011: Storybook for Component Development

- **Date**: 2024-11-01
- **Status**: Accepted
- **Decision Maker**: Frontend Lead
- **Domain**: UI

### Context

UI components were developed directly inside pages, making it impossible to test them in isolation, review them visually, or document them for reuse.

### Decision

Adopt Storybook 7 with the React Vite builder. Every component in the `ui` package has a corresponding `.stories.tsx` file with stories for all variants, states, and viewports. Stories are published to Chromatic for visual regression testing.

### Consequences

- Positive: Components can be developed and tested in isolation
- Positive: Visual regression testing catches unintended changes
- Positive: Living documentation for the component library
- Negative: Additional maintenance — stories must be updated alongside components
- Negative: Slower CI (Chromatic build step)

### Alternatives Considered

- **Pattern Lab**: Rejected — less React-native ecosystem support
- **Docz**: Rejected — smaller community, less maintained
- **No component catalog**: Rejected — proven failure in current codebase

### Implementation Notes

PR: https://github.com/ourcompany/app/pull/102
Storybook URL: https://storybook.ourcompany.com (private, SSO-protected)

---

### Security

## ADR-012: Auth0 for Identity and Access Management

- **Date**: 2024-08-20
- **Status**: Accepted
- **Decision Maker**: Security Lead
- **Domain**: Security

### Context

We needed a secure, compliant authentication system supporting email/password, social login (Google, Microsoft), and enterprise SSO (SAML). Building this in-house would take months and require significant security expertise.

### Decision

Adopt Auth0 as the identity provider. Configured with:
- Database connection for email/password
- Google and Microsoft social connections
- SAML connections for enterprise tenants
- RS256 JWTs with 15-minute access token expiry
- MFA enforcement for admin roles

### Consequences

- Positive: SOC 2 compliant identity management out of the box
- Positive: Built-in MFA, anomaly detection, breached password detection
- Positive: SSO integration with major providers
- Negative: Ongoing cost (approximately $2,000/month at current user count)
- Negative: Vendor dependency — migrating away would be significant work
- Negative: Rate limits on Auth0 Management API (can cause delays in bulk operations)

### Alternatives Considered

- **AWS Cognito**: Rejected — significantly more complex to configure, limited social login support, more expensive at scale
- **Firebase Authentication**: Rejected — Google vendor lock-in, limited enterprise SSO
- **Self-built with Passport.js**: Rejected — would take months to reach parity, security audit required
- **Okta**: Rejected — more expensive, overkill for current needs

### Implementation Notes

PR: https://github.com/ourcompany/app/pull/3
Auth0 tenant: ourcompany.us.auth0.com
Configuration docs: `docs/auth/auth0-configuration.md`

---

## ADR-013: Secrets in AWS Secrets Manager

- **Date**: 2024-09-10
- **Status**: Accepted
- **Decision Maker**: Security Lead
- **Domain**: Security

### Context

Secrets were stored in environment variables in deployment configuration files and, in some cases, committed to git. This is a security risk and a compliance violation.

### Decision

All secrets (database credentials, API keys, JWT secrets, encryption keys) stored in AWS Secrets Manager. Kubernetes pods access secrets via the External Secrets Operator, which syncs Secrets Manager entries to Kubernetes secrets at runtime.

### Consequences

- Positive: Secrets are encrypted at rest and in transit
- Positive: Automatic rotation for supported secret types (RDS credentials)
- Positive: Fine-grained IAM access control for secret access
- Negative: Added latency on pod startup (secrets fetched at initialization)
- Negative: Additional cost ($0.40/secret/month + API call costs)
- Negative: Local development requires either mock secrets or access to AWS

### Alternatives Considered

- **HashiCorp Vault**: Rejected — additional operational overhead to manage
- **Git-crypt / SOPS**: Rejected — secrets still in repository, even if encrypted
- **Kubernetes Secrets only**: Rejected — secrets stored in etcd, less secure, no rotation

### Implementation Notes

PR: https://github.com/ourcompany/app/pull/78
Secret naming convention: `{environment}/{service}/{secret-name}`

---

### Process

## ADR-014: Trunk-Based Development

- **Date**: 2024-10-01
- **Status**: Accepted
- **Decision Maker**: Engineering Lead
- **Domain**: Process

### Context

The team used GitFlow with long-lived feature branches. Merges were painful, integration issues were discovered late, and releases required complex branching coordination.

### Decision

Adopt trunk-based development with short-lived feature branches (max 2 days). Feature toggles (LaunchDarkly) protect incomplete features. Branches are merged to `main` via squash-merge pull requests with linear history.

### Consequences

- Positive: Continuous integration — code is merged and tested multiple times per day
- Positive: No merge hell — branches are short-lived
- Positive: Simple, linear git history
- Negative: Requires feature flag discipline — incomplete features must be hidden
- Negative: Some developers prefer longer feature branches for complex work
- Negative: Squash merges lose intermediate commit history

### Alternatives Considered

- **GitFlow**: Rejected — too complex for a single-team project, release overhead
- **GitHub Flow**: Similar to trunk-based; adopted with the addition of feature flags
- **Forking workflow**: Rejected — unnecessary for a single-team project

### Implementation Notes

PR: N/A (process change documented in CONTRIBUTING.md)
Feature flag policy: `docs/feature-flags.md`

---

## ADR-015: Conventional Commits

- **Date**: 2024-10-01
- **Status**: Accepted
- **Decision Maker**: Engineering Lead
- **Domain**: Process

### Context

Commit messages were inconsistent, making changelog generation impossible, release notes manual, and historical understanding difficult.

### Decision

Adopt Conventional Commits specification (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `perf:`, `ci:`, `build:`, `style:`). Commit messages are enforced via a commitlint hook. Changelogs are auto-generated from commit history.

### Consequences

- Positive: Auto-generated, accurate changelogs
- Positive: Semantic version bumps can be automated
- Positive: Clear, standardized commit history
- Negative: Learning curve for the team
- Negative: Commit message format errors cause CI failures until fixed
- Negative: Some commits don't fit neatly into a single type

### Alternatives Considered

- **No convention**: Rejected — chaotic commit history as demonstrated
- **Angular commit convention**: Very similar; adopted as the base for our convention

### Implementation Notes

PR: https://github.com/ourcompany/app/pull/103
Configuration: `commitlint.config.js` in repository root

---

## Superseded and Deprecated Decisions

## ADR-001a: Use Yarn Workspaces (Superseded)

- **Date**: 2024-09-15
- **Status**: Superseded by ADR-001 (Turborepo)
- **Domain**: Architecture

### Context

Original decision was Yarn Workspaces without Turborepo.

### Decision

Use Yarn Workspaces for monorepo management.

### Why Superseded

Yarn Workspaces lacked build caching, task orchestration, and pipeline capabilities that Turborepo provides. Migrated to Turborepo for better DX and faster CI.

---

## ADR-002a: Pages Router (Deprecated)

- **Date**: 2024-10-01
- **Status**: Deprecated by ADR-002 (App Router)
- **Domain**: Architecture

### Context

Original migration to Next.js used the Pages Router.

### Decision

Use Next.js Pages Router for initial migration.

### Why Deprecated

App Router provides better performance, nested layouts, and Server Components. All new pages use App Router. Existing Pages Router pages are migrated incrementally.

---

## ADR-008a: API Authentication via Session Cookies (Superseded)

- **Date**: 2024-08-01
- **Status**: Superseded
- **Domain**: API

### Context

Initial API authentication used session cookies with server-side sessions.

### Decision

Session cookie-based authentication for API endpoints.

### Why Superseded

Replaced with JWT bearer tokens (ADR-012) for better mobile app support, statelessness, and third-party API access.
