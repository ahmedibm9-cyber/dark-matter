# Workflow Map — Complete System Workflow Documentation

> **Version:** 1.0.0
> **Last Updated:** 2026-06-25
> **Status:** Active

---

## Table of Contents

1. [Workflow Dependency Diagram](#workflow-dependency-diagram)
2. [Workflow Notation](#workflow-notation)
3. [Core Workflows](#core-workflows)
   - [WF-001: User Registration](#wf-001-user-registration)
   - [WF-002: Authentication & Login](#wf-002-authentication--login)
   - [WF-003: Password Reset](#wf-003-password-reset)
   - [WF-004: User Profile Management](#wf-004-user-profile-management)
   - [WF-005: Data Ingestion](#wf-005-data-ingestion)
   - [WF-006: Data Processing Pipeline](#wf-006-data-processing-pipeline)
   - [WF-007: Report Generation](#wf-007-report-generation)
   - [WF-008: Scheduled Reporting](#wf-008-scheduled-reporting)
   - [WF-009: Webhook Processing](#wf-009-webhook-processing)
   - [WF-010: Notification Delivery](#wf-010-notification-delivery)
   - [WF-011: Account Deletion (GDPR)](#wf-011-account-deletion-gdpr)
   - [WF-012: Data Export](#wf-012-data-export)
   - [WF-013: Database Migration](#wf-013-database-migration)
   - [WF-014: Deployment Pipeline](#wf-014-deployment-pipeline)
   - [WF-015: Rollback Procedure](#wf-015-rollback-procedure)
   - [WF-016: Health Check & Monitoring](#wf-016-health-check--monitoring)
   - [WF-017: Backup & Recovery](#wf-017-backup--recovery)
   - [WF-018: API Rate Limiting](#wf-018-api-rate-limiting)
   - [WF-019: Session Management](#wf-019-session-management)
   - [WF-020: Audit Logging](#wf-020-audit-logging)
4. [Workflow Interactions Matrix](#workflow-interactions-matrix)

---

## Workflow Dependency Diagram

```
                    ┌──────────────────────────────────────┐
                    │           WF-013: Database            │
                    │           Migration                   │
                    └────────────┬─────────────────────────┘
                                 │
                    ┌────────────▼─────────────────────────┐
                    │           WF-017: Backup &            │
                    │           Recovery                    │
                    └────────────┬─────────────────────────┘
                                 │
┌───────────────────┐    ┌──────▼──────────────────────┐    ┌───────────────────┐
│  WF-014: Deploy   │◄──►│        APPLICATION          │◄──►│  WF-015: Rollback │
│  Pipeline         │    │        RUNTIME               │    │  Procedure        │
└────────┬──────────┘    └──────────────────────────────┘    └────────┬──────────┘
         │                              │                             │
         │                              │
         │              ┌───────────────┴────────────────┐
         │              │                                │
         ▼              ▼                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            REQUEST LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  WF-002: Auth & Login     │  WF-001: Registration     │  WF-018: Rate Limiting│
│  WF-003: Password Reset   │  WF-019: Session Mgmt     │  WF-020: Audit Logging│
└───────────┬──────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CORE BUSINESS LAYER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                             ┌──────────────────────┐                       │
│     WF-004: User Profile   │  WF-005: Data         │                       │
│     Management             │  Ingestion            │                       │
│                             └──────────┬───────────┘                       │
│                             ┌──────────▼───────────┐                       │
│                             │  WF-006: Data         │                       │
│                             │  Processing Pipeline  │                       │
│                             └──────────┬───────────┘                       │
│                             ┌──────────▼───────────┐                       │
│                             │  WF-007: Report       │                       │
│                             │  Generation           │                       │
│                             └──────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INTEGRATION & OUTPUT LAYER                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  WF-008: Scheduled  │  WF-009: Webhook   │  WF-010: Notifications          │
│  Reporting          │  Processing        │  Delivery                       │
│  WF-011: Acct Del   │  WF-012: Data      │                                 │
│  (GDPR)             │  Export            │                                 │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          OBSERVABILITY LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  WF-016: Health Check & Monitoring                                         │
│  WF-020: Audit Logging                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Workflow Notation

Each workflow is documented with the following structure:

- **Workflow ID:** Unique identifier (WF-NNN)
- **Workflow Name:** Human-readable name
- **Description:** One-paragraph summary of what the workflow accomplishes
- **Trigger:** What initiates this workflow (user action, system event, scheduled)
- **Actors:** Who or what participates (User, System, Admin, External Service)
- **Inputs:** Data and parameters required
- **Preconditions:** Conditions that must be true before execution
- **Processing Steps:** Numbered sequence of operations
- **Outputs:** Data produced and side effects
- **Postconditions:** Expected state after successful execution
- **Dependencies:** Other workflows, services, or systems required
- **Failure Points:** Known failure modes with error handling
- **Edge Cases:** Non-standard scenarios that must be handled
- **Performance Budget:** Maximum acceptable execution time/latency
- **Related Files:** Source files involved in the workflow

---

## Core Workflows

---

### WF-001: User Registration

**Description:** New user creates an account by providing email, password, and profile information. System validates input, creates user record, sends verification email, and establishes initial session.

**Trigger:** User submits registration form on web or mobile app.

**Actors:** User, System, Email Service (SendGrid/NodeMailer)

**Inputs:**
- Email address (validated format)
- Password (minimum strength requirements)
- Full name
- Optional: company, role, phone number
- reCAPTCHA token (bot prevention)

**Preconditions:**
- Email is not already registered
- Password meets complexity requirements
- reCAPTCHA validation passes
- System is accepting new registrations (not in maintenance mode)

**Processing Steps:**

```
Step 1:  [Validate Input]        Validate email format, password strength,
                                  name length, and reCAPTCHA token.
Step 2:  [Check Duplicate]       Query user table for existing email. If
                                  found, return 409 Conflict.
Step 3:  [Hash Password]         Generate bcrypt hash of password with 12
                                  salt rounds.
Step 4:  [Create User Record]    INSERT new user record with status=PENDING,
                                  role=USER, email, passwordHash, name.
Step 5:  [Generate Verification]  Create email verification token (JWT,
                                  24h expiry). Store hash in DB.
Step 6:  [Send Verification]      Send verification email via notification
                                  service with link containing token.
Step 7:  [Generate Tokens]       Generate access token (15min) and refresh
                                  token (7 days) for immediate session.
Step 8:  [Log Audit Event]       Record registration event with timestamp,
                                  email, IP address, user agent.
Step 9:  [Return Response]       Return 201 Created with user profile
                                  (excl. passwordHash) and tokens.
```

**Outputs:**
- New user record in database (status: PENDING)
- Email verification token in database
- Verification email sent to user's inbox
- Access token and refresh token in response
- Audit log entry created

**Postconditions:**
- User is created but cannot access full features until email verified
- Session is established (user is logged in)
- Verification email is queued for delivery

**Dependencies:** WF-002 (uses auth service), WF-010 (notification service), WF-020 (audit logging)

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Duplicate email | User cannot register | Return 409 with "email already registered" message (don't reveal if account exists) |
| Weak password | Security vulnerability | Reject with specific password requirements |
| Email service down | Verification not sent | Queue email for retry. Allow login with limited access. |
| Database write failure | User not created | Return 500. Log error. No partial state. |
| reCAPTCHA failure | Bot registration | Reject with "verification failed" |
| Race condition on email | Duplicate accounts | Use unique constraint + transaction |

**Edge Cases:**
- User registers with same email moments apart → transaction prevents duplicate
- Email contains Unicode or special characters → normalize before storage
- User closes browser before confirmation → email still sent, account exists
- Registration during database migration → handle gracefully with maintenance page
- International characters in name → store as UTF-8, validate length in bytes
- User registers with + alias (Gmail) → treat as distinct or normalized per policy

**Performance Budget:** < 2 seconds end-to-end; < 500ms for token generation

**Related Files:**
- `src/api/routes/auth.routes.ts`
- `src/api/controllers/auth.controller.ts`
- `src/services/auth.service.ts`
- `src/db/models/user.model.ts`
- `src/utils/hash.ts`
- `src/utils/jwt.ts`
- `src/utils/response.ts`

---

### WF-002: Authentication & Login

**Description:** User authenticates with email and password to obtain access and refresh tokens for subsequent API calls.

**Trigger:** User submits login form with credentials.

**Actors:** User, System, Rate Limiter

**Inputs:**
- Email address
- Password
- Optional: 2FA code (if enabled)
- Device fingerprint / user agent

**Preconditions:**
- Account exists
- Account is not locked
- Account is not deleted/suspended
- IP is not blocked
- Rate limit not exceeded

**Processing Steps:**

```
Step 1:  [Rate Limit Check]      Check IP-based and email-based rate limits.
                                  5 failed attempts in 15 minutes triggers
                                  temporary block.
Step 2:  [Lookup User]           Query user by email. If not found, return
                                  generic "invalid credentials" error.
Step 3:  [Check Account Status]  Verify account is active, not suspended,
                                  not deleted. If pending email verification,
                                  allow login with restrictions.
Step 4:  [Verify Password]       Compare submitted password against stored
                                  bcrypt hash using constant-time comparison.
Step 5:  [Check 2FA]             If 2FA enabled, verify TOTP/backup code.
Step 6:  [Check Lockout]         If too many failed attempts, increment
                                  counter. Apply exponential lockout.
Step 7:  [Reset Failed Counters] On success, reset failed attempt counters.
Step 8:  [Generate Tokens]       Create access token (JWT, 15min expiry,
                                  signed with RS256). Create refresh token
                                  (opaque, 7 day expiry, stored in DB).
Step 9:  [Create Session]        Create session record with device info,
                                  IP, last activity timestamp.
Step 10: [Log Audit Event]       Record successful login with metadata.
Step 11: [Return Response]       Return 200 with access token, refresh token,
                                  token type, expiry timestamps, user profile.
```

**Outputs:**
- Access token (in response body and Set-Cookie header)
- Refresh token (in response body and httpOnly cookie)
- Session record in database
- Audit log entry (success or failure)

**Postconditions:**
- User is authenticated for subsequent requests
- Session is active and tracked
- Failed attempt counters are reset (on success) or incremented (on failure)

**Dependencies:** WF-020 (audit logging), WF-018 (rate limiting), WF-019 (session management)

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Invalid credentials | Authentication fails | Generic error "invalid email or password" — never reveal which is wrong |
| Account locked | User cannot log in | Show lockout message with remaining time. Offer password reset. |
| 2FA code expired | Cannot complete 2FA | Show "code expired" and let user request new code |
| Rate limit hit | Temporarily blocked | Return 429 with Retry-After header |
| Token signing key rotated | Existing tokens invalid | Implement key rotation with grace period. Validate against current + previous key. |

**Edge Cases:**
- User has multiple active sessions (mobile + desktop) → each session independent
- Token expired mid-request → client should use refresh token to get new access token
- Concurrent login attempts from different IPs → could be credential stuffing
- Password changed while other sessions active → invalidate all other sessions
- Account deleted but login attempted → return generic error, don't reveal account status
- User logged in on compromised device → implement "logout all devices" feature

**Performance Budget:** < 1 second end-to-end; < 300ms for password verification

**Related Files:**
- `src/api/routes/auth.routes.ts`
- `src/api/controllers/auth.controller.ts`
- `src/services/auth.service.ts`
- `src/api/middleware/auth.middleware.ts`
- `src/api/middleware/rate-limit.middleware.ts`
- `src/utils/jwt.ts`
- `src/utils/hash.ts`
- `src/db/models/user.model.ts`

---

### WF-003: Password Reset

**Description:** User requests a password reset via email link. System generates a time-limited reset token, sends email, and allows secure password change.

**Trigger:** User clicks "Forgot Password" and submits email.

**Actors:** User, System, Email Service

**Inputs:**
- Email address
- (Later) Reset token + new password

**Preconditions:**
- Account exists for the submitted email
- User has access to the registered email inbox

**Processing Steps:**

```
REQUEST PHASE:
Step 1:  [Validate Email]        Validate email format exists in system.
Step 2:  [Rate Limit]            Check per-email and per-IP rate limits for
                                  password reset requests (max 3 per hour).
Step 3:  [Generate Reset Token]  Create cryptographically random token with
                                  1-hour expiry. Store hashed token + expiry
                                  in database.
Step 4:  [Send Reset Email]      Send email with reset link containing the
                                  raw token (hashed token stored server-side).
Step 5:  [Log Event]             Record password reset request in audit log.
Step 6:  [Return Response]       Return 200 (always, even if email not found
                                  — prevents email enumeration).

EXECUTION PHASE:
Step 7:  [Validate Token]        Hash the submitted token, compare against
                                  stored hash. Check expiry.
Step 8:  [Validate New Password] Check new password meets strength requirements.
Step 9:  [Hash New Password]     Generate new bcrypt hash.
Step 10: [Update Password]       UPDATE user record with new password hash.
Step 11: [Invalidate Sessions]   Delete all sessions for this user except
                                  current one (if authenticated).
Step 12: [Invalidate Token]      Delete the reset token (one-time use).
Step 13: [Notify User]           Send confirmation email "Your password was
                                  changed" for security awareness.
Step 14: [Log Event]             Record password change in audit log.
Step 15: [Return Response]       Return 200 with success message.
```

**Outputs:**
- Reset email sent (request phase)
- Password updated in database (execution phase)
- All sessions invalidated (user must log in again)
- Confirmation email sent
- Audit log entries

**Postconditions:**
- User can log in with new password
- Old password no longer works
- All active sessions (except current) are terminated
- Reset token is consumed and cannot be reused

**Dependencies:** WF-002 (login with new password), WF-010 (notification), WF-020 (audit logging)

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Token expired | User cannot reset | Offer to request new reset link |
| Token already used | Cannot reset with same token | Show "link already used, request a new one" |
| Email service down | No reset email sent | Queue and retry. Show "email sent" anyway (don't reveal delivery status). |
| Weak new password | Security vulnerability | Reject with strength requirements |
| User enters wrong email | No reset received | Don't reveal whether email exists |
| Token tampered/invalid | Cannot reset | Show generic error, log attempted abuse |

**Edge Cases:**
- User requests multiple resets → only last token is valid (invalidate previous)
- Attacker requests reset for someone else's account → legitimate user receives email, can ignore
- Token leaked via email compromise → time-limited window, attacker must act fast
- User resets password but doesn't remember → can request another reset
- Email delivery delayed beyond token expiry → user needs to request new link

**Performance Budget:** < 500ms for each phase

**Related Files:**
- `src/api/routes/auth.routes.ts`
- `src/api/controllers/auth.controller.ts`
- `src/services/auth.service.ts`
- `src/db/models/user.model.ts`
- `src/utils/jwt.ts`
- `src/utils/hash.ts`
- `src/services/notification.service.ts`

---

### WF-004: User Profile Management

**Description:** Authenticated user views and updates their profile information, preferences, and account settings.

**Trigger:** User navigates to profile page or submits profile update form.

**Actors:** User (authenticated), System, Admin (for user management)

**Inputs:**
- Authentication token (identifies user)
- Profile fields: name, phone, avatar, timezone, preferences
- (Admin) Target user ID for admin operations

**Preconditions:**
- User is authenticated
- User exists and account is active
- (Profile update) Valid input data

**Processing Steps:**

```
VIEW PROFILE:
Step 1:  [Authenticate]          Verify access token, extract user ID.
Step 2:  [Authorize]             Check user can access requested profile
                                  (own profile OR admin role).
Step 3:  [Fetch User]            Query user record with selected fields
                                  (exclude passwordHash, security fields).
Step 4:  [Return Profile]        Return 200 with user profile data.

UPDATE PROFILE:
Step 5:  [Validate Inputs]       Validate updated fields against schemas
                                  (name length, phone format, etc.).
Step 6:  [Check Uniqueness]      If email changed, verify new email not taken.
Step 7:  [Update Record]         UPDATE user record with new values.
Step 8:  [Clear Cache]           Invalidate cached user profile.
Step 9:  [Log Event]             Record profile update in audit log.
Step 10: [Return Updated Profile] Return 200 with updated profile data.

AVATAR UPLOAD:
Step 11: [Validate File]         Check file type (image/*), size (< 5MB),
                                  dimensions, and scan for malware.
Step 12: [Process Image]         Resize to standard dimensions (200x200),
                                  convert to WebP, generate thumbnail.
Step 13: [Upload Storage]        Store in S3/CDN with unique filename.
Step 14: [Update Avatar URL]     Update user record with new avatar URL.
Step 15: [Delete Old Avatar]     Remove previous avatar from storage.
Step 16: [Log Event]             Record avatar change in audit log.
```

**Outputs:**
- User profile data (view)
- Updated user record (update)
- New avatar stored in CDN with old avatar cleaned up
- Audit log entries
- Cache invalidation event

**Postconditions:**
- Profile data is current in database
- Cache is updated (or invalidated)
- Old avatar is deleted (no orphaned storage)
- User sees confirmation of changes

**Dependencies:** WF-002 (authentication), WF-020 (audit logging), WF-019 (session management)

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Email change conflicts | Cannot update email | Return 409 "email already in use" |
| Avatar too large | Upload rejected | Return 413 with max size limit |
| Malicious file upload | Security risk | Scan with ClamAV. Reject with 400. |
| Storage service unavailable | Avatar cannot be saved | Queue upload for retry. Return 202 with placeholder. |
| Cache invalidation fails | Stale data served | Log error. TTL will eventually expire. |

**Edge Cases:**
- User changes email -> should verify new email if not using OAuth
- User uploads transparent PNG -> ensure avatar has visible background option
- User sets timezone -> all displayed timestamps should respect this
- Admin updates another user's profile -> audit log must record admin ID
- User deletes avatar -> set to default avatar, don't show broken image

**Performance Budget:** < 500ms for view; < 2s for avatar upload

**Related Files:**
- `src/api/routes/user.routes.ts`
- `src/api/controllers/user.controller.ts`
- `src/services/user.service.ts`
- `src/db/models/user.model.ts`
- `src/services/cache.service.ts`

---

### WF-005: Data Ingestion

**Description:** Ingest data from various sources (API upload, file upload, webhook, batch import). Validate, sanitize, and store in staging area for processing.

**Trigger:** API POST request with data payload, file upload, webhook reception, or scheduled batch import.

**Actors:** External System, API Consumer, System, Queue Worker

**Inputs:**
- Data payload (JSON, CSV, XML, Parquet)
- Source metadata (source type, timestamp, schema version)
- Optional: file attachment, webhook payload
- Authentication/API key

**Preconditions:**
- Source is authenticated and authorized
- Data format matches expected schema
- System has capacity for ingestion (backpressure check)

**Processing Steps:**

```
Step 1:  [Authenticate Source]   Verify API key or JWT token for the
                                  submitting system/user.
Step 2:  [Validate Payload]      Validate data format, schema, required
                                  fields, data types using Zod schema.
Step 3:  [Sanitize Data]         Strip dangerous content, escape strings,
                                  normalize encoding. Reject malicious input.
Step 4:  [Check Duplicates]      Apply deduplication logic based on
                                  fingerprint hash. Return 409 if duplicate.
Step 5:  [Size Check]            Verify payload size within limits (10MB
                                  default). Stream to disk for large payloads.
Step 6:  [Store in Staging]      INSERT raw data into staging table with
                                  status=RECEIVED, source metadata, timestamp.
Step 7:  [Enqueue Processing]    Push job to processing queue with reference
                                  to staging record ID.
Step 8:  [Return Ack]            Return 202 Accepted with ingestion ID and
                                  estimated processing time.
Step 9:  [Log Event]             Record ingestion in audit log with volume
                                  metrics and source info.
```

**Outputs:**
- Staging record(s) in database (status: RECEIVED)
- Processing job in queue
- Ingestion ID returned to caller
- Audit log entry

**Postconditions:**
- Data is safely stored in staging (not yet in production tables)
- Processing pipeline is triggered asynchronously
- Caller has tracking ID for status queries

**Dependencies:** WF-006 (processing pipeline), WF-007 (triggers report if configured), WF-020 (audit logging)

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Invalid schema | Data rejected | Return 422 with validation errors |
| Duplicate data | Data integrity risk | Return 409 or upsert per config |
| Payload too large | Memory pressure | Stream to disk, reject at 50MB |
| Queue unavailable | Data not processed | Store with status=PENDING_RETRY, retry with backoff |
| Database unavailable | Data lost | Return 503. Use circuit breaker. |
| Malicious payload (XSS/SQLi) | Security breach | Sanitize input, reject suspicious patterns |

**Edge Cases:**
- Empty payload -> accept with 0 records processed, return warning
- Unicode edge cases (zero-width characters, BOM) -> normalize to NFC
- Extremely large batch (>1M records) -> chunk into sub-batches with progress tracking
- Schema version mismatch -> apply migration or reject with schema version info
- Concurrent ingestion of same data -> deduplication must be atomic
- Network interruption mid-stream -> use resumable upload with range headers

**Performance Budget:** < 5 seconds for standard payload; streaming for large

**Related Files:**
- `src/api/routes/data.routes.ts`
- `src/api/controllers/data.controller.ts`
- `src/services/data.service.ts`
- `src/services/queue.service.ts`
- `src/db/models/data.model.ts`

---

### WF-006: Data Processing Pipeline

**Description:** Process ingested data through transformation, validation, enrichment, and loading stages. Produces clean, validated business data.

**Trigger:** Job enqueued by WF-005 (Data Ingestion) or manual reprocessing request.

**Actors:** Queue Worker, System, External Enrichment Services

**Inputs:**
- Staging record ID
- Raw data payload
- Processing configuration (transform rules, validation rules)
- Source metadata

**Preconditions:**
- Staging record exists with status=RECEIVED or PENDING_RETRY
- Worker capacity available
- Required enrichment services are reachable

**Processing Steps:**

```
STAGE 1 - TRANSFORM:
Step 1:  [Claim Job]             Dequeue job, mark staging record as
                                  PROCESSING, set started_at timestamp.
Step 2:  [Load Raw Data]         Retrieve raw data from staging table.
Step 3:  [Apply Transforms]      Execute transformation rules: field mapping,
                                  type conversion, normalization, aggregation.
Step 4:  [Validate Transformed]  Validate transformed data against business
                                  rules and target schema.

STAGE 2 - ENRICH:
Step 5:  [Geo Enrichment]        If applicable, resolve geolocation data.
Step 6:  [Reference Enrichment]  Look up related entities, join foreign keys.
Step 7:  [Calculate Fields]      Compute derived fields, aggregations.

STAGE 3 - LOAD:
Step 8:  [Open Transaction]      BEGIN transaction for atomic load.
Step 9:  [Write Production]      INSERT/UPDATE production tables with
                                  validated data.
Step 10: [Update Staging]        Mark staging record as status=COMPLETED,
                                  set completed_at timestamp.
Step 11: [Commit Transaction]    COMMIT transaction.
Step 12: [Post-Process]          Trigger downstream workflows (reports,
                                  notifications, webhooks).

ERROR HANDLING:
Step 13: [On Failure]            If any step fails, mark staging as FAILED,
                                  record error details, rollback transaction.
Step 14: [Retry Logic]           If retryable failure, increment retry count,
                                  set status=PENDING_RETRY, schedule retry
                                  with exponential backoff.
Step 15: [Dead Letter]           After max retries (3), move to dead letter
                                  queue for manual intervention.
```

**Outputs:**
- Production data records created/updated
- Staging record status updated (COMPLETED/FAILED)
- Processing metrics captured (duration, record count, error count)
- Downstream workflows triggered
- Audit log entries

**Postconditions:**
- Data is available in production tables
- Original raw data preserved in staging for traceability
- Processing metrics logged for observability
- Failures are captured with detailed error info for debugging

**Dependencies:** WF-005 (input from ingestion), WF-007 (triggers report generation), WF-009 (triggers webhooks), WF-020 (audit logging)

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Transformation error | Records fail to process | Skip record, log error, continue batch |
| Enrichment service down | Incomplete data | Skip enrichment, mark as unenriched, retry later |
| Production DB constraint violation | Load failure | Rollback transaction, log exact constraint violation |
| Transaction too large | DB lock contention | Batch into smaller chunks (1000 records) |
| Worker crash mid-process | Orphaned processing state | Use heartbeat + timeout to detect and reset stuck jobs |
| Data quality below threshold | Trust issues | Implement quality gates: reject if >5% failure rate |

**Edge Cases:**
- Processing takes longer than queue visibility timeout -> extend lease, heartbeat
- Same record ingested twice -> deduplicate during load stage
- Enrichment returns changed data -> version tracking for audit trail
- Source schema changed between ingestion and processing -> schema version check
- Partial batch failure -> atomic per batch, not per entire job
- Circular reference in data -> detect and reject with clear error

**Performance Budget:** < 30 seconds for standard batch; < 5 minutes for large batch

**Related Files:**
- `src/services/data.service.ts`
- `src/services/queue.service.ts`
- `src/db/models/data.model.ts`
- `src/db/index.ts`

---

### WF-007: Report Generation

**Description:** Generate formatted reports (PDF, CSV, XLSX) from business data with configurable parameters, filters, and scheduling.

**Trigger:** User requests report via API or dashboard, or scheduled trigger.

**Actors:** User, System, Report Worker, Storage Service

**Inputs:**
- Report type (sales, performance, audit, custom)
- Filter parameters (date range, segments, dimensions)
- Output format (PDF, CSV, XLSX)
- Schedule configuration (for recurring reports)
- User ID (for access control and notification)

**Preconditions:**
- User has permission for requested report type
- Required data exists in date range
- System resources available for generation
- Template exists for report type

**Processing Steps:**

```
Step 1:  [Validate Request]      Validate report type, parameters, format.
                                  Check user permissions for data access.
Step 2:  [Check Cache]           Check if identical report exists in cache
                                  and is still fresh. Return cached if valid.
Step 3:  [Queue Generation]      If not cached, enqueue report generation
                                  job with parameters.
Step 4:  [Return Pending]        Return 202 Accepted with report ID and
                                  estimated completion time.
Step 5:  [Worker Claims Job]     Dequeue job. Set status=GENERATING.
Step 6:  [Query Data]            Execute database queries with filters,
                                  aggregations, and sorting.
Step 7:  [Apply Calculations]    Compute totals, averages, percentages,
                                  trends, and derived metrics.
Step 8:  [Build Report]          Populate template with data. Generate
                                  output in requested format using
                                  report engine (PDFKit, ExcelJS, etc.).
Step 9:  [Upload Result]         Upload generated file to storage (S3/CDN)
                                  with signed URL for secure access.
Step 10: [Update Status]         Set report status=COMPLETED, store file
                                  URL and metadata in database.
Step 11: [Notify User]           Send notification (in-app + optional email)
                                  that report is ready.
Step 12: [Log Event]             Record report generation metrics (duration,
                                  size, record count) in audit log.
```

**Outputs:**
- Generated report file in storage
- Report metadata record in database
- Notification to requesting user
- Cache entry for identical future requests

**Postconditions:**
- Report is available for download (default 7-day retention)
- User is notified of completion
- Generation metrics are logged

**Dependencies:** WF-005 (data source), WF-006 (processed data), WF-010 (notification), WF-020 (audit logging)

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| No data in range | Empty report | Generate report with "no data" message, not an error |
| Template rendering error | Report malformed | Log template error. Fall back to simple format. |
| Storage unavailable | Report not saved | Retry with backoff. Keep in memory temporarily. |
| Request timeout | User waiting | Async processing prevents this. Provide progress polling. |
| Memory exhaustion on large report | Worker crash | Stream to disk. Implement row limits with pagination. |

**Edge Cases:**
- Report generation takes hours -> user polls for status, progress percentage
- User cancels generation -> mark job as CANCELLED, clean up partial data
- Same report requested by multiple users -> cache for efficiency
- Report contains PII -> apply access control on download, mask sensitive fields
- Generated file exceeds storage limits -> compress, or split into parts
- Timezone handling in date filters -> convert all timestamps to user's timezone

**Performance Budget:** < 1 minute for standard reports; async for complex

**Related Files:**
- `src/api/routes/report.routes.ts`
- `src/api/controllers/report.controller.ts`
- `src/services/report.service.ts`
- `src/services/queue.service.ts`
- `src/services/cache.service.ts`
- `src/services/notification.service.ts`

---

### WF-008: Scheduled Reporting

**Description:** Automatically generate and distribute reports on a recurring schedule (daily, weekly, monthly).

**Trigger:** Cron schedule or job scheduler (node-cron, Bull repeatable jobs).

**Actors:** Scheduler, System, Email Service, Storage Service

**Inputs:**
- Report definition (type, parameters, format)
- Schedule configuration (cron expression, timezone)
- Distribution list (email recipients)
- Retention policy

**Preconditions:**
- Scheduled report is configured and active
- Source data is available for the period

**Processing Steps:**

```
Step 1:  [Check Schedule]        Scheduler triggers report job at configured
                                  time. Validate schedule is still active.
Step 2:  [Generate Report]       Same as WF-007 steps 5-10. Uses the
                                  predefined parameters from schedule config.
Step 3:  [Check Completion]      Verify report generated successfully.
                                  If not, retry once after 5 minutes.
Step 4:  [Distribute Report]     Send email with report attachment or link
                                  to each recipient in distribution list.
Step 5:  [Archive Report]        Store report in long-term archive if
                                  retention policy requires.
Step 6:  [Cleanup Old Reports]   Delete reports older than retention period.
Step 7:  [Log Delivery Status]   Record delivery status per recipient.
Step 8:  [Alert on Failure]      If generation or delivery fails, alert
                                  system administrators.
```

**Outputs:**
- Generated report archived
- Emails sent to distribution list
- Delivery status tracked per recipient
- Old reports cleaned up

**Postconditions:**
- Recipients receive report at scheduled time
- Failed deliveries are identified and retried
- Report archive is maintained per policy

**Dependencies:** WF-007 (report generation), WF-010 (notification delivery), WF-020 (audit logging)

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Schedule missed (scheduler down) | Report not sent | Catch-up on next interval, check last run timestamp |
| Data not yet available | Empty or stale report | Delay generation by configurable offset. Alert if data still missing. |
| Recipient email invalid | Bounced email | Remove from distribution list after N bounces |
| Archive storage full | Cannot archive | Alert. Rotate oldest archives. |

**Edge Cases:**
- Daylight saving time changes -> schedule may fire early/late. Use UTC internally.
- Holiday when report should not send -> configure holiday calendar
- Multiple schedules fire simultaneously -> queue capacity planning
- Recipient unsubscribes -> remove from distribution list, respect unsubscribe
- Report size exceeds email attachment limit -> send as download link instead

**Performance Budget:** Complete before next schedule interval

**Related Files:**
- `src/services/report.service.ts`
- `src/services/queue.service.ts`
- `src/services/notification.service.ts`
- `src/db/models/report.model.ts`

---

### WF-009: Webhook Processing

**Description:** Receive and process incoming webhooks from external services (payment gateways, email services, CI/CD tools).

**Trigger:** External service sends HTTP POST to webhook endpoint.

**Actors:** External Service, System, Webhook Validator, Queue Worker

**Inputs:**
- HTTP POST payload (format varies by provider)
- Webhook signature header
- Provider identifier
- Event type

**Preconditions:**
- Webhook endpoint is registered and active
- Provider's public key/secret is stored for signature verification

**Processing Steps:**

```
Step 1:  [Identify Provider]     Match endpoint path or header to configured
                                  webhook provider.
Step 2:  [Verify Signature]      Compute HMAC or verify JWT signature using
                                  provider's secret/key. Reject if invalid.
Step 3:  [Check Replay]          Verify webhook ID not already processed
                                  (idempotency check). Return 200 if duplicate.
Step 4:  [Parse Payload]         Parse event payload according to provider
                                  schema. Validate required fields exist.
Step 5:  [Determine Event Type]  Map provider event type to internal event.
Step 6:  [Enqueue Processing]    Push webhook event to processing queue with
                                  idempotency key.
Step 7:  [Acknowledge]           Return 200 OK to provider immediately.
Step 8:  [Process Event]         Worker processes event: update records,
                                  trigger workflows, send notifications.
Step 9:  [Handle Failure]        If processing fails, retry with backoff.
                                  After max retries, alert admin.
```

**Outputs:**
- 200 OK acknowledgment to provider
- Webhook event record in database (for audit)
- Business action executed (payment recorded, email delivered, etc.)
- Alert if processing fails

**Postconditions:**
- Event is acknowledged and processed or queued for retry
- Duplicate events are silently ignored (idempotency)
- Signature verification prevents forged webhooks

**Dependencies:** WF-006 (triggers data processing), WF-010 (notifications), WF-020 (audit logging)

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Invalid signature | Webhook rejected | Return 401. Log for security monitoring. |
| Replay attack | Duplicate processing | Idempotency key prevents re-execution |
| Provider sends duplicate | Over-processing | Return 200 for duplicates (idempotency check) |
| Processing queue full | Event delayed | Buffer in database. Alert on queue depth. |
| Provider expects 200 fast | Timeout | Acknowledge immediately, process async. |
| Schema change from provider | Parse failure | Version webhook handlers. Alert on parse errors. |

**Edge Cases:**
- Webhook delivered after long delay (>5 min) -> check timestamp, reject if too old
- Provider sends events in wrong order -> process based on event sequence ID
- Multiple webhooks for same entity race condition -> use optimistic locking
- Provider retry storm (>100 requests/min) -> rate limit per provider
- Webhook secret rotation -> support multiple active secrets during transition
- Payload contains escaped Unicode/binary data -> parse with provider-specific decoder

**Performance Budget:** < 100ms to acknowledge; async processing tolerates latency

**Related Files:**
- `src/api/routes/webhook.routes.ts`
- `src/services/webhook.service.ts`
- `src/api/middleware/verify-signature.ts`
- `src/services/queue.service.ts`

---

### WF-010: Notification Delivery

**Description:** Send multi-channel notifications (email, SMS, push, in-app) with template rendering, delivery tracking, and retry logic.

**Trigger:** Business event (user registered, report ready, password changed, data processed, alert triggered).

**Actors:** System, Notification Service, External Providers (SendGrid, Twilio, Firebase)

**Inputs:**
- Recipient(s): user ID, email, phone, device token
- Notification type: template identifier
- Template variables: dynamic data for rendering
- Channel preference: email, SMS, push, in-app
- Priority: high, normal, low

**Preconditions:**
- Recipient has consented to notification channel
- Notification template exists and is compiled
- Provider API is reachable

**Processing Steps:**

```
Step 1:  [Check Consent]         Verify recipient has opted in for the
                                  requested channel and notification type.
Step 2:  [Check Rate Limits]     Enforce per-user and per-channel rate limits
                                  (max 10 emails/hour per user).
Step 3:  [Render Template]       Load template, interpolate variables, apply
                                  locale/translation, generate subject line.
Step 4:  [Channel Routing]       Based on user preference and notification
                                  type, select primary channel.
Step 5:  [Send via Provider]     Submit to external provider (SendGrid for
                                  email, Twilio for SMS, Firebase for push).
Step 6:  [Record Delivery]       Create notification record with status=SENT,
                                  provider message ID, timestamp.
Step 7:  [Handle Provider Response] Parse provider response. If rejected,
                                  mark as FAILED, log provider error.
Step 8:  [Track Delivery]        For email/push, track open and click events
                                  via webhook callbacks.
Step 9:  [Retry on Failure]      If transient failure, retry with exponential
                                  backoff (3 attempts, 5min/15min/1hr).
Step 10: [Fallback Channel]      If primary channel fails after retries, try
                                  secondary channel (SMS -> email).
Step 11: [Alert on Total Failure] If all channels exhausted, alert operations.
```

**Outputs:**
- Notification delivered via selected channel
- Notification record in database with delivery status
- Provider message ID for tracking
- Delivery events tracked (sent, delivered, opened, clicked)
- Alert if all delivery attempts fail

**Postconditions:**
- Recipient receives notification (or fallback attempted)
- Delivery status is recorded for analytics
- Failed notifications are retried or escalated

**Dependencies:** WF-020 (audit logging), External providers (SendGrid, Twilio, Firebase)

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Provider API down | Notifications not sent | Queue and retry. Switch to fallback provider if configured. |
| Invalid email address | Bounced | Increment bounce counter. Suppress after N bounces. |
| SMS carrier failure | SMS not delivered | Retry with different carrier route. |
| Push token expired | Push not deliverable | Remove token, fall back to email/SMS. |
| Rate limited by provider | Delayed delivery | Back off, respect Retry-After header. |

**Edge Cases:**
- User changes email/phone mid-send -> send to original address (captured at send time)
- Notification contains sensitive data (password reset link) -> never include in push notification preview
- User in different timezone -> schedule non-urgent notifications for business hours
- Bulk notification to 100K users -> batch processing, rate limit to provider limits
- Unsubscribe link must be in every marketing email -> regulatory requirement (CAN-SPAM)
- Thread notification vs summary -> user preference for real-time vs digest

**Performance Budget:** < 1 second per notification; batch mode for bulk

**Related Files:**
- `src/services/notification.service.ts`
- `src/config/`
- `src/db/models/notification.model.ts`
- `src/db/models/user.model.ts`

---

### WF-011: Account Deletion (GDPR)

**Description:** Complete user account deletion with data erasure, audit trail, and cascading cleanup across all services.

**Trigger:** User requests account deletion via settings or admin initiates deletion.

**Actors:** User, Admin, System, Queue Worker

**Inputs:**
- User ID
- Deletion reason (optional, for analytics)
- Admin ID (if admin-initiated)
- Confirmation token (user-initiated requires re-authentication)

**Preconditions:**
- User is authenticated or admin has authority
- User has confirmed deletion (second confirmation step)
- No pending financial transactions or legal holds
- Data retention policy is defined

**Processing Steps:**

```
Step 1:  [Authenticate]          Verify user identity. Require recent
                                  re-authentication for sensitive operation.
Step 2:  [Validate Eligibility]  Check for: pending transactions, active
                                  subscriptions, legal holds, data retention
                                  obligations. Block deletion if any apply.
Step 3:  [Confirm Deletion]      Display what will be deleted, what will be
                                  retained (audit logs, financial records).
                                  Require explicit confirmation.
Step 4:  [Anonymize User Data]   Replace PII fields with anonymized values:
                                  email -> deleted-{userId}@domain.com
                                  name -> "Deleted User"
                                  phone -> NULL
                                  avatar -> default
Step 5:  [Cascade Deletion]      Queue jobs for each related service:
                                  - Delete sessions
                                  - Delete API tokens
                                  - Remove from mailing lists
                                  - Delete notification preferences
                                  - Delete file uploads
Step 6:  [Retain Legal Records]  Preserve audit logs, transaction history,
                                  and any records required by law (read-only,
                                  anonymized reference).
Step 7:  [Notify User]           Send confirmation email "Your account has
                                  been deleted."
Step 8:  [Invalidate Sessions]   Log out all active sessions immediately.
Step 9:  [Log Audit Event]       Record deletion in audit log with retention
                                  per regulatory requirements.
Step 10: [Return Confirmation]   Return 200 with deletion confirmation.
```

**Outputs:**
- User account anonymized (not fully deleted — referential integrity)
- PII removed from all systems
- Sessions invalidated
- Confirmation sent to user
- Audit log entry (retained per policy)

**Postconditions:**
- User cannot log in (anonymized credentials)
- User data is irreversibly anonymized
- Legal/financial records preserved with anonymized references
- Re-activation is not possible (must create new account)

**Dependencies:** WF-002 (authentication), WF-004 (profile management), WF-019 (session management), WF-020 (audit logging)

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Active subscription | Cannot delete | Inform user to cancel subscription first |
| Legal hold active | Cannot delete | Inform user. Flag for admin review. |
| Cascade deletion partial failure | Orphaned data | Log errors. Retry failed jobs. Alert ops. |
| Anonymization incomplete | PII leaked | Verify anonymization in audit step. Revert if incomplete. |

**Edge Cases:**
- User re-registers with same email after deletion -> allowed (old record is anonymized)
- GDPR right to be forgotten vs legal retention -> retain anonymized records only
- User has data in third-party integrations -> must send deletion request to partners
- User has team/org memberships -> remove from teams, transfer ownership or disband
- Deletion during active session -> immediate logout, all tokens invalidated
- Data stored in backups -> back up then purge on next backup cycle

**Performance Budget:** < 5 seconds for user-facing response; async cleanup may take hours

**Related Files:**
- `src/api/routes/user.routes.ts`
- `src/api/controllers/user.controller.ts`
- `src/services/user.service.ts`
- `src/db/models/user.model.ts`
- `src/services/queue.service.ts`

---

### WF-012: Data Export

**Description:** Export user data in portable format (JSON, CSV) for data portability compliance (GDPR Article 20).

**Trigger:** User requests data export from privacy settings. Admin triggers bulk export.

**Actors:** User, System, Export Worker, Storage Service

**Inputs:**
- User ID
- Export scope (all data, specific categories)
- Format (JSON, CSV)
- Date range filter (optional)

**Preconditions:**
- User is authenticated
- Export not already in progress (rate limit: 1 per 24 hours)
- System has capacity for export processing

**Processing Steps:**

```
Step 1:  [Rate Limit Check]      Verify user hasn't requested export in
                                  last 24 hours. Return 429 if exceeded.
Step 2:  [Gather Data Sources]   Identify all data categories associated
                                  with user: profile, activity, content,
                                  communications, transactions, preferences.
Step 3:  [Query Each Source]     For each category, query data with user
                                  ID filter. Use cursor-based pagination
                                  for large datasets.
Step 4:  [Assemble Export]       Compile all data into requested format.
                                  Package as ZIP archive with manifest file
                                  describing contents.
Step 5:  [Upload Export]         Upload ZIP to secure storage with
                                  expiring URL (7 days).
Step 6:  [Notify User]           Send email with download link when ready.
Step 7:  [Log Event]             Record export in audit log (GDPR compliance).
Step 8:  [Cleanup]               Schedule deletion of export file after
                                  expiry period.
```

**Outputs:**
- ZIP archive containing user data in portable format
- Manifest file describing data categories
- Download link sent to user email
- Audit log entry

**Postconditions:**
- User can download their complete data for 7 days
- Download link is unique and secure (requires authentication)
- Export file is automatically deleted after expiry

**Dependencies:** WF-004 (profile data), WF-005/WF-006 (business data), WF-010 (notification)

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Data too large (>1GB export) | Memory/storage pressure | Stream directly to storage. Split into multiple volumes. |
| Query timeout on large dataset | Incomplete export | Use pagination. Extend query timeout for export. |
| Storage full | Cannot save export | Alert ops. Retry when space available. |
| Rate limit exceeded | Cannot export | Inform user when they can request again. |

**Edge Cases:**
- User has no data in some categories -> include empty category with "no data" marker
- Export contains data linked to other users -> include but note shared nature
- User requests export then deletes account -> complete export first, then delete
- Binary data (images, files) -> include as files in ZIP, not in JSON/CSV
- Internationalization -> export field names and values in user's locale
- Data in different timezones -> normalize to UTC with timezone indicator

**Performance Budget:** < 5 minutes for most users; longer for heavy users

**Related Files:**
- `src/api/routes/user.routes.ts`
- `src/services/user.service.ts`
- `src/services/data.service.ts`
- `src/services/queue.service.ts`

---

### WF-013: Database Migration

**Description:** Apply version-controlled schema changes to database with safety checks, rollback capability, and zero-downtime strategy.

**Trigger:** Deployment pipeline step, manual migration command.

**Actors:** CI/CD Pipeline, DevOps, System

**Inputs:**
- Migration files (timestamped, sequential)
- Target database connection
- Migration direction (up/down)
- Dry-run flag

**Preconditions:**
- Database is accessible
- Current schema version is known
- No other migration is running (lock acquisition)
- Backup has been created

**Processing Steps:**

```
Step 1:  [Validate Migrations]   Check migration files are syntactically valid,
                                  sequential, and not already applied.
Step 2:  [Acquire Lock]          Acquire advisory lock to prevent concurrent
                                  migrations. Release on completion/failure.
Step 3:  [Create Backup]         Take database snapshot or logical backup
                                  before any schema change.
Step 4:  [Dry Run]               Execute migration in transaction, then
                                  ROLLBACK. Verify no errors.
Step 5:  [Apply Migration]       Execute migration in transaction. COMMIT
                                  if successful, ROLLBACK if error.
Step 6:  [Verify Schema]         Run validation queries to confirm schema
                                  matches expected state.
Step 7:  [Record Migration]      INSERT into migrations table with checksum,
                                  timestamp, and duration.
Step 8:  [Release Lock]          Release advisory lock.
Step 9:  [Log Event]             Record migration details in audit log.

ROLLBACK:
Step 10: [Execute Down]          Run down migration to revert changes.
Step 11: [Verify Rollback]       Confirm schema returned to previous state.
Step 12: [Record Rollback]       Update migration record with rollback info.
```

**Outputs:**
- Updated database schema
- Migration record in database
- Backup file (pre-migration)
- Audit log entries

**Postconditions:**
- Schema is in expected state for current deployment
- Migration is recorded and traceable
- Rollback is possible (down migrations exist)

**Dependencies:** Deployment pipeline, database connection, backup system

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Migration timeout | Schema in unknown state | Rollback. Investigate slow-running DDL. |
| Lock timeout | Migration aborted | Retry after backoff. If persistent, manual intervention. |
| Constraint violation on existing data | Migration fails | Rollback. Clean data, then retry. |
| Out of disk space | Cannot write to DB | Rollback. Alert storage team. |
| Orphaned migration state | Lock held forever | Use lock_timeout. Alert on stale locks. |

**Edge Cases:**
- Migration creates NOT NULL column on table with millions of rows -> provide default, backfill, then add NOT NULL
- Renaming column -> use backward-compatible approach: add new column, dual-write, backfill, drop old
- Foreign key constraint cannot be added due to invalid data -> fix data first
- Zero-downtime migration -> use expand-migrate-contract pattern
- Migration applied to read replica before primary -> track schema version per node

**Performance Budget:** Varies by change; timeout at 30 minutes per migration

**Related Files:**
- `src/db/migrations/`
- `src/db/index.ts`
- `src/config/database.ts`
- `scripts/migrate.sh`

---

### WF-014: Deployment Pipeline

**Description:** CI/CD pipeline that builds, tests, and deploys application to target environment with health verification and rollback capability.

**Trigger:** Push to deployment branch (main, staging), manual workflow dispatch.

**Actors:** GitHub Actions, CI/CD Runner, DevOps, System

**Inputs:**
- Git commit SHA
- Target environment (dev, staging, production)
- Deployment strategy (rolling, blue/green, canary)
- Approval (required for production)

**Preconditions:**
- CI checks pass (lint, typecheck, tests)
- Docker images can be built
- Target environment is healthy (previous deployment stable)

**Processing Steps:**

```
BUILD STAGE:
Step 1:  [Checkout]              Checkout source code at specific commit SHA.
Step 2:  [Install Dependencies]  npm ci (clean install). Cache node_modules.
Step 3:  [Lint & Typecheck]      Run ESLint and TypeScript compiler checks.
Step 4:  [Run Unit Tests]        Execute unit tests with coverage threshold.
Step 5:  [Build Application]     Compile TypeScript, bundle assets.
Step 6:  [Build Docker Image]    Build production Docker image with tag
                                  based on commit SHA.
Step 7:  [Push Image]            Push Docker image to container registry.
Step 8:  [Scan Image]            Security scan Docker image (Trivy/Snyk).

DEPLOY STAGE:
Step 9:  [Prepare Environment]   Verify target environment health. Run
                                  pre-deployment checks.
Step 10: [Run Migrations]        Execute WF-013 (database migration).
Step 11: [Deploy Application]    Deploy new Docker image using strategy:
                                  - Blue/Green: switch traffic after health
                                  - Rolling: update instances gradually
                                  - Canary: route 5% traffic, observe
Step 12: [Health Check]          Verify application health endpoint returns
                                  200. Run smoke tests.
Step 13: [Monitor]               Observe error rates, latency, and resource
                                  usage for 5 minutes post-deploy.
Step 14: [Complete/Finalize]     Mark deployment as successful. Notify team.

ROLLBACK TRIGGER:
Step 15: [On Failure]            If health check fails, error rate spikes,
                                  or monitor detects anomalies, trigger
                                  automatic rollback (WF-015).
```

**Outputs:**
- Docker image in registry
- Deployed application in target environment
- Migration applied (if applicable)
- Deployment record with commit SHA, timestamp, duration
- Health check results

**Postconditions:**
- Application is running new version in target environment
- Old version is available for rollback
- Deployment is recorded and team is notified
- Monitoring is active with post-deploy watch period

**Dependencies:** WF-013 (migration), WF-015 (rollback), WF-016 (health check), all build/test tooling

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Build failure | No deployment | Fail pipeline. Notify team. Fix requires new commit. |
| Migration failure | Schema mismatch | Rollback code deploy. Fix migration, retry. |
| Health check failure | Unhealthy deployment | Automatic rollback. |
| Docker registry unavailable | Cannot push image | Retry with backoff. Fail if persistent. |
| Approval timeout | Deployment stalled | Escalate. Auto-approve for staging. |

**Edge Cases:**
- Multiple commits merged rapidly -> deploy latest, but run all pending migrations in order
- Deployment during peak traffic -> use gradual rollout with careful monitoring
- Dependency vulnerability found during build -> fail or continue per policy (vulnerability threshold)
- Previous deployment still in progress -> queue, don't allow concurrent deploys
- Configuration mismatch between environments -> validate config against environment schema
- Zero-downtime deployment requires connection draining -> implement graceful shutdown

**Performance Budget:** < 15 minutes total for standard deployment

**Related Files:**
- `.github/workflows/deploy.yml`
- `.github/workflows/ci.yml`
- `Dockerfile`
- `scripts/deploy.sh`
- `scripts/migrate.sh`

---

### WF-015: Rollback Procedure

**Description:** Emergency procedure to revert application and/or database to previous known-good state.

**Trigger:** Failed deployment, health check failure, incident detected, manual decision.

**Actors:** CI/CD Pipeline, DevOps, On-Call Engineer

**Inputs:**
- Rollback target (previous version, specific commit)
- Rollback scope (application only, database + application)
- Incident severity (determines speed vs safety)
- Approval (required for production rollback)

**Preconditions:**
- Previous stable version is available (Docker image, build artifact)
- Database rollback migration exists (down migration) if DB was modified
- Backup is available if migration rollback is risky

**Processing Steps:**

```
APPLICATION ROLLBACK:
Step 1:  [Assess Scope]          Determine if database was modified in the
                                  deployment. If yes, plan DB rollback.
Step 2:  [Verify Rollback Target] Confirm previous Docker image/build exists
                                  and is healthy.
Step 3:  [Stop New Traffic]      Drain connections to new version instances
                                  or stop sending traffic to new version.
Step 4:  [Redeploy Previous]     Deploy previous Docker image (same as
                                  WF-014 deploy steps, with old image).
Step 5:  [Health Check]          Run health checks against rolled-back version.
Step 6:  [Verify Functionality]  Run smoke tests to confirm critical paths work.

DATABASE ROLLBACK (if needed):
Step 7:  [Run Down Migration]    Execute the down migration for the change
                                  that was just applied.
Step 8:  [Verify Schema]         Confirm schema matches previous state.
Step 9:  [Validate Data]         Spot-check data integrity.

COMPLETION:
Step 10: [Monitor]               Watch error rates, latency, resources for
                                  10 minutes post-rollback.
Step 11: [Declare Stable]        Confirm incident resolved. Notify team.
Step 12: [Create Incident Report] Document root cause, rollback execution,
                                  and lessons learned.
```

**Outputs:**
- Application running previous version
- Database at previous schema version (if applicable)
- Smoke tests passed
- Incident report initiated
- Team notification

**Postconditions:**
- System is stable on previous known-good version
- Incident is documented with root cause analysis
- Fix workflow is prioritized for next deploy

**Dependencies:** WF-014 (inverse), WF-013 (migration down), WF-016 (health check)

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Previous version not available | Cannot rollback | Restore from backup. Rebuild from tag. |
| Down migration fails | Schema stuck | Restore from database backup taken before deploy. |
| Rollback also fails | Double failure | Deploy emergency fix. Engage whole team. |
| Data migration backward incompatible | Data loss risk | Revert migration manually. Restore from backup. |

**Edge Cases:**
- Multiple deployments ago needs rollback -> rollback sequentially through each version
- Data changed in new schema (new column populated) -> down migration must handle data
- Rollback during peak traffic -> expect brief disruption, communicate outage
- Partial rollback (service A rolled back, service B not) -> verify inter-service compatibility
- Rollback from canary -> simply stop routing traffic to canary instances
- Customer-visible regression -> rollback immediately, restore service, investigate after

**Performance Budget:** < 10 minutes for application rollback; +15 for database rollback

**Related Files:**
- `scripts/rollback.sh`
- `scripts/deploy.sh`
- `.github/workflows/deploy.yml`
- `src/db/migrations/`

---

### WF-016: Health Check & Monitoring

**Description:** Continuous system health verification, performance monitoring, and alerting.

**Trigger:** Scheduled (every 30 seconds), Kubernetes liveness/readiness probes, monitoring system polling.

**Actors:** System, Monitoring Service, On-Call Engineer

**Inputs:**
- Health check request
- System metrics (CPU, memory, disk, network)
- Application metrics (request latency, error rate, throughput)

**Preconditions:**
- Application is running
- Monitoring service is configured (Prometheus, DataDog, Grafana)

**Processing Steps:**

```
LIVENESS CHECK:
Step 1:  [Respond to Ping]       HTTP GET /health — return 200 if process
                                  is alive and not in shutdown.

READINESS CHECK:
Step 2:  [Check Dependencies]    Verify database is reachable (lightweight
                                  query: SELECT 1).
Step 3:  [Check Redis]           Verify Redis is responding to PING.
Step 4:  [Check Queue]           Verify queue connection is active.
Step 5:  [Check Disk]            Verify disk usage below threshold (90%).
Step 6:  [Return Status]         HTTP GET /ready — return 200 if all
                                  dependencies healthy. Return 503 if not.

METRICS COLLECTION:
Step 7:  [Collect Runtime]       CPU, memory, event loop lag, GC stats.
Step 8:  [Collect HTTP Metrics]  Request count, latency (p50/p95/p99), error
                                  rate, active connections.
Step 9:  [Collect DB Metrics]    Connection pool usage, query latency, slow
                                  queries, replication lag.
Step 10: [Collect Queue Metrics] Queue depth, job processing time, failure
                                  rate, dead letter count.
Step 11: [Export Metrics]        Expose via /metrics endpoint for Prometheus
                                  scraping.

ALERTING:
Step 12: [Evaluate Rules]        Check metrics against alert thresholds:
                                  - Error rate > 5% over 5 min
                                  - p99 latency > 2s over 5 min
                                  - Disk usage > 90%
                                  - Queue depth > 10K
Step 13: [Send Alert]            If threshold breached, send alert to PagerDuty/
                                  OpsGenie/Slack with severity level.
Step 14: [Auto-Remediate]        For known conditions, trigger auto-remediation
                                  (restart worker, scale up, clear queue).
```

**Outputs:**
- Health check response (200/503)
- Metrics data (for dashboards)
- Alerts (if thresholds breached)
- Auto-remediation actions

**Postconditions:**
- System health is observable
- Metrics are stored for trending and analysis
- Alerts are triggered when needed
- On-call engineer is notified of issues

**Dependencies:** Monitoring infrastructure (Prometheus, Grafana), logging infrastructure (ELK), alerting

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Database slow but not down | Readiness check may timeout | Use short timeout. Separate liveness from readiness. |
| Metrics endpoint overloaded | Monitoring interference | Use separate port for metrics. Rate limit. |
| Alert fatigue | Important alerts ignored | Tune thresholds. Silence known flapping alerts. |
| Monitoring system down | Blind to issues | Implement redundant health check (external monitoring). |

**Edge Cases:**
- Transient spike vs sustained issue -> alert only after threshold sustained for N minutes
- Dependency cascade failure (DB down -> everything "unhealthy") -> still accurate
- Health check endpoint itself becomes slow -> request timeout and sampling
- Kubernetes killing pod before graceful shutdown -> implement preStop hook
- Metrics volume causes storage growth -> configure retention and aggregation

**Performance Budget:** < 100ms for health check; metrics collection non-blocking

**Related Files:**
- `src/index.ts` (health endpoint)
- `src/config/`
- `scripts/health.sh`

---

### WF-017: Backup & Recovery

**Description:** Automated database backup, secure storage, point-in-time recovery, and disaster recovery procedures.

**Trigger:** Scheduled (daily full backup, hourly incremental), manual.

**Actors:** System, Backup Service, Storage Service, DevOps

**Inputs:**
- Database connection configuration
- Backup schedule
- Retention policy (30 days daily, 12 monthly)
- Encryption keys

**Preconditions:**
- Backup destination is configured and accessible (S3, separate storage)
- Sufficient disk space for backup creation
- Encryption keys are available

**Processing Steps:**

```
BACKUP:
Step 1:  [Initiate Backup]       Start backup at scheduled time or manual
                                  trigger. Log backup start.
Step 2:  [Lock Writes]           Optionally lock writes for consistent
                                  snapshot (varies by DB engine).
Step 3:  [Dump Database]         Create database dump (pg_dump, mysqldump,
                                  mongodump) with compression.
Step 4:  [Unlock Writes]         Release write lock.
Step 5:  [Encrypt Backup]        Encrypt backup file with GPG/AES-256.
Step 6:  [Upload to Storage]     Upload encrypted backup to S3/Blob Storage
                                  with lifecycle policy.
Step 7:  [Verify Backup]         Download and verify checksum of uploaded
                                  backup. Test decryption.
Step 8:  [Cleanup Old Backups]   Remove backups outside retention window.
Step 9:  [Log Backup Result]     Record backup size, duration, checksum.

RECOVERY (POINT-IN-TIME):
Step 10: [Identify Target]       Select restore point (timestamp, backup ID).
Step 11: [Download Backup]       Download encrypted backup from storage.
Step 12: [Decrypt Backup]        Decrypt backup file using stored key.
Step 13: [Restore Database]      Restore from backup file. Use temporary
                                  database for verification.
Step 14: [Verify Data]           Run data integrity checks: record counts,
                                  sample queries, referential integrity.
Step 15: [Promote to Production] If verification passes, rename/redirect
                                  to production database.
```

**Outputs:**
- Encrypted backup file in long-term storage
- Backup verification report
- Backup log entry with metadata

**Postconditions:**
- Backup is securely stored and verifiable
- Recovery procedure is documented and tested
- Retention policy is enforced

**Dependencies:** Database connection, Storage service (S3), Encryption service

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Backup file corrupt | Unusable backup | Verify immediately after creation. Retry if corrupt. |
| Storage upload fails | Backup not persisted | Retry with backoff. Alert if persistent. |
| Encryption key lost | Cannot decrypt backup | Store key in secure vault (not with backup). Have backup key. |
| Recovery takes too long | Extended downtime | Practice recovery regularly. Document expected RTO. |

**Edge Cases:**
- Backup during heavy traffic -> use replica for backup to avoid impacting primary
- Cross-region backup for DR -> replicate backup to secondary region
- Schema changes between backup and restore -> migrations must be replayed
- Partial recovery (single table) -> use table-level restore if supported
- Ransomware protection -> immutable backup storage (WORM)
- Testing recovery -> practice in isolated environment quarterly

**Performance Budget:** Backup within maintenance window; RTO < 4 hours

**Related Files:**
- `src/config/database.ts`
- `scripts/backup.sh`
- `scripts/restore.sh`

---

### WF-018: API Rate Limiting

**Description:** Enforce API request rate limits per user, IP, endpoint, and global to prevent abuse and ensure fair usage.

**Trigger:** Every incoming API request.

**Actors:** Rate Limiter Middleware, Redis, System

**Inputs:**
- Request IP address
- Authenticated user ID (if applicable)
- Request path and method
- API key (if applicable)

**Preconditions:**
- Rate limiter is initialized with Redis backend
- Rate limit rules are configured per plan/endpoint

**Processing Steps:**

```
Step 1:  [Identify Client]       Extract client identifier: user ID for
                                  authenticated, API key for service, IP for
                                  anonymous.
Step 2:  [Select Rule Set]       Determine applicable rate limit rules
                                  based on client tier and endpoint group
                                  (auth routes: stricter; data routes: standard).
Step 3:  [Check Redis Counter]   INCR and GET current count for client key
                                  with TTL matching window (15 minutes).
Step 4:  [Evaluate Limit]        If count > limit, prepare 429 response
                                  with Retry-After header.
Step 5:  [Allow or Reject]       If under limit, proceed with request. If
                                  over limit, return 429.
Step 6:  [Set Response Headers]  Include X-RateLimit-Limit, X-RateLimit-
                                  Remaining, X-RateLimit-Reset headers.
Step 7:  [Log Rate Limit Events]  Log rate limit hits for analytics
                                  (not per-request, just blocked events).
```

**Outputs:**
- Request allowed or rejected (429)
- Rate limit headers on every response
- Logged blocked requests (for abuse analysis)

**Postconditions:**
- Client knows their rate limit status from headers
- Abusive clients are blocked before reaching application logic

**Dependencies:** Redis (for distributed counters), src/config/

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Redis unavailable | No rate limiting | Fall back to in-memory (less accurate). Log Redis failure. |
| Clock skew | Window calculation off | Use Redis TTL, not system clock. |
| Distributed race condition | Slightly over-limit | Acceptable — use approximate counting (sliding window). |
| Counter overflow | Limit bypass | Implement counter reset periodically. |

**Edge Cases:**
- User behind NAT (shared IP) -> more permissive IP limits, stricter user-level limits
- Batch API calls (user uploads many items) -> count as single request or per-item
- Rate limit "burst" allowance -> token bucket algorithm allows short bursts
- Whitelist internal services -> skip rate limiting for internal IPs/service accounts
- Rate limit by endpoint sensitivity -> stricter for auth, looser for reads

**Performance Budget:** < 5ms per request (Redis call overhead)

**Related Files:**
- `src/api/middleware/rate-limit.middleware.ts`
- `src/config/redis.ts`
- `src/config/index.ts`

---

### WF-019: Session Management

**Description:** Manage user sessions across devices with creation, validation, refresh, revocation, and cleanup.

**Trigger:** Login (create), API request (validate), logout (destroy), token refresh.

**Actors:** System, User, Auth Middleware

**Inputs:**
- Access token (JWT or opaque)
- Refresh token
- Device/agent information
- User ID

**Preconditions:**
- User is authenticated

**Processing Steps:**

```
SESSION CREATION (Login):
Step 1:  [Generate Session]      Create session record with user ID, device
                                  info, IP, created/expiry timestamps.
Step 2:  [Issue Access Token]    Generate short-lived JWT (15 min) with
                                  session ID, user ID, role, expiry.
Step 3:  [Issue Refresh Token]   Generate opaque refresh token (7 day),
                                  store hash in session record.

SESSION VALIDATION (Each Request):
Step 4:  [Extract Token]         Parse access token from Authorization header
                                  or cookie.
Step 5:  [Verify JWT]            Verify signature, expiry, issuer, audience.
Step 6:  [Check Session]         Verify session ID from token exists and
                                  is active (not revoked).

TOKEN REFRESH:
Step 7:  [Validate Refresh]      Hash refresh token, compare with stored
                                  hash. Verify not expired/revoked.
Step 8:  [Issue New Tokens]      Generate new access token and refresh token.
                                  Rotate refresh token (invalidates old).
Step 9:  [Update Session]        Update session last_activity timestamp.

SESSION REVOCATION (Logout):
Step 10: [Find Session]          Identify session from token.
Step 11: [Revoke Session]        Mark session as REVOKED. Set revoke timestamp.
                                  Clear refresh token hash.
Step 12: [Return Confirmation]   Clear cookies, return 200.

SESSION CLEANUP (Background):
Step 13: [Purge Expired]         Delete sessions with expired refresh tokens
                                  (batch job, hourly).
Step 14: [Purge Revoked]         Delete sessions revoked > 30 days ago.
```

**Outputs:**
- Session record in database (created/updated/revoked)
- Access token (JWT)
- Refresh token (opaque)
- Session validation result (allowed or rejected)

**Postconditions:**
- Active sessions are tracked per user
- Expired/revoked sessions cannot be used
- Token rotation ensures old tokens are invalidated on refresh

**Dependencies:** WF-002 (authentication), src/utils/jwt.ts, src/db/models/session.model.ts

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Token tampering | Forged session | JWT signature verification prevents this |
| Refresh token reuse (rotation) | Theft detected | Revoke all sessions for user. Alert. |
| Session table too large | Performance impact | Regular cleanup. Index on user_id + expiry. |
| Clock skew between services | Token validation fails | Allow 30-second leeway in JWT validation. |

**Edge Cases:**
- User logs out but malicious actor has access token -> token still valid for remaining 15 min. Use token blacklist for immediate revocation.
- User on multiple devices -> each device has independent session. Logout of all devices available.
- Session fixation -> new session ID generated on login, never accept session from URL parameter
- Concurrent refresh token requests -> implement token rotation: old refresh token is invalidated on use
- Idle session timeout -> implement sliding expiration: reset TTL on activity, absolute max 24h

**Performance Budget:** < 10ms for session validation

**Related Files:**
- `src/services/auth.service.ts`
- `src/api/middleware/auth.middleware.ts`
- `src/utils/jwt.ts`
- `src/db/models/session.model.ts`

---

### WF-020: Audit Logging

**Description:** Immutable audit trail of all security-relevant events for compliance, forensics, and monitoring.

**Trigger:** Security events (login, logout, permission change), data events (CRUD on sensitive data), admin actions.

**Actors:** System, Logger, Audit Storage

**Inputs:**
- Event type (AUTH_LOGIN, USER_UPDATE, DATA_DELETE, etc.)
- Actor (user ID, system, admin)
- Target resource type and ID
- Action performed
- Previous and new values (for modifications)
- IP address, user agent
- Timestamp
- Correlation ID (trace across services)

**Preconditions:**
- Audit logger is configured with storage backend

**Processing Steps:**

```
Step 1:  [Create Event]          Create audit event object with all required
                                  fields: event type, actor, target, action,
                                  timestamp, metadata.
Step 2:  [Enrich Context]        Add correlation ID from request context.
                                  Add environment, service name, version.
Step 3:  [Serialize]             Serialize to JSON with consistent field
                                  ordering and formatting.
Step 4:  [Write to Log]          Write to audit log file/stream. Include
                                  timestamp and sequence number.
Step 5:  [Write to Database]     INSERT audit record into audit_logs table
                                  (for queryable access).
Step 6:  [Hash Chain]            For tamper-evident logs, include hash of
                                  previous event in current event (optional,
                                  for high-security environments).
Step 7:  [Apply Retention]       Enforce retention policy. Archive logs
                                  older than retention period.
```

**Outputs:**
- Audit log file entry
- Database record in audit_logs table
- Archive file (for long-term storage)
- Hash chain (if enabled)

**Postconditions:**
- Security events are recorded with sufficient detail for investigation
- Audit logs are tamper-evident (if hashing enabled)
- Retention policy is enforced

**Dependencies:** src/config/logging.ts, src/utils/logger.ts, src/db/models/audit-log.model.ts

**Failure Points:**

| Failure | Impact | Handling |
|---------|--------|----------|
| Database write fails | Audit event lost | Buffer in memory. Write to fallback file. Alert. |
| Log file rotation missing | Disk full | Implement logrotate configuration. |
| PII logged accidentally | Compliance violation | Sanitize audit events. Review logs regularly. |
| Too many audit events | Performance impact | Sample high-volume events. Batch writes. |

**Edge Cases:**
- Audit logging itself becomes performance bottleneck -> async writes with buffer
- Investigation requires cross-referencing events -> correlation ID links related events
- Legal hold on specific user's logs -> exclude from deletion during retention cleanup
- Compliance with different regulations (GDPR, SOC2, HIPAA) -> configurable retention per event type
- Event contains sensitive data -> mask or hash sensitive fields in audit log

**Performance Budget:** < 5ms per event (async); batching for high volume

**Related Files:**
- `src/utils/logger.ts`
- `src/config/logging.ts`
- `src/db/models/audit-log.model.ts`

---

## Workflow Interactions Matrix

| Workflow | Depends On | Triggers | Triggered By | Risk Level |
|----------|-----------|----------|--------------|------------|
| WF-001 Registration | WF-002, WF-010, WF-020 | WF-010, WF-020 | User action | HIGH |
| WF-002 Auth & Login | WF-018, WF-019, WF-020 | WF-019, WF-020 | User action | CRITICAL |
| WF-003 Password Reset | WF-002, WF-010, WF-020 | WF-010, WF-020 | User action | HIGH |
| WF-004 Profile Mgmt | WF-002, WF-020 | WF-020 | User action | MEDIUM |
| WF-005 Data Ingestion | WF-006, WF-020 | WF-006, WF-020 | External system | HIGH |
| WF-006 Data Processing | WF-005, WF-020 | WF-007, WF-009, WF-020 | WF-005 | CRITICAL |
| WF-007 Report Gen | WF-005, WF-006, WF-010 | WF-010 | User action, WF-008 | MEDIUM |
| WF-008 Scheduled Rpt | WF-007, WF-010 | WF-007 | Cron schedule | LOW |
| WF-009 Webhook | WF-010, WF-020 | WF-006, WF-010 | External system | HIGH |
| WF-010 Notifications | WF-020 | — | WF-001, WF-003, WF-007, WF-009, WF-011 | MEDIUM |
| WF-011 Account Deletion | WF-002, WF-004, WF-019, WF-020 | WF-010, WF-020 | User/Admin | HIGH |
| WF-012 Data Export | WF-004, WF-005, WF-006, WF-010 | WF-010 | User action | MEDIUM |
| WF-013 DB Migration | — | — | Deploy pipeline | CRITICAL |
| WF-014 Deploy | WF-013, WF-015, WF-016 | WF-013, WF-015 | Git push | CRITICAL |
| WF-015 Rollback | WF-013, WF-014, WF-016 | — | WF-014 failure, manual | CRITICAL |
| WF-016 Health Check | — | Alert | Schedule, probes | CRITICAL |
| WF-017 Backup | — | — | Schedule, manual | CRITICAL |
| WF-018 Rate Limiting | — | — | Every request | HIGH |
| WF-019 Session Mgmt | WF-002 | — | WF-002, each request | HIGH |
| WF-020 Audit Logging | — | — | Security events | HIGH |

---

**End of Workflow Map**
