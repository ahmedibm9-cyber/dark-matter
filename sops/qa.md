# SOP: Quality Assurance Audit
Last Updated: 2026-06-25
Owner: QA Lead / Test Manager

## Purpose
Conduct a thorough evaluation of the project's quality assurance practices, test suite health, and overall test effectiveness. This SOP goes beyond coverage metrics to assess test quality, reliability, maintainability, and the team's testing culture. The goal is to identify gaps that allow defects to reach production and recommend improvements.

## When to Execute
- Before a major release to validate release readiness
- When production defects increase despite passing tests
- After significant test suite expansion or restructuring
- Quarterly as part of ongoing quality management
- When onboarding to a new project or team

## Required Inputs
- Full repository access with test project(s) identified
- CI/CD pipeline configuration files
- Test execution history (last 30 days minimum)
- Production defect log correlated with test results
- Coverage reports from recent runs
- Test framework configuration files (jest.config, .csproj test settings, etc.)

## Prerequisites
- Build environment capable of running the full test suite
- Test reporting tools configured (Allure, ReportPortal, or similar)
- Access to CI/CD pipeline logs and artifacts
- Database or service dependencies available for integration tests
- Static analysis tools installed (SonarQube, or similar)

## Procedure

### Step 1: Test Inventory and Categorization
Catalog every test in the repository by type, scope, and purpose.
- Identify test projects/directories:
```
Get-ChildItem -Recurse -Directory -Include "*Test*", "*Tests*", "*Spec*", "*Specs*"
```
- Classify each test file into one of:
  - **Unit tests**: single class/method, no external dependencies, fast (<100ms each)
  - **Integration tests**: multiple components, database/filesystem, medium speed
  - **End-to-end tests**: full system, browser or API, slow (>1s each)
  - **Contract tests**: API contract verification, consumer-driven contracts
  - **Smoke tests**: critical path verification, fast subset
  - **Performance tests**: load, stress, soak scenarios
- Record counts per category and calculate percentages.
- Flag any test file that mixes categories (e.g., unit and integration in same file).

### Step 2: Test Naming Convention Audit
Verify test names communicate intent, not just behavior.
- Check naming pattern compliance (e.g. `MethodName_StateUnderTest_ExpectedBehavior`).
- Scan for uninformative names:
```
Select-String -Pattern "Test\d+|Test1|TestMethod|ShouldWork|DoesThing" -Path *Test*.cs -Recurse
```
- Evaluate: can you tell what's being tested without reading the test body?
- Flag tests named after bugs (e.g. `Bug12345_Test` — should be renamed on fix).
- Count tests with no assertion or with a single generic assertion.

### Step 3: Coverage Quality Analysis
Move beyond line coverage to measure what matters.
- Run coverage with branch and condition granularity:
  - .NET: `dotnet test --collect:"XPlat Code Coverage" --settings coverlet.runsettings`
  - Node: `npx jest --coverage --collectCoverageFrom='src/**/*.js'`
- For each module, record: line%, branch%, function%, and mutation score (if available).
- Identify **coverage gaps**:
  - Error handling paths (catch blocks, exception filters)
  - Edge case branches (null checks, boundary values, empty collections)
  - Configuration-dependent code paths
  - Feature flags toggles (test both states)
- Find **untested public APIs** by cross-referencing exported functions with test imports.
- Calculate the **testing gap score**: (untested public methods / total public methods) * 100.

### Step 4: Test Reliability Assessment
Evaluate flakiness and reproducibility of the test suite.
- Review CI/CD test history for the last 30 days:
  - Count total test runs and failed runs
  - Identify tests that pass/fail intermittently (rerun them 5 times locally)
  - Check for time-dependent tests (DateTime.Now, Thread.Sleep, Task.Delay)
- Search for flaky patterns:
```
Select-String -Pattern "Thread\.Sleep|Task\.Delay|await Task\.Delay|DateTime\.Now|Random\b" -Path *Test*.cs -Recurse
```
- Look for tests dependent on test ordering (shared static state, test suites without isolation).
- Check for tests that modify shared databases or filesystems without cleanup.
- Record the flake rate: (flaky tests / total tests) * 100. Target is <1%.

### Step 5: Test Maintenance Cost Analysis
Determine how much effort tests add to development changes.
- Check a sample of 10 recent PRs:
  - What percentage of changed files required test updates?
  - How many tests broke due to refactoring vs. behavior changes?
  - Were tests updated in the same PR as production code?
- Identify **brittle tests**:
  - Tests that assert on internal implementation (private methods, internal state)
  - Tests that assert on exact string output without semantic comparison
  - Tests that mock too many dependencies (more than 3 mocks per test)
  - Tests using `VerifyAll()` or `VerifyNoOtherCalls()` on every mock (overspecification)
- Search for implementation-coupled assertions:
```
Select-String -Pattern "Verify\(\)|VerifyAll\(\)|Times\.Exactly|\.Received\(1\)" -Path *Test*.cs -Recurse
```

### Step 6: Integration and E2E Test Quality
Evaluate the depth and reliability of higher-level tests.
- For each integration test, verify:
  - Does it clean up test data after execution?
  - Does it use transactions that roll back?
  - Can it run in parallel with other tests?
  - Does it work with a fresh database vs. depending on seed data?
- For E2E tests:
  - Are they idempotent (same result run once or twice)?
  - Do they use data-driven approaches or hardcoded test accounts?
  - What is the average runtime per test? Flag tests >30s.
  - Are they tagged by priority (smoke, critical, regression)?
- Count E2E tests that test the same thing as unit/integration tests (duplicate coverage).

### Step 7: Test Data Strategy Review
Evaluate how tests manage data and whether data hygiene is maintained.
- Identify test data sources: fixtures, factories, builders, seed scripts, shared databases.
- Check for:
  - Shared test fixtures modified by tests (test contamination vector)
  - Hardcoded IDs that conflict when running in parallel
  - Test data that doesn't represent real-world edge cases
  - Missing edge cases: empty states, error responses, null values, boundary conditions
- Evaluate factory/builder pattern usage:
  - Does every test create its own data or use defaults?
  - Can factories produce invalid states for negative testing?
  - Are factories maintained alongside domain changes?

### Step 8: CI/CD Pipeline Effectiveness
Audit how tests are executed in the pipeline and how results are managed.
- Review pipeline configuration for:
  - Test stage placement (lint → unit → integration → E2E → deploy)
  - Parallelization strategy (test splitting, sharding)
  - Timeout settings per test stage
  - Failure behavior (stop on first failure vs. continue)
  - artifact retention (test logs, screenshots, videos, coverage reports)
- Check that:
  - Unit tests run on every commit
  - Integration tests run on every PR
  - E2E tests run on merge to main/release branch
  - Performance tests run on a schedule (nightly/weekly)
- Verify flaky test detection and quarantine process exists.

### Step 9: Mutation Testing (Optional but Recommended)
Evaluate test suite effectiveness by introducing faults and seeing if tests catch them.
- If .NET: `dotnet tool install -g Stryker.NET; stryker`
- If JS/TS: `npx stryker run`
- Review the mutation score: what percentage of injected faults were caught?
- Analyze survived mutations by category:
  - Condition boundary changes (>, >=, <, <= flipping)
  - Math operator changes (+, -, *, /)
  - Boolean negation (!true -> false)
  - Null checks removed
  - Collection expression changes
- Each survived mutation represents a test gap. Document and prioritize fixes.

### Step 10: Reporting and Remediation Planning
Compile the QA audit findings and create an improvement roadmap.
- Generate a QA health scorecard across all dimensions:
  - Coverage (quality, not just %) — weight 20%
  - Reliability/flakiness — weight 25%
  - Maintainability — weight 20%
  - Integration/E2E quality — weight 15%
  - Pipeline effectiveness — weight 10%
  - Test data strategy — weight 10%
- For each finding, include: location, severity, impact, and recommended action.
- Prioritize improvements: immediate fixes (blocking releases), short-term (next sprint), medium-term (next quarter).
- Create tracking items for each prioritized action.
- Save report as `qa-audit-YYYY-MM-DD.md`.

## Verification Steps
- Run the full test suite 3 times and confirm zero flaky failures
- Have a team member review 10 random tests for naming, structure, and assertion quality
- Verify that the mutation score improved by at least 5% from previous audit
- Confirm that all Critical findings have remediation tickets created
- Validate that coverage reports show branch coverage >60% in all modules

## Expected Deliverables
- `qa-audit-YYYY-MM-DD.md` — full QA audit report
- Flaky test inventory with reproduction steps
- Test quality scorecard with module-level breakdown
- Prioritized remediation backlog
- Updated test standards document if gaps were found

## Success Criteria
- Every test category has been inventoried and evaluated against defined quality criteria
- Flake rate is measured and documented, with plan for any tests above 1%
- Mutation score is recorded and baseline established for future comparisons
- Test maintenance cost is estimated and communicated to stakeholders
- All recommendations include effort estimates and business impact reasoning

## Failure Recovery
- If tests cannot run in local environment: reproduce using CI pipeline with debug artifacts enabled
- If coverage tools fail: use manual analysis of test structure against production code structure
- If flaky tests cannot be identified in 30-day history: schedule 10 sequential CI runs to detect them
- If mutation testing exceeds time budget: limit to 3 most critical modules
- If team does not maintain test naming standards: create automated lint rule and enforce in CI

## Related SOPs
- `audit.md` — Full codebase audit
- `code-review.md` — Code review procedures including test review
- `release-audit.md` — Release candidate quality gates
- `performance-review.md` — Performance testing procedures
- `bug-hunting.md` — Systematic bug finding
