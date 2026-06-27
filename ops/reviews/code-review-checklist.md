# Code Review Checklist

> Every PR must pass this checklist before merging. Items marked **BLOCKER**
> must be resolved. Items marked **RECOMMENDED** should be addressed but may
> be deferred with justification.

---

## CORRECTNESS — Logic, edge cases, error handling, state management

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | All code paths return a value or throw intentionally | Scan each function for missing returns; check TypeScript `noImplicitReturns` | BLOCKER |
| 2 | Edge cases handled (empty, null, undefined, zero, max) | Think about what happens when inputs are at boundaries | BLOCKER |
| 3 | Error handling catches and wraps external failures | Look for bare `throw`, unhandled promise rejections, missing try/catch around I/O | BLOCKER |
| 4 | Async operations have proper error propagation | Check `.catch()` on promises, try/catch in async functions | BLOCKER |
| 5 | State mutations are predictable and intentional | Look for accidental mutation of props, redux state, or shared objects | BLOCKER |
| 6 | Floating-point comparisons use epsilon tolerance | Search for `===` with non-integer math results | RECOMMENDED |
| 7 | Race conditions eliminated (timing, shared state) | Check for stale closure values, shared mutable state in async contexts | BLOCKER |
| 8 | Recursion has base case and depth limit | Verify termination condition; review for stack overflow risk | RECOMMENDED |
| 9 | Default values are specified for optional parameters | Check function signatures for missing defaults | RECOMMENDED |
| 10 | Data validation occurs at system boundaries | Look for validation at API routes, file reads, user input handlers | BLOCKER |
| 11 | Type coercions are explicit, not implicit | Scan for `==` vs `===`, `+` on mixed types | RECOMMENDED |
| 12 | Off-by-one errors in loops and array access | Double-check loop bounds, slice/splice arguments | BLOCKER |
| 13 | Callbacks/event listeners are cleaned up on unmount | Check `useEffect` return, `removeEventListener`, `dispose()` | BLOCKER |
| 14 | Fallback values for failed operations (e.g., network) | Look for `??`, `||` defaults after fetch/read calls | RECOMMENDED |
| 15 | Idempotency ensures repeated calls are safe | Check that operations can be retried without side effects | RECOMMENDED |

---

## SECURITY — Auth, injection, secrets, input validation, output encoding

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | Authentication check on every protected endpoint | Trace from entry point to auth guard; ensure no bypass paths | BLOCKER |
| 2 | Authorization checks per resource (not just auth) | Verify that user can only access own resources | BLOCKER |
| 3 | SQL/NoSQL injection prevented (parameterized queries) | Look for string concatenation in DB queries | BLOCKER |
| 4 | Command injection prevented (shell exec) | Search for `exec`, `spawn`, `child_process` with unsanitized input | BLOCKER |
| 5 | XSS prevented by output encoding / CSP | Check template injection, `dangerouslySetInnerHTML`, `v-html` | BLOCKER |
| 6 | No secrets committed (API keys, tokens, passwords) | Search for hardcoded secret patterns, env fallbacks | BLOCKER |
| 7 | Input validation uses allowlist, not denylist | Check that valid inputs are defined, not invalid ones excluded | BLOCKER |
| 8 | Rate limiting on auth/creation endpoints | Verify throttle middleware on sensitive routes | RECOMMENDED |
| 9 | CORS configured correctly, not wildcard in production | Check `Access-Control-Allow-Origin` configuration | BLOCKER |
| 10 | CSRF protection on state-changing endpoints | Verify CSRF token or SameSite cookie attribute | RECOMMENDED |
| 11 | File uploads validated (type, size, path traversal) | Check extension validation, MIME type, path sanitization | BLOCKER |
| 12 | Sensitive data not logged or exposed in errors | Search for error objects sent to client with stack traces | BLOCKER |
| 13 | Session management uses secure, httpOnly cookies | Check `Secure`, `HttpOnly`, `SameSite` flags | RECOMMENDED |
| 14 | Dependency versions pinned, not ranges | Look for `^` / `~` in package.json; prefer exact versions | RECOMMENDED |
| 15 | Tokens expire and are revocable | Check JWT expiry, refresh token rotation | BLOCKER |

---

## PERFORMANCE — N+1 queries, memory leaks, unnecessary renders, bundle impact

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | N+1 query pattern absent in database access | Look for queries inside loops; check eager loading | BLOCKER |
| 2 | Components not re-rendering unnecessarily | Check missing deps arrays, inline functions, unstable references | RECOMMENDED |
| 3 | Large lists are virtualized (windowing) | Check for `react-window`, `react-virtuoso` on long lists | RECOMMENDED |
| 4 | Memoization applied to expensive computations | Look for `useMemo`, `useCallback`, `memo` where appropriate | RECOMMENDED |
| 5 | Lazy loading for route-based code splitting | Verify dynamic imports (`React.lazy`, dynamic `import()`) | RECOMMENDED |
| 6 | Images optimized (sizing, lazy loading, format) | Check `loading="lazy"`, responsive images, WebP/AVIF | RECOMMENDED |
| 7 | Bundle size impact assessed for new dependencies | Check import cost; prefer tree-shakeable libraries | RECOMMENDED |
| 8 | Network requests debounced/throttled where needed | Look for rapid-fire API calls on input change, scroll | RECOMMENDED |
| 9 | Cache headers set on API responses | Check `Cache-Control`, `ETag`, `Last-Modified` headers | RECOMMENDED |
| 10 | Data fetching batched or deduplicated | Look for request deduplication patterns | RECOMMENDED |
| 11 | Memory leaks from subscriptions/timers not cleaned | Verify all `setInterval`, `addEventListener`, `subscribe` have cleanup | BLOCKER |
| 12 | Database queries select only needed columns | Check raw SQL / ORM selects for `SELECT *` | RECOMMENDED |
| 13 | CSS animations use GPU-accelerated properties | Prefer `transform`/`opacity` over `width`/`height`/`top` | RECOMMENDED |
| 14 | Font loading optimized (swap, subset, preload) | Check `font-display: swap`, font subset config | RECOMMENDED |
| 15 | API payload sizes minimized | Check response size, pagination defaults | RECOMMENDED |

---

## TESTING — Test coverage, assertion quality, edge case coverage, test isolation

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | New logic has corresponding unit tests | `git diff --name-only` and check test equivalents exist | BLOCKER |
| 2 | Tests cover happy path AND error paths | Review test file for both success and failure assertions | BLOCKER |
| 3 | No snapshot-only tests (snapshot + assertion) | Verify snapshot tests have additional behavioral assertions | RECOMMENDED |
| 4 | Tests are isolated (no shared mutable state) | Check `beforeEach` reset, no module-level state leaks | BLOCKER |
| 5 | External services are mocked at the boundary | Look for network mocks, database mocks, time mocks | RECOMMENDED |
| 6 | Async tests handle timeouts and rejections | Check `expect.assertions()`, `rejects`, `resolves` | RECOMMENDED |
| 7 | Coverage thresholds enforced (unit: 80%, integration: 60%) | Review CI config for coverage gate | RECOMMENDED |
| 8 | Test names describe behavior, not implementation | "returns 404 when user not found" not "test get_user 1" | RECOMMENDED |
| 9 | Edge case tests for empty, null, large inputs | Look for boundary value tests | RECOMMENDED |
| 10 | Flaky tests identified and quarantined | Review recent CI runs for intermittent failures | RECOMMENDED |
| 11 | Accessibility tests for UI components | Check for `jest-axe`, `@testing-library/jest-dom` assertions | RECOMMENDED |
| 12 | Performance regression tests for critical paths | Look for benchmark tests, Lighthouse CI | SKIP |
| 13 | Contract tests for API changes | Check for schema validation in API tests | RECOMMENDED |
| 14 | Test doubles use interfaces, not concrete classes | Verify mocks implement interfaces, not extend classes | RECOMMENDED |
| 15 | No test-duplication of framework behavior | Don't test that React renders or Express routes work | RECOMMENDED |

---

## MAINTAINABILITY — Naming, complexity, duplication, documentation

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | Functions/methods do one thing (single responsibility) | Check function length >60 lines as a warning flag | RECOMMENDED |
| 2 | Cyclomatic complexity < 10 per function | Run `eslint complexity` or `cyclocomp` linter | RECOMMENDED |
| 3 | No magic numbers or strings without named constants | Search for bare literals; prefer named constants/enums | RECOMMENDED |
| 4 | Variable/function names reveal intent, not implementation | "isActive()" not "checkFlag()" | RECOMMENDED |
| 5 | No code duplication (DRY) | Check for repeated logic that could be extracted | RECOMMENDED |
| 6 | Comments explain WHY, not WHAT | Code should be self-documenting; comments explain rationale | RECOMMENDED |
| 7 | Dead code removed (unused params, variables, imports) | Run `ts-prune`, `eslint no-unused-vars` | RECOMMENDED |
| 8 | Public API is documented (JSDoc, TSDoc, docstrings) | Check exported functions/classes have docs | RECOMMENDED |
| 9 | Error messages are actionable and user-friendly | "File not found: /path/to/file" not "Error ENOENT" | RECOMMENDED |
| 10 | Configuration externalized, not hardcoded | Look for environment variables, config files | RECOMMENDED |
| 11 | Long parameter lists use options object | Functions with >3 positional params should use object param | RECOMMENDED |
| 12 | Side effects are explicit and minimal | Check for global state mutation, console.log, file writes | RECOMMENDED |
| 13 | Deprecation warnings handled with migration path | Search for `@deprecated` usage | RECOMMENDED |
| 14 | Logger levels used appropriately (debug/info/warn/error) | Check log calls use correct level | RECOMMENDED |
| 15 | File/module size does not exceed 400 lines | Check for files approaching this limit | RECOMMENDED |

---

## CONSISTENCY — Style matching, pattern matching, convention following

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | Code follows project ESLint/Prettier/Ruff config | CI lint job must pass | BLOCKER |
| 2 | Import ordering matches project convention | Check imports are grouped (built-in, external, internal) | RECOMMENDED |
| 3 | File naming convention followed (kebab-case, PascalCase) | Check file name casing matches project convention | RECOMMENDED |
| 4 | Component/file structure mirrors existing patterns | New component should match directory structure of peers | RECOMMENDED |
| 5 | Same error handling pattern used throughout | Check that errors are handled same way as existing code | RECOMMENDED |
| 6 | Same state management approach used | Don't mix context + Redux + Zustand in same feature | RECOMMENDED |
| 7 | Same testing framework and style as existing tests | Don't use Jest mocks if project uses Vitest | RECOMMENDED |
| 8 | CSS/styling approach consistent with project | Same CSS modules, Tailwind, styled-components approach | RECOMMENDED |
| 9 | API response format consistent across endpoints | Check same envelope (data, error, meta) pattern | RECOMMENDED |
| 10 | Language and terminology consistent in UI | "Delete" vs "Remove" — pick one and stay consistent | RECOMMENDED |
| 11 | Naming conventions for types/interfaces consistent | `IUser` vs `User` vs `UserType` — match project choice | RECOMMENDED |
| 12 | Directory structure follows project conventions | Feature-based vs layer-based — match existing | RECOMMENDED |
| 13 | Commit messages follow conventional commits | Check commitlint passes | RECOMMENDED |
| 14 | Same code style in tests as in production code | Tests should follow same formatting conventions | RECOMMENDED |
| 15 | Same logging/debugging approach as rest of codebase | Don't add `console.log` if project uses `pino` | RECOMMENDED |

---

## ARCHITECTURE — Layering violations, coupling, cohesion, abstraction leaks

| # | Check | How to Verify | Severity |
|---|-------|---------------|----------|
| 1 | Layering violations absent (UI imports DB directly) | Check import paths; UI should not import from data layer | BLOCKER |
| 2 | Circular dependencies detected and resolved | Run `madge --circular` on the codebase | BLOCKER |
| 3 | Domain logic not leaked into infrastructure layer | Business rules in services, not in controllers/repos | BLOCKER |
| 4 | Abstractions hide implementation details | Consumers should not know about DB driver, HTTP client details | RECOMMENDED |
| 5 | Dependency injection used for testability | Check constructors accept interfaces, not concrete classes | RECOMMENDED |
| 6 | Feature toggles for incremental delivery | New features behind flag, not branch-per-environment | RECOMMENDED |
| 7 | Cross-cutting concerns (logging, auth, metrics) in middleware | Check middleware/guard pattern not duplicated per handler | RECOMMENDED |
| 8 | Public API surface minimized | Only export what other modules need; rest is private | RECOMMENDED |
| 9 | Modules depend on abstractions, not concretions | Import from interfaces/index files, not implementations | RECOMMENDED |
| 10 | Appropriate use of composition over inheritance | Prefer small composable units over deep class hierarchies | RECOMMENDED |
| 11 | Event-driven decoupling for cross-module communication | Check for event bus, message queue, pub/sub patterns | RECOMMENDED |
| 12 | Database schema changes have migration scripts | Check for migration files alongside schema changes | BLOCKER |
| 13 | API versioning strategy for breaking changes | Check URL prefix or header-based versioning | RECOMMENDED |
| 14 | Third-party dependencies wrapped behind adapters | External libs behind interfaces for swap-ability | RECOMMENDED |
| 15 | Configuration/environment abstraction (env per stage) | No hardcoded stage-specific values | RECOMMENDED |

---

## Final Review Decision

- [ ] **APPROVED** — All BLOCKER items resolved
- [ ] **CHANGES_REQUESTED** — One or more BLOCKER items need addressing
- [ ] **COMMENTED** — All BLOCKER items resolved, RECOMMENDED items noted

**Reviewer:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ **Date:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_
