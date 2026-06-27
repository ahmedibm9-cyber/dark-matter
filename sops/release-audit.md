# SOP: Release Candidate Audit
Last Updated: 2026-06-25
Owner: Release Manager / Engineering Manager

## Purpose
Evaluate a release candidate against defined quality, security, and operational criteria to make a data-driven go/no-go decision. This SOP ensures every release is thoroughly vetted before reaching production, minimizing the risk of regressions, outages, and security incidents. It covers change analysis, critical functionality verification, blocker identification, and rollback readiness assessment.

## When to Execute
- After a release candidate is built and deployed to staging/pre-production
- Before every production deployment (mandatory for major/minor releases)
- Before hotfix deployments (abbreviated process, minimum critical checks)
- When a release has been delayed and the candidate includes late changes
- As part of the final sign-off in the release pipeline

## Required Inputs
- Release candidate build number and artifact location
- Changelog or release notes (draft)
- Full list of commits/PRs included in this release
- Test suite results (unit, integration, E2E, performance)
- Known issues list (tracked bugs not fixed in this release)
- Deployment runbook and environment configuration changes
- Rollback plan and verification procedure
- Monitoring dashboard links for staging environment
- Previous release audit report (for comparison)

## Prerequisites
- Staging/pre-production environment identical to production
- Full test suite has been executed against the RC
- Smoke test suite is defined and documented
- Monitoring and alerting configured on staging environment
- Rollback procedure has been tested recently (within last 30 days)
- All required approvals are configured in the release pipeline
- Feature flags are configured if dark launches are used

## Procedure

### Step 1: Change Analysis
Analyze all changes included in the release candidate.
- Generate the diff from the last release tag:
```
git log --oneline --no-merges v1.0.0..HEAD
git diff --stat v1.0.0..HEAD
git shortlog -sn v1.0.0..HEAD
```
- Categorize every change:
  - **New features**: new functionality, endpoints, services
  - **Bug fixes**: defect corrections
  - **Refactoring**: code changes without functional impact
  - **Dependency updates**: library upgrades
  - **Configuration changes**: environment, feature flags
  - **Infrastructure**: deployment, pipeline, or infrastructure code
  - **Documentation**: non-code changes
- Calculate **change risk score**:
  - Infrastructure changes: 5 points each
  - Database migrations: 10 points each
  - New external dependencies: 5 points each
  - Modified core domain code: 3 points per module
  - Refactoring >500 LOC: 2 points per module
  - Configuration changes: 1 point per file
  - Total risk: sum (threshold: <20 low, 20-50 medium, >50 high)
- Check that each change has a corresponding test update (or documented exemption).
- Identify changes that touch critical paths (authentication, payments, data export).

### Step 2: Blocker Identification
Run through the defined blocker checklist.
- **Blocker criteria** (any YES means stop the release):
  - Are there any unfixed Critical or High severity bugs?
  - Does the test suite have any failing tests in the RC branch?
  - Are there known security vulnerabilities in included dependencies?
  - Is there a database migration that cannot be rolled back?
  - Is the rollback procedure untested or incomplete?
  - Are there API changes that break backward compatibility without a migration path?
  - Are there unaddressed performance regressions (>10% degradation)?
  - Is monitoring/alarming not configured for new metrics?
  - Are there incomplete feature flags for dark-launched features?
  - Are release notes incomplete or inaccurate?
- Document each blocker with evidence. If any blocker exists, the release is NO-GO until resolved.

### Step 3: Critical Functionality Verification
Execute the critical functionality test suite against the RC.
- Define critical paths (varies by application, but typically):
  - **Authentication**: can users log in? Can new users register?
  - **Authorization**: do users have correct access? Are permissions enforced?
  - **Core workflow**: can users complete the primary task (place order, create document, etc.)?
  - **Payment processing**: can users complete payments? Are refunds working?
  - **Data persistence**: is data saved and retrieved correctly?
  - **Search**: is search returning correct results?
  - **Notifications**: are emails/push notifications being sent?
  - **Admin functions**: can admins perform their tasks?
- For each critical path, run the predefined smoke test (manual or automated).
- Document pass/fail for each critical path. Any failure is a HIGH priority issue.
- Verify that new features work end-to-end in staging, not just locally.

### Step 4: Regression Verification
Ensure existing functionality has not been broken by the new changes.
- Review test suite results:
  - Unit tests: 100% pass rate required
  - Integration tests: 100% pass rate required
  - E2E tests: 100% pass rate required (known flaky tests excluded with evidence)
  - Performance tests: no regression >5% on p50/p95/p99 latency
- Check coverage of changed files:
  - Are new methods covered by tests?
  - Are changed methods covered by existing tests?
  - Are there integration tests that exercise the modified code paths?
- For any failing tests:
  - Determine if the failure is related to the RC changes
  - If unrelated (flaky test, infrastructure issue): document and quarantine
  - If related: categorize as blocker if critical path
- Run a targeted regression on modules affected by the change diff.

### Step 5: Performance Validation
Verify the RC meets performance requirements.
- Run the performance test suite against the RC:
  - **Load test**: expected peak traffic, sustained for 30 minutes
  - **Stress test**: 2x expected peak, identify breaking point
  - **Endurance test**: normal load for 4+ hours (memory leak detection)
- Record key metrics and compare to baseline:
  - API response times (p50, p95, p99)
  - Throughput (requests/second)
  - Error rate (target: <0.1%)
  - CPU and memory utilization
  - Database query performance (slow query log)
  - P95 response time >2x baseline → performance regression → NO-GO
- Check for new endpoints in the RC and ensure they have performance baselines.
- Verify database migration scripts don't lock tables or degrade query performance.

### Step 6: Upgrade and Rollback Path Verification
Ensure the release can be safely deployed and, if needed, rolled back.
- **Upgrade path**:
  - Verify the upgrade procedure in the runbook is current
  - Check database migration scripts are reversible
  - Verify migration script handles concurrent access during upgrade
  - Check for data format changes that affect existing data
  - Verify backward compatibility with any API consumers
- **Rollback path**:
  - Verify the rollback procedure is documented and tested
  - Check that database migrations have down scripts
  - Verify rollback restores the previous application version
  - Check that rollback preserves any new data created during the RC window
  - Identify potential data loss scenarios during rollback
  - Verify rollback time is within the defined SLA (typically <30 minutes)
- **Feature flag verification**:
  - Check that feature flags for incomplete features are OFF
  - Verify toggling flags doesn't cause errors
  - Check that flags can be toggled without deployment
  - Verify monitoring tracks feature flag state

### Step 7: Security Validation
Perform targeted security checks on the RC.
- Run security scan against the RC on staging:
  - SAST scan on the RC branch (already run in CI, confirm results)
  - DAST scan against staging (OWASP ZAP or similar)
  - Dependency vulnerability scan (confirm no new vulnerabilities)
  - Secrets scan (confirm no credentials committed)
- Verify security controls on new endpoints:
  - Authentication required (if applicable)
  - Authorization enforced
  - Input validation present
  - Rate limiting configured
  - Audit logging added for sensitive operations
- Check that security headers are present on all responses.
- Verify that no debug endpoints or developer tools are exposed.

### Step 8: Configuration and Secrets Review
Audit all configuration changes for the release.
- Compare configuration files between current and RC versions:
  - Feature flags and their intended values
  - Environment-specific overrides
  - Connection strings and service endpoints
  - Third-party API keys and service accounts
- Verify that secrets are managed correctly:
  - No secrets in configuration files (use vault or secret store)
  - All secrets in the target environment exist and are valid
  - Service-to-service authentication credentials are configured
- Check logging configuration:
  - Log levels are appropriate for production (not DEBUG)
  - Sensitive data is not logged (PII, credentials, tokens)
  - New log entries have consistent formatting and context

### Step 9: Monitoring and Observability Verification
Confirm the RC is observable in production.
- Verify dashboards exist for:
  - New endpoints and features
  - Business metrics (signups, orders, etc.)
  - Error rates and exception types
  - Response times and throughput
- Check that alerts are configured for:
  - Error rate spike (>1% error rate triggered)
  - P95 latency spike (>2x baseline)
  - Service downtime (health check failures)
  - Business metric anomalies (orders dropping to zero)
- Verify log aggregation is ingesting logs from the RC.
- Check that tracing is configured for distributed calls.
- Verify health check endpoints are working and returning accurate status.

### Step 10: Go/No-Go Decision and Sign-off
Make the final decision with documented evidence.
- Compile the release audit report:
  - Release summary (version, build number, commit hash)
  - Change risk score and analysis
  - Blocker checklist results
  - Critical functionality verification results
  - Test suite summary (pass/fail counts, coverage)
  - Performance test results vs. baseline
  - Security scan summary
  - Upgrade/rollback verification status
  - Monitoring configuration verification
  - Known issues list (non-blocker)
- Decision criteria:
  - **GO**: all blockers resolved, critical functionality passes, rollback verified, security clear
  - **NO-GO**: any blocker exists, critical functionality fails, rollback untested, or unresolved security issue
  - **CONDITIONAL GO**: non-critical issues exist with documented mitigation plan and stakeholder acceptance
- Obtain formal sign-off from:
  - Release Manager (process compliance)
  - QA Lead (quality verification)
  - Security Lead (security sign-off)
  - Engineering Manager (risk acceptance)
  - Product Owner (business acceptance)
- Save the signed report as `release-audit-YYYY-MM-DD-vX.Y.Z.md`.
- Tag the release candidate in version control: `git tag -a vX.Y.Z-rc -m "Release candidate vX.Y.Z"`

## Verification Steps
- Blocker checklist is fully populated with pass/fail evidence for each item
- Critical functionality is tested end-to-end in staging, not just unit-tested
- Performance test results are compared to baseline with % change documented
- Rollback procedure is verified by actually executing it in a test environment
- All required sign-offs are obtained and documented
- Release audit report is saved to the designated repository location

## Expected Deliverables
- `release-audit-YYYY-MM-DD-vX.Y.Z.md` — completed release audit report
- Blocker checklist with evidence for each item
- Critical functionality verification results (pass/fail per scenario)
- Performance comparison report (RC vs. baseline)
- Security scan results summary
- Signed go/no-go decision with rationale

## Success Criteria
- Every RC change has been analyzed and risk-scored
- Critical functionality passes 100%
- All blockers are resolved before GO decision
- Rollback procedure is verified and timed (<30 min target)
- Monitoring and alerts are confirmed operational for all new features
- Decision is documented with supporting evidence for every criterion

## Failure Recovery
- If a blocker is found: notify the team immediately, escalate severity, track remediation with a P1 ticket
- If performance regression is detected: engage the performance team, identify root cause, evaluate if it can be fixed within the release window
- If rollback is untested: delay release until rollback is verified in a non-production environment
- If critical functionality fails in staging but passes locally: check environment configuration, data seeding, and dependency versions
- If sign-off cannot be obtained from a required stakeholder: escalate to release governance board with documented attempts
- If the release is NO-GO: create a new RC with fixes, restart the audit from Step 1

## Related SOPs
- `deployment-review.md` — Detailed deployment plan and runbook review
- `qa.md` — Test suite quality and coverage for release decisions
- `security-audit.md` — Security validation for release candidates
- `performance-review.md` — Performance benchmark procedures
- `audit.md` — Broader codebase health assessment
