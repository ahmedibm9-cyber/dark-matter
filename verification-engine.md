# Verification Engine

> Every implementation must pass through this verification system before it can be considered complete. No exceptions.

---

## 1. Requirements Verification

### 1.1 Verifying All Requirements Are Met

Each requirement must be verified against one of these evidence types:

| Evidence Type | Description | Example |
|---------------|-------------|---------|
| Test | Automated test proves requirement | Unit test, integration test, E2E test |
| Review | Manual review confirms requirement | A11y audit, security review |
| Measure | Metric confirms requirement | P95 latency < 200ms, error rate < 0.1% |
| Artifact | Document or output confirms requirement | Architecture diagram updated, ADR written |

### 1.2 Traceability Matrix Template

Every feature or change must produce a traceability matrix:

```markdown
## Traceability Matrix: [Feature/Change Name]

| Req ID | Requirement | Implemented In | Verified By | Status |
|--------|-------------|----------------|-------------|--------|
| REQ-1 | User can log in with email/password | src/auth/login.ts | test_auth_login.py | ✅ |
| REQ-2 | Session expires after 24h | src/auth/session.ts | test_session_expiry.py | ✅ |
| REQ-3 | Rate limit: 5 attempts/min | src/middleware/rate-limit.ts | Load test SC-123 | ✅ |
```

**Status values**: ✅ Verified, ❌ Not Verified, ⚠️ Partially Verified, N/A Not Applicable

### 1.3 Requirements Coverage Checklist

Before marking a feature complete:

- [ ] Every functional requirement has at least one passing test
- [ ] Every non-functional requirement (SLA, compliance) has a measurement
- [ ] Traceability matrix is complete and reviewed
- [ ] No requirements marked "Not Verified" or "Partially Verified"
- [ ] Stakeholder has signed off on the traceability matrix
- [ ] Negative requirements (what the system must NOT do) are verified
- [ ] Requirements that changed during development are re-verified

---

## 2. Edge Case Verification

### 2.1 Common Edge Case Categories

Every implementation must be checked against these categories:

| Category | Description | Example |
|----------|-------------|---------|
| Empty | Zero-length inputs, empty collections, no results | Empty search query, empty cart |
| Null | Null/undefined values where non-null expected | Missing optional field, null reference |
| Max Length | Input at or exceeding maximum allowed length | 256-char username, 10MB file upload |
| Special Characters | Unicode, control chars, injection payloads | Emoji in name, SQL injection attempt |
| Boundary Values | Values at, below, and above thresholds | Exactly 0 stock, -1 quantity, 2^31-1 ID |
| Concurrent Access | Race conditions, deadlocks, optimistic lock failures | Two users booking same seat |
| Network Failure | Timeout, disconnect, DNS failure, packet loss | API call after WiFi disconnect |
| Permission Denied | 401, 403, missing scopes | User without admin role accessing admin panel |
| Rate Limited | Throttled requests, quota exceeded | 1001st request when limit is 1000 |
| Expired | Tokens, sessions, cache entries, timestamps | Expired JWT, stale cache, past-due payment |
| Duplicate | Idempotency violations, duplicate submissions | Double-clicking submit, duplicate webhook |
| Partial Data | Incomplete payloads, interrupted uploads | Missing required field, partial CSV row |
| Data Type Mismatch | String where number expected, wrong format | "abc" in price field, wrong date format |
| State Order | Operations in wrong order, missing prerequisites | Cancel before create, pay before checkout |
| Large Data | Pagination, streaming, memory exhaustion | 1M results returned without pagination |

### 2.2 Edge Case Discovery Methodology

For each new feature, discover edge cases through:

1. **Input Space Analysis**: List all input parameters and their valid/invalid ranges
2. **State Machine Analysis**: Map all possible states and transitions; find illegal transitions
3. **Failure Mode Analysis**: What happens when each dependency fails? (DB, API, cache, queue)
4. **Boundary Analysis**: Test values at, just below, and just above every boundary
5. **Pairwise Testing**: Test combinations of edge case inputs together
6. **Experience-Based**: Consult the team's collective experience with similar features

### 2.3 Edge Case Test Template

```markdown
## Edge Case: [Title]

**Category**: [From section 2.1]

**Scenario**: [Brief description]

**Input**: [Specific input values]

**Expected Behavior**: [What should happen]

**Actual Behavior**: [What happens — fill in during testing]

**Risk Level**: [Critical / High / Medium / Low]

**Mitigation**: [How to handle this edge case]

**Test ID**: [Link to test case]
```

### 2.4 Edge Case Verification Checklist

- [ ] All relevant edge case categories from section 2.1 are checked
- [ ] Edge case discovery performed using methodology in 2.2
- [ ] At least one test per identified edge case
- [ ] Edge cases covering input, state, failure, and boundary types
- [ ] Edge cases covering both valid and invalid paths (positive and negative testing)
- [ ] Edge cases are automated (not just manual)
- [ ] Any "Critical" risk edge case has been reviewed by a senior engineer
- [ ] Edge case handling degrades gracefully (no crashes, meaningful error messages)

---

## 3. Security Verification

### 3.1 Security Verification Checklist Per Change Type

**For ALL changes:**

- [ ] No secrets committed
- [ ] No new dependencies with known vulnerabilities (check against advisory DB)
- [ ] No sensitive data in logs, error messages, or URLs
- [ ] Input validation on all external entry points
- [ ] Output encoding for all user-controlled data in responses

**For API changes:**

- [ ] Authentication enforced on all endpoints (no missing auth)
- [ ] Authorization checks on each resource access
- [ ] Rate limiting applied
- [ ] Request size limiting applied
- [ ] CORS configured correctly

**For Database changes:**

- [ ] SQL injection prevention (parameterized queries, no raw SQL concatenation)
- [ ] Least-privilege database credentials
- [ ] Column-level encryption for PII
- [ ] Audit logging for sensitive data access

**For UI changes:**

- [ ] XSS prevention (no dangerouslySetInnerHTML, proper escaping)
- [ ] CSRF protection
- [ ] Content Security Policy headers
- [ ] Iframe sandboxing where applicable
- [ ] Secure cookie flags (HttpOnly, Secure, SameSite)

**For Infrastructure changes:**

- [ ] Least-privilege IAM roles
- [ ] Network segmentation (private subnets, security groups)
- [ ] TLS termination configuration
- [ ] No default credentials
- [ ] Security group rules reviewed

### 3.2 Common Vulnerability Patterns to Check

| Pattern | Risk | How to Check |
|---------|------|--------------|
| IDOR (Insecure Direct Object Reference) | High | Test accessing another user's resource by changing ID in URL |
| Mass Assignment | High | Test sending unexpected fields in request body |
| Path Traversal | High | Test `../../../etc/passwd` in file paths |
| Open Redirect | Medium | Test redirect URLs pointing to external domains |
| SSRF | High | Test internal URLs in fetch/request operations |
| Prototype Pollution | High | Check for unsafe object merge/clone operations |
| ReDoS | Medium | Test regex against malicious input strings |
| Race Condition | Medium | Test concurrent requests on critical operations |
| Broken Access Control | Critical | Test all user roles against all endpoints |
| Injection (SQL, NoSQL, LDAP, Command) | Critical | Test special characters and injection payloads |

### 3.3 Security Test Requirements

| Test Type | Required For | Frequency |
|-----------|-------------|-----------|
| SAST (Static Analysis) | All code changes | Every PR |
| Dependency Scan | All dependency changes | Every PR |
| Secret Scan | All commits | Every commit (blocking) |
| DAST (Dynamic Analysis) | All API changes | Every release |
| Penetration Test | Major releases, auth changes | Quarterly / per major |
| Threat Model Review | New features, architecture changes | Per design phase |

---

## 4. Performance Verification

### 4.1 Performance Regression Detection

Every change must answer:

1. **Does this change affect a hot path?** (P99 request, DB query > 10/s, background job)
2. **What is the baseline?** (current P50, P95, P99 for affected path)
3. **What is the expected impact?** (theoretical analysis before measurement)
4. **Was the impact measured?** (benchmark, load test, or profile diff)

**Rule**: Any change that degrades P99 latency by > 10% or adds > 50ms to response time must be approved by engineering lead.

### 4.2 Performance Budget Checklist

| Metric | Budget | Breach Action |
|--------|--------|--------------|
| API response time (P50) | < 200ms | Optimize or add caching |
| API response time (P99) | < 1000ms | Profile and optimize hot path |
| Page load (First Contentful Paint) | < 1.5s | Optimize bundle, lazy load |
| Page load (Time to Interactive) | < 3.5s | Reduce JS, code split |
| Database query time (P50) | < 50ms | Add index or optimize query |
| Database query time (P99) | < 500ms | Add caching or denormalize |
| Bundle size (JS initial) | < 200KB gzipped | Code split, tree shake |
| Memory usage (per request) | < 50MB | Profile and optimize |
| CPU usage (per request) | < 100ms | Optimize hot loops |
| External API call timeout | < 5s | Circuit breaker |

### 4.3 Load Test Requirements by Change Type

| Change Type | Load Test Required? | Target Throughput | Duration |
|-------------|-------------------|-------------------|----------|
| Simple bug fix | No | N/A | N/A |
| New endpoint (read) | Yes | 3x expected peak | 10 min |
| New endpoint (write) | Yes | 3x expected peak | 10 min |
| Database schema change | Yes | 2x expected peak | 15 min |
| Background job | Yes | 5x expected volume | 30 min |
| Caching layer change | Yes | 5x expected peak | 20 min |
| Infrastructure change | Yes | Match current load | 30 min |
| Major refactor (no behavior change) | Yes | Match current load | 20 min |

---

## 5. Regression Risk Verification

### 5.1 Impact Analysis Methodology

For every change, determine impact scope:

1. **Direct Impact**: Files and modules directly modified
2. **Dependency Impact**: Modules that depend on the modified code
3. **API Contract Impact**: Any change to public interfaces, request/response shapes
4. **Data Impact**: Any change to data shape, storage, or access patterns
5. **Behavioral Impact**: Any change to business logic outcomes

### 5.2 Dependency Tracing Procedure

```
For each modified file:
├── Find all direct consumers (importers, callers)
├── Find all indirect consumers (consumers of consumers, 2 levels)
├── Find all side-effect consumers (event handlers, webhook receivers)
├── Find all data consumers (readers of same data)
└── For each:
    ├── Evaluate risk: Does the change affect this consumer's behavior?
    ├── Low risk → No additional testing needed
    ├── Medium risk → Add integration test
    └── High risk → Add E2E test + manual QA sign-off
```

### 5.3 Regression Test Selection

| Modification Type | Minimal Test Set | Full Test Set |
|------------------|-----------------|--------------|
| Comment / documentation change | Build only | Full suite |
| Simple logic change (no branching) | Unit tests for changed module | Unit + integration |
| Branching logic change | Unit + integration for changed path | Unit + integration + E2E |
| API endpoint change | Unit + integration for endpoint | Full E2E suite |
| Data model change | Unit + integration + migration test | Full suite |
| Infrastructure change | Smoke tests | Full E2E + load tests |
| Dependency upgrade | Integration tests for affected modules | Full suite |

---

## 6. Documentation Verification

### 6.1 Documentation Update Requirements

The following must be evaluated for documentation changes with every PR:

| Documentation | When to Update | Who Verifies |
|---------------|---------------|--------------|
| README.md | New feature, changed setup, changed API | PR reviewer |
| API docs (OpenAPI) | Any endpoint change | Automated diff check |
| Architecture docs | Any architecture decision | ADR author + reviewer |
| Runbook / Operations | New deployment, changed config, alert changes | DevOps reviewer |
| Onboarding docs | Changed setup steps, new prerequisites | Team lead |
| CHANGELOG | Any user-facing change | PR author |
| Migration guide | Breaking changes | Tech lead |
| Comments in code | Changed logic that was previously commented | PR reviewer |

### 6.2 Documentation Freshness Check

- [ ] All docs that reference the changed code are updated
- [ ] Outdated examples removed or updated
- [ ] Deprecation notices added where applicable
- [ ] Setup/installation instructions re-verified
- [ ] Links verified (no broken links)
- [ ] API examples match current request/response shapes
- [ ] Screenshots or diagrams updated if UI changed
- [ ] Environment variables documented
- [ ] Error codes and their meanings documented

---

## 7. Before-Completion Checklist

This checklist must be completed and signed off before any change is merged or deployed:

### Verification Gate

- [ ] All requirements verified against traceability matrix
- [ ] All edge cases identified and handled (with tests)
- [ ] Security reviewed (SAST, dependency scan, secret scan passed)
- [ ] Performance impact assessed and within budget
- [ ] Regression risk analyzed and mitigated
- [ ] Documentation updated (or N/A noted)

### Testing Gate

- [ ] All tests pass (unit, integration, E2E)
- [ ] New code has tests (coverage meets project threshold)
- [ ] Tests cover happy path, error path, and edge cases
- [ ] Tests are deterministic (no flaky tests introduced)
- [ ] Load tests pass (if applicable)

### Build Gate

- [ ] Build passes
- [ ] Lint passes (no new warnings)
- [ ] Type checking passes (no new type errors)
- [ ] Bundle size within budget (if applicable)

### Review Gate

- [ ] Code reviewed by at least one peer
- [ ] Reviewer has verified all items in this checklist
- [ ] All review comments resolved
- [ ] Author has self-reviewed before requesting review

### Deployment Gate

- [ ] Deployment plan documented
- [ ] Rollback plan documented
- [ ] Monitoring and alerting configured
- [ ] Feature flag in place (if applicable)
- [ ] Release notes prepared (if user-facing)
- [ ] Stakeholders notified of deployment window

---

## 8. Verification Failure Protocol

If any verification step fails:

1. **Stop**: Do not proceed to the next step
2. **Assess**: Determine the severity of the failure
   - **Critical**: Security vulnerability, data loss risk, SLA breach → Escalate immediately
   - **Major**: Broken functionality, regression, performance degradation → Fix before merging
   - **Minor**: Documentation gap, non-critical edge case → Can proceed with ticket created
3. **Document**: Record the failure in the verification log
4. **Fix**: Address the failure and re-run verification
5. **Learn**: Add to team's lessons learned to prevent recurrence

---

## 9. Verification Log

| Change ID | Change Description | Requirement Verified | Edge Cases | Security | Performance | Regression | Docs | Reviewer | Date |
|-----------|-------------------|---------------------|------------|----------|-------------|------------|------|----------|------|
| | | | | | | | | | |

---

*Verification is not a gate to slow you down. It is a net that catches the mistakes you would have made at 3 AM.*
