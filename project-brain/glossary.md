# Glossary

## Using This Glossary

This glossary defines project-specific terminology, technical concepts, business domain terms, and acronyms. Terms are organized alphabetically with cross-references to related terms and code locations where applicable.

**Cross-reference format**: See [Related Term](#term) or See Acronym

---

## A

### Access Control List (ACL)
A list of permissions attached to an object (document, report, folder) specifying which users or roles can perform which actions. Implemented at the database level using PostgreSQL Row-Level Security (RLS).
- **Code**: `packages/api/src/middleware/acl.ts`
- **Related**: [RBAC](#rbac), [ABAC](#abac)

### Activation Rate
The percentage of new signups who complete onboarding and perform their first core action (creating a report, importing data) within 7 days of registration. A key product metric and strategic goal.
- **Related**: [Onboarding](#onboarding)

### Active-Passive
A disaster recovery configuration where one environment (primary) handles all production traffic while a second environment (standby) remains ready to take over if the primary fails. Our DR strategy uses warm standby in us-west-2.
- **Related**: [Disaster Recovery](#disaster-recovery)

### ADR (Architecture Decision Record)
A document capturing an important architectural decision, including context, decision, consequences, and alternatives considered. See [decisions.md](./decisions.md) for the full register.
- **Code**: `docs/decisions.md`

### AKS / EKS
**Amazon Elastic Kubernetes Service** — AWS-managed Kubernetes cluster. Our application runs on EKS with Fargate launch type.
- **Related**: [Kubernetes](#kubernetes), [Fargate](#fargate)

### API Gateway
The entry point for API requests. In our architecture, the Application Load Balancer (ALB) serves as the API gateway, handling SSL termination, routing, and basic request validation. API-specific concerns (rate limiting, authentication) are handled by application middleware.
- **Related**: [Rate Limiting](#rate-limiting)

### Audit Log
An append-only record of security-sensitive operations (logins, permission changes, data exports, deletions). Audit logs are stored in a dedicated PostgreSQL table and exported to the SIEM for compliance.
- **Code**: `packages/api/src/services/audit-log.ts`
- **Related**: [SIEM](#siem)

### Auth0
Third-party identity provider used for authentication. Handles user login, password management, MFA, social login, and SSO. Configured at ourcompany.us.auth0.com.
- **Related**: [JWT](#jwt), [MFA](#mfa), [SSO](#sso)

### Auto-Scaling
Automatic adjustment of compute resources based on demand. Our EKS cluster uses Horizontal Pod Autoscaler (HPA) to scale pods based on CPU/memory metrics, and Cluster Autoscaler to scale nodes.
- **Related**: [HPA](#hpa)

---

## B

### B2B (Business-to-Business)
Our product is sold to businesses, not individual consumers. This affects feature prioritization (SSO, audit logs, role management) and pricing (per-seat pricing with tiered plans).

### Backfill
The process of populating a new data structure (column, table, index) with historical data. Typically done after a schema migration that adds a new required field — existing records need the new field populated.
- **Related**: [Migration](#migration)

### BFF (Backend for Frontend)
An API layer specifically designed for a particular frontend (web, mobile). We use a BFF pattern for the mobile app to optimize data transfer and reduce the number of API calls from mobile devices.
- **Related**: [GraphQL](#graphql)

### Bounded Context
A boundary within which a particular domain model applies. From Domain-Driven Design — helps manage complexity by dividing the system into distinct contexts with clear interfaces between them.
- **Related**: [Domain-Driven Design](#domain-driven-design)

### Build Cache
A stored copy of previous build outputs to avoid rebuilding unchanged code. Turborepo provides remote caching to share build caches across developer machines and CI.
- **Code**: `turbo.json`

---

## C

### Canary Deployment
A deployment strategy where a new version is rolled out to a small percentage of users (e.g., 10%) before being rolled out to everyone. Errors are monitored during the canary phase, and if metrics are healthy, the rollout continues.
- **Related**: [Rollback](#rollback)

### CDN (Content Delivery Network)
A geographically distributed network of proxy servers that cache static content (images, JavaScript, CSS) close to users. We use CloudFront as our CDN.
- **Related**: [CloudFront](#cloudfront)

### CI/CD (Continuous Integration / Continuous Deployment)
CI: Automated testing of every code change merged to the main branch. CD: Automated deployment of tested changes to staging and, after approval, to production. We use GitHub Actions for CI/CD.
- **Code**: `.github/workflows/deploy.yml`

### CloudFront
AWS global CDN service. Serves static assets, handles SSL termination, and provides DDoS protection. Configured with multiple origins (S3 for static files, ALB for dynamic content).
- **Related**: [CDN](#cdn)

### CLS (Cumulative Layout Shift)
A Core Web Vital metric measuring visual stability. CLS quantifies how much visible content shifts during page load. Our target is <0.1.
- **Related**: [Core Web Vitals](#core-web-vitals), [LCP](#lcp)

### Core Web Vitals
A set of real-world metrics measuring key aspects of user experience: LCP (loading), FID/INP (interactivity), CLS (visual stability). Used as performance targets and monitored via Datadog RUM.
- **Related**: [CLS](#cls), [LCP](#lcp), [INP](#inp)

### CSP (Content Security Policy)
An HTTP security header that restricts which resources (scripts, styles, fonts) can be loaded on a page. Mitigates XSS attacks. Our CSP policy is configured in the web app's middleware.
- **Code**: `packages/web/src/middleware.ts`
- **Related**: [XSS](#xss)

### CSV (Comma-Separated Values)
A plain-text file format for tabular data. Supported as an export format throughout the application.

---

## D

### Data Subject Access Request (DSAR)
A GDPR-guaranteed right for individuals to request access to their personal data held by an organization. We provide automated DSAR fulfillment via Settings > Data > Download My Data.
- **Related**: [GDPR](#gdpr)

### Design Token
A named value representing a design attribute (color, spacing, typography, shadow). Design tokens are the single source of truth for the visual language and are consumed by both design tools (Figma) and code (Tailwind config).
- **Code**: `tailwind.config.js`
- **Related**: [Tailwind CSS](#tailwind-css)

### Disaster Recovery (DR)
The process of restoring IT infrastructure and systems after a catastrophic failure. Our DR strategy uses a warm standby in us-west-2 with automated failover procedures.
- **Related**: [Active-Passive](#active-passive), [RPO](#rpo), [RTO](#rto)

### DPO (Data Protection Officer)
A role required by GDPR for organizations that process personal data. Our DPO is Maria Garcia (privacy@ourcompany.com).
- **Related**: [GDPR](#gdpr)

### DTO (Data Transfer Object)
An object that carries data between processes. In our API, DTOs define the shape of request/response bodies and are validated using Zod schemas.

---

## E

### EKS (Elastic Kubernetes Service)
See [AKS / EKS](#aks--eks)

### ElastiCache
AWS-managed Redis and Memcached service. We use ElastiCache for Redis (cluster mode) for caching and session storage.
- **Related**: [Redis](#redis)

### Event Sourcing
A pattern where state changes are stored as a sequence of events rather than as the current state. Partially implemented for the billing domain — payment events are stored immutably and used to compute account balances.
- **Related**: [Event-Driven Architecture](#event-driven-architecture)

### Event-Driven Architecture
An architectural pattern where components communicate by producing and consuming events. Used for cross-service communication (Redis Pub/Sub for internal events, Kafka for domain events).
- **Related**: [Event Sourcing](#event-sourcing), [Kafka](#kafka)

---

## F

### Fargate
AWS serverless compute engine for containers. Our EKS cluster uses Fargate for worker nodes, eliminating the need to manage EC2 instances.
- **Related**: [EKS](#aks--eks)

### FCP (First Contentful Paint)
A performance metric measuring the time from navigation to when the browser renders the first piece of content. Our target: <1.5s.
- **Related**: [Core Web Vitals](#core-web-vitals), [LCP](#lcp)

### Feature Flag
A mechanism to turn features on or off without deploying code. Implemented via LaunchDarkly. Used for canary releases, gradual rollouts, and kill switches.
- **Code**: `packages/shared/src/flags.ts`
- **Related**: [LaunchDarkly](#launchdarkly)

### Flyway
Database migration tool. Applies version-controlled SQL migration scripts in order. Chosen for its checksum verification and database-agnostic approach.
- **Code**: `packages/api/src/main/resources/db/migration/`
- **Related**: [Migration](#migration)

---

## G

### GDPR (General Data Protection Regulation)
EU regulation governing the processing of personal data. Requirements include DSAR, right to erasure, data portability, consent management, and breach notification within 72 hours.
- **Related**: [DSAR](#data-subject-access-request-dsar), [DPO](#dpo)

### GraphQL
A query language for APIs. Not currently used in production (we standardized on REST in ADR-008), but planned for the mobile BFF layer (ADR-008 scope includes GraphQL for mobile).
- **Related**: [BFF](#bff), [REST](#rest)

---

## H

### HPA (Horizontal Pod Autoscaler)
Kubernetes resource that automatically scales the number of pod replicas based on CPU, memory, or custom metrics. Configured in our Helm chart.
- **Code**: `infrastructure/helm/app/templates/hpa.yaml`
- **Related**: [Auto-Scaling](#auto-scaling)

### HSM (Hardware Security Module)
A dedicated hardware device for managing encryption keys. Used for the most sensitive secrets (database master keys, certificate authorities). We use AWS CloudHSM.
- **Related**: [KMS](#kms)

---

## I

### IAM (Identity and Access Management)
AWS service for managing users, groups, roles, and permissions. Used for infrastructure-level access control. Application-level access control uses our RBAC/ABAC system.
- **Related**: [RBAC](#rbac), [ABAC](#abac)

### Idempotency
The property of an operation that can be applied multiple times without changing the result beyond the first application. Important for webhook handlers and payment processing to prevent duplicate charges.
- **Code**: `packages/api/src/middleware/idempotency.ts`

### INP (Interaction to Next Paint)
A Core Web Vital metric replacing FID. Measures the time from when a user interacts with the page to when the next paint occurs. Our target: <200ms.

### IdP (Identity Provider)
A service that authenticates users and provides identity tokens. Auth0 is our primary IdP; Google, Microsoft, and SAML providers are secondary IdPs.
- **Related**: [Auth0](#auth0), [SSO](#sso)

---

## J

### JIT (Just-In-Time) Provisioning
Automatic creation of user accounts on first SSO login. Users don't need to be pre-provisioned; their account is created when they first authenticate via their corporate IdP.
- **Related**: [SCIM](#scim), [SSO](#sso)

### JWT (JSON Web Token)
A compact, URL-safe token format used for API authentication. We use RS256-signed JWTs with a 15-minute access token lifetime and 30-day refresh token lifetime.
- **Code**: `packages/api/src/middleware/auth.ts`
- **Related**: [Auth0](#auth0)

---

## K

### Kafka
Distributed event streaming platform. Used for domain events that require persistence, replay, and multiple consumers. Deployed via AWS MSK (Managed Streaming for Kafka).
- **Related**: [Event-Driven Architecture](#event-driven-architecture), [MSK](#msk)

### KMS (Key Management Service)
AWS service for creating and managing encryption keys. Used for encrypting data at rest (RDS, S3, EBS) and managing key rotation policies.
- **Related**: [HSM](#hsm)

### Kubernetes (K8s)
Container orchestration platform. Our application runs on Amazon EKS with Fargate nodes. Managed via Helm charts and Kustomize overlays.
- **Related**: [EKS](#aks--eks), [Helm](#helm)

---

## L

### LaunchDarkly
Feature flag management platform. Used for gradual rollouts, canary releases, A/B testing, and kill switches. Flags are evaluated server-side and passed to the frontend.
- **Related**: [Feature Flag](#feature-flag)

### LCP (Largest Contentful Paint)
A Core Web Vital metric measuring the time from navigation to when the largest content element (image, text block) is rendered. Our target: <2.5s.
- **Related**: [Core Web Vitals](#core-web-vitals), [FCP](#fcp)

---

## M

### MFA (Multi-Factor Authentication)
Authentication method requiring two or more verification factors. Implemented via Auth0 with TOTP (authenticator app) as the primary method and SMS as backup.
- **Related**: [Auth0](#auth0)

### Migration (Database)
A versioned, repeatable change to the database schema. Managed by Flyway. Types: Versioned (V), Repeatable (R), Undo (U).
- **Code**: `packages/api/src/main/resources/db/migration/`
- **Related**: [Flyway](#flyway)

### mTLS (Mutual TLS)
TLS where both the client and server present certificates. Used for inter-service communication within the Kubernetes cluster (enforced by Istio service mesh).
- **Related**: [TLS](#tls)

### MSK (Managed Streaming for Kafka)
AWS-managed Kafka service. Used for domain events. Provides automatic broker management, scaling, and security.
- **Related**: [Kafka](#kafka)

### MVP (Minimum Viable Product)
The smallest version of a feature that delivers value to users. Used in our iterative development process — features are shipped in MVP state first, then enhanced based on feedback.

---

## N

### NPS (Net Promoter Score)
A customer loyalty metric measured by asking "How likely are you to recommend our product?" (0-10 scale). Our current score: 32. Target: 50+.

---

## O

### OIDC (OpenID Connect)
An authentication protocol built on top of OAuth 2.0. Used for SSO integration with Google Workspace and Microsoft Entra ID.
- **Related**: [SSO](#sso), [SAML](#saml)

### OKR (Objectives and Key Results)
A goal-setting framework used for quarterly planning. Objectives are qualitative goals; Key Results are quantitative measures of progress toward the objective.

### OpenSearch
AWS-managed Elasticsearch-compatible search and analytics engine. Used for full-text search across documents, reports, and user data.
- **Related**: [Search Index](#search-index)

### OPA (Open Policy Agent)
Policy engine used for enforcing Kubernetes security policies (Pod Security Standards, network policies). Integrated as OPA Gatekeeper.
- **Related**: [Kubernetes](#kubernetes)

---

## P

### p95 / p99 Latency
The 95th/99th percentile of request latency. If p95 latency is 800ms, then 95% of requests complete in 800ms or less. More representative than average latency because it excludes outliers.

### PagerDuty
Incident management and on-call scheduling platform. Critical alerts are routed to PagerDuty, which pages the on-call engineer via phone call and mobile push notification.

### PKCE (Proof Key for Code Exchange)
An extension to the OAuth 2.0 authorization code flow that prevents authorization code interception attacks. Used in our login flow.
- **Related**: [OIDC](#oidc)

### PostgreSQL
Our primary database. Version 15, deployed on RDS (Multi-AZ in production). Accessed via Prisma ORM with raw SQL for complex queries.
- **Code**: `packages/api/prisma/schema.prisma`

### Prisma
TypeScript ORM used for database access. Provides auto-generated types, migrations (though we use Flyway for actual migrations), and a type-safe query builder.
- **Related**: [PostgreSQL](#postgresql)

### Pub/Sub (Publish/Subscribe)
A messaging pattern where publishers send messages without knowing the subscribers. Used for internal events via Redis Pub/Sub. See ADR-003.
- **Related**: [Redis](#redis)

---

## R

### Rate Limiting
Controlling the rate of API requests to prevent abuse. Implemented at multiple levels: WAF (global), API Gateway (per-IP, per-user), and application middleware (per-endpoint).
- **Code**: `packages/api/src/middleware/rate-limit.ts`

### RBAC (Role-Based Access Control)
An authorization model where permissions are assigned to roles, and roles are assigned to users. We have 6 default roles: Viewer, Editor, Manager, Admin, Super Admin.
- **Related**: [ABAC](#abac), [ACL](#access-control-list-acl)

### RDS (Relational Database Service)
AWS-managed database service. Our PostgreSQL database runs on RDS with Multi-AZ deployment, automated backups, and IAM authentication.
- **Related**: [PostgreSQL](#postgresql)

### Redis
In-memory data structure store used for caching, session storage, and pub/sub messaging. Deployed via ElastiCache (cluster mode). Accessed via ioredis.
- **Related**: [ElastiCache](#elasticache), [Pub/Sub](#pubsub)

### REST (Representational State Transfer)
Architectural style for API design. We use RESTful principles: resource-oriented URLs, HTTP methods (GET, POST, PUT, DELETE), and JSON bodies.
- **Related**: [GraphQL](#graphql)

### Rollback
The process of reverting a deployment to a previous version. Automated rollback triggers on error rate increase, latency spike, or health check failure.
- **Related**: [Canary Deployment](#canary-deployment)

### RPO (Recovery Point Objective)
The maximum acceptable data loss in a disaster, measured in time. Our RPO: 5 minutes (determined by WAL shipping interval).
- **Related**: [Disaster Recovery](#disaster-recovery), [RTO](#rto)

### RTO (Recovery Time Objective)
The maximum acceptable time to restore service after a disaster. Our RTO: 30 minutes for region failover.
- **Related**: [Disaster Recovery](#disaster-recovery), [RPO](#rpo)

---

## S

### S3 (Simple Storage Service)
AWS object storage service. Used for file uploads, static assets, backups, and log archives.
- **Related**: [CDN](#cdn)

### SAST (Static Application Security Testing)
Security testing that analyzes source code without executing it. We use SonarQube and CodeQL for SAST in CI. Blocks PRs with critical/high findings.
- **Related**: [SonarQube](#sonarqube)

### SAML (Security Assertion Markup Language)
XML-based authentication protocol used for enterprise SSO. Supported for enterprise customers who cannot use OIDC.
- **Related**: [OIDC](#oidc), [SSO](#sso)

### SCIM (System for Cross-domain Identity Management)
A standard for automating user provisioning and deprovisioning between identity systems. Used to sync users from enterprise IdPs to our application.
- **Related**: [JIT Provisioning](#jit-just-in-time-provisioning), [SSO](#sso)

### Search Index
A data structure that enables fast full-text search. Built and maintained by OpenSearch. Documents are indexed asynchronously after creation or modification.
- **Related**: [OpenSearch](#opensearch)

### SIEM (Security Information and Event Management)
A system that aggregates and analyzes security logs from multiple sources. We export audit logs to Splunk Cloud for SIEM analysis.
- **Related**: [Audit Log](#audit-log)

### SOC 2
An auditing standard for service organizations, focusing on security, availability, processing integrity, confidentiality, and privacy. We are pursuing SOC 2 Type II certification (target: Q3 2026).
- **Related**: [Compliance](#compliance)

### SonarQube
Code quality and security analysis platform. Used in CI to enforce code quality gates (test coverage, code smells, security vulnerabilities).
- **Related**: [SAST](#sast)

### SSO (Single Sign-On)
Authentication method allowing users to log in with their corporate credentials. Supports OIDC (Google, Microsoft) and SAML (enterprise IdPs).
- **Related**: [Auth0](#auth0), [OIDC](#oidc), [SAML](#saml)

### Storybook
Tool for developing and documenting UI components in isolation. Stories are written for every component variant and state. Published to Chromatic for visual regression testing.
- **Code**: `packages/ui/src/**/*.stories.tsx`

---

## T

### Tailwind CSS
Utility-first CSS framework used for styling. All visual properties derive from design tokens configured in `tailwind.config.js`.
- **Code**: `tailwind.config.js`
- **Related**: [Design Token](#design-token)

### Terraform
Infrastructure-as-code tool for managing AWS resources. State is stored in an S3 bucket with DynamoDB locking.
- **Code**: `infrastructure/terraform/`

### TLS (Transport Layer Security)
Cryptographic protocol for secure communication over networks. We require TLS 1.2 minimum (TLS 1.3 preferred) for all connections.
- **Related**: [mTLS](#mtls)

### Turborepo
Monorepo build system providing build caching, task orchestration, and parallel execution. Used to manage our monorepo with npm workspaces.
- **Code**: `turbo.json`

### TTI (Time to Interactive)
A performance metric measuring when a page is fully interactive (all event handlers registered, page responds to user input within 50ms). Our target: <3.5s.

---

## U

### UAT (User Acceptance Testing)
Testing performed by end users to verify that a feature meets their requirements. Conducted before each major release.

---

## V

### VPC (Virtual Private Cloud)
An isolated section of AWS containing our infrastructure. Divided into public subnets (load balancers) and private subnets (application, database, cache).

---

## W

### WAF (Web Application Firewall)
A firewall that monitors and filters HTTP traffic. We use AWS WAF with OWASP Top 10 rules, IP reputation lists, and rate limiting rules.
- **Related**: [OWASP](#owasp)

### WAL (Write-Ahead Log)
PostgreSQL's transaction log. Used for Point-in-Time Recovery (PITR) and replication. WAL segments are shipped to S3 every 5 minutes for backup.
- **Related**: [PostgreSQL](#postgresql)

### WCAG (Web Content Accessibility Guidelines)
Accessibility standards. We target WCAG 2.1 Level AA compliance for all features.
- **Related**: [Accessibility](#accessibility)

### Webhook
An HTTP callback that delivers real-time notifications to external systems when events occur. Our webhook system delivers events with retry logic and signature validation.
- **Code**: `packages/api/src/services/webhooks.ts`

---

## X

### XSS (Cross-Site Scripting)
A security vulnerability where an attacker injects malicious scripts into web pages. Mitigated by CSP headers, output encoding, and input validation.
- **Related**: [CSP](#csp)

---

## Common Misconceptions

### "Feature flags are temporary development tools"
**Reality**: Feature flags (LaunchDarkly) are used throughout the feature lifecycle — development (protect incomplete work), testing (targeted rollouts), production (gradual rollout, A/B testing), and operations (kill switches).

### "Microservices are always better than monoliths"
**Reality**: We use a modular monolith with clear bounded contexts. Microservices extraction will happen only when justified by scaling needs, not as a premature optimization. See [ADR-003](#adr-003).

### "PostgreSQL can't handle high traffic"
**Reality**: PostgreSQL with proper indexing, connection pooling (PgBouncer), read replicas, and caching handles our scale effectively. The issues we've faced are from missing indexes and unoptimized queries, not from PostgreSQL limitations.

### "Server Components replace all client-side JavaScript"
**Reality**: React Server Components handle data fetching and static rendering, but interactive features (forms, real-time updates, drag-and-drop) still require Client Components. The choice is per-component based on interactivity needs.

### "SOC 2 certification means we're secure"
**Reality**: SOC 2 Type II certifies that we have controls in place and they operate effectively. It's a snapshot in time. Security is an ongoing practice, not a checkbox.

### "ACID compliance guarantees data consistency"
**Reality**: ACID guarantees transaction-level consistency, not application-level consistency. Application code must still enforce business rules, handle concurrent modifications, and manage eventual consistency in event-driven flows.

---

## Terms by Domain (Quick Reference)

| Domain | Key Terms |
|--------|-----------|
| Architecture | Monorepo, Turborepo, Event-Driven, Bounded Context, BFF, Modular Monolith |
| Backend | Express, Prisma, PostgreSQL, Redis, Kafka, Flyway, REST, GraphQL |
| Frontend | Next.js, React, Tailwind CSS, Storybook, Design Token, Server Component |
| Infrastructure | EKS, Terraform, Helm, CloudFront, RDS, ElastiCache, VPC, Fargate |
| Security | Auth0, JWT, MFA, SSO, SAML, OIDC, RBAC, ABAC, WAF, CSP, SAST |
| Compliance | GDPR, SOC 2, DSAR, DPO, Audit Log, SIEM |
| Process | OKR, ADR, MVP, UAT, CI/CD, Trunk-Based Development, Conventional Commits |
| Performance | Core Web Vitals, LCP, FCP, CLS, INP, p95, p99 |
| DevOps | Canary, Rollback, HPA, Auto-Scaling, Disaster Recovery, RPO, RTO |

---

## Need to Add a Term?

If you encounter a term that isn't defined here, please:
1. Check if it's already used in the codebase (grep for it)
2. Add it to this file in the appropriate alphabetical position
3. Include: term name, definition, code reference (if applicable), and related terms
4. Submit a PR with the addition
