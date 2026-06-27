# Decision Log (Architecture Decision Records)

## ADR-001: Use PostgreSQL as Primary Database
- **Date**: 2025-01-15
- **Status**: Accepted
- **Context**: Needed a relational database for e-commerce data with ACID compliance, complex queries, and JSON support for flexible product attributes.
- **Decision**: Use PostgreSQL 16. Rejected MySQL due to weaker JSON support and less mature ecosystem. Rejected MongoDB due to lack of transactions across shards.
- **Consequences**: Requires careful connection pooling (PgBouncer). JSONB columns enable schema flexibility without a separate document store. Read replicas can scale query throughput.
- **Compliance**: All services must use Prisma ORM with PostgreSQL adapter.

## ADR-002: Use Redis for Caching and Queuing
- **Date**: 2025-01-20
- **Status**: Accepted
- **Context**: Needed low-latency caching for session data, product catalog, and API responses. Also needed a message broker for background jobs.
- **Decision**: Use Redis for both cache and queue (BullMQ). Avoids operational complexity of maintaining a separate message broker like RabbitMQ.
- **Consequences**: Single point of failure if Redis goes down — must deploy in cluster mode with sentinel. Memory pressure requires careful TTL management and eviction policies (allkeys-lru).
- **Compliance**: Use BullMQ for job queues. Use Redis cache with max 1 hour TTL.

## ADR-003: Adopt CQRS for Order Processing
- **Date**: 2025-02-01
- **Status**: Accepted
- **Context**: Order read patterns (order history, search) differ significantly from write patterns (placement, cancellation). The same model was causing contention and slow queries.
- **Decision**: Separate read and write models. Write model uses normalized tables. Read model uses denormalized materialized views refreshed by domain events.
- **Consequences**: Increased code complexity due to two models. Eventual consistency of up to 1 second for read models. Requires event versioning for schema evolution.
- **Compliance**: All order queries must use the read model. All mutations must go through the write model.

## ADR-004: Use Hono Instead of Express
- **Date**: 2025-02-10
- **Status**: Accepted
- **Context**: Express.js has historical performance issues and a middleware model that makes TypeScript integration awkward. Need a lightweight, fast, TypeScript-native framework.
- **Decision**: Use Hono as the HTTP framework for API services. Rejected Fastify due to plugin complexity. Rejected Express due to TypeScript ergonomics.
- **Consequences**: Smaller ecosystem than Express. Must build or adopt middleware for auth, rate limiting, etc. Hono's RPC mode enables type-safe client-server communication.
- **Compliance**: New API services must use Hono. Existing Express services will be migrated incrementally.

## ADR-005: Use Prisma as ORM
- **Date**: 2025-02-15
- **Status**: Accepted
- **Context**: Needed type-safe database access with migrations, relationship handling, and excellent developer experience.
- **Decision**: Use Prisma. Rejected TypeORM due to slower development cycle and complex decorator syntax. Rejected Drizzle due to smaller ecosystem at time of decision.
- **Consequences**: Prisma generates types from schema, reducing boilerplate. Migrations are declarative. N+1 query prevention requires explicit include/select clauses. Can be slower than raw SQL for complex queries — may need raw query escape hatch.
- **Compliance**: All database access must use Prisma client. Raw queries allowed only with explicit review.

## ADR-006: Use Zod for Runtime Validation
- **Date**: 2025-02-20
- **Status**: Accepted
- **Context**: Need runtime validation that generates TypeScript types to avoid duplication between runtime checks and static types.
- **Decision**: Use Zod for all input validation. Schema definitions produce inferred types consumed by the rest of the codebase.
- **Consequences**: Single source of truth for data shapes. Eliminates manual type interface definitions. Adds build-time step for type generation. Schema sharing between frontend and backend possible via package.
- **Compliance**: Every API endpoint must have a Zod schema for request validation.

## ADR-007: Use OpenTelemetry for Observability
- **Date**: 2025-03-01
- **Status**: Accepted
- **Context**: Needed vendor-neutral observability standard to avoid lock-in. Multiple team members had experience with OpenTelemetry.
- **Decision**: Adopt OpenTelemetry for traces, metrics, and logs. Export to Datadog via OpenTelemetry collector.
- **Consequences**: Standardized instrumentation across services. Can switch vendors by changing collector configuration. Requires careful sampling strategy to manage cost (head-based sampling for high-traffic endpoints).
- **Compliance**: All services must be instrumented with OpenTelemetry SDK. Health check endpoints excluded from tracing.

## ADR-008: Use Kubernetes for Container Orchestration
- **Date**: 2025-03-10
- **Status**: Accepted
- **Context**: Need auto-scaling, rolling deployments, self-healing, and environment parity. Application is containerized.
- **Decision**: Deploy on Kubernetes (EKS). Rejected ECS due to vendor lock-in concerns. Rejected Nomad due to smaller community.
- **Consequences**: Operational complexity requires dedicated DevOps support. Resource requests/limits must be tuned per service. Helm charts needed for consistent deployments. Cluster autoscaling required for variable load.
- **Compliance**: All services must have Dockerfile and Helm chart. Health checks and resource limits are mandatory.

## ADR-009: Use Terraform for Infrastructure as Code
- **Date**: 2025-03-15
- **Status**: Accepted
- **Context**: Need declarative, version-controlled infrastructure provisioning across multiple cloud providers.
- **Decision**: Use Terraform with remote state in S3. Rejected Pulumi due to team preference for HCL over general-purpose languages.
- **Consequences**: State management requires S3 locking with DynamoDB. Module reuse reduces duplication. Plan output must be reviewed in CI before apply.
- **Compliance**: All infrastructure must be defined in Terraform. Manual infrastructure changes are prohibited.

## ADR-010: Use BullMQ for Job Queue
- **Date**: 2025-03-20
- **Status**: Accepted
- **Context**: Need reliable job queue with retries, delays, rate limiting, and job scheduling. Redis already selected as infrastructure dependency.
- **Decision**: Use BullMQ. Rejected Sidekiq (Ruby-only). Rejected Bee-Queue (limited features). Leverages existing Redis infrastructure.
- **Consequences**: Job processing stops if Redis is unavailable. Requires worker process management (separate deployment). Job definitions should include timeout, retry strategy, and failure handling.
- **Compliance**: All background jobs must be defined as BullMQ workers. Job failure handlers must be implemented.

## ADR-011: Access Tokens with 15-Minute TTL
- **Date**: 2025-04-01
- **Status**: Accepted
- **Context**: Need balance between security (short-lived tokens limit exposure) and UX (frequent re-authentication is annoying). Need refresh tokens for seamless experience.
- **Decision**: Access tokens expire in 15 minutes. Refresh tokens expire in 7 days with rotation on each use.
- **Consequences**: Clients must implement token refresh logic. Refresh token rotation prevents replay attacks. Compromised refresh tokens are limited to 7-day window.
- **Compliance**: All clients must use the standardized token refresh flow. Server must reject rotated refresh tokens.

## ADR-012: Microservices over Monolith
- **Date**: 2025-04-10
- **Status**: Accepted
- **Context**: Team is growing, codebase complexity is increasing, deployment frequency is slowing down. Need independent deployability.
- **Decision**: Adopt microservices architecture with API Gateway. Existing monolith will be decomposed via Strangler Fig pattern.
- **Consequences**: Increased operational complexity. Requires investment in service discovery, API gateway, and observability. Communication complexity increases (network calls instead of function calls). Data consistency requires saga pattern.
- **Compliance**: Each microservice owns its data. Cross-service communication via events only (no direct DB access).
