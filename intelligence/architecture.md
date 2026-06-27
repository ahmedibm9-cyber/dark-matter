# Architecture

## System Context
The system operates as a multi-service platform deployed on cloud infrastructure. It consists of a frontend application, a backend API layer, background job workers, a relational database, a cache layer, a message queue, and third-party integrations. All services communicate over HTTPS or via the internal message bus.

## System Diagram (Textual)
```
[Client Browser] --HTTPS--> [CDN] --HTTPS--> [Load Balancer]
                                                    |
                          +-------------------------+-------------------------+
                          |                         |                         |
                     [Web App]               [API Gateway]           [Admin Panel]
                          |                         |                         |
                     [Static Files]            [Auth Service]           [Admin API]
                                                   |
                          +------------------------+------------------------+
                          |                        |                        |
                    [API Service]           [Background Worker]      [WebSocket Hub]
                          |                        |
                    [Cache Layer]              [Message Queue]
                          |                        |
                    [Primary DB]             [Search Index]

                    [External Integrations: Payment, Email, SMS, Analytics]
```

## Key Architectural Patterns
1. **Microservices** — Services are independently deployable, each owning its data.
2. **API Gateway** — Single entry point for client requests, handles auth, rate limiting, routing.
3. **CQRS** — Read models are optimized separately from write models for high-traffic paths.
4. **Event-Driven** — Services communicate via asynchronous events through the message queue.
5. **Saga Pattern** — Distributed transactions are implemented as choreographed sagas.
6. **Strangler Fig** — Legacy monolith is being incrementally replaced by microservices.
7. **Circuit Breaker** — External dependencies are protected with circuit breakers and fallbacks.
8. **Bulkhead** — Critical resources are isolated to prevent cascading failures.
9. **Idempotency** — All mutating endpoints support idempotency keys for safe retries.
10. **Observability** — Every service emits structured logs, metrics, and traces.

## Technology Decisions

### Frontend
| Technology | Purpose | Decision Rationale |
|---|---|---|
| React 18 | UI framework | Broad ecosystem, team expertise, SSR support via Next.js |
| TypeScript | Type safety | Catches class of runtime errors, improves DX |
| Next.js | SSR/SSG | SEO requirements, performance, file-based routing |
| Tailwind CSS | Styling | Utility-first, rapid prototyping, small bundle |
| React Query | Data fetching | Caching, deduplication, optimistic updates |
| Zustand | State management | Lightweight, simple, no boilerplate |
| Playwright | E2E tests | Cross-browser, reliable, modern API |
| Vitest | Unit tests | Fast, compatible with Vite toolchain |

### Backend
| Technology | Purpose | Decision Rationale |
|---|---|---|
| Node.js 22 | Runtime | Team expertise, NPM ecosystem, async I/O |
| Hono | HTTP framework | Lightweight, fast, TypeScript-native |
| Prisma | ORM | Type-safe queries, migrations, excellent DX |
| PostgreSQL | Database | ACID compliance, JSON support, extensibility |
| Redis | Cache/Queue | In-memory speed, pub/sub, built-in data structures |
| BullMQ | Job queue | Redis-backed, delayed jobs, rate limiting |
| Zod | Validation | Runtime type safety, inferred TypeScript types |
| OpenTelemetry | Observability | Vendor-neutral, standard for traces/metrics/logs |

### Infrastructure
| Technology | Purpose | Decision Rationale |
|---|---|---|
| Docker | Containerization | Consistent environments, CI/CD parity |
| Kubernetes | Orchestration | Auto-scaling, rolling updates, self-healing |
| Terraform | IaC | State management, multi-cloud support |
| GitHub Actions | CI/CD | Tight GitHub integration, matrix builds |
| Datadog | Monitoring | APM, dashboards, alerting, log management |
| Vault | Secrets management | Dynamic secrets, audit logging, rotation |

## Module Boundaries

### Web App Module
- **Responsibility**: Server-side rendering, static generation, API route handlers.
- **Owns**: Page components, layouts, middleware, public assets.
- **Depends On**: API Service, Auth Service, Cache Layer.
- **Exposes**: HTTP endpoints for SSR, GraphQL for client data fetching.

### API Service Module
- **Responsibility**: Business logic, data validation, orchestration.
- **Owns**: Domain models, use cases, repositories, event publishers.
- **Depends On**: PostgreSQL, Redis, Message Queue.
- **Exposes**: RESTful HTTP API consumed by Web App and external clients.

### Auth Service Module
- **Responsibility**: Authentication, authorization, session management.
- **Owns**: User credentials, roles, permissions, tokens, MFA.
- **Depends On**: PostgreSQL (users), Redis (sessions).
- **Exposes**: OAuth2/OIDC-compliant endpoints, token validation middleware.

### Background Worker Module
- **Responsibility**: Asynchronous job processing, scheduled tasks.
- **Owns**: Job definitions, worker logic, retry policies.
- **Depends On**: Redis (BullMQ), PostgreSQL, external APIs.
- **Exposes**: No external API; consumes from message queue.

### Admin Panel Module
- **Responsibility**: Internal administration UI, user management, audit logs.
- **Owns**: Admin-specific pages, moderation tools, reporting dashboards.
- **Depends On**: Admin API Service, Primary DB (read replicas).

## Data Flow Examples

### User Registration
```
Client -> API Gateway -> Auth Service -> Validate Input -> Check Duplicates ->
Hash Password -> Insert User -> Publish UserCreated Event -> Send Welcome Email (Worker) ->
Return 201 with Session Token.
```

### Order Placement
```
Client -> API Gateway -> API Service -> Validate Cart -> Check Inventory ->
Reserve Stock -> Create Order -> Publish OrderPlaced Event ->
Charge Payment (Worker) -> Send Confirmation (Worker) ->
Return Order Object.
```

## Deployment Architecture
- **Staging**: Single-node Kubernetes cluster, reduced replicas, mock external services.
- **Production**: Multi-node Kubernetes cluster across 3 AZs, HPA autoscaling, read replicas.
- **DR**: Cross-region backup, RPO of 15 minutes, RTO of 1 hour.

## Security Architecture
- **Network**: Private subnets, security groups, WAF, DDoS protection.
- **Application**: Input validation, CSRF tokens, rate limiting, Content Security Policy.
- **Data**: Encryption at rest (AES-256), encryption in transit (TLS 1.3).
- **Secrets**: Vault for dynamic secrets, rotation every 30 days.
- **Auth/OAuth**: OAuth2 with PKCE, JWT with short TTL, refresh token rotation.
