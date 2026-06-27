# SOP: Bug Hunting
Last Updated: 2026-06-25
Owner: Senior Developer / QA Lead

## Purpose
Systematically identify, isolate, and document software defects across the entire application. This SOP describes structured techniques for finding logic errors, workflow inconsistencies, state management bugs, concurrency issues, data corruption scenarios, and validation failures. The goal is to discover defects before they reach production through a combination of automated analysis, manual inspection, and targeted testing strategies.

## When to Execute
- Before every major release (regression bug hunt)
- When a production incident reveals a class of bugs that may exist elsewhere
- After significant refactoring of shared infrastructure
- During stabilization sprints
- When user-reported bugs suggest systematic quality issues
- Before demo or milestone presentations

## Required Inputs
- Full repository access with build capability
- User stories and acceptance criteria for recent features
- Known bug tracker entries (Jira, GitHub Issues, etc.)
- Production error logs and exception tracking data (Sentry, App Insights, etc.)
- Test suite results from recent runs
- API documentation or Postman collections
- Database schema and seed data scripts

## Prerequisites
- Development environment configured to run the full application
- Debugger and profiler tools (Visual Studio, VS Code debugger, Chrome DevTools)
- Database client with query execution capability
- Log aggregation access (if available)
- Exploratory testing tools (if applicable)
- Performance profiling tools for suspected performance bugs

## Procedure

### Step 1: Bug Pattern Identification from Historical Data
Analyze existing bug reports and production errors to identify patterns.
- Export last 90 days of production errors:
  - Group by exception type, module, and error message
  - Identify top 10 most frequent error types
  - Identify modules with highest error rates
- Analyze bug tracker for recurring themes:
  - Categorize bugs by type: logic, state, data, concurrency, validation, UI, performance
  - Check for bugs reopened after being marked "fixed" (fragile fixes)
  - Identify components with highest bug density (bugs per KLOC)
- Create a bug hypothesis list:
  - "Similar patterns to previous bugs may exist in other modules"
  - "Components recently refactored may have regressions"
  - "Edge cases not covered by existing tests are likely buggy"

### Step 2: Automated Static Analysis for Bug Patterns
Run automated tools that detect common bug patterns at compile/analysis time.
- Null reference analysis:
  - .NET: enable nullable reference types, fix all nullable warnings
  - Java: IntelliJ @NotNull/@Nullable analysis
  - JS/TS: TypeScript strict mode analysis
  - Python: mypy strict mode
- Common bug pattern tools:
```
# .NET: Roslyn analyzers
dotnet build /warnaserror

# JavaScript/TypeScript: ESLint with bug-detection rules
npx eslint --rule 'no-unused-vars: error' --rule 'no-undef: error' src/

# FindBugs/SpotBugs for Java
spotbugs -textui -high build/classes/

# Python bug detectors
flake8 --select=F src/
pylint --disable=all --enable=E src/
```
- Search for known bug-prone patterns:
```
# Race conditions - async void
Select-String -Pattern "async void" -Path *.cs -Recurse

# Thread safety - shared mutable state
Select-String -Pattern "static\s+\w+\s+\w+\s*\{.*set;" -Path *.cs -Recurse

# Comparison bugs - floating point equality
Select-String -Pattern "\bfloat\b|\bdouble\b" -Path *.cs -Recurse

# Resource leaks - unclosed connections
Select-String -Pattern "new SqlConnection|new HttpClient\(\)" -Path *.cs -Recurse
```

### Step 3: Logic Bug Deep Dive
Systematically analyze conditional logic and business rules.
- **Boundary condition analysis**: For every numeric input, test boundaries (0, 1, max, max+1, min, min-1, negative).
- **Boolean logic analysis**: Check complex conditions for operator precedence errors and short-circuit issues.
  ```
  # Complex boolean expressions
  Select-String -Pattern "&&.*\|\||\|\|.*&&" -Path *.cs -Recurse
  ```
- **Switch/if-else completeness**:
  - Identify all switch statements without default cases
  - Identify if-else chains that don't handle all enum values
  - Check for missing else clauses where default behavior is important
- **Math and precision bugs**:
  - Check integer division where float is expected
  - Check rounding logic (Banker's rounding vs. standard)
  - Check for overflow in unchecked contexts
  - Check date/time arithmetic across DST boundaries
- **String comparison bugs**:
  - Check case-sensitive comparisons for case-insensitive data (emails, usernames)
  - Check culture-sensitive comparisons for invariant data
  - Check for ordinal vs. invariant vs. current culture mismatches

### Step 4: Workflow and State Machine Bugs
Model and verify every stateful process in the application.
- Map all workflows and state transitions:
  - Order processing: Created → Paid → Shipped → Delivered
  - User lifecycle: Registered → Verified → Active → Suspended → Deleted
  - Document workflow: Draft → Review → Approved → Published → Archived
- For each state machine, verify:
  - **All states are represented** (no implicit states)
  - **All valid transitions are allowed** (no missing transitions)
  - **All invalid transitions are blocked** (no illegal state changes)
  - **Transitions are atomic** (partial state changes don't leave system inconsistent)
- Check for **race conditions in state transitions**:
  - Can two concurrent requests process the same entity in the same state?
  - Is optimistic/pessimistic locking applied to state change operations?
- Search for state-related bugs:
```
Select-String -Pattern "if.*Status.*==" -Path *.cs -Recurse
Select-String -Pattern "switch.*Status|case.*Status\." -Path *.cs -Recurse
```
- Verify each state transition logs the before/after state and who initiated it.

### Step 5: Concurrency and Threading Bug Hunt
Identify race conditions, deadlocks, and synchronization defects.
- Code review for thread safety:
  - Identify all shared mutable state (static fields, cached data, global collections)
  - Check that each access is synchronized (lock, SemaphoreSlim, Mutex)
  - Check for lock ordering consistency (always acquire locks in the same order)
  - Check for locks that are held too long (I/O operations inside lock)
- Async/await patterns:
  - Check for `.Result` or `.Wait()` on async calls (deadlock risk):
  ```
  Select-String -Pattern "\.Result\b|\.Wait\(\)|\.GetAwaiter\(\)\.GetResult\(\)" -Path *.cs -Recurse
  ```
  - Check for `async void` (exception escapes to synchronization context):
  ```
  Select-String -Pattern "async void" -Path *.cs -Recurse
  ```
  - Check for ConfigureAwait(false) consistency
  - Check for missing CancellationToken propagation
- Concurrent collection usage:
  - Are `ConcurrentDictionary`, `ConcurrentQueue`, `ConcurrentBag` used where needed?
  - Check for iteration over concurrent collection without snapshot
  - Check for check-then-act patterns on concurrent collections

### Step 6: Data Integrity and Corruption Bugs
Audit all data operations for correctness and consistency.
- **CRUD operation correctness**:
  - Check Create: are all required fields populated? Are defaults applied correctly?
  - Check Read: are queries returning the right data? Are joins correct?
  - Check Update: are only intended fields modified? Is the correct record updated?
  - Check Delete: are related records handled? Soft vs. hard delete consistency?
- **Data race conditions**:
  - Check for read-modify-write without locking:
  ```
  Select-String -Pattern "\w+\s*=\s*\w+\s*\+\s*1|\w+\+=" -Path *.cs -Recurse
  ```
  - Check for select-then-insert without unique constraint
  - Check for delete-then-recreate patterns (orphan risk)
- **Corruption scenarios**:
  - Check for encoding mismatches (UTF-8 vs. ASCII, byte order marks)
  - Check for culture-sensitive data stored without culture info
  - Check for precision loss in type conversions (decimal→double, long→int)
  - Check for timezone handling (store UTC, display local; never store local)
- **Transaction integrity**:
  - Check that multi-step operations are wrapped in transactions
  - Check that transactions are properly committed or rolled back
  - Check for nested transaction handling
  - Check for distributed transaction boundaries

### Step 7: Input Validation and Edge Case Hunt
Probe all input points with malicious and boundary data.
- **Fuzzing approach** for each input field:
  - Empty/null values
  - Maximum length strings (10K+ characters)
  - Unicode and special characters
  - SQL injection payloads
  - Script injection payloads (XSS)
  - Negative numbers where positive expected
  - Extremely large numbers (overflow/underflow)
  - Invalid enum values
  - Future dates, past dates, null dates
  - Duplicate submissions (idempotency check)
- **API endpoint fuzzing**:
  ```
  # Example: OWASP ZAP fuzzer
  zap-cli fuzz -c fuzz-config.yaml https://staging-app.example.com/api/
  ```
- **File upload edge cases**:
  - Empty files, very large files, files with no extension
  - Renamed executables (.exe renamed to .pdf)
  - Files with path traversal in filename (../../../etc/passwd)
  - Zip bombs, symlink files
  - Corrupted file headers

### Step 8: Resource Management and Leak Detection
Find bugs related to memory, connections, handles, and file descriptors.
- **Memory leaks**:
  - Check for event handler subscriptions without unsubscription
  - Check for captured variables in closures that prevent GC
  - Check for static collections that grow unbounded
  - Check for large object heap fragmentation
  - Search for cache implementations without eviction policies:
  ```
  Select-String -Pattern "new Dictionary|ConcurrentDictionary|static.*List<" -Path *.cs -Recurse
  ```
- **Connection/resource leaks**:
  - Check that all IDisposable resources are in `using` blocks or disposed
  - Check for database connections, HTTP connections, file streams, network streams
  - Check that transactions are properly disposed after use
  - Check for thread pool starvation (blocking async calls)
- **Handle leaks**:
  - Check file operations for proper close/dispose
  - Check socket operations
  - Check process handle management

### Step 9: Integration and External Dependency Bugs
Test interactions with external systems and services.
- **API client bugs**:
  - Check for missing timeout configurations
  - Check for retry logic (exponential backoff?)
  - Check for circuit breaker implementation
  - Check for response parsing errors
  - Check for header/parameter encoding issues
- **Database interaction bugs**:
  - Check for N+1 query patterns
  - Check for incorrect join conditions
  - Check for missing index hints
  - Check for batch operation boundaries
  - Check for connection pool exhaustion scenarios
- **Third-party SDK bugs**:
  - Check for version compatibility
  - Check for thread-safety of SDK methods
  - Check for error handling around SDK calls
  - Check for SDK initialization/lifecycle management

### Step 10: Bug Documentation and Reproduction
Every confirmed bug must be reproducibly documented.
- For each bug found:
  - **Title**: clear description of the issue
  - **Severity**: Critical (data loss/security), High (broken feature), Medium (incorrect behavior), Low (cosmetic)
  - **Component**: affected module/feature
  - **Environment**: where it was reproduced (dev/staging/production)
  - **Preconditions**: exact state required before reproducing
  - **Steps to reproduce**: numbered, exact sequence of actions
  - **Expected behavior**: what should happen
  - **Actual behavior**: what actually happens
  - **Evidence**: screenshots, logs, stack traces, request/response payloads
  - **Regression range**: when was it introduced (git bisect)
  - **Suggested fix**: if identified, suggest the correction
- Create test cases for each bug to prevent regression:
  - Unit test that reproduces the bug
  - Integration test for the failing scenario
  - Add to regression test suite
- Tag bugs discovered during this hunt with a common label (e.g., `bug-hunt-YYYY-MM`).

## Verification Steps
- Every bug is reproducible by a different team member following the documented steps
- Regression tests pass for all newly fixed bugs
- No high-severity bugs remain unaddressed at the end of the hunt
- Bug density trends decrease across consecutive bug hunts
- All bugs found are entered into the tracking system with proper severity and component classification

## Expected Deliverables
- Bug tracker entries with full reproduction steps for all discovered defects
- Regression test cases for each confirmed bug
- Bug density report by module (bugs per KLOC)
- Bug hunt summary report with trends and recommendations
- Updated test cases for edge cases discovered during the hunt

## Success Criteria
- Minimum of 10 person-hours of focused bug hunting completed
- All high-severity paths (authentication, payment, data integrity) have been probed
- Bug finding rate is documented (bugs found per hour) for comparison across hunts
- All confirmed bugs have regression tests added
- Bug report quality meets the standard defined in Step 10
- No Critical bugs remain in the backlog

## Failure Recovery
- If reproduction steps are incomplete: pair with another team member to validate
- If a bug is intermittent: add detailed logging, run 100 iterations, capture all failures
- If environment issues prevent testing: use containerized reproduction with Docker Compose
- If a bug affects production data: document safe querying approach, avoid running risky queries directly
- If time runs out: prioritize remaining untested modules by risk score (bug history + complexity + churn)

## Related SOPs
- `qa.md` — Systematic test suite analysis
- `code-review.md` — Code review practices to catch bugs before merge
- `security-audit.md` — Security-focused bug hunting
- `performance-review.md` — Performance bug identification
- `release-audit.md` — Ensuring bugs are fixed before release
