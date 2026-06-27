# Coding Standards

> This document defines the coding standards and conventions for every language and technology used in the project. Adherence to these standards is enforced through linting, formatting, type checking, and code review.

---

## 1. Language-Specific Standards

### 1.1 TypeScript / JavaScript

#### Runtime Version

- **Minimum Node.js version:** 20 LTS
- **Target ECMAScript version:** ES2022
- **Module system:** ESM (ECMAScript Modules) — use `import`/`export`, not `require`
- **TypeScript strict mode:** Enabled — use `strict: true` in tsconfig.json

#### TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": false,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "isolatedModules": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}
```

#### Lint Rules (ESLint)

- **Base:** `@typescript-eslint/recommended` + `prettier`
- **Additional rules:**
  - `@typescript-eslint/no-explicit-any` — error (forbid `any`)
  - `@typescript-eslint/explicit-function-return-type` — warn on public API
  - `@typescript-eslint/no-unused-vars` — error with `argsIgnorePattern: "^_"`
  - `@typescript-eslint/consistent-type-imports` — error
  - `import/order` — enforce grouped import order
  - `no-console` — error (use logger instead)
  - `max-lines` — warn at 300 lines per file
  - `max-depth` — warn at 4 levels of nesting
  - `complexity` — warn at 10 cyclomatic complexity
  - `prefer-const` — error
  - `no-var` — error

#### Prettier Configuration

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

### 1.2 Python (if applicable)

#### Runtime Version

- **Minimum Python version:** 3.12

#### Lint Rules (Ruff)

- Line length: 100
- Docstring convention: Google style
- Import ordering: isort-compatible

### 1.3 Go (if applicable)

#### Runtime Version

- **Minimum Go version:** 1.22

#### Formatting

- `gofmt` is always run — no exceptions
- Line length: 120
- Comment sentences: Capitalized, period-terminated

---

## 2. Naming Conventions

### 2.1 File and Directory Naming

| Entity | Convention | Example | Notes |
|---|---|---|---|
| Source files | kebab-case | `user-service.ts` | Except React components |
| React components | PascalCase | `UserProfile.tsx` | Matches component name |
| Test files | `.test.ts` or `.spec.ts` | `user-service.test.ts` | Same name as source |
| Directory names | kebab-case | `user-management/` | Plural for collections |
| Style files | kebab-case | `button-styles.css` | |
| Configuration | kebab-case | `eslint.config.js` | Framework conventions respected |

### 2.2 Variable and Identifier Naming

| Entity | Convention | Example | Notes |
|---|---|---|---|
| Variables | camelCase | `userName`, `orderTotal` | |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` | Only for truly immutable values |
| Booleans | prefix with `is`, `has`, `should`, `can` | `isActive`, `hasPermission` | Improves readability |
| Private fields | underscore prefix | `_privateField` | TypeScript `#` also acceptable |
| Functions | camelCase, verb-first | `getUser()`, `validateOrder()` | |
| Classes | PascalCase | `UserService`, `OrderAggregate` | |
| Interfaces | PascalCase | `UserRepository` | No `I` prefix |
| Types | PascalCase | `UserStatus`, `OrderDto` | |
| Enums | PascalCase (enum + PascalCase members) | `OrderStatus.Pending` | |
| Generics | Single uppercase | `<T>`, `<K, V>` | Descriptive if needed: `<TEntity>` |
| React hooks | `use` prefix | `useAuth()`, `useDebounce()` | |
| React contexts | PascalCase with Context suffix | `AuthContext` | |
| CSS classes | kebab-case | `user-card`, `btn-primary` | BEM for complex cases |
| Environment variables | UPPER_SNAKE_CASE | `DATABASE_URL` | |

### 2.3 Database Naming

See `database.md` for full details. Summary:

- Tables: snake_case, plural (`users`, `order_items`)
- Columns: snake_case (`created_at`, `first_name`)
- Indexes: `idx_[table]_[column]`
- Constraints: `uq_[table]_[column]`, `ck_[table]_[description]`

---

## 3. File Structure Conventions

### 3.1 Maximum File Size

| Level | Threshold | Action |
|---|---|---|
| Warning | > 300 lines | Consider refactoring |
| Error | > 500 lines | Blocking in code review — must refactor |

### 3.2 Maximum Function/Method Size

| Level | Threshold | Action |
|---|---|---|
| Warning | > 30 lines | Consider extracting helper |
| Error | > 60 lines | Blocking — must refactor |

### 3.3 Maximum Parameters

- **Warning:** > 3 parameters
- **Action:** Use options object (destructured in function signature)

```typescript
// Good
function createUser({ name, email, role, avatarUrl }: CreateUserParams)

// Bad
function createUser(name: string, email: string, role: string, avatarUrl?: string)
```

### 3.4 Import Order

Imports must be grouped and ordered:

1. **Node built-ins** (`fs`, `path`, `os`)
2. **External libraries** (`react`, `express`, `zod`) — alphabetical
3. **Internal modules** (`@/modules/user`, `@/shared/kernel`) — alphabetical by path
4. **Relative imports** (`./user-service`, `../types`) — alphabetical
5. **CSS/styles** (`./button.css`) — last

Each group separated by a blank line. No blank lines within a group.

```typescript
import { readFile } from 'node:fs';
import path from 'node:path';

import express from 'express';
import { z } from 'zod';

import { User } from '@/modules/user/domain/user';
import { Logger } from '@/shared/infrastructure/logger';

import { createUserSchema } from './create-user-schema';
import type { CreateUserResponse } from './types';

import './create-user.css';
```

---

## 4. Component Architecture Standards (Frontend)

### 4.1 Component Classification

| Type | Directory | State | Side Effects | Reusable |
|---|---|---|---|---|
| **Page** | `pages/` | Route state | Yes | No |
| **Feature** | `features/` | Feature state | Yes | Within feature |
| **UI** | `ui/` | None (or presentational) | No | Yes, across app |
| **Layout** | `layouts/` | None | No | Yes |
| **HOC / Provider** | `providers/` | Context state | Setup only | Yes |

### 4.2 Component Structure

Every component file follows this structure:

```typescript
// 1. Imports (grouped as per import order rules)
// 2. Types and interfaces
// 3. Constants (if any)
// 4. Helper functions (if any)
// 5. Component definition
// 6. Exports (prefer named exports over default)
```

### 4.3 Component Rules

- **One component per file** (except small, tightly coupled sub-components like `Label`, `Item`)
- **Props interface defined at top of file** — exported if used by parent
- **No complex inline JSX** — extract into named sub-render functions or separate components
- **No business logic in components** — logic lives in hooks, services, or state management
- **Hooks follow rules of hooks** — called at top level, not in conditionals
- **Error boundaries** wrap every page and feature

### 4.4 Component Template

```typescript
import { type ReactNode, useCallback } from 'react';

export interface UserCardProps {
  userId: string;
  userName: string;
  avatarUrl?: string;
  onFollow: (userId: string) => void;
  className?: string;
}

export function UserCard({
  userId,
  userName,
  avatarUrl,
  onFollow,
  className,
}: UserCardProps) {
  const handleFollow = useCallback(() => {
    onFollow(userId);
  }, [userId, onFollow]);

  return (
    <div className={className}>
      <img src={avatarUrl} alt={`${userName}'s avatar`} />
      <span>{userName}</span>
      <button onClick={handleFollow}>Follow</button>
    </div>
  );
}
```

---

## 5. API Design Standards

### 5.1 REST API Conventions

- **URLs:** Plural nouns for resources (`/api/users`, `/api/orders`)
- **HTTP methods:** GET (read), POST (create), PUT (full update), PATCH (partial update), DELETE (remove)
- **Status codes:** Use appropriate HTTP status codes consistently
- **Consistent nesting:** `/api/users/:userId/orders`
- **Query parameters:** camelCase (`?pageSize=20&sortBy=createdAt`)
- **Request body:** JSON with `Content-Type: application/json`

### 5.2 Response Envelope

```json
{
  "success": true,
  "data": {},
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

For errors:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "code": "INVALID_FORMAT"
      }
    ]
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 5.3 GraphQL Conventions (if applicable)

- **Mutations** are verbs (`createUser`, `updateOrder`)
- **Queries** are nouns (`user`, `users`, `order`)
- **Input types** use `Input` suffix (`CreateUserInput`)
- **Type naming** PascalCase, field naming camelCase

---

## 6. Error Handling Standards

### 6.1 Error Handling Principles

1. **Never swallow errors** — if you catch, you must handle, log, or re-throw.
2. **Fail fast** — validate inputs at the boundary, reject invalid state immediately.
3. **Use typed errors** — custom error classes or discriminated unions for expected failures.
4. **No silent failures** — every error path is observable (logged, metrified).
5. **Graceful degradation** — non-critical features may fail without crashing the system.

### 6.2 Error Categories

| Category | HTTP Status | Example | Handling |
|---|---|---|---|
| ValidationError | 400 | Invalid email format | Return field-level errors |
| AuthenticationError | 401 | Missing/invalid token | Redirect to login |
| AuthorizationError | 403 | Insufficient permissions | Show forbidden page |
| NotFoundError | 404 | User not found | Show 404 page |
| ConflictError | 409 | Duplicate email | Show conflict message |
| RateLimitError | 429 | Too many requests | Show retry message |
| InternalError | 500 | Database connection failed | Show generic error, log details |

### 6.3 Error Handling Patterns

```typescript
// Custom error class
export class AppError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number,
    public details?: unknown[],
  ) {
    super(message);
    this.name = this.constructor.name;
  }
}

// Result pattern (for expected failures)
export type Result<T, E = AppError> =
  | { success: true; data: T }
  | { success: false; error: E };

// Usage
function divide(a: number, b: number): Result<number> {
  if (b === 0) {
    return { success: false, error: new AppError('Division by zero', 'DIVISION_BY_ZERO', 400) };
  }
  return { success: true, data: a / b };
}
```

### 6.4 Global Error Handler

A global error handler at the application boundary:

- Catches all unhandled errors
- Logs the error with full context (correlation ID, user ID, request path)
- Maps the error to a standardized error response
- Returns a safe error to the client (no stack traces in production)

---

## 7. Testing Standards

### 7.1 Testing Philosophy

- **Test behavior, not implementation** — tests should validate what the code does, not how it does it.
- **Write tests first (TDD)** for business logic and complex workflows.
- **One assertion per test** where possible. If multiple assertions, they should all test the same logical concept.
- **Tests are code** — same standards apply (lint, format, review).

### 7.2 Test Pyramid Coverage Targets

| Level | Target Coverage | Responsibility |
|---|---|---|
| Unit | 90%+ | Individual functions, classes, pure logic |
| Integration | 70%+ | Module interactions, database, API endpoints |
| E2E | 20%+ | Critical user journeys |
| Visual/UI | 50%+ (screens) | Visual regression for key pages (frontend) |

### 7.3 Naming Convention

**Test files:** `[source-file-name].test.ts` (co-located with source)

**Test descriptions:** Read as a sentence

```typescript
describe('UserService', () => {
  describe('createUser', () => {
    it('creates a user with valid input', async () => { ... });
    it('throws ValidationError when email is missing', async () => { ... });
    it('throws ConflictError when email already exists', async () => { ... });
    it('triggers welcome email notification', async () => { ... });
  });
});
```

### 7.4 Test Structure (AAA Pattern)

```typescript
// Arrange
const email = 'test@example.com';
const password = 'ValidP@ss123';
const userService = new UserService(mockRepository, mockEmailService);

// Act
const result = await userService.createUser({ email, password });

// Assert
expect(result.success).toBe(true);
expect(result.data.email).toBe(email);
```

### 7.5 Mocking Rules

- Mock at the boundary — mock interfaces/ports, not implementation details
- Prefer fakes over mocks for in-memory test implementations
- No mocking of types/classes you don't own (wrap in adapter, mock the adapter)
- Use realistic data in mocks (not all `null` or empty strings)

### 7.6 What to Mock

| Dependency | Mock? | Strategy |
|---|---|---|
| External APIs | Yes | HTTP mock server (MSW, WireMock) |
| Database | Prefer in-memory | Testcontainers for true integration |
| File system | Yes | Mock filesystem (memfs) |
| Time | Yes | Mock timers (jest.useFakeTimers) |
| Random/UUID | Yes | Deterministic mock |
| Logger | Yes | Spy logger, assert log calls |
| Message queue | Yes | In-memory queue implementation |

---

## 8. Documentation Standards

### 8.1 Code Comments

- **Comments explain "why", not "what"** — the code should be self-documenting for "what".
- **No commented-out code** — delete it. Git history has the original.
- **TODO comments** must include a ticket number: `// TODO(PROJ-123): Refactor this when auth module is updated`.
- **JSDoc/TSDoc** for public API surfaces (exported functions, classes, types).

### 8.2 JSDoc/TSDoc Standards

```typescript
/**
 * Creates a new user in the system.
 *
 * @param params - The user creation parameters.
 * @param params.email - User's email address (must be unique).
 * @param params.password - User's password (min 8 chars, 1 uppercase, 1 number).
 * @returns The created user with generated ID.
 * @throws {ValidationError} When email or password fails validation.
 * @throws {ConflictError} When email already exists.
 *
 * @example
 * const user = await createUser({ email: 'test@example.com', password: 'ValidP@ss1' });
 * // user.id is a UUID
 */
export async function createUser(params: CreateUserParams): Promise<User> { ... }
```

### 8.3 README Standards

Every module/subsystem has a `README.md` containing:

- **Purpose:** What does this module do?
- **Ownership:** Which team owns it?
- **Dependencies:** What does it depend on?
- **Configuration:** Environment variables, feature flags
- **Getting Started:** How to run/test locally
- **API:** Public API surface (if applicable)

---

## 9. Git Workflow Standards

### 9.1 Branch Strategy

- **Main branch:** `main` — always deployable, protected (no direct pushes)
- **Feature branches:** `feature/PROJ-123-description`
- **Bugfix branches:** `fix/PROJ-456-description`
- **Release branches:** `release/v1.2.3`
- **Hotfix branches:** `hotfix/PROJ-789-description`

### 9.2 Commit Message Convention (Conventional Commits)

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` — New feature
- `fix` — Bug fix
- `chore` — Maintenance, tooling, dependencies
- `refactor` — Code change that neither fixes a bug nor adds a feature
- `test` — Adding or modifying tests
- `docs` — Documentation only
- `style` — Formatting, missing semicolons, etc. (no logic change)
- `perf` — Performance improvement
- `ci` — CI/CD configuration changes
- `build` — Build system changes

**Examples:**
```
feat(auth): add password reset flow

fix(api): handle empty email in login endpoint

chore(deps): upgrade express from 4.18 to 4.19

refactor(orders): extract pricing logic into dedicated service

docs(readme): add local development setup instructions
```

### 9.3 Pull Request Standards

- **Title:** Follows conventional commit format
- **Description:** What, why, how, testing notes, screenshots (if UI change)
- **Size:** Max 400 lines changed per PR (exceptions documented)
- **Reviewers:** At least 1 for simple changes, 2 for complex changes
- **CI:** Must pass before merge — no exceptions
- **Merge strategy:** Squash merge (clean history)

### 9.4 Code Review Standards

See Section 10.

---

## 10. Code Review Standards

### 10.1 Reviewer Responsibilities

1. **Understand the change** — read the description first, then the code.
2. **Focus on correctness** — does the code do what it's supposed to?
3. **Look for design issues** — is the architecture right? Is there a simpler approach?
4. **Check for standards compliance** — lint, naming, file structure, testing.
5. **Verify test coverage** — are the right tests written? Do they test behavior?
6. **Check for security issues** — SQL injection, XSS, CSRF, authz missing, data exposure.
7. **Check for performance issues** — N+1 queries, memory leaks, blocking operations.

### 10.2 Review Comments Format

| Prefix | Meaning | Action Required |
|---|---|---|
| `nit:` | Minor style preference | Optional |
| `suggestion:` | Alternative approach | Consider |
| `question:` | Clarification needed | Answer |
| `issue:` | Problem that blocks merge | Must fix |
| `blocking:` | Critical bug or security issue | Must fix before merge |
| `praise:` | Something well done | None |

### 10.3 What Blocks a Merge

- Test failures
- Lint/type errors
- Missing test coverage for new logic
- Security vulnerability
- Performance regression without documented compromise
- Blocking or issue comments unresolved

---

## 11. Performance Standards

### 11.1 Frontend Performance Budgets

| Metric | Target | Measurement |
|---|---|---|
| First Contentful Paint (FCP) | < 1.5s | Lighthouse |
| Largest Contentful Paint (LCP) | < 2.5s | Lighthouse |
| Time to Interactive (TTI) | < 3.5s | Lighthouse |
| Cumulative Layout Shift (CLS) | < 0.1 | Lighthouse |
| Bundle size (initial) | < 200 KB (gzipped) | Webpack/Vite |
| API response time (p95) | < 500ms | Grafana |
| Image weight per page | < 500 KB | Lighthouse |

### 11.2 Backend Performance Targets

| Metric | Target | Measurement |
|---|---|---|
| API response time (p50) | < 100ms | APM (Datadog/New Relic) |
| API response time (p99) | < 500ms | APM |
| Database query time (p95) | < 50ms | Database monitoring |
| Memory usage per request | < 50 MB | APM |
| CPU usage | < 70% under peak | Infrastructure monitoring |

### 11.3 Performance Best Practices

- **Lazy load** — images, components, routes loaded on demand
- **Debounce/throttle** — high-frequency events (scroll, resize, search)
- **Memoize** — expensive computations and React components
- **Code split** — route-based chunking, dynamic imports
- **Optimize images** — WebP, responsive srcset, lazy loading
- **Minimize re-renders** — React.memo, useMemo, useCallback
- **Bundle analysis** — run webpack-bundle-analyzer before major releases
- **Database indexing** — indexes on all query patterns (see database.md)
- **Connection pooling** — reuse database connections, don't open/close per request

---

## 12. Accessibility Standards

### 12.1 Target Level

WCAG 2.1 Level AA compliance required. Level AAA targeted for public-facing content.

### 12.2 Mandatory Practices

- All images have `alt` text (decorative images: `alt=""`)
- All form inputs have associated `<label>` elements
- Color is not the only means of conveying information
- Color contrast ratio meets WCAG AA (4.5:1 for normal text, 3:1 for large)
- All interactive elements are keyboard accessible
- Focus indicators are visible (not removed via `outline: none` without replacement)
- ARIA landmarks used for page structure (`<nav>`, `<main>`, `<aside>`, `<footer>`)
- Heading hierarchy is logical (h1 -> h2 -> h3, no skipping)
- Error messages are associated with inputs via `aria-describedby`
- Dynamic content changes are announced via `aria-live` regions

### 12.3 Testing

- Automated: axe-core in CI (via @axe-core/playwright or jest-axe)
- Manual: Screen reader testing (VoiceOver / NVDA) before release
- Keyboard audit: Tab through every interactive element

---

## 13. Security Standards

### 13.1 Input Validation

- All user input is validated at the boundary (API layer)
- Use schema validation library (Zod, Joi, Yup) for runtime validation
- Sanitize all user-generated HTML (DOMPurify)
- Parameterize all database queries (no string concatenation)
- Validate file uploads: type, size, content scanning

### 13.2 Authentication & Session Management

- Passwords hashed with bcrypt (cost factor 12+) or Argon2id
- JWTs signed with RS256 or HS256 (key rotation supported)
- Access token TTL: 15 minutes maximum
- Refresh token TTL: 7 days (configurable, shorter for high-security)
- Session invalidation on password change
- Rate limiting on login endpoint (5 attempts per minute per IP)
- Account lockout after 10 failed attempts (15 minute cooldown)

### 13.3 Data Protection

- All data in transit encrypted with TLS 1.2+
- PII encrypted at rest (column-level encryption)
- Secrets stored in secrets manager (AWS Secrets Manager, Azure Key Vault, Vault)
- No secrets in code, config files, or environment variable documentation
- API keys and tokens are revocable and rotatable

### 13.4 Dependency Security

- Automated vulnerability scanning on every commit
- No dependencies with known HIGH or CRITICAL vulnerabilities
- Lockfile integrity verified (package manager integrity checks)
- Dependencies pinned to exact versions

### 13.5 HTTP Security Headers

```http
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

---

## Appendix A: Tooling Configuration

| Tool | Configuration File | Enforced In |
|---|---|---|
| ESLint | `eslint.config.js` | CI, pre-commit hook |
| Prettier | `.prettierrc` | CI, pre-commit hook |
| TypeScript | `tsconfig.json` | CI, editor |
| Stylelint | `.stylelintrc` (if CSS-in-JS not used) | CI |
| Commitlint | `commitlint.config.js` | CI, pre-commit hook |
| Lint-staged | `lint-staged.config.js` | Pre-commit hook |
| Husky | `.husky/` | Pre-commit hook |

## Appendix B: Pre-commit Hook Commands

```bash
npx lint-staged
# Runs: prettier --check, eslint, stylelint, tsc (noEmit)
```

## Appendix C: Code Review Checklist Template

- [ ] Code follows naming conventions
- [ ] Code follows file structure conventions
- [ ] No commented-out code
- [ ] Error handling covers all failure modes
- [ ] Tests cover happy path and all error paths
- [ ] No security vulnerabilities introduced
- [ ] No performance regressions
- [ ] Accessibility requirements met
- [ ] Documentation updated (if API/public surface changed)
- [ ] Commit messages follow convention

## Appendix D: Change Log

| Date | Author | Change | Rationale |
|---|---|---|---|
| [DATE] | [AUTHOR] | Initial creation | Standards baseline |
| [DATE] | [AUTHOR] | [CHANGE] | [RATIONALE] |
