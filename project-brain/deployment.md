# Deployment

## Deployment Architecture Overview

The application is deployed on AWS EKS (Kubernetes) with a multi-region (us-east-1 primary, us-west-2 DR) architecture. Traffic flows through CloudFront (CDN) → WAF → ALB → EKS (Fargate) → AWS managed services (RDS, ElastiCache, OpenSearch, S3).

### Architecture Diagram

```
                          ┌──────────────────────┐
                          │   CloudFront (CDN)    │
                          │   SSL Termination     │
                          └──────────┬───────────┘
                                     │
                          ┌──────────┴───────────┐
                          │   WAF (AWS WAF)       │
                          │   OWASP Rules + Rate  │
                          └──────────┬───────────┘
                                     │
                          ┌──────────┴───────────┐
                          │   ALB (Load Balancer) │
                          │   SSL + Routing       │
                          └──────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
    ┌─────────┴─────────┐  ┌────────┴─────────┐  ┌────────┴─────────┐
    │  EKS (us-east-1)   │  │  EKS (us-west-2)  │  │  EKS Fargate     │
    │  - API Pods        │  │  (DR)             │  │  - Workers       │
    │  - Worker Pods     │  │  Standby          │  │  - CronJobs      │
    │  - CronJobs        │  │  Replicas: 1      │  │                  │
    │  Replicas: 3-8     │  │  Auto-scaled      │  │                  │
    └─────────┬─────────┘  └───────────────────┘  └───────────────────┘
              │
    ┌─────────┴───────────────────────────────────────────────┐
    │                    AWS Managed Services                  │
    │                                                          │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │
    │  │  RDS     │  │  Redis   │  │OpenSearch│  │  S3     │  │
    │  │PostgreSQL│  │ElastiCache│  │          │  │Objects  │  │
    │  │Multi-AZ  │  │Cluster   │  │ 3 nodes  │  │Bucket   │  │
    │  └──────────┘  └──────────┘  └──────────┘  └─────────┘  │
    └──────────────────────────────────────────────────────────┘
```

## Environment Strategy

| Environment | Purpose | URL | Auto-deploy | Data | Scale |
|-------------|---------|-----|-------------|------|-------|
| **dev** | Feature development, integration testing | dev.app.ourcompany.com | Every PR merge to `main` | Anonymized subset (10%) | 1 replica, single-AZ |
| **staging** | Pre-production validation, performance testing | staging.app.ourcompany.com | Manual trigger after dev smoke tests | Full anonymized copy (production schema) | 2 replicas, single-AZ |
| **prod** | Production traffic | app.ourcompany.com | Manual approval after staging | Production data | 3-8 replicas, multi-AZ, auto-scaling |

### Environment Configuration

| Configuration | dev | staging | prod |
|--------------|-----|---------|------|
| Kubernetes namespace | `app-dev` | `app-staging` | `app-prod` |
| DB instance class | db.t3.medium | db.r6g.large | db.r6g.xlarge (multi-AZ) |
| Redis node type | cache.t3.micro | cache.r6g.large | cache.r6g.xlarge (cluster mode) |
| OpenSearch nodes | 1 (t3.small.search) | 2 (r6g.large.search) | 3 (r6g.xlarge.search) |
| CDN enabled | No | Yes (staging-only behavior) | Yes (production behavior) |
| Log retention | 7 days | 30 days | 365 days (audit), 90 days (app) |
| Monitoring alerts | Slack only | Slack + Email | Slack + Email + PagerDuty |

## Infrastructure as Code

### Tooling

- **Terraform** (v1.7+) for all AWS infrastructure
- **Helm** (v3.14+) for Kubernetes application deployments
- **Kustomize** for environment-specific Kubernetes overlay patches
- **Terragrunt** for Terraform state management and module composition

### Repository Structure

```
infrastructure/
├── terraform/
│   ├── modules/
│   │   ├── eks/                  # EKS cluster module
│   │   ├── rds/                  # RDS PostgreSQL module
│   │   ├── redis/                # ElastiCache Redis module
│   │   ├── opensearch/           # OpenSearch domain module
│   │   ├── s3/                   # S3 bucket module
│   │   ├── networking/           # VPC, subnets, security groups
│   │   ├── cdn/                  # CloudFront distribution
│   │   └── monitoring/           # CloudWatch, alarms, dashboards
│   ├── environments/
│   │   ├── dev/
│   │   │   ├── main.tf
│   │   │   ├── terraform.tfvars
│   │   │   └── backend.tf
│   │   ├── staging/
│   │   └── prod/
│   └── global/
│       ├── iam/                  # IAM roles, policies
│       └── route53/              # DNS zones
├── helm/
│   └── app/
│       ├── Chart.yaml
│       ├── values/
│       │   ├── dev.yaml
│       │   ├── staging.yaml
│       │   └── prod.yaml
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── ingress.yaml
│           ├── hpa.yaml
│           ├── configmap.yaml
│           ├── secrets.yaml
│           ├── serviceaccount.yaml
│           └── _helpers.tpl
└── kustomize/
    ├── base/
    │   ├── kustomization.yaml
    │   ├── deployment.yaml
    │   └── service.yaml
    └── overlays/
        ├── dev/
        ├── staging/
        └── prod/
```

### Infrastructure Change Process

1. Developer creates a PR modifying Terraform/Helm/Kustomize files
2. CI runs `terraform plan` and posts the diff as a PR comment
3. PR is reviewed by a team member with infrastructure permissions
4. On merge to `main`, CI applies `terraform plan` to dev (auto-approve)
5. Staging and prod require manual approval via GitHub Environments
6. All state changes are logged with CloudTrail

## CI/CD Pipeline

### Pipeline Overview (GitHub Actions)

```
                    ┌──────────────────┐
                    │  PR Opened/Sync   │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Lint + Typecheck │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Unit Tests       │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Build (Docker)   │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  🧪 Integration   │
                    │  Tests            │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Security Scan    │
                    │  (SAST + Dep +   │
                    │   Container)     │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Deploy to Dev    │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Smoke Tests (Dev)│
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Manual Approval  │
                    │  (Staging)        │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Deploy to Staging│
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Smoke + E2E      │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Manual Approval  │
                    │  (Production)     │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Deploy to Prod   │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Canary (10%)      │
                    ├── 30 min watch ──┤
                    ├── Rollout (50%)   │
                    ├── 30 min watch ──┤
                    ├── Rollout (100%)  │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │  Post-Deploy      │
                    │  Smoke + Monitors │
                    └──────────────────┘
```

### Pipeline Configuration (GitHub Actions Workflow)

```yaml
name: Deploy
on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        type: choice
        options: [dev, staging, prod]
      version:
        description: 'Docker image tag (default: git SHA)'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run test -- --coverage
      - run: npm run test:integration
      - name: Security scans
        run: |
          npm audit --audit-level=high
          npx snyk test --severity-threshold=high

  build:
    needs: [test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build & push Docker image
        run: |
          docker build -t ${{ vars.ECR_REGISTRY }}/app:${{ github.sha }} .
          docker push ${{ vars.ECR_REGISTRY }}/app:${{ github.sha }}
      - name: Scan image
        run: trivy image ${{ vars.ECR_REGISTRY }}/app:${{ github.sha }}

  deploy-dev:
    needs: [build]
    environment: dev
    steps:
      - run: ./deploy.sh dev ${{ github.sha }}
      - run: npm run smoke:dev

  deploy-staging:
    needs: [deploy-dev]
    environment: staging
    steps:
      - run: ./deploy.sh staging ${{ github.sha }}
      - run: npm run smoke:staging
      - run: npm run test:e2e

  deploy-prod:
    needs: [deploy-staging]
    environment: prod
    steps:
      - name: Canary 10%
        run: ./deploy.sh prod ${{ github.sha }} --canary=10
      - name: Watch metrics (30 min)
        run: ./watch-canary.sh --timeout=30
      - name: Rollout 50%
        run: ./deploy.sh prod ${{ github.sha }} --canary=50
      - name: Watch metrics (30 min)
        run: ./watch-canary.sh --timeout=30
      - name: Rollout 100%
        run: ./deploy.sh prod ${{ github.sha }} --canary=100
      - name: Post-deploy smoke tests
        run: npm run smoke:prod
```

## Build Process

### Docker Image

```dockerfile
# Multi-stage build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV NODE_ENV=production
CMD ["node", "server.js"]
```

### Build Artifacts

| Artifact | Location | Retention |
|----------|----------|-----------|
| Docker image | Amazon ECR (app repo) | Latest 50 tags, all tags < 90 days |
| Static assets | S3 (assets bucket) | Immutable (versioned), never deleted |
| Source code | GitHub | Permanent |
| npm packages | npm registry (private) | Permanent |
| Terraform state | S3 (terraform-state bucket) | Versioned, never deleted |
| Build logs | GitHub Actions | 90 days |
| Deployment logs | CloudWatch Logs | 365 days |

## Database Migration Process

### Migration Strategy

- **Tool**: Flyway (Java-based, but runs as a Kubernetes job)
- **Versioning**: Sequential numeric versions (V001__description.sql, V002__description.sql)
- **Location**: `src/main/resources/db/migration/`
- **Idempotency**: Migrations are written with `IF NOT EXISTS` / `IF EXISTS` guards

### Migration Types

| Type | Prefix | Example | Rollback |
|------|--------|---------|----------|
| Versioned | `V` | `V042__add_user_preferences_table.sql` | Manual (reverse migration script) |
| Repeatable | `R` | `R__user_permissions_view.sql` | Re-run on change |
| Undo | `U` | `U042__drop_user_preferences_table.sql` | Explicit undo script |

### Migration Process in CI/CD

1. CI builds the application image (includes migration scripts)
2. Pre-deploy hook runs `flyway migrate` against the target database
3. If migration fails:
   - Pipeline stops (stage: failed)
   - `flyway repair` is NOT automatically run (requires manual intervention)
   - On-call engineer investigates and resolves
4. If migration succeeds, application deployment proceeds
5. Rollback: `flyway undo` (if undo script exists) or manual SQL restore from backup

### Zero-Downtime Migration Guidelines

- **Add column**: Use `ALTER TABLE ... ADD COLUMN ... DEFAULT ...` (PostgreSQL 11+ handles this without table rewrite for non-null defaults)
- **Remove column**: Deploy in two phases: (1) stop writing to column, (2) remove column
- **Rename column**: Deploy in three phases: (1) add new column, (2) dual-write + backfill, (3) remove old column
- **Add index**: Use `CONCURRENTLY` to avoid table locks
- **Drop constraint**: Can be immediate if no active transactions depend on it
- **Large data migration**: Run as background job, not in migration script

## Deployment Steps

### Standard Deployment (Manual Trigger)

1. **Verify readiness**: Check monitoring dashboards for any active incidents
2. **Create release**: Tag commit with semantic version (`git tag v2.4.0 && git push --tags`)
3. **Trigger pipeline**: `gh workflow run deploy.yml -f environment=staging`
4. **Monitor staging**: Verify smoke tests pass, check staging monitoring dashboard
5. **Trigger staging → prod approval**: Review the diff, approve in GitHub Environments
6. **Monitor canary (10%)**: Watch error rates, latency, CPU/memory for 30 minutes
7. **Manual canary promotion**: If metrics healthy, promote to 50%
8. **Monitor 50%**: Watch same metrics for 30 minutes
9. **Full rollout**: Promote to 100%
10. **Post-deploy verification**: Run smoke tests, verify critical user journey manually
11. **Announce**: Post in `#deployments` Slack channel with release notes link

### Emergency Deployment (Hotfix)

1. Branch from the production tag (not from `main`)
2. Commit the minimal fix
3. Push branch and create PR targeting `main`
4. CI runs tests on the branch
5. **Skipped**: Staging deployment (skipped for hotfixes — risk accepted)
6. Deploy directly to production using `workflow_dispatch` with `environment: prod`
7. Fix forward: merge hotfix PR into `main`

### Deployment Script (simplified)

```bash
#!/bin/bash
# deploy.sh — Deploy to EKS
set -euo pipefail

ENV=$1
TAG=$2
CANARY=${3:-100}

echo "Deploying ${TAG} to ${ENV} (canary: ${CANARY}%)"

# Authenticate with EKS
aws eks update-kubeconfig --region us-east-1 --name "app-${ENV}"

# Update deployment image
kubectl set image deployment/app "app=${ECR_REGISTRY}/app:${TAG}" -n "app-${ENV}"

# For canary deployments, adjust replica weights
if [ "$CANARY" != "100" ]; then
  CANARY_REPLICAS=$(( $(kubectl get deployment app -n "app-${ENV}" -o jsonpath='{.spec.replicas}') * CANARY / 100 ))
  kubectl scale deployment app-canary --replicas=$CANARY_REPLICAS -n "app-${ENV}"
  echo "Canary scaled to ${CANARY_REPLICAS} replicas (${CANARY}%)"
fi

# Wait for rollout
kubectl rollout status deployment/app -n "app-${ENV}" --timeout=300s

echo "Deployment to ${ENV} complete"
```

## Rollback Procedure

### Automated Rollback (Triggers)

Rollback is automatically triggered if any of these conditions are met within 30 minutes of deployment:

1. Error rate increases by >5% (baseline: previous 24h average)
2. p95 latency increases by >50% (baseline: previous 24h average)
3. 5xx response rate >1% of total requests
4. Health check endpoint returns non-200 for 3 consecutive checks
5. Any P1/P2 alert fires on the new deployment

### Manual Rollback Steps

```bash
# Step 1: Identify previous stable revision
kubectl rollout history deployment/app -n app-prod

# Step 2: Rollback to previous revision
kubectl rollout undo deployment/app -n app-prod --to-revision=42

# Step 3: Verify rollback
kubectl rollout status deployment/app -n app-prod
kubectl get pods -n app-prod | grep app

# Step 4: Check monitoring
# Verify error rate drops, latency normalizes

# Step 5: If DB migration was part of the release:
#   - Check if migration is backward-compatible (should be)
#   - If not, run the revert/undo migration
flyway undo -target=<previous-version>

# Step 6: Communicate in #deployments
```

### Database Rollback

- **Schema changes**: Must have corresponding `U` (undo) migration script
- **Data changes**: Restore from backup (automated, ~15 min RTO for RDS)
- **If rollback is required and no undo script exists**: Restore from backup

## Smoke Test Procedure

### Automated Smoke Tests

Run after every deployment to all environments:

```typescript
// smoke-tests.ts
const tests = [
  { name: "Homepage loads", url: "/", expect: 200, expectBody: "root" },
  { name: "Login page loads", url: "/login", expect: 200 },
  { name: "API health check", url: "/api/health", expect: 200, expectBody: '"status":"ok"' },
  { name: "Static assets served", url: "/assets/app-abc123.js", expect: 200 },
  { name: "404 page returns correctly", url: "/nonexistent-page", expect: 404 },
  { name: "Auth redirects unauthenticated", url: "/dashboard", expect: 302 },
  { name: "Database connection", url: "/api/health/db", expect: 200 },
  { name: "Redis connection", url: "/api/health/redis", expect: 200 },
  { name: "OpenSearch connection", url: "/api/health/search", expect: 200 },
  { name: "CDN cache hit", url: "/", expect: 200, expectHeader: "x-cache: Hit from cloudfront" },
];

for (const test of tests) {
  const response = await fetch(`${BASE_URL}${test.url}`);
  assert(response.status === test.expect, `Expected ${test.expect}, got ${response.status}`);
  if (test.expectBody) {
    const body = await response.text();
    assert(body.includes(test.expectBody), `Body missing ${test.expectBody}`);
  }
  console.log(`✅ ${test.name}`);
}
```

### Manual Smoke Test Checklist (Pre-Production)

- [ ] Login with email/password
- [ ] Login with Google SSO
- [ ] Login with MFA
- [ ] Create a new document
- [ ] Edit and save an existing document
- [ ] Search for content and verify results
- [ ] Generate and export a report (CSV, PDF)
- [ ] Upload a file (small and large)
- [ ] Invite a user to the organization
- [ ] Change user role and verify permission changes
- [ ] Verify notification bell shows unread count
- [ ] Navigate between all major sections
- [ ] Verify mobile responsive layout
- [ ] Toggle dark mode and verify rendering
- [ ] Logout and verify session cleared

## Monitoring and Alerting

### Infrastructure Monitoring

| Tool | Purpose | Coverage |
|------|---------|----------|
| CloudWatch | AWS metrics, logs, alarms | All AWS resources |
| Datadog | APM, traces, custom metrics, dashboards | Application containers, databases |
| PagerDuty | Incident alerting and on-call scheduling | Critical alerts |
| Statuspage | External status page | Public-facing availability |
| Grafana | Custom dashboards, log analytics | Aggregated metrics from CloudWatch + Datadog |

### Key Metrics Dashboard

```yaml
dashboard:
  title: "Production Health Overview"
  panels:
    - title: "Request Rate (req/s)"
      metric: "app.requests.total"
      stat: "sum"
      interval: "1m"
    - title: "Error Rate (%)"
      metric: "app.requests.errors / app.requests.total * 100"
      stat: "avg"
      threshold: 1
    - title: "p95 Latency (ms)"
      metric: "app.latency.p95"
      stat: "avg"
      threshold: 1000
    - title: "Active Users"
      metric: "app.sessions.active"
      stat: "avg"
    - title: "Database Connections"
      metric: "aws.rds.connections"
      stat: "avg"
      threshold: 80 (percent of max)
    - title: "CPU Utilization (%)"
      metric: "aws.ecs.cpu"
      stat: "avg"
      threshold: 70
    - title: "Memory Utilization (%)"
      metric: "aws.ecs.memory"
      stat: "avg"
      threshold: 80
```

### Alert Rules

| Alert | Condition | Severity | Notification |
|-------|-----------|----------|--------------|
| High error rate | Error rate > 5% for 5 minutes | P1 | PagerDuty + Slack |
| High latency | p95 > 2000ms for 5 minutes | P1 | PagerDuty + Slack |
| Health check failure | Health endpoint 5xx for 3 consecutive checks | P1 | PagerDuty + Slack |
| Database connection pool | Connections > 80% of max for 5 minutes | P2 | Slack |
| CPU throttling | CPU > 80% for 10 minutes | P2 | Slack |
| Disk space | Disk > 85% for 5 minutes | P2 | Slack |
| Certificate expiry | TLS certificate expires in < 30 days | P2 | Slack + Email |
| Backup failure | Scheduled backup fails | P2 | Slack |
| SSL certificate expired | Certificate has expired | P1 | PagerDuty + Slack |
| Rate limit threshold | > 80% of rate limit used | P3 | Slack |

## Logging Infrastructure

### Log Aggregation

```
Application Logs (stdout) → CloudWatch Logs → Subscription Filter → Datadog Logs
                                                                    ↓
                                                              S3 Archive (Parquet)
                                                                    ↓
                                                              Athena Queries
```

### Log Levels

| Level | Usage | Retention |
|-------|-------|-----------|
| ERROR | Unhandled exceptions, failed operations, security events | 365 days |
| WARN | Recoverable errors, degraded performance, deprecated API usage | 90 days |
| INFO | Business events (user created, report generated), request lifecycle | 30 days |
| DEBUG | Detailed debugging information (disabled in production) | 7 days (dev only) |
| TRACE | Request-level tracing (disabled in production) | 1 day (dev only) |

### Log Format

```json
{
  "timestamp": "2026-06-25T14:30:00.123Z",
  "level": "ERROR",
  "service": "api",
  "environment": "prod",
  "trace_id": "abc123def456",
  "span_id": "789012ghi345",
  "message": "Failed to process payment",
  "error": {
    "type": "PaymentError",
    "message": "Card declined: insufficient funds",
    "stack": "PaymentError: ..."
  },
  "user": {
    "id": "usr_abc123",
    "org_id": "org_def456"
  },
  "request": {
    "method": "POST",
    "path": "/api/v1/payments",
    "status": 402,
    "duration_ms": 1234
  },
  "metadata": {
    "payment_provider": "stripe",
    "payment_intent_id": "pi_abc123"
  }
}
```

## Backup and Restore

### Backup Schedule

| Data Source | Type | Frequency | Retention | Storage |
|-------------|------|-----------|-----------|---------|
| PostgreSQL (production) | Full dump | Daily | 30 days daily, 12 monthly, 3 yearly | S3 (encrypted) |
| PostgreSQL (production) | WAL archiving | Continuous (5 min) | 7 days | S3 (encrypted) |
| PostgreSQL (production) | pg_dump | Weekly | 6 months | S3 (Glacier) |
| Redis | RDB snapshot | Every 6 hours | 7 days | S3 (encrypted) |
| OpenSearch | Snapshot | Daily | 14 days | S3 (encrypted) |
| S3 user uploads | Cross-region replication | Real-time | Same as source | S3 (us-west-2) |
| Application configs | Terraform state | On change | Versioned indefinitely | S3 (versioned bucket) |

### Restore Procedure

```bash
# Step 1: Identify the backup to restore
aws s3 ls s3://app-backups/prod/postgresql/
# Locate the desired backup file: prod_2026-06-25_143000.sql.gz.gpg

# Step 2: Decrypt and decompress
aws s3 cp s3://app-backups/prod/postgresql/prod_2026-06-25_143000.sql.gz.gpg .
gpg --decrypt --output prod_2026-06-25.sql.gz prod_2026-06-25_143000.sql.gz.gpg
gunzip prod_2026-06-25.sql.gz

# Step 3: Restore to target database
# Target must be a new, empty database (never restore to an existing production DB)
createdb app_restore_20260625
psql -d app_restore_20260625 -f prod_2026-06-25.sql

# Step 4: Verify restore
psql -d app_restore_20260625 -c "SELECT COUNT(*) FROM users;"

# Step 5: Point application to restored database
# (Update ConfigMap/Secrets and restart pods)

# Step 6: Verify application functionality with restored data
```

### Point-in-Time Recovery (PITR)

- **RDS PITR**: Supported for PostgreSQL (restore to any point within the backup retention window)
- **Procedure**: Use AWS Console/CLI to restore to a specific timestamp
- **Recovery Point Objective (RPO)**: 5 minutes (WAL shipping interval)
- **Recovery Time Objective (RTO)**: 1 hour (database restore + verification)

## Disaster Recovery Plan

### DR Strategy: Active-Passive (Warm Standby)

| Component | Primary (us-east-1) | DR (us-west-2) |
|-----------|-------------------|----------------|
| Database | Primary RDS (Multi-AZ) | Read replica promoted to primary |
| Cache | Redis cluster | Redis cluster (empty) |
| Application | EKS Fargate (3+ replicas) | EKS Fargate (1 replica, auto-scale) |
| Storage | S3 bucket | Cross-region replicated S3 |
| DNS | Route53 (Active) | Route53 (standby, failover record) |

### DR Scenarios

#### Single-AZ Failure (us-east-1a → us-east-1b)

- RDS Multi-AZ automatically fails over (30-60s downtime)
- EKS spreads pods across AZs automatically
- ALB routes to healthy targets
- No manual intervention required

#### Region Failure (us-east-1)

1. **Detection**: Route53 health check fails for 5 consecutive checks
2. **Notification**: P1 alert pages on-call + infrastructure team (automated)
3. **Database failover**: Promote us-west-2 read replica to primary (manual approval required)
4. **Application failover**: Scale up us-west-2 EKS cluster; update DNS in Route53
5. **DNS propagation**: Route53 failover record updates (TTL: 60s)
6. **Verification**: Run smoke tests against DR URL

**DR RTO**: 30 minutes (database promotion + DNS propagation + application scaling)
**DR RPO**: 5 minutes (synchronous replication: planned; asynchronous: actual ~30s-2min)

### DR Test Schedule

- Quarterly: Tabletop exercise (walk through DR plan with team)
- Annually: Full DR test (actual failover to us-west-2, run for 4 hours, fail back)

## Incident Response Procedure

### Incident Lifecycle

1. **Detection**: Alert triggers, user report, or monitoring dashboard anomaly
2. **Triage (5 min)**: On-call engineer acknowledges, assesses severity
3. **Contain (15 min)**: Apply immediate mitigation (revert deploy, block traffic, scale up)
4. **Diagnosis (30 min)**: Root cause analysis — logs, metrics, traces
5. **Resolution (60 min)**: Deploy fix or apply workaround
6. **Recovery (15 min)**: Verify fix, monitor stabilization
7. **Post-mortem (5 business days)**: RCA document, action items, timeline

### Incident Severity Matrix

| Severity | Definition | Response | Communication |
|----------|------------|----------|---------------|
| SEV-1 | Complete outage, data loss, security breach | Immediate, all hands | #incidents Slack, status page update |
| SEV-2 | Major feature broken, degraded performance for >10% of users | < 15 min response | #incidents Slack |
| SEV-3 | Minor feature degraded, < 5% of users affected | < 1 hour response | #engineering Slack |
| SEV-4 | Cosmetic issues, non-critical bugs | Next business day | Jira ticket |

### On-Call Schedule

| Week | Primary | Secondary | Escalation |
|------|---------|-----------|------------|
| Week 1 | Alice | Bob | Carol (Eng Lead) |
| Week 2 | Bob | Carol | Alice (Eng Lead) |
| Week 3 | Carol | Alice | Bob (Eng Lead) |
| Week 4 | Dave | Eve | Frank (SRE Lead) |

## Runbooks (Quick Reference)

### Runbook: High Error Rate

```
1. Check Datadog APM dashboard for error distribution by service
2. Check if error correlates with recent deployment (if so, rollback)
3. Check CloudWatch logs for error patterns
4. Check database connection pool utilization
5. Check for upstream service degradation (Stripe, SendGrid, Auth0)
6. If database-related: check pg_stat_activity for long-running queries
7. If upstream: enable circuit breaker for that service
8. If inconclusive: enable DEBUG logging on affected service, reproduce
```

### Runbook: Database Connection Pool Exhaustion

```
1. Check RDS Connections dashboard (CloudWatch)
2. Kill idle transactions: SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle in transaction' AND state_change < NOW() - INTERVAL '5 min'
3. Check for blocking locks: SELECT * FROM pg_locks WHERE NOT granted
4. Kill blocking sessions if necessary
5. Increase pool size in application config if needed (hotfix)
6. Add read replicas for read-heavy workloads
```

### Runbook: Slow Application Response

```
1. Check Datadog traces for slow endpoints
2. Identify slow database queries (pg_stat_statements)
3. Check missing indexes (pg_stat_user_indexes)
4. Check cache hit ratios (Redis, CDN)
5. Check for memory leaks (container memory usage over time)
6. Check for garbage collection pressure (Node.js heap dumps)
7. Scale up or right-size instances if resource-constrained
```

## Capacity Planning

### Current Utilization

| Resource | Current Usage | Capacity | Growth Rate | Projected Exhaustion |
|----------|--------------|----------|-------------|---------------------|
| RDS (db.r6g.xlarge) | 45% CPU, 60% connections | 200 max connections | +15% quarterly | Q1 2027 |
| Redis (cache.r6g.xlarge) | 55% memory, 40% CPU | 52 GB | +10% quarterly | Q2 2027 |
| OpenSearch (3 x r6g.xlarge) | 50% storage, 30% CPU | 1.5 TB each | +20% quarterly | Q3 2026 (storage) |
| EKS CPU | 40% average, 70% peak | 32 vCPU (8 nodes) | +15% quarterly | Q4 2026 |
| EKS Memory | 50% average, 75% peak | 128 GB (8 nodes) | +15% quarterly | Q4 2026 |
| S3 Storage | 2.5 TB | Unlimited (request scaling) | +25% quarterly | Request rate: Q1 2027 |
| CDN (CloudFront) | 500 GB/month | 10 TB/month (AWS default) | +20% quarterly | Q2 2027 |

### Scaling Triggers

| Resource | Scale Up Trigger | Scale Down Trigger |
|----------|-----------------|-------------------|
| EKS (HPA) | CPU > 70% or Memory > 75% for 5 min | CPU < 30% and Memory < 40% for 15 min |
| RDS | CPU > 75% for 10 min or Connections > 80% for 5 min | CPU < 30% and Connections < 40% for 7 days |
| Redis | Memory > 80% for 5 min | Memory < 50% for 7 days |
| OpenSearch | Storage > 75% or CPU > 70% for 10 min | Manual review required |

### Quarterly Review

Capacity is reviewed quarterly (first sprint of each quarter) as part of the planning process. The review includes:
1. Current utilization metrics
2. Growth trends (last 3 quarters)
3. Planned feature launches and expected load impact
4. Budget for infrastructure scaling
5. Recommendations for instance size changes or architecture changes
