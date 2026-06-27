# Post-Release Checklist — AI Agent Tasks

> Run immediately after production deployment and monitor for 24 hours.

## 1. Deployment Verification
- **Task**: Confirm the deployment completed successfully.
- **Commands**:
  ```bash
  kubectl get pods --all-namespaces | grep -E "Pending|CrashLoopBackOff|Error"
  gh run list --limit 5 --json conclusion,displayTitle,createdAt
  ```
- **Steps**:
  1. Verify all pods are in Running state.
  2. Confirm the correct version/tag is deployed.
  3. Check that rollback did not occur (verify current version).
  4. Confirm database migrations ran successfully.
  5. Verify static assets and CDN cache are updated.
- **Verification**: All services running expected version. No deployment errors.

## 2. Monitoring Verification
- **Task**: Verify monitoring is correctly reporting after deployment.
- **Commands**:
  ```bash
  # Check Datadog dashboard for new deployment marker
  # Open monitoring dashboards and verify data is flowing
  ```
- **Steps**:
  1. Confirm metrics are being emitted from all services.
  2. Verify new dashboards (if any) are showing data.
  3. Check that deployment marker is visible in monitoring.
  4. Verify alerts are active and correctly configured.
  5. Confirm log shipping is working for all services.
  6. Check tracing shows complete request flows.
- **Verification**: All monitoring systems operational. Metrics, logs, and traces flowing.

## 3. Error Rate Check
- **Task**: Verify error rates are within acceptable thresholds.
- **Commands**:
  ```bash
  # Check error rate in Datadog APM
  # Alternatively:
  kubectl logs --tail=1000 -l app=api-service | grep -i error | wc -l
  ```
- **Steps**:
  1. Check 5xx error rate — should be < 0.1% of all requests.
  2. Check 4xx error rate — should be < 5% (expected for auth failures).
  3. Verify no new error types appearing that weren't in staging.
  4. Check application-level error rate (exceptions thrown).
  5. Compare error rate against pre-deployment baseline.
- **Verification**: Error rates within acceptable thresholds. No new error types.

## 4. Performance Check
- **Task**: Verify performance is within expected parameters.
- **Commands**:
  ```bash
  # Check p50/p95/p99 latency in Datadog
  # kubectl top pods --all-namespaces
  ```
- **Steps**:
  1. Compare p99 latency against pre-deployment baseline.
  2. Check CPU and memory utilization across services.
  3. Verify database query performance (slow query log).
  4. Check Redis cache hit rate — should be > 85%.
  5. Verify CDN cache hit ratio.
  6. Check autoscaler is behaving correctly (no scale-up/down thrashing).
- **Verification**: Latency not increased. Resource utilization normal. Cache hit rates healthy.

## 5. Business Metrics Verification
- **Task**: Verify key business metrics are unaffected.
- **Steps**:
  1. Check checkout conversion rate.
  2. Verify registration completion rate.
  3. Check order placement success rate.
  4. Verify payment processing success rate.
  5. Compare all metrics against pre-deployment baseline.
- **Verification**: Business metrics are stable or improved. No degradation.

## 6. Documentation Update
- **Task**: Update all relevant documentation with release information.
- **Steps**:
  1. Update intelligence/architecture.md if deployment architecture changed.
  2. Update intelligence/api-catalog.md if any endpoints changed.
  3. Update intelligence/database-catalog.md if schema changed.
  4. Update intelligence/feature-catalog.md if features changed.
  5. Update intelligence/business-rules.md if rules changed.
  6. Update intelligence/workflow-map.md if workflows changed.
  7. Mark all affected documents with "last verified: today".
- **Verification**: All intelligence documents updated to reflect release changes.

## 7. Changelog Update
- **Task**: Ensure changelog is accurate and complete.
- **Commands**:
  ```bash
  git log --oneline --no-decorate HEAD...vPrevTag
  ```
- **Steps**:
  1. Confirm all commit messages are represented in the changelog.
  2. Verify the changelog entry has the correct version and date.
  3. Check that breaking changes are called out with migration notes.
  4. Confirm contributors are credited.
- **Verification**: Changelog is complete and accurate.

## 8. Retrospective Notes
- **Task**: Record observations for the release retrospective.
- **Steps**:
  1. Note any unexpected issues encountered during the release.
  2. Record the actual deployment duration vs. estimated duration.
  3. Document any workarounds used during the release.
  4. Capture any improvements suggested for the next release.
  5. Note any manual steps that should be automated.
  6. Record the rollback trigger threshold values (actual, not planned).
  7. Document any alerting gaps discovered.
- **Verification**: Retrospective notes saved to the release artifact directory.

## 9. Post-Release Bug Triage
- **Task**: Review any new bugs reported since the release.
- **Commands**:
  ```bash
  gh issue list --label bug --limit 10 --json number,title,createdAt
  ```
- **Steps**:
  1. Check for any bug reports created since deployment.
  2. Determine severity and priority for each.
  3. Add to intelligence/known-bugs.md if applicable.
  4. Schedule fixes based on severity.
- **Verification**: All post-release bugs are documented and prioritized.

## 10. Long-Term Monitoring Plan
- **Task**: Schedule follow-up monitoring checkpoints.
- **Steps**:
  1. Schedule 24-hour post-release check (automated alert if possible).
  2. Schedule 7-day post-release performance review.
  3. Schedule 30-day post-release business metrics review.
  4. Add calendar reminders for each checkpoint.
- **Verification**: Monitoring checkpoints are scheduled.

## 11. Release Sign-Off
- **Task**: Confirm release is fully complete.
- **Steps**:
  1. Verify all checklist items above are completed.
  2. Send release completion notification to team.
  3. Mark release as complete in the deployment system.
  4. Close the release ticket.
- **Verification**: Release is officially complete. All stakeholders notified.
