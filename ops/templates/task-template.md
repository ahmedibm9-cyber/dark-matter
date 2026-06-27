# Task Definition Template

> **Purpose:** Standardized task definition for AI agent execution. Every task assigned to an AI agent MUST use this template. Fill all sections. Empty sections indicate incomplete task definition.
> **Version:** 1.0.0

---

## 1. Task Identification

| Field          | Value                                          |
|----------------|------------------------------------------------|
| **Task ID**    | `TASK-{NNN}` (sequential, unique per project) |
| **Title**      | Short, action-oriented description             |
| **Type**       | `feature` / `bugfix` / `refactor` / `docs` / `config` / `test` / `research` |
| **Priority**   | `P0` (critical) / `P1` (high) / `P2` (medium) / `P3` (low) |
| **Status**     | `draft` / `assigned` / `in-progress` / `under-review` / `completed` / `cancelled` |
| **Assignee**   | Agent or human identifier                      |
| **Created**    | YYYY-MM-DD                                     |
| **Deadline**   | YYYY-MM-DD (or `none`)                         |
| **Requestor**  | Person or system that created the task         |

---

## 2. Description

**Summary:**
One to three paragraphs describing the task in plain language. What is the problem? What is the desired outcome? Why is this task important now?

**User Story (if applicable):**
```
As a <role>,
I want <capability>,
So that <benefit>.
```

**Current Behavior (for bugfix tasks):**
Describe what currently happens, including any error messages, incorrect outputs, or undesired behavior.

**Expected Behavior:**
Describe what should happen after the task is completed.

---

## 3. Acceptance Criteria (Success Criteria)

These are the measurable, verifiable conditions that MUST be true for the task to be considered complete. Each criterion must be objective and testable.

```
AC-01: [Description of criterion]
AC-02: [Description of criterion]
AC-03: [Description of criterion]
...
```

**Examples:**
```
AC-01: User can register with email and password.
AC-02: Registration sends confirmation email within 30 seconds.
AC-03: Duplicate email registration returns 409 Conflict with message "Email already registered".
AC-04: Password must be at least 8 characters with 1 uppercase, 1 lowercase, 1 digit.
AC-05: All registration tests pass with 100% code coverage of the registration handler.
```

**Verification method for each criterion:**
```
AC-01 → Automated E2E test: `test_registration_success.py`
AC-02 → Integration test with SMTP mock: `test_confirmation_email_sent.py`
AC-03 → Unit test: `test_registration_duplicate_email.py`
AC-04 → Unit test: `test_password_policy.py`
AC-05 → Coverage report check
```

---

## 4. Scope

### In Scope (exact files and changes)

List every file, configuration, and artifact that is expected to be created or modified.

**Source Code:**
- `src/path/to/file1.ts` — Add registration handler
- `src/path/to/file2.ts` — Update user model with password fields
- `src/path/to/file3.ts` — Add email service integration

**Tests:**
- `tests/path/to/test_file1.ts` — New registration tests
- `tests/path/to/test_file2.ts` — Update existing user tests

**Configuration:**
- `config/default.yaml` — Add SMTP configuration section
- `.env.example` — Add SMTP environment variables

**Documentation:**
- `docs/api/register.md` — New API endpoint documentation
- `CHANGELOG.md` — Add entry for registration feature

**Database:**
- `migrations/20260625_add_users_table.up.sql`
- `migrations/20260625_add_users_table.down.sql`

### Out of Scope (explicit exclusions)

List what is NOT to be done in this task. This prevents scope creep.

- OOS-01: Password reset flow (separate task TASK-004)
- OOS-02: OAuth/social login (separate task TASK-007)
- OOS-03: Email template customization (MVP uses built-in template)
- OOS-04: User profile page (separate task TASK-005)
- OOS-05: Admin user management UI (separate task TASK-012)

---

## 5. Dependencies

### Prerequisites (must be done before this task)
- `TASK-001` — User data model design and review
- `TASK-002` — SMTP service provisioning and credentials in vault
- Decision `ADR-003` — Password hashing algorithm selection

### Blocked By (this task blocks these)
- `TASK-004` — Password reset flow (depends on registration)
- `TASK-005` — User profile page (depends on registration)
- `TASK-006` — Login flow (depends on registration)

### External Dependencies
- SMTP server access (host, port, credentials)
- Email delivery service (SendGrid / AWS SES / Mailgun)
- Recaptcha v3 API key (for spam prevention)

---

## 6. Risks

| # | Risk Description | Likelihood | Severity | Mitigation |
|---|---|---|---|---|
| R1 | SMTP credentials exposed in code | Low | Critical | Use vault, scan for hardcoded secrets (Constitution R21) |
| R2 | Duplicate registration race condition | Medium | High | Unique constraint on email column + application-level check |
| R3 | Password hashing performance degradation | Low | Medium | Use bcrypt with cost factor 10, test with concurrent registrations |
| R4 | Email delivery delay or failure | Medium | Medium | Async email sending with retry queue, log failures |
| R5 | Backward compatibility with existing user tokens | None | N/A | No existing users in system (greenfield) |

---

## 7. Rollback Plan

### Pre-Deployment Rollback
```
Action:     Do not merge the PR
Procedure: Close PR without merging
Outcome:   No changes deployed
```

### Post-Deployment Rollback (Code)
```
Action:     Revert the merge commit
Procedure: git revert <merge-commit-hash>
Verify:    git log --oneline -5 (confirm HEAD is pre-change)
Outcome:   Code returns to pre-change state
```

### Post-Deployment Rollback (Database)
```
Action:     Run down migration
Procedure: dotnet ef migrations remove OR apply <down-migration>
Verify:    SELECT * FROM information_schema.tables WHERE table_name = 'users' (should not exist)
Outcome:   Database returns to pre-migration schema; WARNING: user data is lost on rollback
```

### Data Recovery (if applicable)
```
Action:     Restore from backup
Procedure: psql -h <host> -d <database> -f backup_20260625.sql
Outcome:   Data restored to backup state
```

---

## 8. Verification Steps

### Build Verification
```bash
dotnet build --no-restore
# Expected: Build succeeded with 0 warnings, 0 errors
```

### Lint Verification
```bash
dotnet format --verify-no-changes
# Expected: No formatting issues found
```

### Test Verification
```bash
dotnet test --filter "Category=Registration"
# Expected: 15 passed, 0 failed, 0 skipped
dotnet test  # Full suite regression
# Expected: 342 passed, 0 failed, 0 skipped (same count as baseline)
```

### Migration Verification
```bash
dotnet ef database update  # up migration
# Expected: Database updated successfully
dotnet ef database update <previous-migration>  # down migration
# Expected: Database reverted successfully
```

### Edge Case Verification
- [ ] Empty email field → validation error
- [ ] Invalid email format → validation error
- [ ] Password shorter than 8 chars → validation error
- [ ] Password without uppercase → validation error
- [ ] Maximum field lengths → stored correctly
- [ ] SQL injection attempts → rejected
- [ ] Concurrent duplicate registration → only one succeeds
- [ ] Network timeout during email sending → queued for retry

---

## 9. Required Documentation Updates

| Document | Update Required | Details |
|---|---|---|
| `CHANGELOG.md` | Yes | Add under "Added" for `v1.2.0` — "User registration with email/password" |
| `docs/api/README.md` | Yes | Add link to new registration endpoint doc |
| `docs/api/register.md` | Yes | New file — endpoint spec, request/response examples |
| `docs/architecture/auth-flow.md` | No | Registration flow covered by existing ADR |
| `docs/deployment/env-vars.md` | Yes | Add SMTP_* environment variables |
| `docs/dev/local-setup.md` | Yes | Add SMTP mock setup instructions |
| `ADR-003` | No | Already covers password hashing decision |

---

## 10. Handoff Summary

> **This section is filled by the agent at task completion or at session handoff.**

### What Was Done
[Brief summary of implemented changes, including file paths and key decisions]

### What Was Learned
[Surprises, insights, patterns discovered during implementation]

### What Remains
[Pending work, deferred items, follow-up tasks]

### Decisions Made
- Decision 1: [Description]
- Decision 2: [Description]

### Risks Identified During Implementation
- Risk 1: [Description] (mitigation: [approach])
- Risk 2: [Description] (mitigation: [approach])

### Open Questions
- Question 1: [Description]
- Question 2: [Description]

### Artifacts
| Artifact | Location |
|---|---|
| PR | https://github.com/org/repo/pull/42 |
| Migration scripts | `migrations/20260625_add_users_table/*.sql` |
| Test results | `artifacts/task-003-test-results.log` |
| Coverage report | `artifacts/task-003-coverage.html` |

### Rollback Instructions
```bash
# Code rollback
git revert <sha>

# Database rollback
dotnet ef database update <pre-migration-name>

# Verification
dotnet test
```

### Session Duration
- **Started:** YYYY-MM-DD HH:MM
- **Ended:** YYYY-MM-DD HH:MM
- **Total:** X hours Y minutes

---

## 11. Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Assignee | | YYYY-MM-DD | accepted / rejected / needs-revision |
| Reviewer | | YYYY-MM-DD | approved / changes-requested |
| Stakeholder | | YYYY-MM-DD | approved / rejected |

---

## Task Lifecycle

```
[ DRAFT ] ──→ [ ASSIGNED ] ──→ [ IN PROGRESS ] ──→ [ UNDER REVIEW ] ──→ [ COMPLETED ]
     │                                                                    │
     └──→ [ CANCELLED ]                                                  └──→ [ CANCELLED ]
```

- **DRAFT:** Task is being defined, not yet ready for assignment
- **ASSIGNED:** Task is assigned to an agent or human, ready to begin
- **IN PROGRESS:** Work is actively being done
- **UNDER REVIEW:** Implementation is complete, awaiting verification
- **COMPLETED:** All acceptance criteria met, all artifacts delivered
- **CANCELLED:** Task will not be completed (with reason documented)
