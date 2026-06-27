# Repository DNA

> The fundamental identity, principles, and personality of this project. This document defines what makes this project what it is — and what it refuses to become.

---

## 1. Project Philosophy

### 1.1 How This Project Thinks About Software

This project believes that software is a **means to an end**, not the end itself. Every line of code exists to deliver value to users, to reduce risk, or to increase the speed of future delivery. Code that does none of these is debt.

We operate on these core beliefs:

- **Correctness over cleverness**: The right solution is the one that is obviously correct. Clever code that requires 5 minutes to understand is wrong.
- **Simplicity is the ultimate sophistication**: The most maintainable system is the one you don't have to think about. Every abstraction, indirection, and design pattern must justify its existence.
- **Boring is beautiful**: We prefer proven, well-understood technologies and patterns over novel ones. There is no prize for using the newest framework.
- **Observability is a feature**: If you can't see what the system is doing, you can't operate it. Every component must be observable by default.
- **Fail fast, fail clearly**: When something goes wrong, the system should fail immediately and with a clear error, not silently corrupt data or hang indefinitely.

### 1.2 Key Architectural Principles

| Principle | Statement | Why It Matters |
|-----------|-----------|----------------|
| Loose Coupling | Modules communicate through well-defined interfaces, not implementation details | Enables independent evolution, testing, and deployment |
| High Cohesion | Related things belong together; unrelated things belong apart | Reduces cognitive load when working in a module |
| Explicit Dependencies | Dependencies are declared, not discovered | Makes the system understandable and testable |
| Defense in Depth | Security at every layer, not just the perimeter | No single point of failure for security |
| Incremental Delivery | Ship small, safe changes frequently | Reduces risk, increases feedback speed |
| Contract First | Define interfaces before implementations | Enables parallel work, clear boundaries, and testing |
| Principle of Least Astonishment | The system should behave as users (and developers) expect | Reduces bugs and confusion |

### 1.3 What Makes This Project Unique

1. **Decision-first development**: Architecture decisions are made using a formal framework (see `decision-framework.md`) before implementation begins. Every significant decision is traceable to an ADR.
2. **Verification-gated delivery**: No change is considered complete until it passes the verification engine (see `verification-engine.md`). Quality is not an afterthought — it is a prerequisite.
3. **Explicit tradeoff documentation**: We document not just what we decided, but what we gave up. Every decision explicitly states its consequences (both positive and negative).
4. **Collective code ownership**: No individual owns a module. The team owns the codebase. Bus factor is treated as a technical risk.
5. **Learning as a deliverable**: When we discover something during development (a gotcha, a pattern, a failure mode), we document it. Knowledge capture is not optional.

### 1.4 Non-Negotiable Principles

These principles cannot be overridden by deadlines, budget, or convenience:

- **Security is not negotiable**: Authentication, authorization, encryption, and input validation are never skipped or deferred
- **Data integrity is sacred**: We never risk data loss or corruption. Migrations, backups, and consistency checks are mandatory.
- **Users deserve respect**: No dark patterns, no deceptive UIs, no data harvesting without consent
- **Accessibility is a right**: WCAG compliance is not optional. The product must be usable by everyone.
- **The system must be operable**: If you can't deploy, monitor, debug, and recover it, you haven't built it.

---

## 2. Structure Principles

### 2.1 Why the Project Is Structured This Way

The project structure follows the **structure-by-domain** pattern, not structure-by-layer. This means:

```
src/
├── orders/          # Domain: orders
│   ├── domain/      # Business logic, entities, value objects
│   ├── application/ # Use cases, application services
│   ├── infra/       # Repositories, external adapters
│   └── api/         # REST/GraphQL endpoints, DTOs
├── payments/        # Domain: payments
│   ├── domain/
│   ├── application/
│   ├── infra/
│   └── api/
└── shared/          # Shared kernel (cross-domain concepts)
    ├── kernel/      # Domain-agnostic building blocks
    └── infra/       # Shared infrastructure (DB config, logging client)
```

This structure ensures that a developer working on "orders" never needs to understand "payments" internals. It makes modules independently deployable, testable, and understandable.

### 2.2 Module Boundary Philosophy

- **Modules communicate by contract, not by sharing**: If two modules share internal types, they are not separate modules.
- **Module internals are sealed**: Internal functions, classes, and types are not accessible outside the module.
- **Shared kernel is minimal and stable**: The `shared/` directory contains only concepts that are truly domain-agnostic (money, currency, timestamps, IDs). Adding to shared kernel requires senior approval.
- **Circular dependencies are forbidden**: If module A depends on module B and B depends on A, they are one module.

### 2.3 Dependency Direction Rules

```
Shared Kernel ← Domain Layer ← Application Layer ← Infrastructure Layer ← API Layer
```

- **Domain layer has zero external dependencies** (pure business logic, plain objects/functions)
- **Application layer depends on domain layer only** (use cases orchestrate domain objects)
- **Infrastructure layer implements domain interfaces** (repositories, external services)
- **API layer depends on application layer** (controllers call use cases)
- **Dependencies never flow inward**: API → Infra → Application → Domain is the only valid direction

### 2.4 Layer Isolation Principles

- **Domain logic never depends on infrastructure**: No import from a database library in a domain entity. Domain entities are pure business logic.
- **Infrastructure code never contains business logic**: DB queries, HTTP clients, and file I/O are pure translation layers.
- **Application layer is thin**: Orchestration only. No business logic in application services.
- **API layer is dumb**: Controllers parse input, call use cases, format responses. No decisions.
- **Tests mirror the structure**: `tests/orders/domain/`, `tests/orders/application/`, etc.

---

## 3. Change Principles

### 3.1 What Principles Govern Changes

1. **Every change must have a clear "why"**: If the justification is "we've always done it this way", the change is rejected. All changes must link to a requirement, bug, or ADR.
2. **Every change is reversible**: The cost of rollback must be lower than the cost of the change being wrong. If a change cannot be safely rolled back, it must be behind a feature flag.
3. **Small changes over big bangs**: A 50-line PR that does one thing is better than a 500-line PR that does five things. This is non-negotiable for production changes.
4. **Changes must be independently deployable**: No change introduces deployment dependencies on another change. Every commit could theoretically go to production.

### 3.2 How to Evaluate if a Change Is Correct

A change is correct when:

1. It meets the defined requirements (traceable to requirements)
2. It handles all identified edge cases (with tests)
3. It does not break existing behavior (regression tests pass)
4. It follows the project's architectural patterns (consistent with existing code)
5. It is observable (logs, metrics, tracing added)
6. It is reversible (rollback plan exists)
7. It is reviewed (at least one peer has approved)
8. It is documented (API docs, ADR, or comments as appropriate)

### 3.3 What Must Never Change (Inviolable Rules)

These rules cannot be changed by any individual or team without explicit architectural board approval:

- **The dependency direction rule** (section 2.3)
- **The secret management rule** (section 6, never commit secrets)
- **The authentication rule** (section 6, never skip auth)
- **The input validation rule** (section 6, never trust client input)
- **The error handling rule** (section 6, never skip error handling)
- **The migration rule** (section 6, never modify DB without migration)
- **The testing rule** (section 6, never deploy without tests passing)
- **The review rule** (section 6, never skip code review for production)

### 3.4 What Can Evolve (Flexible Areas)

These areas are expected to evolve as the project grows:

- **Technology choices**: Libraries, frameworks, cloud providers (with ADR)
- **Code style specifics**: Formatting, linting rules (team consensus)
- **Module boundaries**: As understanding of the domain deepens (with migration plan)
- **CI/CD pipeline**: As the team and deployment frequency grow
- **Testing approach**: As new testing techniques prove valuable
- **Documentation format**: As tools and team preferences evolve

---

## 4. Quality Principles

### 4.1 Testing Philosophy

**Not just coverage — coverage of what matters.**

- **Test behavior, not implementation**: Tests should break when behavior changes, not when code is refactored. Mock at boundaries, not internals.
- **Test the happy path, the sad path, and the weird path**: Every feature needs tests for success, failure, and edge cases. See verification-engine.md for edge case categories.
- **Prefer realistic tests over isolated tests**: An integration test that uses a test database is worth more than a unit test with five mocks.
- **Test at the right level**:
  - **Domain logic**: Unit tests (fast, comprehensive, no mocks)
  - **Application use cases**: Integration tests (real dependencies for all but external services)
  - **API endpoints**: E2E tests (real database, real external calls stubbed)
  - **Critical paths**: Smoke tests in production (synthetic transactions)
- **Flaky tests are a bug**: If a test fails intermittently, it is treated as a P1 bug. Flaky tests erode trust in the test suite.

### 4.2 Code Review Philosophy

- **Review for correctness first, style second**: The primary goal is to catch bugs, logic errors, and security vulnerabilities. Style is handled by formatters and linters.
- **Review in multiple passes**:
  1. Does this solve the right problem?
  2. Is it correct for all inputs?
  3. Is it secure?
  4. Is it maintainable?
  5. Is it well-tested?
- **Be respectful, be specific**: "This doesn't handle the case where X is null" is helpful. "This is wrong" is not.
- **Small PRs get better reviews**: If a PR is larger than 400 lines, the reviewer should ask for it to be split.
- **The author is responsible for getting reviews**: Follow up, make it easy to review, respond to comments promptly.

### 4.3 Documentation Philosophy

- **Document the why, not the what**: Code shows what it does. Documentation should explain why it does it that way.
- **Document at the right level**:
  - **README**: What is this project? How do I run it?
  - **ADRs**: Why was this decision made? What were the alternatives?
  - **Runbook**: How do I operate this? What do I do when it breaks?
  - **API docs**: What does each endpoint do? What are the request/response shapes?
  - **Code comments**: Non-obvious reasoning, tradeoffs, gotchas
- **Keep documentation close to the code**: Inline comments, docstrings, and docs/ directory next to the code
- **Outdated documentation is worse than no documentation**: When you change code, update its documentation. If you can't update it, remove it.
- **Self-documenting code is the ideal**: Choose clear names over comments. If you need a comment to explain what a function does, rename the function.

### 4.4 Performance Philosophy

- **Measure before optimizing**: No optimization is accepted without a benchmark proving it helps.
- **Optimize for the 99th percentile, not the average**: Users experience the worst request, not the median one.
- **Performance is a feature**: Degrading performance is a product decision, not an engineering accident.
- **Optimized code must still be readable**: No obfuscated optimizations. If code must be less readable for performance, document why.
- **Beware premature optimization**: The fastest code is the code you don't write. 90% of performance problems come from 10% of the code.

### 4.5 Security Philosophy

- **Security is everyone's responsibility**: Every engineer is responsible for the security of their code. There is no "security team" that cleans up after the engineering team.
- **Least privilege**: Every component, user, and service gets only the permissions it needs to function. Nothing more.
- **Assume breach**: Design the system as if it is already compromised. Defense in depth, not reliance on a single security measure.
- **Fail secure**: When something goes wrong, default to the secure state. Deny access, don't grant it.
- **Security debt is technical debt**: Security vulnerabilities are not "bugs" — they are failures of process. Fix the process that allowed the vulnerability.

---

## 5. The Project's Personality

### 5.1 Pragmatic vs Purist

**This project is pragmatic.** We follow principles, but we don't follow them off a cliff. The 80/20 rule applies: 80% of the benefits come from 20% of the rigor. We apply full rigor to security, data integrity, and operability. We accept pragmatic shortcuts in areas where the risk is low and the cost of perfection is high.

**What this means in practice:**
- We use patterns intentionally, not dogmatically
- We will write a quick script to solve a one-time problem
- We will skip documentation for a trivial internal utility (but not for user-facing features)
- We will accept technical debt when the cost of perfection exceeds the risk

### 5.2 Ship Fast vs Get It Right

**This project ships fast, but not at the expense of safety.** We optimize for velocity that is sustainable — not the maximum possible speed at the cost of quality.

**What this means in practice:**
- We ship small changes frequently (multiple deploys per day)
- We use feature flags to ship incomplete features safely
- We prioritize a working MVP over a perfect architecture
- We never skip security, testing, or review to meet a deadline
- We push back on deadlines that would require cutting quality corners

### 5.3 Monolith vs Microservice

**This project is modular monolith first, microservices when proven necessary.** We start with well-structured modules that communicate through in-process interfaces. We extract services only when there is a measurable benefit (independent scaling, independent deployment, team boundaries).

**What this means in practice:**
- The codebase is organized into domain modules that could become services
- Module boundaries are as strict as service boundaries
- We accept the initial simplicity of a monolith deploy
- We extract services based on data, not dogma

### 5.4 Convention Over Configuration

**This project strongly prefers convention over configuration.** We use standardized patterns, folder structures, and naming conventions so that developers can move between modules without learning new conventions.

**What this means in practice:**
- Every module follows the same structure (domain/application/infra/api)
- Error handling is standardized across all endpoints
- Logging is standardized across all services
- Configuration is externalized and follows a standard pattern
- If you need to configure something that is not explicitly supported, the convention is the answer

### 5.5 The Tradeoff Preferences This Project Makes

| Tradeoff | Preference | Rationale |
|----------|-----------|-----------|
| Time to market vs Clean architecture | Slight tilt toward clean architecture | Paying down architectural debt later is much more expensive |
| Consistency vs Innovation | Consistency | Predictable codebases are faster to work in |
| Flexibility vs Safety | Safety | Protect users and data first |
| Build vs Buy | Buy (for non-core) | Focus engineering on what differentiates us |
| Generalization vs Specialization | Generalizable patterns | Avoid bespoke solutions that only one person understands |
| Synchronous vs Async | Async by default | Loosely coupled systems scale better |
| Strong typing vs Dynamic typing | Strong typing | Catching errors at compile time > catching them in production |
| Libraries vs Frameworks | Libraries (composable) | Avoid being locked into a framework's worldview |

---

## 6. Rules That Must Never Be Violated

These rules are absolute. Violation of any of these is an incident.

| Rule | Why | Consequence of Violation |
|------|-----|--------------------------|
| Never expose secrets | Secrets in code are immediately compromised | Incident response, credential rotation, postmortem |
| Never skip auth | Unauthenticated access is unauthorized access | Security incident, possible data breach |
| Never trust client input | All client input is potentially malicious | XSS, SQL injection, data corruption |
| Never skip error handling | Unhandled errors cause unpredictable behavior | Data loss, crash, security bypass |
| Never break backward compatibility without migration plan | Breaking changes harm users | User frustration, churn, support burden |
| Never deploy without tests passing | Untested changes are assumed broken | Regression incidents, rollback |
| Never modify database without migration | Manual DB changes are unreviewable and unrepeatable | Data loss, inconsistent state, no rollback |
| Never skip code review for production changes | Every production change needs a second pair of eyes | Uncaught bugs, security vulnerabilities |

Each violation triggers:
1. Immediate remediation (fix or revert)
2. Incident postmortem
3. Root cause analysis
4. Process improvement to prevent recurrence

---

## 7. Signatures

### 7.1 Code Patterns That Identify This Project

These patterns are found throughout the codebase and should be followed in all new code:

**Error Handling Pattern:**
```typescript
// Not this:
function getUser(id) {
  try {
    return db.users.findById(id);
  } catch (e) {
    throw e;
  }
}

// But this:
function getUser(id: UserId): Result<User, AppError> {
  return Result.from(() => db.users.findById(id))
    .mapError(() => AppError.notFound("User", id));
}
```

**Module Structure Pattern:**
```typescript
// Each module exports only:
export { UserService } from "./application/UserService";
export { UserRepository } from "./domain/UserRepository";
export type { User } from "./domain/User";
// Internal types and functions are NOT exported
```

**Controller Pattern:**
```typescript
// Controllers do three things: parse, call, respond
async function createUser(req: Request, res: Response) {
  const dto = parseBody(CreateUserDTO, req.body);     // Parse
  const result = await userService.create(dto);        // Call
  respond(res, Status.CREATED, result);                // Respond
}
```

### 7.2 Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Files | kebab-case | `user-service.ts` |
| Classes | PascalCase | `UserService` |
| Functions/Variables | camelCase | `getUserById` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Types/Interfaces | PascalCase | `CreateUserDTO` |
| Enums | PascalCase (enum), UPPER_SNAKE_CASE (values) | `enum OrderStatus { PENDING, CONFIRMED }` |
| Directories | kebab-case | `order-service/` |
| Tests | `{module}.test.ts` | `user-service.test.ts` |
| Database tables | snake_case, plural | `order_items` |
| Database columns | snake_case | `created_at` |
| API endpoints | kebab-case, plural | `/api/v1/order-items` |
| Environment variables | UPPER_SNAKE_CASE | `DATABASE_URL` |

### 7.3 Architectural Patterns That Must Be Respected

| Pattern | Where | Why |
|---------|-------|-----|
| Repository Pattern | Data access layer | Decouples business logic from persistence |
| Dependency Injection | Service composition | Makes dependencies explicit and testable |
| Result Pattern | Error handling | Types errors instead of throwing them |
| Value Objects | Primitives with constraints | Encapsulates validation and behavior |
| Domain Events | Cross-module communication | Loose coupling between domains |
| Middleware Pipeline | API layer | Pluggable cross-cutting concerns |
| Feature Flags | Deployment control | Safe, incremental rollouts |
| Circuit Breaker | External dependencies | Graceful degradation |
| Outbox Pattern | Critical writes | Reliable message delivery |
| CQRS (where justified) | Read-heavy paths | Optimized read and write models |

---

## 8. Evolution of This Document

This document is not static. It evolves as the project and team evolve.

| Version | Date | Change | Author |
|---------|------|--------|--------|
| 1.0 | | Initial creation | |
| | | | |

**Proposing changes**: Any team member can propose a change to this document via PR. The PR must:
1. Explain why the current rule is no longer appropriate
2. Describe a concrete situation where the current rule caused harm
3. Propose the new rule with justification
4. Be reviewed by at least 3 senior contributors

---

*This is who we are. This is how we build. This is what we stand for. When in doubt, refer to this document. When this document is wrong, change it — carefully.*
