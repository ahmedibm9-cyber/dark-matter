# SOP: Deployment Review
Last Updated: 2026-06-25
Owner: DevOps Lead / Release Engineer

## Purpose
Review and validate all deployment artifacts, procedures, and configurations before a production deployment. This SOP ensures deployment plans are complete, migration scripts are safe, rollback procedures work, smoke tests confirm functionality, and monitoring is configured to detect issues. The goal is to make every deployment predictable, repeatable, and reversible.

## When to Execute
- Before every production deployment (mandatory)
- When deploying to a new environment (new staging, DR site, new region)
- After significant infrastructure changes
- When the deployment tooling or pipeline has been updated
- When onboarding a new service or microservice
- As part of the release audit process

## Required Inputs
- Deployment plan / runbook document
- Release notes with version number and changelog
- Infrastructure as Code files (Terraform, Pulumi, CloudFormation, ARM templates)
- Database migration scripts (up and down)
- Application configuration files for each environment
- Docker images or build artifacts with tags
- Helm charts or Kubernetes manifests (if applicable)
- CI/CD pipeline configuration files
- Smoke test suite definition
- Monitoring and alerting configuration templates
- Previous deployment review reports (for comparison)

## Prerequisites
- Deployment environment (staging) is available and representative of production
- CI/CD pipeline has executed successfully for this RC
- All artifacts are built, tagged, and stored in the artifact repository
- Database migration scripts have been tested against a copy of production data
- Rollback procedure is documented and has been exercised within the last 30 days
- Access to deployment environment (SSH, kubectl, cloud CLI) is configured
- Monitoring tools are installed and configured in the target environment

## Procedure

### Step 1: Deployment Plan Review
Review the deployment plan for completeness, clarity, and safety.
- **Plan structure review**: verify the plan includes:
  - Pre-deployment checks (environment health, dependency availability)
  - Deployment sequence (order of operations for multi-service deployments)
  - Database migration execution timing (before or after app deployment)
  - Configuration changes and their application order
  - Feature flag changes and their timing
  - Post-deployment verification steps
  - Rollback procedure (with trigger conditions)
  - Communication plan (who to notify, when)
- **Timeline review**: verify:
  - Deployment duration estimate (with buffer for unexpected issues)
  - Maintenance window alignment (if applicable)
  - Change freeze periods are not violated
  - Resource availability (team members on call)
- **Risk assessment**: identify:
  - Single points of failure in the deployment process
  - Steps that rely on manual intervention
  - External dependencies that could delay deployment
  - Concurrent changes happening in the same window
- Score the plan: 1-10 (10 = complete, no gaps). Score <7 requires plan revision.

### Step 2: Deployment Script and Pipeline Review
Audit the CI/CD pipeline configuration and deployment scripts.
- **Pipeline configuration**:
  - Verify pipeline stages: build → test → package → deploy to staging → smoke test → deploy to production → smoke test
  - Check manual approval gates are in the right places
  - Verify environment-specific variables are parameterized (not hardcoded)
  - Check that secrets are injected from a secure vault, not pipeline variables
  - Verify rollback triggers are automated (not requiring manual pipeline rerun)
- **Deployment scripts**:
  - Check for idempotency: running the script multiple times produces the same result
  - Check for proper error handling (exit on failure, meaningful error messages)
  - Verify timeout configurations
  - Check that health checks are performed after each component is deployed
  - Verify cleanup logic (remove temp files, close connections)
- **Container/orchestration review**:
  - Verify image tags are immutable (not `latest` tag)
  - Check readiness and liveness probe configurations
  - Verify resource limits (CPU/memory) are set
  - Check pod disruption budgets are configured
  - Verify secret mounts are read-only
  - Check that init containers or sidecars are properly configured

### Step 3: Database Migration Script Review
Thoroughly review all database migrations for safety and correctness.
- **Migration design review**:
  - Are migrations reversible? (every Up has a corresponding Down script)
  - Are migrations backward-compatible with the previous application version?
    - Adding a column: OK (old code ignores unknown columns)
    - Removing a column: NOT OK (old code will try to read it)
    - Renaming a column: NOT OK (do: add new + migrate data + drop old separately)
    - Changing column type: NOT OK if data loss possible
  - Do migrations handle large tables gracefully? (batch processing, online operations)
  - Are there table locks that would cause downtime?
  - Are check constraints or foreign keys added safely (with validation checks)?
- **Migration execution review**:
  - Verify migration order is correct and dependencies are documented
  - Check that migrations are transactional (all or nothing)
  - Verify migration timeout is adequate for data volume
  - Check for migrations that depend on application-level data transformation
  - Verify that seed data migrations are idempotent
- **Data integrity checks**:
  - Are there validation queries to run before/after migration?
  - Are there row-count verification steps?
  - Are there referential integrity checks after the migration?
  - Are orphaned records handled?

### Step 4: Rollback Procedure Review
Verify the rollback plan is complete, tested, and fast enough.
- **Rollback procedure completeness**:
  - Application rollback: deploy previous artifact version (automated?)
  - Database rollback: run Down scripts (data loss assessment documented)
  - Configuration rollback: restore previous configuration version
  - Feature flag rollback: disable newly enabled features
  - DNS/LB rollback: route traffic to previous infrastructure
- **Rollback triggers**:
  - Error rate spike (>X% of requests failing)
  - P95 latency spike (>2x baseline)
  - Health check failures in >1 instance
  - Business metric anomalies (orders dropping, signups stopping)
  - Manual trigger (any team member can initiate)
- **Rollback timing**:
  - Measure rollback duration (start to fully restored)
  - Target: <30 minutes for the complete rollback
  - Verify automated rollback is faster than manual
- **Rollback testing evidence**:
  - Last rollback test date (should be within 30 days)
  - Rollback test results (did it work? any issues?)
  - Data loss assessment for each migration's rollback
  - Known rollback failure scenarios documented

### Step 5: Smoke Test Plan Review
Verify the smoke test plan covers all critical paths and can be executed quickly.
- **Smoke test scope**:
  - Minimum critical path: authentication, core workflow, data persistence
  - Service-level health: all services respond to health checks
  - Integration points: external dependencies are reachable
  - New features: all new functionality in the release
- **Smoke test characteristics**:
  - Fast execution: complete within 5 minutes
  - Automated: runnable via a single command or pipeline step
  - Deterministic: same results every time on a healthy system
  - Self-validating: pass/fail output, no manual interpretation
  - Independent: no dependency on test data that could be modified
- **Smoke test execution**:
  - Verify smoke tests are run automatically after deployment
  - Check that smoke test failure triggers automatic rollback
  - Verify smoke test results are recorded and visible to the team
  - Check that smoke tests are maintained alongside application changes

### Step 6: Configuration and Environment Review
Audit all environment-specific configurations.
- **Configuration comparison**:
  - Compare staging vs. production configurations:
    - Connection strings (should point to different databases)
    - API endpoints (should point to different services)
    - Log levels (staging may be more verbose)
    - Feature flags (should be in correct state for production)
    - Resource limits (production may have higher limits)
  - Flag any configuration value that is identical between staging and production when it should differ
  - Flag any configuration that references `localhost` or non-production URLs
- **Secret management**:
  - Verify no secrets in configuration files (use vault/secrets manager)
  - Confirm all required secrets exist in the target environment
  - Check secret rotation dates (avoid deploying with soon-to-expire secrets)
  - Verify service accounts have correct permissions
- **SSL/TLS configuration**:
  - Verify certificate validity dates
  - Check certificate chain completeness
  - Verify TLS version minimum (1.2 or higher)
  - Check that HTTPS redirect is configured

### Step 7: Infrastructure Change Review
Review any infrastructure changes included in the deployment.
- **Infrastructure as Code review**:
  - Verify IaC changes match the deployment plan
  - Check for resource naming consistency
  - Verify tagging strategy compliance (cost allocation, ownership)
  - Check that resource sizing is appropriate for the workload
  - Verify network security group / firewall rule changes
- **Scaling configuration**:
  - Verify auto-scaling policies are configured
  - Check minimum/maximum instance counts
  - Verify scale-in/scale-out cooldown periods
  - Check that new instances are registered with load balancers
- **Disaster recovery**:
  - Verify multi-AZ or multi-region configuration
  - Check backup configuration (frequency, retention, restoration testing)
  - Verify data replication is correctly configured
  - Check that DR failover procedures are documented

### Step 8: Monitoring and Alerting Configuration Review
Verify monitoring coverage for the deployment and the new release.
- **Monitoring coverage**:
  - New endpoints: are they instrumented with request count, latency, error rate?
  - New services: are they included in dashboards?
  - Database migrations: are query performance metrics available?
  - Infrastructure changes: are new resources emitting metrics?
- **Alerting configuration**:
  - Verify alerts exist for deployment-specific risks:
    - Migration execution failure
    - Migration duration exceeding threshold
    - Service startup failure
    - Health check failure
    - Error rate spike after deployment
    - Rollback initiated
  - Check alert severity levels are correctly assigned
  - Verify alert notification channels (PagerDuty, Slack, email)
  - Check that alert response runbooks exist for deployment-related alerts
- **Dashboard updates**:
  - Verify dashboards include new metrics
  - Check that baseline comparisons are configured
  - Verify SLA/SLO tracking dashboards are updated

### Step 9: Compliance and Approval Gates
Verify all required approvals and compliance checks are passed.
- **Approval gates**:
  - Verify required approvers are defined in the pipeline
  - Check that approvals were obtained after the RC build (not pre-approved)
  - Verify approvers are not the same individuals who wrote the code
- **Compliance checks**:
  - Are audit logs enabled for the deployment?
  - Are change management records being created?
  - Are deployment artifacts signed or checksummed?
  - Are deployment scripts reviewed for malicious code?
- **Documentation**:
  - Verify deployment window is scheduled in the team calendar
  - Check that release notes are reviewed and approved
  - Verify deployment communication has been sent to stakeholders
  - Check that on-call team is aware of the deployment

### Step 10: Deployment Go/No-Go and Checklist Sign-off
Final review and sign-off before deployment execution.
- Compile the deployment review checklist:
  - Deployment plan scored >7/10
  - CI/CD pipeline reviewed and passes
  - Database migrations reviewed and reversible
  - Rollback procedure verified and tested
  - Smoke tests defined and automated
  - Configuration audited for production readiness
  - Infrastructure changes reviewed
  - Monitoring and alerting configured
  - All required approvals obtained
  - No unresolved issues from previous deployment review
- Decision:
  - **APPROVED**: all checks pass, proceed with deployment
  - **CONDITIONAL**: minor issues identified with documented mitigations, proceed with caution
  - **REJECTED**: major issues found, do not deploy until resolved
- Document the review report as `deployment-review-YYYY-MM-DD-vX.Y.Z.md`.
- Execute the pre-deployment communication to stakeholders.

## Verification Steps
- Deployment plan is reviewed and scored by a peer engineer (not the author)
- Database migration scripts are verified by running against a copy of production data
- Rollback procedure is validated by a dry-run in staging
- Smoke tests are executed in staging and all pass
- Monitoring dashboards are verified to show new service metrics
- All approval gates are confirmed passed in the deployment pipeline

## Expected Deliverables
- `deployment-review-YYYY-MM-DD-vX.Y.Z.md` — completed deployment review report
- Scored deployment plan with reviewer comments
- Database migration review checklist
- Rollback procedure validation results
- Smoke test execution results from staging
- Configuration audit findings
- Monitoring and alerting verification report

## Success Criteria
- Deployment plan scores >7/10 and is peer-reviewed
- Every database migration has a tested Down script
- Rollback procedure has been tested within 30 days and timing is documented
- Smoke tests execute in <5 minutes and all critical paths pass
- No secrets are present in configuration files
- Monitoring and alerts are confirmed operational for the release
- All required approvals are documented and obtained

## Failure Recovery
- If database migration is not reversible: do not deploy, redesign migration with reversible steps
- If rollback procedure is out of date: schedule a rollback drill before deployment
- If smoke tests fail in staging: engage QA to determine if it's a test issue or a release issue
- If configuration values are incorrect: fix in the correct environment, verify the fix
- If monitoring is not receiving metrics: troubleshoot the instrumentation before deployment
- If required approval is missing: delay deployment until approval is obtained
- If plan is scored <7: revise the plan with identified gaps, re-review

## Related SOPs
- `release-audit.md` — Release candidate go/no-go decision
- `database-review.md` — Detailed database migration review
- `performance-review.md` — Performance validation in deployment
- `security-audit.md` — Security configuration review
- `code-review.md` — Infrastructure code review standards
