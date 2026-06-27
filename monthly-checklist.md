# Monthly Checklist — AI Agent Tasks

> Run on the first day of each month. Deep audit across all areas.

## 1. Full Dependency Audit
- **Task**: Comprehensive review of all dependencies for outdated or vulnerable packages.
- **Commands**:
  ```bash
  npm outdated 2>&1
  npm audit 2>&1
  npx npm-check-updates --format repo 2>&1
  ```
- **Steps**:
  1. Review all outdated packages (major, minor, patch).
  2. For each package, determine if update is safe (changelog review, breaking changes).
  3. Update non-breaking packages — batch into a single PR.
  4. Schedule breaking-change updates as separate PRs with migration plans.
  5. Remove unused dependencies (check with `npx depcheck`).
  6. Verify lockfile integrity (`npm ci` succeeds).
  7. Run full test suite after updates.
- **Verification**: No packages > 2 major versions behind. Zero critical vulnerabilities. Lockfile is valid.

## 2. Technical Debt Audit
- **Task**: Full review of technical-debt.md with cost-benefit re-evaluation.
- **Commands**:
  ```bash
  wc -l intelligence/technical-debt.md
  cat intelligence/technical-debt.md | grep -E "^(### TDEBT|Priority|Estimated Cost|Estimated Effort)"
  ```
- **Steps**:
  1. Review every open debt item.
  2. Re-estimate cost and effort based on current understanding.
  3. Re-prioritize based on business impact and current velocity.
  4. Identify any debt that has become irrelevant (mark as cancelled).
  5. Propose a top-3 list for the next sprint planning.
  6. Calculate the total estimated effort across all items.
- **Verification**: All items have current estimates. Top-3 list is proposed for sprint planning.

## 3. Performance Audit
- **Task**: System-wide performance review covering all critical paths.
- **Commands**:
  ```bash
  # Run load tests for all critical paths
  # npx artillery run tests/performance/all-flows.yml
  ```
- **Steps**:
  1. Review p99 latency trends across all services over the past month.
  2. Check database query performance (slow query log analysis).
  3. Review Redis cache hit rates and memory usage.
  4. Check API gateway rate limiting effectiveness.
  5. Review CDN cache hit ratios.
  6. Check database connection pool utilization.
  7. Identify top-3 performance bottlenecks.
  8. Create optimization tickets for each bottleneck.
- **Verification**: Performance metrics collected and trended. Top-3 bottlenecks documented.

## 4. Logging and Monitoring Review
- **Task**: Audit observability infrastructure for gaps.
- **Commands**:
  ```bash
  grep -r "console.log\|console.error" apps/ services/ --include="*.ts" | grep -v "__tests__" | wc -l
  ```
- **Steps**:
  1. Review Datadog dashboard usage — are all dashboards actively used?
  2. Check alert configuration — any stale or noisy alerts?
  3. Verify all services emit OpenTelemetry traces (ADR-007 compliance).
  4. Audit log retention — are we within BR-022 compliance?
  5. Check PII masking in logs (BR-023 compliance).
  6. Review error tracking — any recurring errors not captured?
  7. Update monitoring runbooks for any new services or endpoints.
- **Verification**: All services instrumented. No PII in logs. All alerts are actionable.

## 5. CI/CD Pipeline Review
- **Task**: Review CI/CD pipeline health, speed, and reliability.
- **Commands**:
  ```bash
  gh run list --limit 20 --json conclusion,displayTitle,createdAt,duration
  ```
- **Steps**:
  1. Calculate CI success rate over the past month.
  2. Review average CI duration — is it trending up?
  3. Check for flaky tests (tests that pass/fail non-deterministically).
  4. Review deployment frequency and success rate.
  5. Check for pipeline security issues (e.g., secrets in logs).
  6. Review pipeline configuration for optimization opportunities.
  7. Update CI/CD documentation in the intelligence layer.
- **Verification**: CI success rate > 95%. Average duration < 30 min. No flaky tests identified.

## 6. Documentation Freshness
- **Task**: Verify all intelligence layer documents are current.
- **Commands**:
  ```bash
  git log --oneline --since="1 month ago" -- "intelligence/*.md"
  Intelligence file last-modified dates
  ```
- **Steps**:
  1. Check the last-modified date of each intelligence document.
  2. Identify documents not updated in 30+ days.
  3. Review each stale document against the current codebase.
  4. Update documents with missing or incorrect information.
  5. Add any new features, APIs, or DB objects not yet documented.
  6. Verify feature-catalog.md references match actual source files.
  7. Verify api-catalog.md matches actual API implementations.
- **Verification**: All documents updated within 30 days. Catalog files match codebase reality.

## 7. Security Compliance Check
- **Task**: Verify security policies and compliance requirements are met.
- **Steps**:
  1. Verify BR-021 (audit trail) coverage across all entities.
  2. Verify BR-022 (data retention) policies are enforced.
  3. Verify BR-023 (PII masking) in logs and support interfaces.
  4. Check secret rotation — are Vault secrets rotated within 30 days?
  5. Review access control — any users with inappropriate permissions?
  6. Verify rate limiting is active on all public endpoints.
  7. Check WAF rules are up to date.
- **Verification**: All business rules verified. No compliance gaps identified.
