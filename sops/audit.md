# SOP: Full Codebase Audit
Last Updated: 2026-06-25
Owner: Lead Architect / Engineering Manager

## Purpose
Conduct a comprehensive, systematic audit of an entire codebase to evaluate architecture quality, technical debt, security posture, dependency health, and documentation completeness. This SOP produces a quantified, actionable report that prioritizes remediation efforts across all dimensions.

## When to Execute
- Before major refactoring or re-architecture initiatives
- As part of quarterly or bi-annual quality reviews
- When onboarding onto a legacy or unfamiliar codebase
- Prior to a major release or public launch
- When tech debt has been flagged as impacting velocity

## Required Inputs
- Repository URL or local clone path
- Access credentials (if private repo)
- CI/CD pipeline configuration files
- Project README and any existing architecture docs
- List of known pain points from the team
- Previous audit reports (if any)

## Prerequisites
- Git client installed and configured
- Node.js / Python / relevant runtime for the project
- Docker (if project uses containerization)
- jq, yq, and other parsing tools installed
- Adequate disk space for full clone and dependency installation
- Read access to all repositories and dependency registries

## Procedure

### Step 1: Repository Cloning and Initial Survey
Clone the repository and perform an initial structural survey.
```
git clone <repo-url> audit-workspace
cd audit-workspace
git log --oneline -20
git branch -a
git remote -v
```
Record the commit hash, branch structure, and number of contributors.
Count top-level files and directories: `Get-ChildItem -Depth 0`.
Identify the project type (monolith, microservices, monorepo, etc.).

### Step 2: Language and Framework Inventory
Identify all programming languages, frameworks, and build tools in use.
```
Get-ChildItem -Recurse -Filter "*.csproj" | ForEach-Object { $_.FullName }
Get-ChildItem -Recurse -Filter "package.json" | ForEach-Object { $_.FullName }
Get-ChildItem -Recurse -Filter "*.cs" | Select-Object -ExpandProperty Extension -Unique
```
Check for `Dockerfile`, `docker-compose.yml`, `Makefile`, `*.sln`, `*.config`.
Record versions of each runtime/framework found. Identify deprecated or EOL versions.

### Step 3: Architecture Layer Analysis
Map the codebase to architectural layers by directory convention.
- Inspect `src/`, `api/`, `web/`, `services/`, `data/`, `infrastructure/` directories.
- Check for proper separation: presentation layer, business logic, data access, infrastructure.
- For each layer, count files, lines of code, and public interfaces.
```
Get-ChildItem -Recurse -Filter "*.cs" | Group-Object DirectoryName
```
Look for forbidden cross-layer dependencies (e.g., UI directly accessing data layer).
Flag any layer that exceeds 5000 LOC or 50 files as a consolidation candidate.

### Step 4: Technical Debt Identification
Run static analysis and code quality tools.
- If .NET: `dotnet tool install -g dotnet-format; dotnet format --check`
- If Node: `npx eslint . --ext .js,.ts --format json > eslint-report.json`
- If Python: `pip install pylint; pylint src/ --output-format=json > pylint-report.json`
Examine results for:
- Files with >15 linting warnings (flagged as high debt)
- Functions exceeding 50 lines (extraction candidates)
- Classes exceeding 500 lines (refactoring candidates)
- Switch statements with >5 cases (strategy pattern candidates)
- Magic numbers and string literals (constant extraction candidates)
Count TODO/FIXME/HACK/XXX comments:
```
Select-String -Pattern "TODO|FIXME|HACK|XXX|BUG|WORKAROUND" -Path *.cs, *.js, *.ts, *.py -Recurse | Group-Object Pattern
```
Flag files with >5 such comments as technical debt hotspots.

### Step 5: Security Review
Scan for common security issues using automated tools and manual pattern search.
- Run `dotnet list package --vulnerable` or `npm audit --json` or `pip audit`.
- Search for hardcoded credentials:
```
Select-String -Pattern "(password|secret|api[_-]?key|connectionstring|token)\s*[:=]\s*[""'][^""']+[""']" -Path *.cs, *.js, *.json, *.config, *.yaml -Recurse -CaseSensitive:$false
```
- Check for SQL injection vectors:
```
Select-String -Pattern "ExecuteQuery|ExecuteCommand|\.Raw\b|\.SqlQuery" -Path *.cs -Recurse
```
- Check for XXE, SSRF, and insecure deserialization patterns.
- Verify HTTPS enforcement and authentication middleware presence.
- Generate a findings list with severity (Critical/High/Medium/Low).

### Step 6: Dependency Analysis
Generate a complete dependency tree and check for issues.
- If .NET: `dotnet list package --include-transitive > dependencies.txt`
- If Node: `npm ls --all > dependencies.txt`
- Parse the output to identify:
  - Packages with >3 levels of transitive depth (dependency bloat)
  - Packages used by <2 files (potential dead weight)
  - Packages with known vulnerabilities
  - Peer dependency mismatches
  - Duplicate packages at different versions
- Cross-reference with `libraries.io` or `npm audit` for maintenance status.
Flag packages not updated in >2 years as abandonment risks.

### Step 7: Test Coverage and Quality Assessment
Evaluate the test suite's health beyond coverage percentages.
- Locate test files: `Get-ChildItem -Recurse -Filter "*Test*" -or "*Spec*" -or "*Tests*"`
- Run coverage tool:
  - .NET: `dotnet test --collect:"XPlat Code Coverage"`
  - Node: `npx jest --coverage`
- Record metrics: line coverage, branch coverage, function coverage.
- Evaluate test quality:
  - Count assertion-less tests (tests that never fail)
  - Count tests mocking external dependencies (integration test gaps)
  - Count tests using hardcoded data vs. factories/fixtures
  - Identify tests that test implementation details (brittle tests)
- Measure test-to-code ratio across modules. Flag modules with <20% coverage.

### Step 8: Documentation Freshness Check
Audit all documentation files for accuracy and completeness.
- List all `.md` files: `Get-ChildItem -Recurse -Filter "*.md"`
- For each README, verify it contains: description, setup, usage, configuration, contributing guide.
- Check API documentation against actual interfaces (look for undocumented public methods):
```
Select-String -Pattern "public (async |static )?\w+ \w+\(" -Path *.cs -Recurse | Measure-Object
```
- Cross-reference documented endpoints with actual route registrations.
- Count documentation files older than 6 months based on git history.
- Flag modules with zero documentation or docs that contradict implementation.

### Step 9: Configuration and Environment Audit
Review all configuration files for security and consistency.
- List all config files: `*.json`, `*.yaml`, `*.yml`, `*.config`, `*.env*`, `*.ini`.
- Check for:
  - Configuration values referencing localhost that should be parameterized
  - Environment-specific values not using environment variables
  - Connection strings without encryption markers
  - Hardcoded URLs, ports, and timeout values
  - Missing appsettings sections compared to template
- Verify that `appsettings.Development.json` differs only in appropriate values from `appsettings.Production.json`.

### Step 10: Report Generation
Compile all findings into a structured audit report.
- Create an executive summary with overall health score (scale 1-10).
- Categorize findings by severity: Critical (immediate action), High (this quarter), Medium (this year), Low (watch list).
- For each finding include: file location, description, impact, recommended action, estimated effort.
- Include visualizations: layer dependency graph, tech debt trend chart, coverage by module heatmap.
- Prioritize the top 10 remediation items with rationale.
- Save the report as `audit-report-YYYY-MM-DD.md` in the project root.
- Archive raw tool outputs in `audit-artifacts/` directory.

## Verification Steps
- Re-run the top 3 static analysis checks after remediation to confirm reduction
- Have a second reviewer independently assess a 10% sample of findings for accuracy
- Verify that all Critical findings have corresponding tickets or remediation PRs
- Confirm the report was shared with all stakeholders and acknowledged

## Expected Deliverables
- `audit-report-YYYY-MM-DD.md` — comprehensive audit report
- `audit-artifacts/` — raw tool outputs, logs, and data files
- Prioritized remediation backlog in project tracking system
- One-pager executive summary for non-technical stakeholders
- Presentation deck for team review meeting

## Success Criteria
- All Critical and High findings have been verified by automated tools (not just manual inspection)
- Report includes quantified metrics for all 6 audit dimensions
- No false positives in Critical/High categories exceed 10%
- Remediation estimates include effort hours for each finding
- Report was delivered within agreed timeline (typically 3-5 days for 100K LOC)

## Failure Recovery
- If automated tools fail due to build issues: document the failure and perform maximum manual inspection, note the gap in the report
- If repository clone is incomplete: use shallow clone (`--depth 1`) and document limitation
- If access is denied to specific modules: document access gap and scope the audit accordingly
- If report exceeds 50 pages: create modular sub-reports by dimension
- If conflicting findings between tools: run a third tool as tiebreaker and document the discrepancy

## Related SOPs
- `security-audit.md` — Deep-dive security assessment
- `architecture-review.md` — Focused architecture evaluation
- `dependency-review.md` — Detailed dependency analysis
- `code-review.md` — Individual code review procedures
- `qa.md` — Quality assurance audit specifics
