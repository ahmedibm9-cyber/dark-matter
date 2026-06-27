# SOP: Architecture Review
Last Updated: 2026-06-25
Owner: Software Architect / Technical Lead

## Purpose
Evaluate the software architecture of a project against established design principles, quality attributes, and architectural patterns. This SOP ensures the architecture is maintainable, scalable, testable, and aligned with business goals. It produces quantified metrics for coupling, cohesion, layer compliance, and pattern consistency, along with actionable recommendations for improvement.

## When to Execute
- During design phase of new features or services
- When planning significant refactoring or re-architecture
- Quarterly as part of ongoing architecture governance
- When performance or maintainability issues are reported
- Before merging large architectural changes
- As part of the onboarding process for new team members

## Required Inputs
- Full repository access
- Architecture decision records (ADRs)
- Current architecture diagrams (C4 model, UML, or equivalent)
- List of known architectural pain points from the team
- Business requirements and domain model documentation
- Performance and scalability requirements (SLOs/SLAs)
- Deployment topology and infrastructure architecture

## Prerequisites
- Static analysis tools: NDepend (for .NET), Structure101, or equivalent
- Dependency analysis tool: `dotnet-format`, `madge` (JS), `pylint` (Python), or similar
- Code visualization tool: dependency graph generators (D2, Graphviz, PlantUML)
- Metrics collection tools: SonarQube, CodeMR, or equivalent
- Access to production monitoring data (if available) for validation

## Procedure

### Step 1: Architecture Documentation Review
Verify the documented architecture matches the implemented architecture.
- Gather all architecture documentation:
  - ADRs in `docs/adr/` or `decisions/` directory
  - Architecture diagrams (C4, UML component diagrams)
  - README architecture section
  - Wiki pages or Confluence documentation
- For each documented component, trace to actual code:
  - Does the code structure reflect the documented layers?
  - Are component boundaries where the documentation says they are?
  - Are there undocumented components or layers in the code?
- Identify drifts: documented vs. implemented. Flag discrepancies as architecture debt.
- Score documentation accuracy: (correctly documented components / total components) * 100.

### Step 2: Layer Structure Analysis
Analyze the codebase's layer organization and separation of concerns.
- Identify architectural layers:
  - **Presentation/API Layer**: Controllers, handlers, middleware, views
  - **Application/Service Layer**: Use cases, orchestrators, commands, queries
  - **Domain/Business Layer**: Entities, value objects, domain services, aggregates
  - **Infrastructure/Data Layer**: Repositories, database access, external services
- For each layer:
  - Count files and lines of code
  - Identify public interfaces exposed
  - Measure the number of external dependencies
- Check layer compliance:
  - Verify Presentation only references Application (not Domain/Infrastructure directly)
  - Verify Application references Domain (not Infrastructure directly)
  - Verify Domain has zero external dependencies
  - Verify Infrastructure implements Domain interfaces
- Flag violations as **layer breaches**. Examples:
  - A controller directly using a database context (bypassing service layer)
  - A domain entity depending on an ORM attribute
  - Application logic in a view template or stored procedure

### Step 3: Coupling Measurement
Quantify coupling between components using multiple metrics.
- **Afferent Coupling (Ca)**: number of components that depend on a component
- **Efferent Coupling (Ce)**: number of components a component depends on
- **Instability (I)**: Ce / (Ca + Ce). 0 = maximally stable, 1 = maximally unstable
- **Abstractness (A)**: number of abstract types / total types in a component
- **Distance from Main Sequence (D)**: |A + I - 1|. Values near 0 = balanced, near 1 = problematic

```
# Example: NDepend CQL query for high coupling
SELECT TOP 10 TYPES WHERE EfferentCoupling > 20 ORDER BY EfferentCoupling DESC

# Example: madge for JS/TS
npx madge --circular --extensions ts,js src/
npx madge --image dep-graph.svg src/
```
- Identify **god classes** (high Ce, >500 lines):
```
Select-String -Pattern "class \w+" -Path *.cs -Recurse | ForEach-Object { 
    $file = $_.Path; $line = (Get-Content $file | Measure-Object -Line).Lines; 
    if ($line -gt 500) { "$file : $line lines" }
}
```
- Flag components with Ce > 20 as high coupling risk.
- Flag components with D > 0.5 as architectural imbalance.
- Detect and count circular dependencies (A → B → C → A). Any circular dependency is a violation.

### Step 4: Cohesion Analysis
Evaluate whether components have a single, well-defined responsibility.
- **LCOM (Lack of Cohesion of Methods)**:
  - Calculate per class: methods that don't share fields / total methods
  - LCOM > 0.8 indicates the class has multiple responsibilities
- **Relational Cohesion (H)**: (internal relationships + 1) / number of types. Higher is better.
- For low-cohesion classes:
  - Check if they can be split into smaller, focused classes
  - Identify groupings of methods that could form new classes
  - Check if the class name matches its actual responsibilities
- Flag classes with >3 distinct responsibility areas (check method groupings).
- Flag "Manager", "Helper", "Util", "Service" classes without clear domain focus.

### Step 5: Modularity and Boundary Analysis
Assess how well the code is organized into bounded contexts or modules.
- Identify module boundaries:
  - Feature-based modules (e.g., `Orders/`, `Payments/`, `Shipping/`)
  - Layer-based modules (e.g., `API/`, `Core/`, `Infrastructure/`)
  - Hybrid structures
- For each module, measure:
  - **Module cohesion**: are all related types in the same module?
  - **Module coupling**: how many other modules does this module reference?
  - **Module size**: total LOC and file count
- Check for **anemic modules**: modules with infrastructure code but no business logic.
- Check for **god modules**: modules exceeding 10,000 LOC or covering multiple bounded contexts.
- Evaluate **dependency direction** between modules (should point inward toward domain).
- Flag modules that import from sibling modules (should use abstractions).

### Step 6: Pattern Consistency Check
Verify consistent use of architectural and design patterns.
- Identify declared patterns from ADRs or documentation:
  - CQRS, Event Sourcing, Repository Pattern, Unit of Work, etc.
  - Clean Architecture, Hexagonal Architecture, Onion Architecture
  - Domain-Driven Design tactical patterns (Aggregate, Entity, Value Object, Domain Event)
- For each pattern, verify correct implementation:
  - **Repository Pattern**: repositories return domain objects, queries are separate
  - **CQRS**: commands don't return domain data, queries don't modify state
  - **Domain Events**: event handlers are in the correct layer, events are immutable
  - **Aggregates**: consistency boundaries are enforced, child entities accessed through root
- Check for **pattern anti-patterns**:
  - Repository pattern implemented as CRUD wrapper over every table
  - CQRS with no real separation (same handler does read and write)
  - Domain Events that are processed synchronously in the same transaction
  - Value Objects that are mutable or have identity
- Flag inconsistent pattern usage (e.g., sometimes using Repository, sometimes direct DbContext).

### Step 7: Dependency Injection and Composition Root Review
Evaluate the dependency injection configuration and composition root.
- Locate the composition root:
  - .NET: `Startup.cs`, `Program.cs`, `CompositionRoot.cs`
  - Java: configuration classes, module files
  - Node: container configuration, inversion of control setup
- Verify:
  - All external dependencies are injected (no `new()` of services within classes)
  - Lifetime management is correct (singleton, scoped, transient) for each registration
  - No service locator pattern (anti-pattern)
  - No ambient context (HttpContext.Current, ThreadStatic, CallContext)
  - Registration is centralized in composition root
- Check for **DI container abuse**:
  - Resolving from container in application code (should only happen in composition root)
  - Too many constructor parameters (>4-5 suggests SRP violation)
  - Registration of infrastructure types as concrete classes (should use interfaces)

### Step 8: Scalability and Performance Architecture
Evaluate architectural decisions that impact scalability and performance.
- **Statelessness**: can any component horizontally scale?
- **Caching strategy**: where is caching applied? Is cache invalidation correct?
- **Database access patterns**: N+1 queries, pagination, large result sets
- **Async/Concurrency**: is async used appropriately (not sync-over-async)?
- **Message queue usage**: is there async processing for long-running operations?
- **Connection pooling**: are HTTP, database, and message queue connections pooled?
- **Bulkhead pattern**: are critical paths isolated from non-critical?
- **Circuit breaker**: are external service calls protected?
- Identify synchronous calls that should be async. Flag blocking waits on async code.
- Check for missing or incorrect timeout configurations on external calls.

### Step 9: Testability Assessment
Evaluate how well the architecture supports testing.
- **Testability score**: what percentage of classes can be unit tested without integration?
- Check for:
  - Sealed/final classes that can't be mocked (testability blocker)
  - Static methods that can't be substituted
  - Direct instantiation of dependencies (no DI) in constructors
  - Hidden dependencies (DateTime.Now, Random, file system, environment)
  - Large constructors (>4 parameters) that are hard to set up
- Identify untestable patterns:
  ```
  Select-String -Pattern "DateTime\.Now|DateTime\.UtcNow|Directory\b|File\.|Environment\." -Path *.cs -Recurse
  ```
- For each untestable component, suggest refactoring to support testability.

### Step 10: Technical Debt Quantification and Final Report
Quantify architecture debt and produce the final report.
- Calculate an **Architecture Health Score** across dimensions:
  - Documentation accuracy (weight: 10%)
  - Layer compliance (weight: 25%)
  - Coupling metrics (weight: 20%)
  - Cohesion metrics (weight: 15%)
  - Pattern consistency (weight: 15%)
  - Testability (weight: 15%)
- Generate architecture dependency graph:
  ```
  # Using Graphviz or equivalent
  dot -Tsvg dep-graph.dot -o architecture-graph.svg
  ```
- For each finding, classify as:
  - **Critical**: architectural violations that block feature development or cause defects
  - **High**: significant maintenance cost, scalability limits, or testability issues
  - **Medium**: pattern inconsistency, minor coupling issues, documentation gaps
  - **Low**: style/naming, non-critical technical debt
- Provide before/after metrics for each recommended change.
- Save report as `architecture-review-YYYY-MM-DD.md`.

## Verification Steps
- All layer breaches are confirmed by tracing actual code paths
- Coupling and cohesion metrics are reproducible with documented tools
- Architecture dependency graph is validated against actual project structure
- Pattern consistency findings are reviewed with the team for context
- Testability findings are verified by attempting to write unit tests for flagged components

## Expected Deliverables
- `architecture-review-YYYY-MM-DD.md` — full architecture review report
- Architecture dependency graph (SVG/PNG)
- Architecture health scorecard with dimension breakdown
- Prioritized refactoring backlog with effort estimates
- Updated ADRs for any architectural decisions changed during review

## Success Criteria
- Architecture health score is measured and baseline documented
- All layer breaches have been identified and categorized
- No circular dependencies exist (or a plan to eliminate them)
- Pattern usage is documented and consistent across the codebase
- Testability blockers are identified with recommended refactoring approaches
- Recommendations are prioritized and include estimated effort

## Failure Recovery
- If dependency analysis tools are not available: use manual inspection of using/import statements
- If architecture documentation does not exist: reconstruct from code using C4 reverse-engineering techniques, note in report
- If full static analysis is too time-consuming: focus on top 5 most-changed modules
- If team disagrees with coupling metrics: provide concrete examples of impact on development velocity
- If pattern violations are intentional (not accidental): document as architectural decision and update ADRs

## Related SOPs
- `audit.md` — Full codebase audit (includes architecture overview)
- `code-review.md` — Architectural compliance in code reviews
- `performance-review.md` — Performance architecture validation
- `database-review.md` — Data architecture consistency
- `documentation-review.md` — Architecture documentation accuracy
