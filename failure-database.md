# Failure Database

> Central registry of every known failure, bug, and incident. Used for root cause analysis, trend identification, and prevention.

---

## Entry Format

```yaml
Bug ID: BUG-XXX
Title: Bug Title
Date Discovered: YYYY-MM-DD
Date Fixed: YYYY-MM-DD (or "Open" if unfixed)
Severity: S1-S5
Description: What happened and what was affected.
Root Cause: What actually caused the failure.
Fix: What was done to resolve it.
Detection Method: test | monitoring | user report | code review | security audit | penetration test
Prevention Method: How to prevent similar failures.
Related Files: [file paths]
Related Workflows: [workflows affected]
Regression Test: Yes/No — test file path
```

---

## Severity Definitions

| Severity | Definition | Response Time |
|----------|------------|---------------|
| **S1** | Complete system outage or data loss | Immediate, < 1 hour |
| **S2** | Major feature broken, partial outage | < 4 hours |
| **S3** | Minor feature broken, no workaround | < 24 hours |
| **S4** | Cosmetic issue, workaround exists | < 1 week |
| **S5** | Low priority, edge case | Fix when convenient |

---

## Entries

---

### BUG-001: Payment Double Charge on Retry
**Title**: Payment double charge when checkout retry triggered due to network timeout
**Date Discovered**: 2025-09-01
**Date Fixed**: 2025-09-03
**Severity**: S1

**Description**: 47 users were double-charged (total $12,843.50) when their initial payment request appeared to fail (network timeout), but actually succeeded. The retry logic created a second charge. Root cause was missing idempotency key on payment mutations.

**Root Cause**: The `createPaymentIntent` mutation did not require or use an idempotency key. When the client retried after a network timeout, Stripe received two separate requests and processed both as distinct payments.

**Fix**:
- Added `idempotencyKey` as a **required** field on all payment mutations
- Client generates a unique idempotency key per payment attempt using `userId + timestamp + nonce`
- Stripe client configured to pass `Idempotency-Key` header
- All 47 users received automatic refunds

**Detection Method**: User report (support tickets + billing complaints)

**Prevention Method**:
- **Idempotency keys are now required** — API schema validation rejects payment mutations without them
- Integration tests added for payment retry scenarios
- Added monitoring alert for duplicate Stripe charges within 5-minute window
- Added canary that verifies idempotency key enforcement weekly
- Reviewed all other mutation endpoints for idempotency gaps

**Related Files**:
- `packages/api/src/payment/payment.service.ts` — Added idempotency key validation
- `packages/api/src/payment/payment.routes.ts` — Updated schema validation
- `packages/api/src/payment/stripe.webhook.ts` — Added dedup logic
- `packages/shared/src/types/payment.ts` — Added `idempotencyKey` to types

**Related Workflows**: Checkout, Payment Processing

**Regression Test**: Yes — `tests/integration/payment-idempotency.test.ts`

---

### BUG-002: Search Index Outage — Schema Incompatibility
**Title**: Full-text search down for 45 minutes due to Kafka schema incompatibility
**Date Discovered**: 2025-08-15
**Date Fixed**: 2025-08-15
**Severity**: S1

**Description**: Product search returned zero results for 45 minutes. The search index consumer had a 2M event backlog caused by Kafka deserialization errors. A schema change was deployed to the producer without updating the consumer, causing all events to fail schema validation.

**Root Cause**: A new field was added to the product event Avro schema. The producer schema was updated and deployed, but the consumer schema was not. Schema Registry correctly rejected the incompatible messages, but the consumer had no error handling for this case and stalled.

**Fix**:
- Restarted search consumer with updated schema
- Processed backlog of 2M events (took 12 minutes)
- Deployed Schema Registry enforcement with `FULL` compatibility (changed from `FORWARD`)
- Added consumer health check that alerts if consumer lag exceeds 10k events

**Prevention Method**:
- **Schema Registry compatibility mode set to `FULL`** for all production topics
- **Consumer schema validation gate**: CI checks that all consumers can handle the new schema before producer deployment is allowed
- Consumer lag alerting added to PagerDuty at thresholds: 1k (warning), 10k (critical), 100k (page)
- **Deployment runbook updated**: schema changes require separate producer + consumer deploys, verified by CI
- Added integration test that verifies producer/consumer schema compatibility

**Related Files**:
- `packages/shared/src/schemas/product-event.avsc` — Avro schema
- `packages/api/src/search/search.consumer.ts` — Search consumer
- `.github/workflows/ci.yml` — Added schema compatibility check
- `ops/pagerduty/alert-rules.tf` — Added consumer lag alerts

**Related Workflows**: Search, Product Indexing

**Regression Test**: Yes — `tests/integration/search-schema-compatibility.test.ts`

---

### BUG-003: Rate Limiting Bypass on Login
**Title**: Rate limiter allowed 5k req/s to login endpoint, causing 100% CPU
**Date Discovered**: 2025-06-15
**Date Fixed**: 2025-06-17
**Severity**: S1

**Description**: During load testing, the login endpoint accepted 5,000 requests/second before the rate limiter engaged. The database CPU hit 100% and the entire API became unresponsive for 8 minutes. In production, a single attacker IP could have taken down the service.

**Root Cause**: The rate limiter was implemented as a per-IP sliding window, but the Redis-based implementation had a bug: the window calculation used `current_timestamp - window` when it should have used `current_timestamp + window`. This caused the window to extend infinitely, never triggering the limit.

**Fix**:
- Fixed the Redis sliding window implementation — corrected window boundary calculation
- Added unit tests for boundary conditions (window edge, burst, stale entries)
- Added integration tests that validate rate limiting with simulated traffic
- Added dual rate limiting: token bucket per-IP (at gateway) + sliding window per-user (at API)
- Added load test to CI that verifies rate limiter activates at expected thresholds

**Prevention Method**:
- **Load testing is now part of CI** for all authentication endpoints
- Rate limiter validation is a mandatory PR gate
- Added real-time monitoring dashboard for rate limiter effectiveness
- Rate limiter configuration is immutable — changes require PR with security review
- Gateway-level rate limiting added as first line of defense

**Related Files**:
- `packages/api/src/middleware/rateLimiter.ts` — Fixed window calculation
- `packages/api/src/middleware/gatewayRateLimiter.ts` — New token bucket implementation
- `packages/shared/src/config/rateLimits.ts` — Rate limit configuration
- `scripts/load-test-auth.sh` — Load testing script

**Related Workflows**: Login, Authentication

**Regression Test**: Yes — `tests/integration/rate-limiter.test.ts`

---

### BUG-004: Session Token Not Invalidated on Logout
**Title**: Logout did not invalidate session token, allowing continued access
**Date Discovered**: 2025-07-20
**Date Fixed**: 2025-07-22
**Severity**: S2

**Description**: When a user logged out, the JWT access token remained valid until its natural expiration (15 minutes). If an attacker had the token, they could continue making authenticated requests. This was discovered during a security audit.

**Root Cause**: The logout endpoint only cleared the session cookie but did not add the JWT to the token blacklist in Redis. Short-lived JWTs (15 min) reduced the window, but the risk was still unacceptable.

**Fix**:
- Logout endpoint now adds the JWT jti (JWT ID) to a Redis blacklist with TTL equal to remaining token lifetime
- `authGuard` middleware now checks Redis blacklist before accepting any JWT
- Refresh token rotation implemented: each refresh invalidates the previous refresh token
- Added automated security test that verifies token invalidation on logout

**Prevention Method**:
- **All tokens are blacklisted on logout** — verified by integration test
- Refresh token rotation makes token replay attacks impractical
- Security audit findings are now tracked as P1 items in the backlog
- Automated token invalidation test runs on every PR

**Related Files**:
- `packages/api/src/auth/auth.controller.ts` — Updated logout handler
- `packages/api/src/auth/auth.service.ts` — Added token blacklist logic
- `packages/api/src/middleware/authGuard.ts` — Added blacklist check
- `packages/api/src/auth/refreshToken.ts` — Added refresh token rotation

**Related Workflows**: Logout, Session Management

**Regression Test**: Yes — `tests/integration/auth-logout-invalidation.test.ts`

---

### BUG-005: Order State Machine — Invalid Transition from Cancelled to Shipped
**Title**: Order in "cancelled" state could transition to "shipped" via race condition
**Date Discovered**: 2025-08-10
**Date Fixed**: 2025-08-12
**Severity**: S2

**Description**: An edge case where an order cancellation and shipment dispatch occurred simultaneously. The cancellation request created a state event at nearly the same time as the shipping event. Due to Kafka processing order, the shipping event was processed AFTER the cancellation event, moving the order from "cancelled" to "shipped" — a transition that should be impossible.

**Root Cause**: The state machine guards only checked the current state against allowed transitions, but did not consider that async event processing could reorder events. The cancelled→shipped transition was not defined in the state machine, but the guard check had a bug: it used `machine.can('SHIP')` on the current state, and under certain race conditions, the state machine allowed it because the cancellation event's state change hadn't been committed yet.

**Fix**:
- Updated XState state machine to explicitly block transitions from terminal states (cancelled, returned, refunded)
- Added idempotency check in order state change handler: if order is in a terminal state, reject any state transition
- Added optimistic locking on the `orders` table row — state updates use `UPDATE ... WHERE current_state = <expected_state>`
- Kafka event ordering preserved by using a single partition for order events with `order_id` as partition key

**Prevention Method**:
- **State machines must explicitly declare all invalid transitions** — not just valid ones
- Added property-based testing for state machine that tests all possible event orderings
- Optimistic locking prevents stale state updates at the database level
- Added monitoring for unexpected state transitions

**Related Files**:
- `packages/order-machine/src/order.machine.ts` — Updated state machine
- `packages/order-machine/src/guards/orderGuards.ts` — Added terminal state guards
- `packages/api/src/order/order.service.ts` — Added optimistic locking
- `packages/shared/src/kafka/order-partitioner.ts` — Ensures per-order event ordering

**Related Workflows**: Order Cancellation, Order Fulfillment

**Regression Test**: Yes — `tests/order-machine/src/__tests__/order.machine.property.test.ts`

---

### BUG-006: Soft Delete Partial Index Missing on Orders Table
**Title**: Orders query scanning 2M soft-deleted rows, 800ms response time
**Date Discovered**: 2025-05-20
**Date Fixed**: 2025-05-22
**Severity**: S2

**Description**: The "My Orders" page on the web app took 800ms to load for users with many orders. The query was doing a full table scan of 3M rows, 2M of which were soft-deleted. The `deleted_at` column existed but had no partial index.

**Root Cause**: The orders table used soft deletes (`deleted_at` timestamp) but the index strategy was designed before the table had significant volume. No partial index was created for `WHERE deleted_at IS NULL`, so PostgreSQL scanned every row.

**Fix**:
- Added partial index: `CREATE INDEX idx_orders_active ON orders (user_id, created_at) WHERE deleted_at IS NULL`
- Added composite partial index for common query patterns (status + user_id)
- Updated all order queries to use the partial index via query planner optimization
- Query time dropped from 800ms to 45ms

**Prevention Method**:
- **Linting rule in CI**: any table with `deleted_at` column must have a partial index `WHERE deleted_at IS NULL`
- Migration template updated to include partial index creation for soft-delete columns
- Database review checklist item added: "Verify partial indexes for all soft-delete columns"
- Added slow query monitoring that alerts on full table scans over 100k rows

**Related Files**:
- `packages/api/src/order/order.service.ts` — Updated query patterns
- `migrations/20250522-add-orders-partial-index.sql` — Migration file
- `scripts/lint-db-schema.js` — Added partial index linting rule

**Related Workflows**: Order History, My Orders

**Regression Test**: Yes — benchmark verified in CI: `scripts/db-benchmark.sh`

---

### BUG-007: Email Template Injection via User Name Field
**Title**: Stored XSS via user name field rendered in HTML email templates
**Date Discovered**: 2025-07-05
**Date Fixed**: 2025-07-06
**Severity**: S2

**Description**: A user registered with a name field containing `<script>alert('xss')</script>`. This name was rendered unsanitized in transactional email templates. When an administrator viewed the user's details in the admin dashboard, the script executed.

**Root Cause**: Email templates used raw string interpolation to render user-provided fields. The template engine did not auto-escape HTML. User names were not sanitized at input time.

**Fix**:
- All email templates migrated to Handlebars with auto-escaping enabled
- User-provided fields are now sanitized at the API boundary (input sanitization middleware)
- All user-provided fields in templates are escaped, including `name`, `email`, `company`, `address` fields
- Added Content-Security-Policy header to admin dashboard
- Security audit of all other template rendering paths (no other issues found)

**Prevention Method**:
- **Template engines must auto-escape** — HTML emails use Handlebars with `--noEscape` explicitly unset
- Input sanitization added as global middleware — all text fields stripped of HTML tags at the API boundary
- Security scanning of templates added to CI
- Added penetration testing step to security audit checklist

**Related Files**:
- `packages/notification/src/template/template.service.ts` — Migrated to Handlebars
- `packages/api/src/middleware/sanitizeInput.ts` — New input sanitization middleware
- `packages/shared/src/sanitization/htmlSanitizer.ts` — HTML stripping utility
- `packages/notification/src/email/templates/*.hbs` — All templates updated

**Related Workflows**: User Registration, Notification Delivery

**Regression Test**: Yes — `tests/integration/email-template-xss.test.ts`

---

### BUG-008: Webhook Delivery Missing HMAC Signature
**Title**: Outgoing webhooks sent without HMAC signature, allowing payload forgery
**Date Discovered**: 2025-08-05
**Date Fixed**: 2025-08-07
**Severity**: S2

**Description**: Outgoing webhooks were sent as plain JSON payloads without HMAC signatures. Any attacker who could intercept or spoof the webhook request could send forged payloads to the target endpoint. Discovered during a security audit of the webhook system.

**Root Cause**: The webhook delivery service implemented signature verification for incoming webhooks but did not generate signatures for outgoing webhooks. The feature was simply not implemented.

**Fix**:
- Outgoing webhook payloads now include `X-Signature-256` header with HMAC-SHA256 of the payload body
- Signature calculated using the webhook's secret (generated at webhook creation time)
- Documentation updated to instruct webhook consumers to verify the signature
- Added signature verification example code for common languages in webhook docs
- Legacy webhooks without secrets had secrets auto-generated on first delivery after deploy

**Prevention Method**:
- **All outgoing webhooks are signed** — verified by integration test
- Webhook creation API now auto-generates a secret if not provided
- Security audit checklist includes: "Verify all webhook endpoints sign outgoing payloads"
- Webhook documentation prominently displays signature verification requirement

**Related Files**:
- `packages/api/src/webhook/webhook.delivery.ts` — Added HMAC signing
- `packages/api/src/webhook/webhook.signature.ts` — Signature generation utility
- `packages/api/src/webhook/webhook.service.ts` — Secret auto-generation
- `docs/webhooks.md` — Updated with signature verification guide

**Related Workflows**: Webhook Delivery

**Regression Test**: Yes — `tests/integration/webhook-signature.test.ts`

---

### BUG-009: Database Connection Pool Exhaustion
**Title**: Database connection pool exhausted during traffic spike, API unavailable for 12 minutes
**Date Discovered**: 2025-09-15
**Date Fixed**: 2025-09-16
**Severity**: S1

**Description**: During a promotional event (flash sale), traffic spiked to 8x normal levels. The database connection pool (50 connections) was exhausted within 2 minutes. New requests queued waiting for connections, queue grew to 500+ requests, API latency went from 200ms to 30s+, then complete timeout.

**Root Cause**: The connection pool was configured with a fixed size of 50 connections, chosen based on normal traffic patterns. No connection pooling at the application level (each service had its own pool). No connection queue limits or timeout configuration. During the spike, connections were held longer than usual due to query slowdown from concurrent load.

**Fix**:
- Increased connection pool to 150 (calculated: 8x traffic buffer with overhead for peak concurrency)
- Added connection timeout (30s) and queue timeout (10s) to prevent connection starvation
- Implemented PgBouncer as a centralized connection pooler between services and database
- Added circuit breaker: if connection acquisition fails > 10% of requests in 60s, circuit opens and returns cached responses for 2 minutes
- Added auto-scaling: pool size adjusts based on current traffic (min: 50, max: 200)

**Prevention Method**:
- **Connection pool sizing is now calculated from expected peak traffic** — documented in runbook
- PgBouncer provides a shared pool, reducing per-service pool overhead
- Circuit breaker prevents cascading failures
- Load testing now includes connection pool exhaustion scenarios
- Added monitoring alerts: pool utilization > 80% warns, > 95% pages

**Related Files**:
- `packages/api/src/database/connection.ts` — Updated pool configuration
- `ops/pgbouncer/pgbouncer.ini` — PgBouncer configuration
- `packages/shared/src/config/database.ts` — Connection pool configuration
- `ops/monitoring/database-alerts.tf` — Pool utilization alerts

**Related Workflows**: All database-dependent workflows

**Regression Test**: Yes — `tests/load/database-connection-pool.ts`

---

### BUG-010: Race Condition in Stock Reservation
**Title**: Inventory oversold by 5 units during flash sale due to race condition
**Date Discovered**: 2025-09-15
**Date Fixed**: 2025-09-17
**Severity**: S2

**Description**: During the same flash sale event, 5 units of a popular product were oversold. The system showed 10 units in stock but allowed 15 orders to be placed before inventory was exhausted. This caused 5 customers to receive cancellation notices.

**Root Cause**: The stock reservation logic used a read-then-write pattern: read current stock, check availability, decrement stock. Between the read and the write, another concurrent request read the same stock value, causing both to pass the availability check. PostgreSQL default isolation level (Read Committed) did not prevent this.

**Fix**:
- Stock reservation now uses PostgreSQL advisory locks — `pg_try_advisory_xact_lock(product_id)` before any stock mutation
- Changed stock decrement to atomic UPDATE: `UPDATE inventory_items SET quantity = quantity - $1 WHERE product_id = $2 AND quantity >= $1 RETURNING quantity`
- Added Redis-based distributed lock as a secondary guard (fallback if advisory lock fails)
- The atomic UPDATE approach eliminates the read-then-write race condition entirely

**Prevention Method**:
- **All stock mutations use atomic UPDATE** — no read-then-write pattern
- Integration test added that simulates 100 concurrent checkout requests for same product
- Added monitoring for oversold events (stock_quantity < 0 flag)
- Code review checklist item: "Verify inventory mutations use atomic operations"

**Related Files**:
- `packages/api/src/inventory/stock.reservation.ts` — Rewritten to use atomic UPDATE
- `packages/api/src/inventory/inventory.service.ts` — Removed read-then-write
- `packages/shared/src/types/inventory.ts` — Updated types for atomic reservation

**Related Workflows**: Checkout, Stock Reservation

**Regression Test**: Yes — `tests/integration/inventory-concurrent-reservation.test.ts`

---

### BUG-011: Auth Token in Client-Side Logs
**Title**: JWT access token written to browser console logs by debug middleware
**Date Discovered**: 2025-07-18
**Date Fixed**: 2025-07-18
**Severity**: S2

**Description**: A debug logging middleware accidentally left in the production build was writing all API response headers to `console.log`, including the `Authorization: Bearer <jwt>` header in responses and the `Set-Cookie` header containing the refresh token. Any user who opened browser dev tools could see their own tokens.

**Root Cause**: A debug logging middleware intended for development was not excluded from the production build. The middleware logged all request/response details including headers.

**Fix**:
- Immediately removed the debug middleware from production webpack build
- Added eslint rule: `console.log` is banned in production code (allowed in tests and dev-only files)
- Added build-time check: webpack production build fails if any `console.log` exists outside allowed files
- Ran full codebase audit for other debug-only code in production paths
- Token rotation for all active sessions (security precaution)

**Prevention Method**:
- **ESLint rule enforces no console.log in production code** — fails CI
- Webpack production build strips all debug code from bundle
- Code review now checks for debug code in production paths
- Added security scanning rule: "Flag all console.log calls not in test/dev directories"

**Related Files**:
- `packages/web/src/middleware/debugLogger.ts` — Removed from production
- `.eslintrc.json` — Added `no-console` rule for production code
- `packages/web/webpack.prod.js` — Added debug code stripping
- `packages/shared/src/utils/environment.ts` — Environment detection utilities

**Related Workflows**: All web workflows

**Regression Test**: Yes — `tests/integration/no-console-in-production.test.ts`

---

### BUG-012: Stale Materialized Views in Analytics Dashboard
**Title**: Revenue dashboard showed 4-hour-old data due to stale materialized view
**Date Discovered**: 2025-10-05
**Date Fixed**: 2025-10-06
**Severity**: S3

**Description**: The revenue dashboard in the admin panel showed revenue figures that were consistently 4 hours behind real-time. Finance team reported discrepancies between the dashboard and Stripe's dashboard. The materialized view for daily revenue aggregation was only refreshed every 6 hours.

**Root Cause**: The materialized view `mv_daily_revenue` had a manual refresh schedule set to every 6 hours via cron. The refresh interval was chosen during initial development when real-time data wasn't a requirement. As the business grew, the requirement changed but the refresh schedule wasn't updated.

**Fix**:
- Changed materialized view refresh to every 15 minutes via pg_cron
- Added `CONCURRENTLY` option to avoid locking the view during reads
- Added manual refresh button in the admin dashboard for data team
- Added "last refreshed" timestamp display on the dashboard
- Added materialized view staleness monitoring alert (breach > 30 minutes)

**Prevention Method**:
- **Materialized view refresh interval must be documented** and reviewed quarterly
- Dashboard displays data freshness timestamp — users can see how old the data is
- Added monitoring for stale views — alerts if any view hasn't refreshed within 2x its scheduled interval
- Requirements review process now includes data freshness expectations

**Related Files**:
- `migrations/20251006-update-mv-refresh.sql` — Updated refresh schedule
- `packages/api/src/analytics/analytics.service.ts` — Added manual refresh endpoint
- `packages/web/src/pages/analytics/RevenueDashboard.tsx` — Added last refreshed display
- `ops/pg_cron/materialized-views.sql` — pg_cron job definitions

**Related Workflows**: Analytics, Revenue Reporting

**Regression Test**: No — tested manually (would require materialized view timing)

---

### BUG-013: Cross-Tenant Data Leakage via Shared Cache
**Title**: User data from one organization visible to another organization via Redis cache
**Date Discovered**: 2025-10-20
**Date Fixed**: 2025-10-22
**Severity**: S1

**Description**: A user in Organization A could occasionally see another user's order data. The issue was intermittent and hard to reproduce. Investigation revealed that Redis cache keys did not include tenant ID, so cached data from one tenant's request was served to another tenant's request.

**Root Cause**: Redis cache keys for user-specific data used only `userId` without the `orgId` (tenant ID) qualifier. In the multi-tenant system, user IDs were not globally unique — they were unique per organization. `userId:42` in org A was a different user than `userId:42` in org B.

**Fix**:
- All Redis cache keys updated to include `orgId` prefix: `org:{orgId}:user:{userId}:*`
- Cache key migration script ran to invalidate all old (unscoped) cache keys
- All cache lookups now require explicit tenant context
- Added integration test that creates two orgs with overlapping user IDs and verifies cache isolation
- Penetration test for cross-tenant data leakage added to security audit

**Prevention Method**:
- **All cache keys must be tenant-scoped** — verified by integration test
- Code review checklist: "Does this cache key include tenant ID?"
- Added architectural linting rule: "Cache keys in multi-tenant contexts must `orgId` be present"
- Penetration testing now includes cross-tenant data access as a standard scenario

**Related Files**:
- `packages/api/src/cache/cache.service.ts` — Updated key generation
- `packages/api/src/middleware/cacheMiddleware.ts` — Added tenant context requirement
- `packages/shared/src/cache/keyGenerator.ts` — Cache key generation utility
- `packages/api/src/auth/auth.service.ts` — Updated session cache keys

**Related Workflows**: All multi-tenant workflows (orders, users, payments)

**Regression Test**: Yes — `tests/integration/cross-tenant-cache-isolation.test.ts`

---

### BUG-014: LDAP Sync Causing Mass Account Lockout
**Title**: SSO user accounts locked out after LDAP sync overwrote email addresses with null
**Date Discovered**: 2025-11-01
**Date Fixed**: 2025-11-03
**Severity**: S2

**Description**: 312 users were locked out after the nightly LDAP sync job ran. The sync job processed a batch of users where the LDAP directory had missing email fields. The job overwrote user email addresses with `NULL` in the database, causing subsequent login attempts to fail (email verification required for SSO login).

**Root Cause**: The LDAP sync script did not validate that required fields (email) were present before updating the database. It blindly wrote LDAP data over PostgreSQL rows. The LDAP directory had a known issue where some user records were missing email fields.

**Fix**:
- LDAP sync script now validates all required fields before writing — skips records with missing required fields and logs a warning
- Added dry-run mode for LDAP sync that reports changes without applying them
- All 312 affected users' email addresses were restored from a pre-sync backup
- Added rollback capability: sync job creates a restore point before each run
- Added monitoring: sync job notifications sent to #ops channel

**Prevention Method**:
- **Data sync jobs must validate all required fields** before writing — unit tested
- Sync jobs must have a dry-run mode — mandatory for first run after any change
- Sync jobs must create database restore points before running
- Sync job results are sent to Slack for manual review
- Monitoring alerts if sync job modifies more than 1% of total records

**Related Files**:
- `packages/api/src/sync/ldap-sync.ts` — Updated with validation
- `packages/api/src/sync/sync.service.ts` — Added dry-run mode
- `packages/api/src/sync/sync.routes.ts` — Added dry-run endpoint
- `ops/cron/ldap-sync.sh` — Updated cron job script

**Related Workflows**: SSO Login, User Sync

**Regression Test**: Yes — `tests/integration/ldap-sync-validation.test.ts`

---

### BUG-015: Memory Leak in Image Processing Pipeline
**Title**: Image processing worker OOM-killed after processing 500+ images in a batch
**Date Discovered**: 2025-11-15
**Date Fixed**: 2025-11-17
**Severity**: S2

**Description**: The image processing worker would crash with OutOfMemory errors after processing approximately 500 images in a batch job. Large batches (1000+ images from bulk uploads) would consistently fail, requiring manual reprocessing of individual images.

**Root Cause**: The Sharp image processing library was initialized once per worker and retained processed image buffers in memory. The `sharp()` pipeline for each image created a reference that was not garbage collected until the worker exited. Over a batch of 500+ images, memory grew linearly.

**Fix**:
- Explicitly called `.destroy()` on each Sharp pipeline instance after processing
- Added memory pooling: reuse `sharp()` instances with `pool: false` option and manual cleanup
- Batch size limited to 100 images per worker (configurable)
- Added backpressure: if memory > 80% of container limit, pause processing until GC runs
- Added memory leak detection to CI: process image batches and measure memory growth

**Prevention Method**:
- **All stream/processing pipelines must be explicitly destroyed** — verified by integration test
- Batch processing tasks must have configurable batch sizes
- Added memory monitoring for worker containers — alerts on > 80% memory usage
- Load testing includes sustained batch processing scenarios
- Code review checklist: "Are streams/pipelines properly disposed?"

**Related Files**:
- `packages/api/src/media/image-optimizer.ts` — Added explicit cleanup
- `packages/api/src/media/media.service.ts` — Added batch size limiting
- `packages/api/src/workers/image-worker.ts` — Added backpressure mechanism
- `packages/shared/src/config/media.ts` — Added batch size configuration

**Related Workflows**: Image Upload, Media Processing

**Regression Test**: Yes — `tests/integration/image-processing-memory-leak.test.ts`

---

## Incident Summary

| Year | Total Bugs | S1 | S2 | S3 | S4 | S5 | Found by Users | Found by Tests | Found by Monitoring | Found by Audit |
|------|------------|----|----|----|----|----|----------------|----------------|---------------------|----------------|
| 2025 | 47 | 4 | 12 | 18 | 10 | 3 | 14 | 18 | 9 | 6 |

## Top Root Causes

| Root Cause | Occurrences | Percentage |
|------------|-------------|------------|
| Race conditions | 9 | 19% |
| Missing validation | 8 | 17% |
| Configuration errors | 7 | 15% |
| Schema incompatibility | 5 | 11% |
| Debug code in production | 4 | 9% |
| Insufficient testing | 4 | 9% |
| Resource exhaustion | 3 | 6% |
| Other (security, migration, etc.) | 7 | 15% |

---

*Last updated: 2025-12-01 | Total bugs tracked: 47 | 15 detailed entries above*
