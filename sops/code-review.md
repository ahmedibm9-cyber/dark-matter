# SOP: Code Review
Last Updated: 2026-06-25
Owner: Senior Developer / Tech Lead

## Purpose
Establish a standardized, systematic code review process that ensures all code changes meet quality, security, performance, and maintainability standards before being merged. This SOP defines the review workflow, what to check at each level, how to provide effective feedback, and how to verify that feedback has been addressed. The goal is to catch defects early, share knowledge across the team, and maintain consistent code quality.

## When to Execute
- For every pull request or merge request (mandatory)
- For hotfixes (abbreviated review, but at least one reviewer)
- For infrastructure and configuration changes
- For database migration scripts
- For documentation-only changes (lighter review)
- For dependency updates (security-focused review)
- Before merging any code into main/master/release branches

## Required Inputs
- Pull request or commit diff
- Related issue/ticket description and acceptance criteria
- Related test results (CI pipeline execution)
- Coding standards document or style guide
- Architecture decision records (ADRs) for context
- Any related documentation (API specs, README updates)

## Prerequisites
- PR author has self-reviewed their own changes before submitting
- CI pipeline has passed (build + tests + linting)
- PR is not a draft (ready for review)
- PR description includes: what changed, why, how to test
- At least one reviewer is assigned (not the author)
- Code review checklist (this SOP) is accessible to all reviewers

## Procedure

### Step 1: Review Preparation
Prepare for the review by understanding the context and scope.
- **Read the PR description**: understand what problem is being solved, why this approach was chosen, and how to verify the change works.
- **Read the related issue/ticket**: understand the full requirements and acceptance criteria. Check if edge cases were considered.
- **Review the commit history**: are commits logically organized? Do commit messages follow the project convention? Can each commit be reviewed independently?
- **Check CI results**: build passes? All tests pass? Linting passes? Any new warnings?
- **Determine review depth**: based on change type and risk:
  - High risk (auth, payments, data migration, security): full deep review
  - Medium risk (business logic, API changes, UI): standard review
  - Low risk (refactoring, tests only, docs): lightweight review
- **Set expectations**: clarify turnaround time (typically <24 hours for standard review). If you cannot review in time, communicate and suggest alternatives.

### Step 2: Correctness Verification
Verify the code does what it claims to do, correctly.
- **Logic correctness**:
  - Trace the code path for the happy path (expected inputs -> expected outputs).
  - Trace the code path for error scenarios (invalid inputs, null values, network failures).
  - Verify boundary conditions: empty collections, zero values, negative numbers, max values.
  - Check boolean logic: are conditions correct? (AND vs. OR, NOT placement).
  - Check loop correctness: off-by-one errors? Infinite loop conditions?
  - Check recursion: base case? Stack overflow potential?
- **State management**:
  - Is state properly initialized before use?
  - Is state properly cleaned up after use?
  - Are there race conditions if state is shared?
  - Are there implicit state assumptions (ordering, timing)?
- **Error handling**:
  - Are all failure modes handled? (network timeout, API error, database failure, file not found)
  - Are exceptions caught at the right level? (not too broad, not too narrow)
  - Are caught exceptions logged with sufficient context?
  - Are exceptions wrapped with meaningful messages when rethrown?
  - Are finally blocks used for cleanup?
- **Data transformation**:
  - Is data mapping correct? (source field -> target field, type conversion)
  - Are there assumptions about data format that could break?
  - Is encoding handled correctly? (Unicode, timezone, culture)
  - Are there precision issues? (floating point, integer division, rounding)

### Step 3: Security Review
Identify security vulnerabilities in the changed code.
- **Input validation**:
  - Are all user inputs validated? (API parameters, form fields, query strings)
  - Is validation on the server side, not just client side?
  - Is allowlist validation used instead of blocklist?
  - Are file uploads validated (type, size, content)?
- **Authentication and authorization**:
  - Are new endpoints protected with appropriate authentication?
  - Is authorization checked for the correct resource? (not just "is admin" but "can user access this specific record")
  - Are there hardcoded credentials, tokens, or secrets?
  - Are API keys and tokens properly validated?
- **Injection prevention**:
  - Are SQL queries parameterized? (no string concatenation)
  - Are NoSQL queries properly escaped?
  - Are command-line arguments properly escaped?
  - Are template expressions properly escaped (XSS prevention)?
- **Data exposure**:
  - Is sensitive data (PII, credentials) logged? (should not be)
  - Are error messages leaking internal information? (stack traces, server paths, SQL queries)
  - Is sensitive data included in API responses that should be filtered?
  - Are internal endpoints exposed externally?
- **Cryptographic practices**:
  - Are weak algorithms used? (MD5, SHA1, DES, RC4)
  - Are passwords hashed with appropriate algorithms? (bcrypt, argon2, PBKDF2)
  - Are TLS connections properly configured?
  - Are random numbers generated using cryptographically secure RNG?

### Step 4: Performance Review
Identify performance issues in the changed code.
- **Algorithm efficiency**:
  - Is the algorithm appropriate for the expected data size?
  - Are there nested loops that could be optimized?
  - Are there unnecessary database queries (N+1 pattern)?
  - Are there in-memory operations on large datasets?
- **Resource usage**:
  - Are connections (database, HTTP, files) properly disposed?
  - Are there memory allocations in hot paths?
  - Are large objects created unnecessarily?
  - Are there potential memory leaks? (event subscriptions, static collections)
- **Async and concurrency**:
  - Is async used consistently (no sync-over-async)?
  - Are CancellationTokens propagated?
  - Are there thread-safe concerns with shared state?
  - Is parallelization justified for the workload?
- **Caching**:
  - Are expensive operations cached?
  - Is cache invalidation handled correctly?
  - Are cache durations appropriate?
  - Is caching distributed (not in-memory) if multiple instances?

### Step 5: Code Quality and Maintainability
Evaluate code readability, structure, and adherence to standards.
- **Readability**:
  - Are variable and function names descriptive and unambiguous?
  - Is the code self-documenting? (logic is clear without comments)
  - Are functions and methods focused (single responsibility)?
  - Are functions shorter than 50 lines? (flag longer functions)
  - Are classes shorter than 500 lines? (flag larger classes)
- **Structure**:
  - Does the code follow the project's architectural patterns?
  - Are dependencies properly injected (no service locator)?
  - Is there unnecessary coupling? (imports/using statements)
  - Is the code in the correct layer/module?
  - Are there circular dependencies?
- **Testability**:
  - Are dependencies injected (not instantiated inside methods)?
  - Are there static methods that cannot be mocked?
  - Are there hidden dependencies (DateTime.Now, Random, file system)?
  - Can the new code be unit tested?
  - Are there integration test considerations?
- **Coding standards**:
  - Does the code follow the project's style guide? (formatting, naming conventions, file organization)
  - Are there unused imports/usings?
  - Are there commented-out code blocks?
  - Are magic numbers used instead of named constants?
  - Are error messages user-friendly and consistent?

### Step 6: Test Coverage Review
Verify that the change includes appropriate tests.
- **Test presence**:
  - Does the PR include tests for new functionality?
  - Are tests updated for changed functionality?
  - Are there tests for bug fixes (regression tests)?
- **Test quality**:
  - Do tests verify the right behavior? (assert on outcomes, not implementation)
  - Are edge cases tested? (null, empty, boundary, error conditions)
  - Are tests independent and can run in any order?
  - Are tests deterministic (same result every time)?
  - Are test names descriptive? (what is being tested, what is the expected behavior)
- **Test coverage**:
  - Is the happy path covered?
  - Is each error handling path covered?
  - Are configuration-dependent behaviors covered?
  - Are there integration tests for database/file/external service interactions?
- **Test maintenance**:
  - Are tests appropriately simple? (no unnecessary mocks, no over-verification)
  - Are test fixtures and factories used instead of duplicating setup?
  - Are tests efficient? (no unnecessary waits or sleep calls)
  - Could any tests be removed (testing trivial code)?

### Step 7: Documentation Review
Verify that documentation is updated alongside code changes.
- **Code documentation**:
  - Are new public APIs documented? (XML doc, JSDoc, docstrings)
  - Are complex algorithms or business rules explained?
  - Are TODO/FIXME comments justified and tracked?
- **Project documentation**:
  - Does the README need updating? (new features, changed setup steps)
  - Are API docs updated? (OpenAPI spec, endpoint descriptions)
  - Are architecture docs affected? (ADRs, diagrams)
  - Are deployment docs affected? (new configuration, changed steps)
- **Release documentation**:
  - Is the changelog updated?
  - Are migration guides needed for breaking changes?
  - Are deprecation notices documented?

### Step 8: Provide Review Feedback
Write clear, constructive, and actionable review comments.
- **Feedback format**:
  - **Praise**: acknowledge good solutions, clever approaches, and clean code. "Nice use of x pattern here, it makes the intent clear."
  - **Issues**: clearly describe what is wrong, why it is wrong, and how to fix it. "Line 42: The null check is missing. If `user` is null, this throws NullReferenceException. Please add a null guard."
  - **Suggestions**: offer alternative approaches without demanding changes. "Consider extracting this validation logic into a separate validator class for reusability."
  - **Questions**: ask for clarification when something is unclear. "Why is the timeout set to 30 seconds here? The API typically responds in <1s."
- **Severity labels**:
  - **BLOCKING**: must be fixed before merge. Security vulnerabilities, incorrect logic, data loss risk.
  - **REQUIRED**: should be fixed before merge. Style violations, missing tests, incomplete error handling.
  - **SUGGESTION**: optional improvement. Alternative approach, future optimization, nice-to-have.
  - **QUESTION**: request for clarification. Understanding intent before approving.
- **Commenting guidelines**:
  - Reference specific lines or code blocks.
  - Be specific about what needs to change.
  - Explain why the change is needed (not just what to change).
  - Be respectful and constructive. Assume good intent.
  - Avoid absolute language ("always", "never", "obviously").
  - Focus on the code, not the author.
- **Comment grouping**: group related comments together. Use a summary comment for complex feedback.

### Step 9: Review Decision and Follow-up
Make a clear decision and follow up on feedback.
- **Review outcomes**:
  - **APPROVE**: code is ready to merge. No blocking issues. (May include minor suggestions.)
  - **APPROVE WITH COMMENTS**: code is acceptable as-is but has suggestions for future improvement. No blocking issues.
  - **REQUEST CHANGES**: code has issues that must be addressed before merging. List blocking and required items clearly.
  - **COMMENT**: general feedback, no blocking issues, but author should review comments.
- **Follow-up process**:
  - Author responds to each comment: agrees (fixes), disagrees (explains why), or questions.
  - Author pushes additional commits addressing feedback.
  - Reviewer re-reviews changes (may be scoped to only changed lines).
  - If all blocking comments resolved: approve the PR.
  - If new issues found during re-review: request changes again.
- **Merge criteria**:
  - All BLOCKING and REQUIRED comments resolved.
  - CI pipeline passes on the latest commit.
  - At least one approval from a qualified reviewer.
  - No unresolved discussions in the PR.

### Step 10: Post-Merge Verification
Verify the merged code behaves correctly in the target environment.
- **Post-merge checks**:
  - Verify the CI pipeline succeeded on the target branch after merge.
  - Monitor deployment for the first hour: error rates, response times, business metrics.
  - Check that any feature flags are in the correct state.
  - Verify that dependent services are updated if interfaces changed.
- **Knowledge sharing**:
  - If the review uncovered a systemic issue, share the finding with the team.
  - If a new pattern or approach was reviewed, consider documenting it.
  - If the review took unusually long, analyze why and improve the process.
- **Review retrospective** (optional, for large/complex reviews):
  - Was the code review effective? (Did it catch issues? Was it timely?)
  - Could the review have been easier? (Smaller PRs? Better PR description? More context?)
  - What could the author do differently next time?
  - What could the reviewer do differently next time?

## Verification Steps
- Every changed file has been reviewed (not just the diff summary)
- All BLOCKING comments have been resolved and re-reviewed
- CI pipeline passes on the final commit
- Test coverage is adequate for the change (new and modified code)
- No secrets, credentials, or sensitive data in the diff
- Related documentation has been updated

## Expected Deliverables
- Completed code review with documented comments and decisions
- PR merged with all blocking issues resolved
- Updated tests covering the new or changed code
- Updated documentation (if applicable)
- Review summary (for complex reviews)

## Success Criteria
- All changed code is reviewed by at least one qualified reviewer
- No BLOCKING issues remain unresolved at merge time
- Reviewer feedback is specific, actionable, and respectful
- PR is merged within the agreed review SLA (typically <24 hours for standard PRs)
- No production incidents caused by merged code within 7 days of deployment
- Knowledge is shared through the review process (reviewer and author both learn)

## Failure Recovery
- If CI is failing but changes are unrelated: ask author to rebase on latest target branch, escalate if persistent
- If PR is too large to review effectively: ask author to split into smaller, logical PRs; establish <400 line guideline for future
- If a blocking comment is disputed: escalate to tech lead, have a synchronous discussion, document the decision
- If security vulnerability is found: do not approve, escalate to security team, follow security incident process
- If reviewer and author time zones don't overlap: agree on async review process, set clear expectations on response time
- If the same issues appear in multiple reviews: add automated checks (linters, analyzers) to catch them in CI

## Related SOPs
- `audit.md` — Broader codebase quality assessment
- `security-audit.md` — Security-focused review for high-risk changes
- `bug-hunting.md` — Systematic defect detection complementing code review
- `documentation-review.md` — Documentation standards enforced during review
- `architecture-review.md` — Architecture compliance verification during review
