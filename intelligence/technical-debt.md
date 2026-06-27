# Technical Debt Registry

## TDEBT-001: Monolith API Single Deployment
- **Area**: Deployment
- **Description**: All API endpoints are deployed as a single monolith service. This slows down deployments, increases blast radius, and prevents independent scaling of high-traffic endpoints.
- **Estimated Cost**: Each deployment takes 45 minutes. A single buggy endpoint can take down the entire API. Scaling the auth layer also scales search, increasing cost.
- **Estimated Effort**: 8 weeks (to split into 3 services: API, Auth, Admin)
- **Priority**: HIGH
- **Status**: In progress (see ADR-012)
- **Owner**: Platform Team
- **Added**: 2025-01-15
- **Tags**: microservices, deployment, scalability

## TDEBT-002: Missing Error Code Standardization
- **Area**: API Design
- **Description**: Error responses across endpoints are inconsistent. Some return `{error: "message"}`, others return `{errors: [...]}`, and HTTP status codes are sometimes wrong (e.g., 500 instead of 422 for validation errors).
- **Estimated Cost**: Each integration requires custom error handling. Debugging production issues takes longer. AI agents generate inconsistent error handling code.
- **Estimated Effort**: 2 weeks
- **Priority**: HIGH
- **Status**: Open
- **Owner**: Unassigned
- **Added**: 2025-02-01
- **Tags**: api, consistency, developer-experience

## TDEBT-003: No Automated API Contract Tests
- **Area**: Testing
- **Description**: API contracts are documented but not tested automatically. Changes to request/response shapes can break consumers without CI catching it.
- **Estimated Cost**: Consumers discover breaking changes in production or during manual testing. Contract drift between documentation and implementation.
- **Estimated Effort**: 3 weeks
- **Priority**: HIGH
- **Status**: Open
- **Owner**: Unassigned
- **Added**: 2025-02-10
- **Tags**: testing, api, ci-cd

## TDEBT-004: Test Suite Takes 45 Minutes
- **Area**: CI/CD
- **Description**: The full test suite takes 45 minutes to run. Developers skip running tests locally and rely on CI, creating long feedback loops.
- **Estimated Cost**: Average of 3 CI runs per PR = over 2 hours of waiting per PR. Approximately 40 PRs/week = 80 hours/week of wasted CI time.
- **Estimated Effort**: 3 weeks (parallelization, test splitting, worker optimization)
- **Priority**: HIGH
- **Status**: Open
- **Owner**: Unassigned
- **Added**: 2025-02-15
- **Tags**: testing, ci-cd, performance

## TDEBT-005: No Database Migration Rollback Plan
- **Area**: Database
- **Description**: Prisma migrations only support forward. There is no standardized rollback procedure. Failed migrations require manual database intervention.
- **Estimated Cost**: Each failed migration takes 2-4 hours of DBA time to resolve. Production deployment risk is elevated.
- **Estimated Effort**: 2 weeks
- **Priority**: MEDIUM
- **Status**: Open
- **Owner**: Unassigned
- **Added**: 2025-03-01
- **Tags**: database, deployment, risk

## TDEBT-006: Legacy Express Services Not Migrated
- **Area**: Code Quality
- **Description**: Two services still use Express.js instead of Hono (see ADR-004). They have inconsistent error handling and slower performance.
- **Estimated Cost**: 15% slower request throughput, inconsistent middleware patterns, harder to onboard new engineers.
- **Estimated Effort**: 4 weeks (2 weeks per service)
- **Priority**: MEDIUM
- **Status**: Open
- **Owner**: Unassigned
- **Added**: 2025-03-10
- **Tags**: migration, express, hono

## TDEBT-007: Insufficient Observability on Background Workers
- **Area**: Observability
- **Description**: Background workers are not fully instrumented with OpenTelemetry. Job failures are hard to diagnose. There is no tracing for job execution flow.
- **Estimated Cost**: Debugging worker issues takes 3x longer. Silent failures go undetected until users complain.
- **Estimated Effort**: 2 weeks
- **Priority**: MEDIUM
- **Status**: Open
- **Owner**: Unassigned
- **Added**: 2025-03-15
- **Tags**: observability, workers, debugging

## TDEBT-008: No Load Testing in CI
- **Area**: Testing
- **Description**: There are no automated load tests. Performance regressions are only caught after deployment under real traffic.
- **Estimated Cost**: Performance incident every ~2 months. Average incident resolution time: 4 hours.
- **Estimated Effort**: 3 weeks
- **Priority**: MEDIUM
- **Status**: Open
- **Owner**: Unassigned
- **Added**: 2025-03-20
- **Tags**: testing, performance, ci-cd

## TDEBT-009: Hardcoded Configuration Values
- **Area**: Code Quality
- **Description**: Several services have hardcoded configuration values (timeouts, retry counts, URLs) instead of using environment variables or a config service.
- **Estimated Cost**: Configuration changes require code deployments. Environment-specific bugs surface in staging vs production.
- **Estimated Effort**: 1 week
- **Priority**: MEDIUM
- **Status**: Open
- **Owner**: Unassigned
- **Added**: 2025-04-01
- **Tags**: configuration, code-quality

## TDEBT-010: No Feature Flag System
- **Area**: Infrastructure
- **Description**: Feature toggles are implemented ad-hoc with environment variables or commented code. There is no centralized feature flag system.
- **Estimated Cost**: Each feature flag takes 2-4 hours to implement. Canary releases and gradual rollouts are difficult. Kill switches are slow to activate.
- **Estimated Effort**: 4 weeks
- **Priority**: MEDIUM
- **Status**: Open
- **Owner**: Unassigned
- **Added**: 2025-04-05
- **Tags**: infrastructure, releases, risk

## TDEBT-011: Duplicate Validation Logic
- **Area**: Code Quality
- **Description**: Input validation is duplicated between frontend (Zod) and backend (Zod). The shared validation package is not well-maintained, causing drift.
- **Estimated Cost**: 5-10 bugs per quarter caused by validation mismatch. Code review overhead to catch inconsistencies.
- **Estimated Effort**: 2 weeks (enforce shared validation package)
- **Priority**: LOW
- **Status**: Open
- **Owner**: Unassigned
- **Added**: 2025-04-10
- **Tags**: validation, frontend, backend

## TDEBT-012: Incomplete Audit Trail Coverage
- **Area**: Compliance
- **Description**: BR-021 requires audit trails for all mutating operations, but only order operations are currently audited. Products, users, and discounts are not covered.
- **Estimated Cost**: Compliance risk during audit. Harder to debug issues in non-audited areas.
- **Estimated Effort**: 3 weeks
- **Priority**: LOW
- **Status**: Open
- **Owner**: Unassigned
- **Added**: 2025-04-15
- **Tags**: compliance, audit, security
