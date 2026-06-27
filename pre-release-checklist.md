# Pre-Release Checklist — AI Agent Tasks

> Run before every production deployment. All items must pass before releasing.

## 1. Regression Audit
- **Task**: Verify no existing functionality is broken by the release.
- **Commands**:
  ```bash
  npm run test:all 2>&1 | tail -30
  npx playwright test --reporter=list 2>&1 | tail -30
  ```
- **Steps**:
  1. Run full unit test suite — all tests must pass.
  2. Run all integration tests — all tests must pass.
  3. Run full E2E test suite — all tests must pass.
  4. Verify test coverage did not decrease (if coverage check exists).
  5. Check for any new flaky tests introduced.
- **Verification**: All test suites pass 100%. Zero regressions detected.

## 2. Release Candidate Audit
- **Task**: Verify the release candidate is correctly built and versioned.
- **Commands**:
  ```bash
  git log --oneline origin/main..HEAD
  git diff origin/main --stat
  ```
- **Steps**:
  1. Confirm version number is updated correctly (package.json, version file).
  2. Verify CHANGELOG.md is updated with all changes.
  3. Confirm all commits are intentional and no debug/WIP code is included.
  4. Verify `console.log`, `debugger`, `TODO`, `FIXME` are not in production code.
  5. Check that feature flags for in-progress features are disabled.
  6. Ensure database migration scripts are idempotent (can be run multiple times).
- **Verification**: Clean diff from main. All debug artifacts removed. Changelog complete.

## 3. Production Readiness Audit
- **Task**: Verify the application is configured correctly for production.
- **Steps**:
  1. Verify all environment variables for prod are configured in the deployment system.
  2. Check that secrets are stored in Vault (not in source code or env files).
  3. Verify logging level is set to INFO (not DEBUG) for production.
  4. Confirm rate limits are appropriate for production traffic.
  5. Verify CORS configuration allows only the production origin.
  6. Check that CSP headers are configured and correct.
  7. Verify SSL/TLS certificates are valid and not expiring soon.
  8. Confirm health check endpoints are configured for the load balancer.
  9. Verify resource limits (CPU/memory) are set in Kubernetes manifests.
  10. Check that autoscaling policies are configured.
- **Verification**: All production configuration verified and documented.

## 4. Security Audit
- **Task**: Run security checks specific to the release.
- **Commands**:
  ```bash
  npm audit --audit-level=high 2>&1
  # Run SAST scanner if available
  # npx snyk test --severity-threshold=high
  ```
- **Steps**:
  1. Review all new dependencies added in this release for known vulnerabilities.
  2. Verify no secrets are included in the build artifacts.
  3. Check that all API endpoints have proper authentication checks.
  4. Verify input validation is in place for all new endpoints.
  5. Check for any hardcoded URLs that point to staging/test environments.
  6. Verify any new environment variables are documented.
- **Verification**: Zero high-severity vulnerabilities. No secrets exposed. Auth is enforced.

## 5. Deployment Plan Verification
- **Task**: Confirm the deployment plan is complete and safe.
- **Steps**:
  1. Verify deployment order: migrations first, then services.
  2. Check if zero-downtime deployment is configured (rolling update).
  3. Verify database migrations are backward-compatible (no breaking schema changes).
  4. Confirm canary deployment percentage is set (e.g., 10% traffic initially).
  5. Verify rollback procedure is tested and documented.
  6. Confirm runbook for this release is written.
  7. Verify monitoring dashboards for this release are configured.
  8. Confirm on-call engineer is notified of the release window.
- **Verification**: Deployment plan is reviewed and approved. Runbook is ready.

## 6. Rollback Plan Verification
- **Task**: Verify the rollback plan is complete and tested.
- **Steps**:
  1. Verify the previous version's Docker images are available and tagged.
  2. Confirm database migration rollback scripts exist (if applicable).
  3. Document rollback trigger conditions (e.g., error rate > 1%, latency > 2s).
  4. Verify rollback procedure is automated or has clear step-by-step instructions.
  5. Confirm rollback can be completed within 15 minutes.
  6. Test rollback in staging environment if possible.
  7. Verify notification plan for stakeholders if rollback is executed.
- **Verification**: Rollback procedure is documented and tested. Rollback images are available.

## 7. Smoke Test Plan
- **Task**: Define and verify smoke tests to run immediately after deployment.
- **Commands**:
  ```bash
  # Example smoke test commands (customize per release)
  curl -s -o /dev/null -w "%{http_code}" https://example.com/api/health
  curl -s https://example.com/api/products?limit=1 | jq '.data | length'
  ```
- **Smoke Test List**:
  1. Health endpoint returns 200.
  2. Homepage loads and renders correctly.
  3. User registration flow works.
  4. User login flow works.
  5. Product listing loads with expected data.
  6. Product detail page loads.
  7. Cart add/remove works.
  8. Checkout flow completes successfully (test order).
  9. Admin panel loads for admin users.
  10. All API endpoints return correct status codes.
- **Verification**: All smoke tests pass in production. No obvious issues.

## 8. Final Approval Checklist
- **Task**: Confirm all stakeholders have signed off.
- **Steps**:
  1. QA sign-off obtained.
  2. Product owner approval received.
  3. Tech lead approval received.
  4. Security review completed (if applicable).
  5. Release notes reviewed and approved.
  6. Change management ticket approved (if applicable).
  7. Communication sent to stakeholders about release timing.
- **Verification**: All approvals documented. Release is authorized to proceed.
