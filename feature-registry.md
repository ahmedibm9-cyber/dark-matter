# Feature Registry

> Central registry of every feature in the system. Tracks purpose, files, dependencies, workflows, risks, and testing status.

---

## Feature Entry Format

```yaml
Feature ID: F-XXX
Name: Feature Name
Purpose: One to two sentence description.
Files: [list of source files]
Dependencies (Internal): [internal package/service dependencies]
Dependencies (External): [third-party services/libraries]
Workflows: [workflows that use this feature]
Database Objects: [tables, views, functions]
APIs: [endpoints]
Risks: [what could go wrong]
Tests: [test file locations and coverage status]
Status: [Active | Deprecated | Planned]
Owner: [Team/Person]
```

---

## Features

---

### F-001: User Authentication & Authorization
**Purpose**: Handle user login, registration, SSO, MFA, session management, and role-based access control.

**Files**:
- `packages/api/src/auth/auth.controller.ts`
- `packages/api/src/auth/auth.service.ts`
- `packages/api/src/auth/auth.routes.ts`
- `packages/api/src/auth/refreshToken.ts`
- `packages/api/src/middleware/authGuard.ts`
- `packages/api/src/middleware/roleGuard.ts`
- `packages/web/src/pages/login.tsx`
- `packages/web/src/pages/register.tsx`
- `packages/web/src/hooks/useAuth.ts`
- `packages/web/src/components/AuthGuard.tsx`
- `packages/shared/src/types/auth.ts`

**Dependencies (Internal)**: User service, notification service
**Dependencies (External)**: Auth0, Redis (session store), PostgreSQL

**Workflows**: Login, Registration, Password Reset, SSO Login, MFA Challenge, Session Refresh

**Database Objects**: `users`, `sessions`, `refresh_tokens`, `roles`, `user_roles`, `mfa_devices`, `login_attempts`

**APIs**:
- `POST /v1/auth/login`
- `POST /v1/auth/register`
- `POST /v1/auth/refresh`
- `POST /v1/auth/logout`
- `POST /v1/auth/password-reset`
- `POST /v1/auth/mfa/verify`
- `GET /v1/auth/session`
- `GraphQL: login, register, refreshToken, logout`

**Risks**:
- S1: Authentication bypass (critical, mitigated by Auth0 + JWT validation)
- S2: Session hijacking (mitigated by short-lived tokens + refresh token rotation)
- S2: Rate-limit bypass leading to brute force (mitigated by per-IP + per-user rate limiting)
- S3: Auth0 outage affecting login (mitigated by cached sessions for 5 minutes)

**Tests**:
- `packages/api/src/auth/__tests__/auth.controller.test.ts` — Coverage: 92%
- `packages/api/src/auth/__tests__/auth.service.test.ts` — Coverage: 88%
- `packages/api/src/middleware/__tests__/authGuard.test.ts` — Coverage: 95%
- `packages/web/src/hooks/__tests__/useAuth.test.ts` — Coverage: 85%
- Integration: `tests/integration/auth-flow.test.ts` — Coverage: full login/register/refresh/logout flow

**Status**: Active
**Owner**: Platform Team (Alice Chen)

---

### F-002: Payment Processing
**Purpose**: Handle payment capture, refunds, subscriptions, invoicing, and payment method management via Stripe.

**Files**:
- `packages/api/src/payment/payment.controller.ts`
- `packages/api/src/payment/payment.service.ts`
- `packages/api/src/payment/payment.routes.ts`
- `packages/api/src/payment/stripe.webhook.ts`
- `packages/api/src/payment/invoice.service.ts`
- `packages/web/src/pages/checkout/payment.tsx`
- `packages/web/src/components/StripeElements.tsx`
- `packages/web/src/hooks/usePayment.ts`
- `packages/shared/src/types/payment.ts`
- `packages/order-machine/src/guards/paymentGuards.ts`

**Dependencies (Internal)**: Order service, user service, notification service, invoice service
**Dependencies (External)**: Stripe, PostgreSQL, Kafka (payment events)

**Workflows**: Checkout, Subscription Billing, Refund, Invoice Generation, Payment Method Update

**Database Objects**: `payments`, `payment_methods`, `subscriptions`, `invoices`, `invoice_line_items`, `refunds`, `payouts`

**APIs**:
- `POST /v1/payment/create-intent`
- `POST /v1/payment/confirm`
- `POST /v1/payment/refund`
- `GET /v1/payment/methods`
- `POST /v1/payment/methods`
- `DELETE /v1/payment/methods/:id`
- `GET /v1/payment/invoices`
- `POST /v1/payment/subscription`
- `Webhook POST /webhooks/stripe`
- `GraphQL: createPaymentIntent, confirmPayment, refundPayment`

**Risks**:
- S1: Double charge (mitigated by idempotency keys — required on all mutations)
- S1: Payment data leak (mitigated by PCI compliance via Stripe, no raw card data stored)
- S2: Failed payment not retried (mitigated by automated retry with exponential backoff)
- S2: Refund failure (mitigated by async refund with manual fallback)
- S3: Stripe API outage (mitigated by queueing payments for retry)

**Tests**:
- `packages/api/src/payment/__tests__/payment.service.test.ts` — Coverage: 90%
- `packages/api/src/payment/__tests__/stripe.webhook.test.ts` — Coverage: 88%
- `packages/api/src/payment/__tests__/invoice.service.test.ts` — Coverage: 85%
- `packages/web/src/hooks/__tests__/usePayment.test.ts` — Coverage: 80%
- Integration: `tests/integration/payment-flow.test.ts` — Coverage: full checkout flow with idempotency test
- E2E: `tests/e2e/checkout.spec.ts` — Coverage: happy path + error scenarios

**Status**: Active
**Owner**: Payments Team (Bob Martinez)

---

### F-003: Order Management
**Purpose**: Full order lifecycle management from creation through fulfillment, including state machine transitions and customer communication.

**Files**:
- `packages/api/src/order/order.controller.ts`
- `packages/api/src/order/order.service.ts`
- `packages/api/src/order/order.routes.ts`
- `packages/order-machine/src/order.machine.ts`
- `packages/order-machine/src/actions/orderActions.ts`
- `packages/order-machine/src/guards/orderGuards.ts`
- `packages/web/src/pages/orders/`
- `packages/web/src/components/OrderStatusBadge.tsx`
- `packages/web/src/hooks/useOrders.ts`
- `packages/shared/src/types/order.ts`
- `packages/notification/src/events/orderEvents.ts`

**Dependencies (Internal)**: Payment service, inventory service, shipping service, notification service, user service
**Dependencies (External)**: PostgreSQL, Kafka, XState

**Workflows**: Create Order, Cancel Order, Refund Order, Fulfill Order, Return Order, Track Order

**Database Objects**: `orders`, `order_items`, `order_status_history`, `order_notes`, `order_documents`

**APIs**:
- `POST /v1/orders`
- `GET /v1/orders`
- `GET /v1/orders/:id`
- `PUT /v1/orders/:id/cancel`
- `PUT /v1/orders/:id/return`
- `GET /v1/orders/:id/status`
- `GraphQL: createOrder, cancelOrder, getOrder, getOrders`

**Risks**:
- S1: Order state inconsistency (mitigated by XState state machine — impossible to reach invalid state)
- S2: Duplicate order (mitigated by idempotency key on order creation)
- S2: Order cancellation race condition with fulfillment (mitigated by state machine guard)
- S3: Late order status notifications (mitigated by Kafka-backed async notifications)

**Tests**:
- `packages/api/src/order/__tests__/order.service.test.ts` — Coverage: 91%
- `packages/order-machine/src/__tests__/order.machine.test.ts` — Coverage: 94% (all state transitions tested)
- `packages/order-machine/src/__tests__/orderGuards.test.ts` — Coverage: 92%
- `packages/web/src/hooks/__tests__/useOrders.test.ts` — Coverage: 82%
- Integration: `tests/integration/order-flow.test.ts` — Coverage: full lifecycle

**Status**: Active
**Owner**: Orders Team (Carol Nguyen)

---

### F-004: Search & Discovery
**Purpose**: Full-text search across products, users, and orders with filtering, faceting, and relevance scoring.

**Files**:
- `packages/api/src/search/search.controller.ts`
- `packages/api/src/search/search.service.ts`
- `packages/api/src/search/search.consumer.ts` (Kafka consumer for indexing)
- `packages/web/src/pages/search.tsx`
- `packages/web/src/components/SearchBar.tsx`
- `packages/web/src/components/SearchFilters.tsx`
- `packages/web/src/components/SearchResults.tsx`
- `packages/web/src/hooks/useSearch.ts`
- `packages/shared/src/types/search.ts`

**Dependencies (Internal)**: Product service, user service, order service, event bus
**Dependencies (External)**: Elasticsearch (migrating to Meilisearch), Kafka, PostgreSQL

**Workflows**: Product Search, User Search, Order Search, Auto-complete, Faceted Filtering

**Database Objects**: (search is handled by Elasticsearch/Meilisearch, not PostgreSQL; PostgreSQL triggers populate indexing queue)

**APIs**:
- `GET /v1/search`
- `GET /v1/search/suggest`
- `GraphQL: search, searchSuggest`

**Risks**:
- S2: Index out of sync with database (mitigated by Kafka event-driven indexing with at-least-once delivery)
- S2: Search outage (mitigated by fallback to PostgreSQL full-text search)
- S3: Poor relevance ranking (mitigated by manual relevance tuning + A/B testing)
- S3: Slow autocomplete (mitigated by debounced frontend + dedicated suggest endpoint)

**Tests**:
- `packages/api/src/search/__tests__/search.service.test.ts` — Coverage: 87%
- `packages/api/src/search/__tests__/search.consumer.test.ts` — Coverage: 83%
- `packages/web/src/hooks/__tests__/useSearch.test.ts` — Coverage: 79%
- Integration: `tests/integration/search-indexing.test.ts` — Coverage: indexing pipeline

**Status**: Active (migrating from Elasticsearch to Meilisearch)
**Owner**: Search Team (David Kim)

---

### F-005: Notification System
**Purpose**: Multi-channel notification delivery (email, SMS, push, in-app) with templates, preferences, and batching.

**Files**:
- `packages/notification/src/notification.service.ts`
- `packages/notification/src/email/email.service.ts`
- `packages/notification/src/sms/sms.service.ts`
- `packages/notification/src/push/push.service.ts`
- `packages/notification/src/in-app/in-app.service.ts`
- `packages/notification/src/template/template.service.ts`
- `packages/notification/src/consumer/notification.consumer.ts`
- `packages/api/src/notification/notification.controller.ts`
- `packages/api/src/notification/notification.routes.ts`
- `packages/web/src/components/NotificationBell.tsx`
- `packages/web/src/pages/notifications.tsx`
- `packages/web/src/hooks/useNotifications.ts`
- `packages/shared/src/types/notification.ts`

**Dependencies (Internal)**: User service, order service, payment service
**Dependencies (External)**: SendGrid (email), Twilio (SMS), Firebase (push), PostgreSQL, Redis, Kafka

**Workflows**: Order Confirmation, Shipping Update, Payment Receipt, Password Reset, Marketing Email, Weekly Digest

**Database Objects**: `notifications`, `notification_templates`, `notification_preferences`, `notification_logs`, `email_bounces`

**APIs**:
- `GET /v1/notifications`
- `PUT /v1/notifications/:id/read`
- `PUT /v1/notifications/preferences`
- `POST /v1/notifications/test`
- `GraphQL: getNotifications, markNotificationRead, updateNotificationPreferences`

**Risks**:
- S2: Email deliverability issues (mitigated by SendGrid reputation monitoring + bounce handling)
- S2: SMS provider outage (mitigated by fallback to email + push)
- S3: Notification spam (mitigated by rate limiting + preference controls)
- S3: Template rendering errors (mitigated by unit tests + preview mode)

**Tests**:
- `packages/notification/src/__tests__/notification.service.test.ts` — Coverage: 89%
- `packages/notification/src/email/__tests__/email.service.test.ts` — Coverage: 86%
- `packages/notification/src/template/__tests__/template.service.test.ts` — Coverage: 93%
- `packages/web/src/hooks/__tests__/useNotifications.test.ts` — Coverage: 81%
- Integration: `tests/integration/notification-delivery.test.ts`

**Status**: Active
**Owner**: Platform Team (Alice Chen)

---

### F-006: Admin Dashboard
**Purpose**: Internal admin interface for user management, order management, content moderation, and system monitoring.

**Files**:
- `packages/admin/src/pages/`
- `packages/admin/src/components/`
- `packages/admin/src/hooks/`
- `packages/api/src/admin/admin.controller.ts`
- `packages/api/src/admin/admin.service.ts`
- `packages/api/src/admin/admin.routes.ts`
- `packages/api/src/middleware/adminGuard.ts`

**Dependencies (Internal)**: User service, order service, payment service, notification service, search service
**Dependencies (External)**: PostgreSQL, Redis (analytics cache), Grafana (embedded dashboards)

**Workflows**: User Lookup, Order Management, Content Moderation, Analytics Viewing, System Health Check

**Database Objects**: `admin_audit_log`, `admin_actions`

**APIs**:
- `GET /v1/admin/users`
- `GET /v1/admin/users/:id`
- `PUT /v1/admin/users/:id/status`
- `GET /v1/admin/orders`
- `GET /v1/admin/analytics`
- `GET /v1/admin/health`
- `GraphQL: adminUsers, adminOrders, adminAnalytics`

**Risks**:
- S3: Admin privilege escalation (mitigated by strict role-based access + audit logging)
- S3: Data exposure from overly broad admin queries (mitigated by field-level permissions + query limits)
- S4: Slow analytics queries (mitigated by pre-aggregated materialized views)
- S4: UI complexity (mitigated by role-specific dashboard views)

**Tests**:
- `packages/api/src/admin/__tests__/admin.controller.test.ts` — Coverage: 88%
- `packages/api/src/middleware/__tests__/adminGuard.test.ts` — Coverage: 95%
- `packages/admin/src/hooks/__tests__/` — Coverage: 75%

**Status**: Active
**Owner**: Platform Team (Eve Johnson)

---

### F-007: Inventory Management
**Purpose**: Track product inventory levels, manage stock reservations, handle restock alerts, and synchronize with warehouse systems.

**Files**:
- `packages/api/src/inventory/inventory.controller.ts`
- `packages/api/src/inventory/inventory.service.ts`
- `packages/api/src/inventory/inventory.routes.ts`
- `packages/api/src/inventory/stock.reservation.ts`
- `packages/web/src/pages/inventory/`
- `packages/web/src/components/StockIndicator.tsx`
- `packages/web/src/hooks/useInventory.ts`
- `packages/shared/src/types/inventory.ts`

**Dependencies (Internal)**: Product service, order service, notification service
**Dependencies (External)**: PostgreSQL, Redis (stock reservation cache), Kafka (stock events)

**Workflows**: Stock Check, Reserve Stock, Release Stock, Adjust Stock, Restock Alert, Warehouse Sync

**Database Objects**: `inventory_items`, `stock_reservations`, `stock_movements`, `warehouses`, `restock_alerts`, `inventory_snapshots`

**APIs**:
- `GET /v1/inventory/:productId`
- `GET /v1/inventory/:productId/warehouses`
- `POST /v1/inventory/reserve`
- `POST /v1/inventory/release`
- `PUT /v1/inventory/adjust`
- `GET /v1/inventory/alerts`
- `GraphQL: getInventory, reserveStock, releaseStock, adjustStock`

**Risks**:
- S2: Overselling due to race condition in stock reservation (mitigated by optimistic locking + Redis atomic operations)
- S2: Stale inventory data (mitigated by real-time Kafka events + periodic reconciliation)
- S3: Warehouse sync failure (mitigated by dead-letter queue + manual reconciliation tool)

**Tests**:
- `packages/api/src/inventory/__tests__/inventory.service.test.ts` — Coverage: 89%
- `packages/api/src/inventory/__tests__/stock.reservation.test.ts` — Coverage: 92%
- `packages/web/src/hooks/__tests__/useInventory.test.ts` — Coverage: 80%
- Integration: `tests/integration/inventory-flow.test.ts`

**Status**: Active
**Owner**: Operations Team (Frank Lee)

---

### F-008: Multi-Tenant Organization Management
**Purpose**: Support organization/workspace accounts with team management, billing, and role hierarchies.

**Files**:
- `packages/api/src/org/org.controller.ts`
- `packages/api/src/org/org.service.ts`
- `packages/api/src/org/org.routes.ts`
- `packages/api/src/org/team.service.ts`
- `packages/api/src/middleware/tenantGuard.ts`
- `packages/web/src/pages/org/`
- `packages/web/src/components/OrgSwitcher.tsx`
- `packages/web/src/hooks/useOrg.ts`
- `packages/shared/src/types/org.ts`

**Dependencies (Internal)**: User service, payment service (org billing), notification service
**Dependencies (External)**: PostgreSQL, Auth0 (org-level SSO)

**Workflows**: Create Organization, Invite Team Members, Manage Roles, Org Billing, Org Settings

**Database Objects**: `organizations`, `org_members`, `org_roles`, `org_invitations`, `org_settings`, `org_billing_plans`

**APIs**:
- `POST /v1/orgs`
- `GET /v1/orgs`
- `GET /v1/orgs/:id`
- `PUT /v1/orgs/:id`
- `POST /v1/orgs/:id/invite`
- `DELETE /v1/orgs/:id/members/:userId`
- `PUT /v1/orgs/:id/billing`
- `GraphQL: createOrg, getOrg, inviteMember, updateOrgBilling`

**Risks**:
- S2: Cross-tenant data leakage (mitigated by row-level security in PostgreSQL + tenant ID in all queries)
- S2: Orphaned orgs after billing failure (mitigated by automated suspension + notification workflow)
- S3: Invite token forgery (mitigated by signed + expiring invite tokens)
- S3: Role escalation (mitigated by strict role hierarchy enforcement in middleware)

**Tests**:
- `packages/api/src/org/__tests__/org.service.test.ts` — Coverage: 90%
- `packages/api/src/org/__tests__/team.service.test.ts` — Coverage: 88%
- `packages/api/src/middleware/__tests__/tenantGuard.test.ts` — Coverage: 94%
- `packages/web/src/hooks/__tests__/useOrg.test.ts` — Coverage: 82%
- Integration: `tests/integration/org-flow.test.ts`

**Status**: Active
**Owner**: Platform Team (Alice Chen)

---

### F-009: File Upload & Media Management
**Purpose**: Handle file uploads, image optimization, video transcoding, CDN delivery, and secure access control.

**Files**:
- `packages/api/src/media/media.controller.ts`
- `packages/api/src/media/media.service.ts`
- `packages/api/src/media/media.routes.ts`
- `packages/api/src/media/image-optimizer.ts`
- `packages/api/src/media/video-transcoder.ts`
- `packages/web/src/components/FileUploader.tsx`
- `packages/web/src/components/ImageGallery.tsx`
- `packages/web/src/hooks/useMedia.ts`
- `packages/shared/src/types/media.ts`

**Dependencies (Internal)**: User service, product service (product images), notification service
**Dependencies (External)**: S3-compatible storage (MinIO), Cloudflare CDN, Sharp (image processing), FFmpeg (video), PostgreSQL

**Workflows**: Upload Profile Photo, Upload Product Image, Upload Document, Video Upload, Media Gallery

**Database Objects**: `media_items`, `media_variants`, `media_access_tokens`, `media_jobs`

**APIs**:
- `POST /v1/media/upload`
- `GET /v1/media/:id`
- `DELETE /v1/media/:id`
- `GET /v1/media/:id/variants/:variant`
- `POST /v1/media/generate-token`
- `GraphQL: uploadMedia, deleteMedia, getMedia`

**Risks**:
- S2: Malicious file upload (mitigated by file type validation, content-type verification, virus scanning, and CDN WAF)
- S2: Storage cost explosion (mitigated by lifecycle policies + max file size limits + user quota)
- S3: Slow image processing (mitigated by async processing pipeline + WebP/AVIF optimization)
- S4: CDN cache miss on first request (mitigated by cache warming for critical images)

**Tests**:
- `packages/api/src/media/__tests__/media.service.test.ts` — Coverage: 87%
- `packages/api/src/media/__tests__/image-optimizer.test.ts` — Coverage: 91%
- `packages/web/src/hooks/__tests__/useMedia.test.ts` — Coverage: 78%
- Integration: `tests/integration/media-upload.test.ts`

**Status**: Active
**Owner**: Platform Team (Grace Patel)

---

### F-010: Audit Logging
**Purpose**: Immutable audit trail for all security-relevant events, data changes, and admin actions.

**Files**:
- `packages/api/src/audit/audit.service.ts`
- `packages/api/src/audit/audit.middleware.ts`
- `packages/api/src/middleware/auditLogger.ts`
- `packages/shared/src/types/audit.ts`

**Dependencies (Internal)**: All services (emits audit events)
**Dependencies (External)**: PostgreSQL (immutable audit tables), Kafka, S3 (cold storage archive)

**Workflows**: All workflows log audit events — login, payment, order change, admin action, data export

**Database Objects**: `audit_logs`, `audit_log_archives`, `audit_log_retention_policies`

**APIs**:
- `GET /v1/audit/logs` (admin only)
- `GET /v1/audit/logs/:id`
- `GET /v1/audit/export` (admin only)
- `GraphQL: getAuditLogs, exportAuditLogs`

**Risks**:
- S2: Audit log tampering (mitigated by append-only tables + cryptographic chaining of log entries + S3 WORM archive)
- S3: Storage growth (mitigated by configurable retention + automated archival to S3 Glacier)
- S3: Performance impact of logging (mitigated by async Kafka-based logging + batch inserts)
- S4: Missing audit events (mitigated by canary events that verify logging pipeline health)

**Tests**:
- `packages/api/src/audit/__tests__/audit.service.test.ts` — Coverage: 93%
- `packages/api/src/audit/__tests__/audit.middleware.test.ts` — Coverage: 90%
- Integration: `tests/integration/audit-pipeline.test.ts`

**Status**: Active
**Owner**: Security Team (Henry Wu)

---

### F-011: Reporting & Analytics
**Purpose**: Generate business reports, analytics dashboards, data exports, and scheduled report delivery.

**Files**:
- `packages/api/src/analytics/analytics.controller.ts`
- `packages/api/src/analytics/analytics.service.ts`
- `packages/api/src/analytics/analytics.routes.ts`
- `packages/api/src/analytics/report-generator.ts`
- `packages/api/src/analytics/schedule.service.ts`
- `packages/web/src/pages/analytics/`
- `packages/web/src/components/Charts/`
- `packages/web/src/hooks/useAnalytics.ts`
- `packages/shared/src/types/analytics.ts`

**Dependencies (Internal)**: User service, order service, payment service
**Dependencies (External)**: PostgreSQL (materialized views), Redis (cached aggregations), S3 (report storage)

**Workflows**: Generate Report, Schedule Report, View Dashboard, Export Data, Revenue Analysis

**Database Objects**: `report_definitions`, `report_schedules`, `report_executions`, `report_outputs`, `analytics_materialized_views`, `dashboard_definitions`

**APIs**:
- `POST /v1/analytics/reports`
- `GET /v1/analytics/reports`
- `GET /v1/analytics/reports/:id`
- `POST /v1/analytics/reports/:id/run`
- `POST /v1/analytics/schedules`
- `GET /v1/analytics/dashboards/:id`
- `GraphQL: createReport, runReport, getDashboard, scheduleReport`

**Risks**:
- S3: Long-running report queries impacting production DB (mitigated by read replicas + query timeout + resource limits)
- S3: Stale materialized views (mitigated by scheduled refresh + manual refresh option)
- S4: Report data inconsistency (mitigated by point-in-time snapshots + timestamp tracking)
- S4: Scheduled report delivery failure (mitigated by retry logic + failure notification)

**Tests**:
- `packages/api/src/analytics/__tests__/analytics.service.test.ts` — Coverage: 84%
- `packages/api/src/analytics/__tests__/report-generator.test.ts` — Coverage: 86%
- `packages/api/src/analytics/__tests__/schedule.service.test.ts` — Coverage: 88%
- `packages/web/src/hooks/__tests__/useAnalytics.test.ts` — Coverage: 76%

**Status**: Active
**Owner**: Data Team (Iris Tanaka)

---

### F-012: Webhook System
**Purpose**: Provide outgoing webhooks for external integrations, allowing third-party services to receive real-time events.

**Files**:
- `packages/api/src/webhook/webhook.service.ts`
- `packages/api/src/webhook/webhook.controller.ts`
- `packages/api/src/webhook/webhook.routes.ts`
- `packages/api/src/webhook/webhook.delivery.ts`
- `packages/api/src/webhook/webhook.signature.ts`
- `packages/web/src/pages/settings/webhooks.tsx`
- `packages/web/src/hooks/useWebhooks.ts`
- `packages/shared/src/types/webhook.ts`

**Dependencies (Internal)**: All services produce webhook events via event bus
**Dependencies (External)**: PostgreSQL, Redis (delivery queue), Kafka

**Workflows**: Create Webhook, Configure Events, Receive Webhook Callback, Webhook Retry, Webhook Logs

**Database Objects**: `webhooks`, `webhook_events`, `webhook_delivery_logs`, `webhook_secrets`

**APIs**:
- `POST /v1/webhooks`
- `GET /v1/webhooks`
- `PUT /v1/webhooks/:id`
- `DELETE /v1/webhooks/:id`
- `POST /v1/webhooks/:id/test`
- `GET /v1/webhooks/:id/logs`
- `GET /v1/webhooks/:id/events`
- `GraphQL: createWebhook, updateWebhook, getWebhookLogs`

**Risks**:
- S3: Webhook delivery failure (mitigated by retry with exponential backoff + dead-letter after 10 retries)
- S3: Leaked webhook secrets (mitigated by encrypted storage + masked display + rotation endpoint)
- S3: Malicious payload injection to target (mitigated by HMAC signature verification on all deliveries)
- S4: Webhook flood to slow targets (mitigated by circuit breaker + rate limiting per webhook)

**Tests**:
- `packages/api/src/webhook/__tests__/webhook.service.test.ts` — Coverage: 90%
- `packages/api/src/webhook/__tests__/webhook.delivery.test.ts` — Coverage: 91%
- `packages/api/src/webhook/__tests__/webhook.signature.test.ts` — Coverage: 95%
- `packages/web/src/hooks/__tests__/useWebhooks.test.ts` — Coverage: 79%
- Integration: `tests/integration/webhook-delivery.test.ts`

**Status**: Active
**Owner**: Platform Team (Alice Chen)

---

### F-013: Feature Flag System
**Purpose**: Manage feature flags for gradual rollouts, A/B testing, and kill switches.

**Files**:
- `packages/api/src/featureflag/featureflag.service.ts`
- `packages/api/src/featureflag/featureflag.controller.ts`
- `packages/api/src/featureflag/featureflag.routes.ts`
- `packages/api/src/middleware/featureFlag.ts`
- `packages/web/src/hooks/useFeatureFlag.ts`
- `packages/web/src/components/FeatureFlagGuard.tsx`
- `packages/shared/src/types/featureflag.ts`

**Dependencies (Internal)**: User service (for targeting)
**Dependencies (External)**: Unleash (self-hosted), PostgreSQL (Unleash), Redis (Unleash cache)

**Workflows**: Create Flag, Toggle Flag, Gradual Rollout, A/B Test, Kill Switch, Flag Cleanup

**Database Objects**: (managed by Unleash — `features`, `strategies`, `metrics`, `events`)

**APIs**:
- (Consumed via Unleash SDK, not custom API)
- Admin: `GET /v1/featureflags` (list active flags in code)
- `GraphQL: isFeatureEnabled, getFeatureFlags`

**Risks**:
- S3: Orphaned flags in code (mitigated by mandatory cleanup label on flag rollout tickets)
- S3: Incorrect targeting (mitigated by gradual rollout + monitoring)
- S4: Unleash outage (mitigated by client-side cached flag evaluation + fallback to default values)

**Tests**:
- `packages/web/src/hooks/__tests__/useFeatureFlag.test.ts` — Coverage: 87%
- `packages/api/src/middleware/__tests__/featureFlag.test.ts` — Coverage: 86%
- Integration: `tests/integration/featureflag-behavior.test.ts`

**Status**: Active
**Owner**: Platform Team (Alice Chen)

---

## Status Overview

| Status | Count | Features |
|--------|-------|----------|
| Active | 12 | F-001 through F-012 |
| Deprecated | 1 | F-013 (legacy flags before Unleash) |
| Planned | 2 | F-014 (AI recommendations), F-015 (chat support) |

---

*Last updated: 2025-12-01 | Total features: 13 documented*
