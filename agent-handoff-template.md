# Agent Handoff Template

> Read this file FIRST before doing anything else.

## Instructions for Incoming Agent

1. **Read this entire file before touching any code.**
2. If any section references a file, read that file next.
3. If there are active tasks, start with the highest-priority item in `ACTIVE TASKS`.
4. Check `WARNINGS` to avoid known pitfalls.
5. When your session is complete, fill out a fresh copy of this template and leave it in the project root.

---

## CURRENT STATUS

<!-- Provide a one-paragraph summary of the current state of the project/sprint. Include what phase of development is active, any major blockers, and the overall health of the codebase. -->

Replace this with a concise paragraph. Example:

> The auth migration sprint is in week 2 of 3. The new OAuth2 flow is implemented but the token refresh logic has a race condition under investigation. The payment microservice is stable. Search indexing incidents from last month have been resolved with Schema Registry enforcement. No critical bugs in production.

---

## ACTIVE TASKS

| ID | Task | Priority | Status | Blockers | Next Action |
|----|------|----------|--------|----------|-------------|
| T-001 | Implement token refresh race condition fix | P0 | In Progress | Need to reproduce consistently | Add logging around refresh flow to capture race window |
| T-002 | Migrate user search to new indexer | P1 | Blocked | Awaiting DevOps for Kafka cluster upgrade | Ping DevOps in standup |
| T-003 | Update API docs for v2 endpoints | P2 | Not Started | None | Write endpoint specs |
| T-004 | Dependency audit for CVE-2025-1234 | P0 | Complete | N/A | N/A |
| T-005 | Refactor checkout state machine | P2 | In Progress | PR awaiting review | Address PR comments |

---

## COMPLETED TASKS

<!-- List everything accomplished during this session. Include as much context as possible. -->

- [T-004] Dependency audit for CVE-2025-1234 — patched express and lodash across all packages
- [T-006] Fixed Sentry source map upload in CI pipeline
- [T-007] Added integration test for payment idempotency key flow
- [T-008] Updated README with new environment variable documentation
- Investigated and partially diagnosed token refresh race condition (T-001)
- Reviewed PR #892 (checkout state machine refactor) — left 3 comments

---

## KNOWN RISKS

<!-- Risks are events that could cause problems. Use this format: Likelihood (H/M/L) + Impact (H/M/L) + Description -->

| ID | Risk | Likelihood | Impact | Description |
|----|------|------------|--------|-------------|
| R-001 | Kafka cluster upgrade may cause consumer lag | M | H | DevOps upgrading Kafka on Thursday. If consumers aren't paused, we may lose events. |
| R-002 | Deprecated API endpoint removal in v3 | L | H | Some mobile clients still on v2. Removing v2 endpoints without migration period breaks them. |
| R-003 | New developer onboarding without docs | M | M | Two new engineers joining next week. Current onboarding docs are 3 months stale. |

---

## KNOWN BUGS

<!-- Bugs discovered this session that are NOT yet in the issue tracker or are newly discovered. -->

| ID | Bug | Severity | Status | Notes |
|----|-----|----------|--------|-------|
| B-001 | Token refresh returns 500 when access token expired > 24h ago | S2 | Diagnosed, not fixed | Root cause: expired refresh token not handled gracefully. Fix: check refresh token expiry first. |
| B-002 | Search results missing when filtering by date range on leap years | S4 | Open | Edge case in date parsing library. Low priority. |
| B-003 | Admin dashboard charts not rendering in Safari 15 | S3 | Fix in progress | Safari 15 lacks ResizeObserver support. Polyfill added. |

---

## CURRENT PRIORITIES

<!-- Ordered list of what should be worked on next, highest priority first. -->

1. **Fix token refresh race condition (T-001)** — P0, actively blocking users. Reproduction is the key challenge; add more granular logging.
2. **Unblock search indexer migration (T-002)** — Ping DevOps about Kafka upgrade. Consider alternative: can we index to a temporary Elasticsearch instance?
3. **Merge checkout state machine PR #892** — Address PR comments, get it merged this week.
4. **Write v3 API migration guide** — Need to notify mobile team about endpoint deprecations.
5. **Update onboarding docs** — Before new engineers arrive next week.

---

## RECENT CHANGES

### Files Modified
- `packages/api/src/auth/refreshToken.ts` — Added logging for race condition debugging
- `packages/api/src/middleware/rateLimiter.ts` — Fixed token bucket reset logic
- `packages/web/src/components/CheckoutWizard.tsx` — Partial refactor (PR #892)
- `packages/shared/src/utils/date.ts` — Fixed leap year date parsing (B-002)
- `packages/api/package.json` — Updated express to 4.20.0, lodash to 4.17.21
- `docs/API.md` — Added v2 deprecation notice headers

### Branches
- `fix/token-refresh-race` — Active, off of `main`
- `feat/search-indexer-v2` — Blocked, off of `main`
- `refactor/checkout-state-machine` — PR #892, awaiting review

### Commits (Recent)
```
abc1234 - Fix leap year date parsing in date utils
def5678 - Add logging for token refresh flow
ghi9012 - Update express and lodash for CVE-2025-1234
jkl3456 - Add integration test for payment idempotency
```

---

## ARCHITECTURE NOTES

<!-- Architectural decisions, contexts, and constraints the next agent needs to understand. -->

### Current Architecture State

- **Frontend**: React 18 + Next.js 14 + Tailwind CSS + React Query + Zustand
- **Backend**: Node.js 20 + Express + TypeScript, microservices (12 services)
- **Database**: PostgreSQL 16 with Sqitch migrations (100+ migrations deployed)
- **Event Bus**: Kafka with Avro Schema Registry (self-hosted)
- **Cache**: Redis (self-hosted) + CDN (Cloudflare)
- **Auth**: Auth0 with JWT + OAuth2
- **Observability**: OpenTelemetry -> Grafana (Tempo + Mimir + Loki)
- **Error Tracking**: Sentry (self-hosted)
- **CI/CD**: GitHub Actions

### Key Architectural Decisions

1. **Microservices extracted from modular monolith** — Services split by team boundary, not technical layer. The `payment` and `order` services are the oldest and most stable.
2. **GraphQL gateway** sits in front of microservices for external consumption. Internal services communicate via gRPC.
3. **Event sourcing with Kafka** for order workflow. Order state machine is defined in XState and stored in `packages/order-machine/`.
4. **Soft deletes everywhere** with partial indexes (`WHERE deleted_at IS NULL`). This is non-negotiable.

### Pending Architectural Changes

- **v3 API** will remove all deprecated v2 endpoints. Migrate all mobile clients first.
- **Search indexer v2** moves from Elasticsearch to Meilisearch for better developer experience.
- **Kafka upgrade** from 3.5 to 3.8 planned this quarter.

---

## WARNINGS

<!-- Pitfalls, gotchas, and things to be careful about. Include common mistakes. -->

### Critical

- **NEVER commit database migration files without both `deploy` and `revert` scripts.** Sqitch requires both.
- **DO NOT deploy schema changes without consumer validation.** Kafka Schema Registry enforcement catches this, but always verify both producer and consumer schemas.
- **ALWAYS include idempotency keys on payment mutations.** Missing idempotency key caused a production incident with 47 double-charged users.
- **NEVER run database migrations against production directly.** Always use CI pipeline with approval gate.

### Important

- **Rate limiting is enforced per-IP AND per-user.** Don't bypass it in dev/test. If you need to disable for testing, use the `X-Disable-RateLimit: <secret>` header (see 1Password).
- **Sentry self-hosted requires regular maintenance.** Check disk space weekly. The cleanup cron job is at `/etc/sentry/cleanup.sh`.
- **Feature flags should be cleaned up after rollout.** Add a `flagged-cleanup` label to the rollout issue and delete the flag code when the issue is closed.
- **Build for production requires `--turbo` flag.** Without it, builds take 3x longer.

### Common Pitfalls

- Forgetting to run `pnpm install` after switching branches — dependency changes between branches.
- Using `console.log` in production code — Sentry captures too many unnecessary events.
- Forgetting partial indexes on new tables with soft deletes.
- Not running `pnpm lint:types` before pushing — CI will fail anyway, save the round trip.

---

## CONTEXT FILES

<!-- Files the next agent should read first, before doing any work. Include why each is important. -->

| File | Why Read It |
|------|-------------|
| `docs/ARCHITECTURE.md` | System architecture overview and service boundaries |
| `docs/ADRS/ADR-014-microservices.md` | Rationale for service boundaries and why they exist |
| `packages/order-machine/src/order.machine.ts` | Current XState order state machine definition |
| `packages/api/src/auth/refreshToken.ts` | Token refresh implementation (active bug location) |
| `packages/api/src/middleware/rateLimiter.ts` | Rate limiting implementation (recently changed) |
| `packages/shared/src/utils/date.ts` | Date utility with leap year fix |
| `docs/API.md` | API documentation with v2 deprecation notices |
| `.github/workflows/ci.yml` | CI pipeline configuration |
| `ops/grafana/dashboards/` | Observability dashboards for debugging |
| `docs/engineering-memory.md` | Historical decisions and lessons learned |

---

## COMMANDS

### Development
```bash
# Start development environment
pnpm dev

# Start specific service
pnpm dev --filter=@project/api

# Run database migrations
pnpm db:migrate

# Revert last migration
pnpm db:rollback
```

### Testing
```bash
# Run all tests
pnpm test

# Run tests for specific package
pnpm test --filter=@project/api

# Run tests in watch mode
pnpm test --watch

# Run integration tests only
pnpm test:integration
```

### Linting & Type Checking
```bash
# Lint all packages
pnpm lint

# Type check all packages
pnpm lint:types

# Format code
pnpm format
```

### Building
```bash
# Build all packages
pnpm build

# Build for production
pnpm build --turbo

# Build specific package
pnpm build --filter=@project/web
```

### Database
```bash
# Verify migration status
pnpm db:verify

# Seed development database
pnpm db:seed

# Reset development database
pnpm db:reset
```

### Deployment
```bash
# Deploy to staging
pnpm deploy:staging

# Deploy to production (requires approval)
pnpm deploy:production
```

---

## RECOMMENDED NEXT STEPS

<!-- Ordered list of what the next agent should do, in priority order. -->

1. **Reproduce and fix token refresh race condition (T-001)** — Start by reading `packages/api/src/auth/refreshToken.ts`. Add the logging changes already in progress, then reproduce with the load test script at `scripts/load-test-auth.sh`. Fix is expected to be in the token revocation check order.

2. **Unblock search indexer migration (T-002)** — Check with DevOps on Kafka upgrade status. If delayed, evaluate indexing to a temporary Elasticsearch instance as a workaround. Decision should be documented in an ADR if we proceed with workaround.

3. **Address PR #892 comments for checkout state machine refactor** — Three comments to address:
   - Line 89: Missing guard for `cancel` transition from `payment_confirmed` state
   - Line 142: State diagram comment is out of date with code
   - `order.machine.test.ts` is missing tests for the new `refund_requested` state

4. **Update onboarding docs** — The docs haven't been updated in 3 months. Focus on:
   - Environment setup steps (any tooling changes)
   - New service architecture diagram
   - Updated deployment process with approval gates
   - Common troubleshooting section

5. **Remove orphaned feature flags** — Search codebase for `useFeatureFlag` calls where the flag key is no longer in Unleash. File a cleanup PR.

---

## SESSION METADATA

| Field | Value |
|-------|-------|
| Agent | [Agent Name/ID] |
| Session Start | [Date/Time] |
| Session End | [Date/Time] |
| Branch | [Branch Name] |
| Working On | [Sprint/Project Name] |
| Context Window Status | [Full/Moderate/Plenty of room] |

---

*Template version 2.0 | Copy this file as `agent-handoff.md` and fill it out before ending your session.*
