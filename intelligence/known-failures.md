# Known Failures

## FAIL-001: Checkout Timeout Under High Load
- **Date**: 2025-02-15
- **Scenario**: During a flash sale event, 15,000 concurrent users attempted to check out simultaneously. The checkout endpoint returned 503 errors for approximately 30% of requests.
- **Root Cause**: The inventory reservation step in the checkout flow made a synchronous HTTP call to an internal inventory service without a circuit breaker. Under load, the inventory service's connection pool was exhausted, causing cascading timeouts.
- **Symptoms**: 30% checkout failure rate, increased latency (from 200ms to 12s), CPU saturation on API service, customer complaints on social media.
- **Detection**: Datadog alert triggered on p99 latency > 5s. Customer support received 200+ tickets within 10 minutes.
- **Impact**: Lost revenue estimated at $45,000. Customer trust erosion.
- **Fix Applied**: 
  1. Added circuit breaker pattern to inventory service calls (timeout: 500ms, threshold: 50% failure in 10s window).
  2. Implemented async inventory reservation via BullMQ queue instead of synchronous HTTP call.
  3. Added connection pooling limits with queueing behavior.
- **Prevention**: 
  1. Load testing must include flash sale scenarios (added to monthly checklist).
  2. All inter-service HTTP calls must use circuit breaker pattern (enforced in code review).
  3. Inventory reservation is now async-first.
- **Monitoring Added**: 
  1. Circuit breaker state metrics (open/closed/half-open).
  2. Checkout success rate dashboard.
  3. Inventory service connection pool utilization.
- **Related**: TDEBT-008 (no load testing in CI)

## FAIL-002: Data Loss from Missing Soft Delete
- **Date**: 2025-03-01
- **Scenario**: An admin accidentally deleted a product listing from the admin panel. The deletion cascaded to all variants, inventory records, and reviews. Data was permanently lost.
- **Root Cause**: Product deletion performed a hard DELETE from the database. There was no soft delete mechanism, no confirmation dialog requiring explicit typed confirmation, and no undo functionality.
- **Symptoms**: Product page returned 404. All historical order data referencing the deleted product had null variant references. Inventory counts were off by the deleted quantity.
- **Detection**: Customer reported that their order history showed "Product Unavailable" instead of the product name. Internal audit identified missing records.
- **Impact**: 3 hours of database restoration from backup. 45 minutes of data loss (between backup and deletion). Customer support handled 50 inquiries.
- **Fix Applied**:
  1. Implemented soft delete for all core entities (User, Product, Variant, Order).
  2. Added deletedAt column to all tables.
  3. Modified all queries to filter WHERE deletedAt IS NULL by default.
  4. Added "withDeleted()" escape hatch for admin queries.
  5. Implemented admin deletion confirmation requiring "DELETE" typed into a text field.
  6. Added 30-day soft delete window before permanent cleanup.
- **Prevention**:
  1. All delete operations must be soft delete (enforced in code review).
  2. Admin destructive actions require typed confirmation.
  3. Backup frequency increased from 24h to 4h RPO.
- **Related**: BR-021 (audit trail), TDEBT-012 (incomplete audit coverage)

## FAIL-003: Email Notification Backlog
- **Date**: 2025-03-20
- **Scenario**: After a marketing campaign sent 50,000 promotional emails, the email notification queue backed up by 3 hours. Order confirmation and shipping notification emails were delayed.
- **Root Cause**: Background workers for email sending shared the same BullMQ queue as transactional notifications. No priority queuing was implemented. Promotional emails consumed all available worker slots.
- **Symptoms**: Users received order confirmation emails 3 hours after placing orders. Customer support received "where is my confirmation?" tickets. Shipping notifications arrived after packages were already delivered.
- **Detection**: BullMQ dashboard showed queue depth of 50,000+. Grafana alert on queue age > 30 minutes.
- **Impact**: Customer confusion, increased support load (300+ tickets), delayed payment confirmation for some orders.
- **Fix Applied**:
  1. Split email queue into two: `email:transactional` (high priority) and `email:promotional` (low priority).
  2. Configured BullMQ workers with 80% capacity on transactional queue, 20% on promotional.
  3. Added queue monitoring dashboards with per-queue depth and age metrics.
  4. Implemented circuit breaker for SMTP provider to prevent cascading failures.
- **Prevention**:
  1. All queue consumers must define priority tier.
  2. Marketing campaigns must have rate limits (max 10,000/hour).
  3. Weekly checklist includes queue health review.

## FAIL-004: Stale Read Model After Schema Change
- **Date**: 2025-04-05
- **Scenario**: A database migration added a new column to the orders table. The CQRS read model materialized view was not updated to include the new column, causing order detail pages to show incomplete data.
- **Root Cause**: Migration process did not include a step to update the read model. There was no automated test comparing write and read schemas.
- **Symptoms**: Order detail page was missing the "shipping method" field for 2 days. Admin reports showed null values in the shipping method column.
- **Detection**: QA engineer noticed missing field during manual testing of a new feature.
- **Impact**: 2 days of incomplete data in reports. Manual data reconciliation required for affected records.
- **Fix Applied**:
  1. Added migration checklist step: "Update CQRS read model views."
  2. Created automated script to compare write model schema with read materialized view schemas.
  3. Added CI check that runs after migrations.
- **Prevention**:
  1. Migration CI check compares read and write schemas.
  2. Pre-release checklist includes read model verification.

## FAIL-005: Payment Double Charge on Retry
- **Date**: 2025-04-12
- **Scenario**: Payment gateway request timed out but the charge was actually successful. The retry logic created a second charge. Customer was charged twice.
- **Root Cause**: The payment processing worker did not implement idempotency keys. The payment gateway's webhook about the first charge arrived after the 5-second timeout but before the retry completed.
- **Symptoms**: Customer complained about double charge. Payment records showed two captured transactions for the same order.
- **Detection**: Customer support ticket. Manual payment log review confirmed duplicate.
- **Impact**: 12 customers affected. Refunds processed. Lost trust with affected customers.
- **Fix Applied**:
  1. All payment charges now use idempotency keys (order ID + attempt number).
  2. Payment gateway call wrapped in idempotency middleware.
  3. Retry logic checks for existing successful payment before charging.
  4. Added duplicate payment detection alert.
- **Prevention**:
  1. All payment-related code must use idempotency keys (code review enforcement).
  2. Payment processing has dedicated unit tests for retry scenarios.
