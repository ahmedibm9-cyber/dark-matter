# Workflows

> This document defines all business and system workflows in the application. Each workflow is documented with triggers, inputs, steps, outputs, dependencies, failure modes, and edge cases. This serves as the authoritative reference for developers, QA engineers, product managers, and support teams.

---

## 1. Workflow Documentation Standards

### When to Document a Workflow

A workflow should be documented when:
- It spans multiple system components or external services
- It involves multiple user roles or personas
- It has significant business value or risk
- It has complex failure modes or edge cases
- It is audited or regulated
- It handles financial transactions or sensitive data

### Workflow Template

Every workflow uses the following template:

```markdown
## Workflow: [WFL-XXX] — [Workflow Name]

### Metadata

| Attribute | Value |
|---|---|
| Workflow ID | WFL-[XXX] |
| Feature ID | F-[XXX] |
| Version | [MAJOR.MINOR] |
| Status | [Draft / Reviewed / Approved / Deprecated] |
| Owner | [TEAM_OR_PERSON] |
| Last Updated | [DATE] |
| Business Criticality | [Critical / High / Medium / Low] |
| Regulatory Impact | [Yes / No — if yes, which regulation] |

### Description

[One to two paragraph description of what this workflow accomplishes, why it exists, and its business context.]

### Trigger

| Trigger Type | Description |
|---|---|
| User Action | [What the user does to start this workflow] |
| System Event | [What system event starts this workflow] |
| Scheduled | [Cron or schedule if time-triggered] |
| Webhook | [External system callback that initiates this] |

### Actors

| Actor | Role | System |
|---|---|---|
| [USER_TYPE] | [ROLE_IN_WORKFLOW] | [BROWSER / API / MOBILE] |
| [SYSTEM_COMPONENT] | [ROLE_IN_WORKFLOW] | [SERVICE_NAME] |
| [EXTERNAL_SYSTEM] | [ROLE_IN_WORKFLOW] | [THIRD_PARTY_NAME] |

### Preconditions

| # | Condition | Verified By |
|---|---|---|
| 1 | [Condition that must be true before workflow starts] | [Component that checks this] |
| 2 | [Condition that must be true before workflow starts] | [Component that checks this] |
| 3 | [Condition that must be true before workflow starts] | [Component that checks this] |

### Inputs

| Field | Type | Required | Source | Validation | Description |
|---|---|---|---|---|---|
| [field_name] | [string / int / UUID / etc.] | Yes / No | [User / System / API] | [Validation rules] | [Description] |
| [field_name] | [string / int / UUID / etc.] | Yes / No | [User / System / API] | [Validation rules] | [Description] |

### Steps

```
Step 1: [Step Name]
  └── Action:        [What happens]
  └── Component:     [Which service/module handles this]
  └── Input:         [Data consumed]
  └── Output:        [Data produced]
  └── Success:       [How success is determined]
  └── Failure:       [How failure is detected and handled]
  └── Timeout:       [Maximum time for this step]
  └── Retry:         [Retry policy]

Step 2: [Step Name]
  └── Action:        [What happens]
  └── Component:     [Which service/module handles this]
  └── Input:         [Data consumed]
  └── Output:        [Data produced]
  └── Success:       [How success is determined]
  └── Failure:       [How failure is detected and handled]
  └── Timeout:       [Maximum time for this step]
  └── Retry:         [Retry policy]
```

### Outputs

| Field | Type | Description | Consumer |
|---|---|---|---|
| [field_name] | [type] | [Description] | [Who uses this output] |
| [field_name] | [type] | [Description] | [Who uses this output] |

### Postconditions

| # | Condition | Verified By |
|---|---|---|
| 1 | [Condition that must be true after workflow completes] | [Component that verifies] |
| 2 | [Condition that must be true after workflow completes] | [Component that verifies] |

### Dependencies

| Dependency | Type | Impact if Unavailable | Fallback Strategy |
|---|---|---|---|
| [SERVICE_OR_DATA] | [Internal / External] | [What breaks if unavailable] | [Fallback mechanism] |
| [SERVICE_OR_DATA] | [Internal / External] | [What breaks if unavailable] | [Fallback mechanism] |

### Failure Points & Recovery

| Scenario | Failure Mode | Detection | Recovery | Owner |
|---|---|---|---|---|
| [Scenario description] | [What fails] | [How detected] | [How to recover] | [Team] |
| [Scenario description] | [What fails] | [How detected] | [How to recover] | [Team] |

### Edge Cases

| Edge Case | Expected Behavior | Notes |
|---|---|---|
| [Edge case description] | [How system should behave] | [Implementation notes] |
| [Edge case description] | [How system should behave] | [Implementation notes] |

### Non-Functional Requirements

| Requirement | Target | Measurement |
|---|---|---|
| Latency (p95) | [TIME] | [MONITORING_TOOL] |
| Throughput | [REQUESTS/SECOND] | [MONITORING_TOOL] |
| Availability | [PERCENTAGE] | [MONITORING_TOOL] |
| Max concurrent | [COUNT] | [MONITORING_TOOL] |

### Events Emitted

| Event Name | Payload | Publisher | Consumer | Async/Sync |
|---|---|---|---|---|
| [event.name] | [payload schema] | [publisher] | [consumer] | [sync/async] |
| [event.name] | [payload schema] | [publisher] | [consumer] | [sync/async] |

### Sequence Diagram (Text-Based)

```
User              Frontend          API Gateway       App Service        Database
 │                    │                  │                  │                │
 │── Action ─────────>│                  │                  │                │
 │                    │── POST /api ────>│                  │                │
 │                    │                  │── Validate ─────>│                │
 │                    │                  │                  │── Query ──────>│
 │                    │                  │                  │<── Result ─────│
 │                    │                  │                  │── Process ────>│
 │                    │                  │                  │<── Confirm ────│
 │                    │<── Response ─────│<── Result ───────│                │
 │<── Update UI ──────│                  │                  │                │
```

### Related Workflows

| Workflow ID | Relationship |
|---|---|
| WFL-[XXX] | [Parent / Child / Prerequisite / Alternative] |
| WFL-[XXX] | [Parent / Child / Prerequisite / Alternative] |

### Test Coverage

| Test Type | Test ID | Scenario | Automation Status |
|---|---|---|---|
| Unit | [TEST_ID] | [Scenario name] | [Automated / Manual / Not covered] |
| Integration | [TEST_ID] | [Scenario name] | [Automated / Manual / Not covered] |
| E2E | [TEST_ID] | [Scenario name] | [Automated / Manual / Not covered] |
| Performance | [TEST_ID] | [Scenario name] | [Automated / Manual / Not covered] |
| Security | [TEST_ID] | [Scenario name] | [Automated / Manual / Not covered] |
```

---

## 2. Complete Workflow Template (Ready to Use)

Copy the template below for each new workflow:

```markdown
## Workflow: WFL-[XXX] — [Workflow Name]

### Metadata

| Attribute | Value |
|---|---|
| Workflow ID | WFL-[XXX] |
| Feature ID | F-[XXX] |
| Version | 1.0 |
| Status | Draft |
| Owner | |
| Last Updated | |
| Business Criticality | |
| Regulatory Impact | |

### Description

[Description]

### Trigger

| Trigger Type | Description |
|---|---|
| User Action | |
| System Event | |
| Scheduled | |
| Webhook | |

### Actors

| Actor | Role | System |
|---|---|---|
| | | |
| | | |

### Preconditions

| # | Condition | Verified By |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |

### Inputs

| Field | Type | Required | Source | Validation | Description |
|---|---|---|---|---|---|
| | | | | | |

### Steps

```
Step 1: [Step Name]
  └── Action:
  └── Component:
  └── Input:
  └── Output:
  └── Success:
  └── Failure:
  └── Timeout:
  └── Retry:
```

### Outputs

| Field | Type | Description | Consumer |
|---|---|---|---|
| | | | |

### Postconditions

| # | Condition | Verified By |
|---|---|---|
| 1 | | |

### Dependencies

| Dependency | Type | Impact if Unavailable | Fallback Strategy |
|---|---|---|---|
| | | | |

### Failure Points & Recovery

| Scenario | Failure Mode | Detection | Recovery | Owner |
|---|---|---|---|---|
| | | | | |

### Edge Cases

| Edge Case | Expected Behavior | Notes |
|---|---|---|
| | | |

### Non-Functional Requirements

| Requirement | Target | Measurement |
|---|---|---|
| Latency (p95) | | |
| Throughput | | |
| Availability | | |
| Max concurrent | | |

### Events Emitted

| Event Name | Payload | Publisher | Consumer | Async/Sync |
|---|---|---|---|---|
| | | | | |

### Related Workflows

| Workflow ID | Relationship |
|---|---|
| | |

### Test Coverage

| Test Type | Test ID | Scenario | Automation Status |
|---|---|---|---|
| Unit | | | |
| Integration | | | |
| E2E | | | |
| Performance | | | |
| Security | | | |
```

---

## 3. Major Workflows (Placeholders)

### WFL-001: User Registration

**Description:** A new user creates an account, verifies their email, and gains access to the application. This workflow covers the complete registration journey including validation, persistence, email verification, and onboarding.

**Trigger:** User submits registration form on the sign-up page.

**Key Steps:**
1. User submits email, password, and profile information
2. Server validates input format and uniqueness
3. Server hashes password (bcrypt, cost factor 12)
4. Server creates user record (status: pending)
5. Server generates email verification token (JWT, 24h expiry)
6. Server sends verification email via transactional email service
7. User clicks verification link in email
8. Server validates token, activates user account (status: active)
9. Server creates initial user profile and preferences
10. Server issues session tokens (access + refresh)
11. User is redirected to onboarding flow

**Failure Points:**
- Email delivery failure (retry 3x with exponential backoff)
- Duplicate email registration (reject with specific error)
- Token expiry during verification (allow re-send)
- Password too weak (reject with password strength feedback)

**Edge Cases:**
- User registers with OAuth (social login) — skip password step
- User closes browser before verification — token remains valid
- User attempts registration with existing email — return 409 Conflict
- Email provider marks email as spam — user can request re-send

---

### WFL-002: User Login

**Description:** An existing user authenticates with their credentials and receives session tokens for subsequent API access.

**Trigger:** User submits login form.

**Key Steps:**
1. User submits email and password
2. Server looks up user by email
3. Server verifies password hash matches
4. Server checks account status (active / suspended / disabled)
5. Server generates access token (JWT, 15min expiry)
6. Server generates refresh token (opaque, 7-day expiry, stored in DB)
7. Server updates last_login_at timestamp
8. Server logs login event to audit trail
9. Server returns tokens to client
10. Client stores tokens (access in memory, refresh in httpOnly cookie)

**Failure Points:**
- Incorrect credentials (return 401, increment failed attempts counter)
- Account locked after N failed attempts (temporary or permanent lockout)
- Account disabled or suspended (return 403 with appropriate message)
- Database unavailable (return 503, client retries)

**Edge Cases:**
- Concurrent login from multiple devices — both sessions valid
- Login after password change — old refresh tokens invalidated
- Remember me — extend refresh token expiry to 30 days
- SSO login — redirect to identity provider, handle callback

---

### WFL-003: Password Reset

**Description:** A user who forgot their password can securely reset it via email verification.

**Trigger:** User clicks "Forgot Password" link and submits email.

**Key Steps:**
1. User submits email on password reset request form
2. Server validates email exists (return same response regardless to prevent enumeration)
3. Server generates reset token (crypto random, 1h expiry, stored hashed)
4. Server sends reset email with token link
5. User clicks link and submits new password
6. Server validates token (not expired, not used)
7. Server validates new password strength
8. Server hashes and stores new password
9. Server invalidates all existing sessions for this user
10. Server marks token as used
11. Server sends confirmation email
12. Server redirects to login page

**Failure Points:**
- Token expired — user must request new reset
- Token already used — reject with message asking to request new reset
- Email not found — return success to prevent enumeration
- Password same as previous — allow (not stored in history)

**Edge Cases:**
- User requests reset multiple times — only latest token is valid
- User resets password while logged in on another device — other sessions invalidated
- Admin resets password for user — triggers same workflow, no email to admin

---

### WFL-004: Checkout / Order Placement

**Description:** A user purchases one or more products. This workflow validates cart, calculates pricing, processes payment, creates order, and handles fulfillment.

**Trigger:** User clicks "Place Order" on checkout page.

**Key Steps:**
1. User reviews order summary and clicks submit
2. Server validates cart contents (items exist, are in stock, not expired)
3. Server validates shipping address (required fields, format, deliverability)
4. Server calculates pricing (subtotal, tax, shipping, discounts)
5. Server applies any active coupon codes
6. Server reserves inventory (reduce stock, temporary hold with TTL)
7. Server creates payment intent via payment processor
8. Server processes payment (credit card / PayPal / etc.)
9. Server confirms payment with payment processor webhook
10. Server creates order record (status: confirmed)
11. Server creates order items
12. Server releases inventory reservation (convert hold to deduction)
13. Server publishes OrderPlacedEvent
14. Server sends order confirmation email
15. Server redirects user to order confirmation page
16. Fulfillment service picks up the event and begins processing

**Failure Points:**
- Payment declined — inform user, allow retry with different method
- Inventory insufficient — partial fulfillment or cancel entire order
- Pricing changed during checkout — recalculate and inform user
- Payment processor timeout — mark order as payment_pending, reconcile via webhook
- Address validation failure — prompt user to correct address

**Edge Cases:**
- User navigates away during payment — payment may complete via webhook, reconcile on return
- Coupon code expired between cart and checkout — remove discount, inform user
- Tax rate calculation depends on shipping address — recalculate on address change
- Currency conversion for international orders — show final amount in user's currency
- Subscription with trial — first payment is $0, no charge until trial ends

---

### WFL-005: Payment Processing (Webhook)

**Description:** Payment processor sends webhook events for payment status changes. The system processes these events to update order status.

**Trigger:** Payment processor sends webhook to `/api/webhooks/payments`.

**Key Steps:**
1. Webhook received at endpoint
2. Server verifies webhook signature (HMAC with shared secret)
3. Server parses event type (payment_intent.succeeded / failed / etc.)
4. Server looks up order by payment intent ID
5. Server updates order status based on event type
6. Server logs payment event to audit trail
7. Server publishes PaymentProcessedEvent
8. Server returns 200 OK to payment processor
9. If order completed, trigger fulfillment workflow

**Failure Points:**
- Webhook signature invalid — return 401, log security event
- Order not found for payment intent — log error, alert operations
- Duplicate webhook event (same event ID) — idempotency check, return 200
- Processing failure — return 5xx, payment processor will retry

**Edge Cases:**
- Payment succeeds but webhook delayed — order shows as pending_payment until webhook arrives
- Refund processed — webhook triggers refund workflow
- Partial refund — update order totals and item quantities
- Chargeback — webhook triggers dispute workflow, notify support team

---

### WFL-006: Account Deletion / Data Deletion Request

**Description:** User requests deletion of their account and associated data. Handles GDPR/CCPA compliance requirements.

**Trigger:** User submits account deletion request from settings page.

**Key Steps:**
1. User confirms deletion intent (re-authentication required)
2. Server schedules deletion (grace period: 30 days)
3. Server anonymizes or removes personal data immediately (PII fields set to NULL)
4. Server cancels any active subscriptions
5. Server processes pending refunds if applicable
6. Server stores deletion request record with timestamp
7. Server sends confirmation email to user
8. User can cancel deletion during grace period
9. After grace period, server hard-deletes remaining data
10. Server logs deletion for compliance audit

**Failure Points:**
- User has outstanding financial obligations — block deletion until resolved
- User has active subscriptions — cancel subscriptions first, then delete
- User data shared across entities (multi-tenant) — only remove user-specific associations

**Edge Cases:**
- User re-registers with same email during grace period — reactivation versus new account
- Legal hold on user's data — flag account, prevent deletion until hold lifted
- Admin deletion request — same workflow, different authorization check
- Deletion of child account (parental control) — additional authorization required

---

### WFL-007: Content Moderation

**Description:** User-generated content is reviewed for compliance with terms of service. Covers automated and manual moderation flows.

**Trigger:** User submits content (review, comment, image, etc.).

**Key Steps:**
1. Content is submitted by user
2. Automated moderation scan runs:
   a. Toxicity check (ML model)
   b. Spam detection (heuristic + ML)
   c. PII/credit card detection (regex + ML)
   d. Image NSFW detection (if applicable)
3. If auto-moderated: content is approved, rejected, or flagged for review
4. If flagged: content enters manual review queue
5. Moderator reviews content in queue
6. Moderator approves, rejects, or escalates
7. If rejected: user is notified with reason (and appeal option)
8. If approved after manual review: content is published
9. All moderation actions are logged for audit

**Failure Points:**
- ML model service unavailable — fall back to regex-only checks, flag edge cases for manual review
- Manual review queue backlogged — implement SLA, auto-approve low-risk content after threshold
- Moderator action not applied due to race condition — optimistic locking on content record

**Edge Cases:**
- User edits previously approved content — re-runs moderation workflow
- Content reported by another user — adds to review queue with priority flag
- Appeal of rejected content — goes to different moderator for second review
- Bulk content submission — rate limited to prevent spam attacks

---

### WFL-008: Notification Delivery

**Description:** System sends notifications to users via configured channels (email, push, in-app, SMS).

**Trigger:** System event that requires user notification.

**Key Steps:**
1. Notification event is published to notification queue
2. Notification service reads event and determines target users
3. Notification service builds notification content (templates + variables)
4. Notification service checks user's notification preferences
5. For each enabled channel:
   a. Email: render template, send via transactional email service
   b. Push: send via Firebase / APNs
   c. In-app: write to notifications table, mark as unread
   d. SMS: send via SMS gateway
6. Notification delivery status is tracked
7. Failed deliveries are retried (3 attempts with backoff)
8. Final failures are logged and suppressed (no alert for individual notification failure)
9. User's unread count is updated

**Failure Points:**
- Email service rate limits — queue and retry with backoff
- Push notification service unavailable — store and retry, or mark as pending
- User has no enabled channels — log and skip

**Edge Cases:**
- User unsubscribes from notification type — check preferences at delivery time
- Batch notifications (digest mode) — aggregate and send on schedule
- Notification for deleted content — skip or include "content removed" note
- Language preference — render template in user's preferred language

---

## 4. Workflow Dependency Map

### Inter-Workflow Dependencies

```
WFL-001 (Registration)
  └── Prerequisite: None
  └── Triggers: WFL-006 (if user later deletes account), WFL-008 (welcome email)

WFL-002 (Login)
  └── Prerequisite: WFL-001
  └── Triggers: WFL-008 (suspicious login alert)

WFL-003 (Password Reset)
  └── Prerequisite: WFL-001
  └── Triggers: WFL-008 (confirmation email), WFL-002 (re-login)

WFL-004 (Checkout)
  └── Prerequisite: WFL-001, WFL-002
  └── Triggers: WFL-005 (payment processing), WFL-008 (order confirmation)

WFL-005 (Payment Webhook)
  └── Prerequisite: WFL-004
  └── Triggers: WFL-008 (payment confirmation/failure)

WFL-006 (Account Deletion)
  └── Prerequisite: WFL-001, WFL-002
  └── Dependencies: WFL-005 (cancel subscriptions), WFL-008 (confirmation)

WFL-007 (Content Moderation)
  └── Prerequisite: WFL-001, WFL-002
  └── Triggers: WFL-008 (moderation result notification)

WFL-008 (Notification Delivery)
  └── Prerequisite: WFL-001
  └── Consumed by: All workflows
```

### Dependency Graph (Text-Based)

```
                 ┌──────────────┐
                 │  WFL-001     │
                 │ Registration │
                 └──────┬───────┘
                        │
          ┌─────────────┼──────────────┐
          │             │              │
          ▼             ▼              ▼
   ┌────────────┐ ┌────────────┐ ┌──────────────┐
   │ WFL-002    │ │ WFL-003    │ │ WFL-008      │
   │ Login      │ │ PW Reset   │ │ Notifications │
   └──────┬─────┘ └──────┬─────┘ └──────┬───────┘
          │              │              │
          ▼              │              │
   ┌────────────┐        │              │
   │ WFL-004    │◄───────┘              │
   │ Checkout   │                       │
   └──────┬─────┘                       │
          │                             │
          ▼                             │
   ┌────────────┐                       │
   │ WFL-005    │                       │
   │ Payments   │                       │
   └──────┬─────┘                       │
          │                             │
          ▼                             │
   ┌────────────┐                       │
   │ WFL-006    │◄──────────────────────┘
   │ Deletion   │
   └────────────┘
```

---

## 5. Cross-Cutting Workflow Concerns

### Authentication

- Every API workflow verifies the access token in the Authorization header.
- Token validation checks: signature, expiry, issuer, audience, revocation status.
- If token is invalid or expired, the workflow returns 401 and does not proceed.
- If user account is suspended/disabled, the workflow returns 403 regardless of token validity.

### Authorization

- Every workflow checks the user's role and permissions before executing.
- Authorization is checked at the boundary (API gateway or middleware), not deep in business logic.
- Permission model: Role-Based Access Control (RBAC) with optional Attribute-Based Access Control (ABAC) for fine-grained rules.
- Permission denial returns 403 Forbidden with a message that does not reveal whether the resource exists.

### Logging

- Every workflow logs its start, key milestones, and completion (success or failure).
- Log format is structured JSON with fields: `workflow_id`, `correlation_id`, `user_id`, `action`, `duration_ms`, `status`, `error`.
- Correlation ID flows through all steps and is included in all log entries, metrics, and traces.
- PII is never logged directly — use masked or hashed values.
- Log level: DEBUG for development, INFO for production, WARN for recoverable errors, ERROR for failures.

### Error Handling

- **Validation errors:** Return 400 with field-level error messages.
- **Authentication errors:** Return 401 with generic message.
- **Authorization errors:** Return 403 with generic message.
- **Not found:** Return 404 with resource type (no ID in message to prevent enumeration).
- **Conflict:** Return 409 when resource state conflicts with the request.
- **Rate limited:** Return 429 with Retry-After header.
- **Internal errors:** Return 500 with correlation ID (no stack traces in production).
- **Dependency failures:** Return 503 if a required downstream service is unavailable.

### Metrics

Every workflow emits the following metrics:
- `workflow.duration` — histogram of execution time (latency)
- `workflow.count` — counter of executions (by workflow ID, status, error code)
- `workflow.concurrent` — gauge of currently in-flight executions
- `step.duration` — histogram of individual step execution time
- `step.count` — counter of step executions (by step name, status)

### Observability

- **Distributed tracing:** Every workflow step is instrumented with OpenTelemetry spans.
- **Health checks:** Each workflow's critical dependencies have health checks that report status at /health endpoint.
- **Alerting:** PagerDuty alerts are configured for:
  - Workflow error rate > 1% over 5 minutes
  - Workflow p99 latency > 3x baseline over 5 minutes
  - Workflow completely failing (100% errors) for > 1 minute
- **Dashboards:** Grafana dashboards exist for each workflow showing throughput, latency, error rate, and dependency health.

### Data Consistency

- **Synchronous workflows** use database transactions with ACID guarantees.
- **Asynchronous workflows** implement the outbox pattern: events are written to an outbox table in the same transaction as the data mutation.
- **Distributed workflows** use the Saga pattern with compensating transactions for rollback.
- **Idempotency:** Every workflow that can receive duplicate requests implements idempotency (idempotency key stored with result, TTL).

---

## Appendix A: Workflow Review Checklist

- [ ] Workflow ID follows naming convention
- [ ] All triggers documented
- [ ] All inputs documented with validation rules
- [ ] All steps documented with success/failure conditions
- [ ] Error handling defined for every failure point
- [ ] Edge cases identified and handled
- [ ] Dependencies documented with fallback strategies
- [ ] Events documented with payload schema
- [ ] Non-functional requirements defined
- [ ] Test coverage mapped
- [ ] Security review completed (authz checks at every boundary)
- [ ] Performance impact assessed
- [ ] Monitoring and alerting configured

## Appendix B: Change Log

| Date | Author | Change | Rationale |
|---|---|---|---|
| [DATE] | [AUTHOR] | Initial creation | Workflow baseline |
| [DATE] | [AUTHOR] | [CHANGE] | [RATIONALE] |
