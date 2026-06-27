# SOP: Dependency Review
Last Updated: 2026-06-25
Owner: DevOps Lead / Security Engineer

## Purpose
Perform a comprehensive review of all project dependencies to identify security vulnerabilities, outdated packages, unused dependencies, license compliance issues, and potential conflicts. This SOP establishes a systematic process for inventorying, analyzing, and managing the project's dependency graph to reduce attack surface, improve maintainability, and ensure legal compliance.

## When to Execute
- Before every production release
- When adding new dependencies to the project
- When updating existing dependencies
- When a vulnerability is disclosed for a dependency in use
- Monthly or quarterly as part of ongoing dependency management
- Onboarding an existing project (initial dependency audit)
- Before open-sourcing a project (license compliance)

## Required Inputs
- Dependency manifest files (package.json, packages.config, *.csproj, Cargo.toml, requirements.txt, gemfile, go.mod, pom.xml, build.gradle, etc.)
- Lock files (package-lock.json, yarn.lock, packages.lock.json, go.sum, Cargo.lock, Gemfile.lock, etc.)
- CI/CD pipeline configuration (for dependency build steps)
- Dependency vulnerability database access (GitHub Advisory DB, NVD, Snyk, or equivalent)
- License compliance requirements (company policy, OSS license list)
- A list of approved/blacklisted dependencies and licenses
- Previous dependency review reports

## Prerequisites
- Package manager CLI tools (npm, yarn, dotnet, pip, cargo, go mod, bundler, etc.)
- Vulnerability scanning tools (`npm audit`, `dotnet list package --vulnerable`, `safety`, `cargo audit`, `trivy`, `snyk`, `owasp dependency-check`)
- Dependency analysis tools (`depcheck`, `madge`, `pnpm ls`, `cargo tree`)
- License checking tools (`license-checker`, `fossa`, `askalono`)
- Network access to package registries and vulnerability databases
- Build environment that can restore all dependencies

## Procedure

### Step 1: Dependency Inventory
Catalog every dependency in the project with version details.
- **Direct dependencies**: packages explicitly listed in manifest files:
```
# Node.js / JavaScript
npm ls --depth=0 --json > direct-deps.json
yarn list --depth=0 --json > direct-deps.json

# .NET
dotnet list package --format json > direct-deps.json

# Python
pip list --format json > direct-deps.json
pip freeze > requirements-locked.txt

# Rust
cargo tree --prefix depth --format json > deps.json

# Go
go list -m all > all-deps.txt
```
- **Transitive dependencies**: packages brought in by direct dependencies:
```
# Node
npm ls --all --json > all-deps.json

# .NET
dotnet list package --include-transitive --format json > transitive-deps.json

# Rust
cargo tree --prefix depth > dep-tree.txt
```
- For each dependency, record: name, version, license, direct vs. transitive, depth in tree, purpose (production vs. dev vs. build), registry source.
- Calculate total dependency count and dependency depth distribution. Flag packages at depth >3 as deep transitive dependencies (harder to manage).

### Step 2: Outdated Dependency Detection
Identify dependencies that are behind the latest stable version.
```
# Node
npm outdated --json > outdated-deps.json

# .NET
dotnet list package --outdated --format json > outdated-deps.json

# Python
pip list --outdated --format json > outdated-deps.json

# Go
go list -u -m all > outdated-deps.txt
```
- For each outdated dependency, record: current version, wanted version, latest version, how many versions behind.
- Categorize by gap size:
  - **Critical**: >2 major versions behind (API breaking changes, security risk)
  - **High**: 1 major version behind (missing features, security patches)
  - **Medium**: >2 minor versions behind (missing bug fixes)
  - **Low**: patch versions behind (minor fixes, no urgency)
- Calculate the **outdated dependency ratio**: (outdated deps / total deps) * 100. Target: <20%.
- Flag dependencies that have been deprecated by their maintainers.
- Check the release date of the latest version: any dependency without updates in >2 years should be flagged as abandonment risk.

### Step 3: Vulnerability Scanning
Scan all dependencies for known security vulnerabilities.
```
# npm audit
npm audit --json > vuln-report.json

# yarn audit
yarn audit --json > vuln-report.json

# .NET
dotnet list package --vulnerable --include-transitive --format json > vuln-report.json

# Python
pip install safety
safety check --json > vuln-report.json

# Rust
cargo audit --json > vuln-report.json

# Go
govulncheck ./... > vuln-report.txt

# General purpose (Trivy)
trivy fs --scanners vuln --severity CRITICAL,HIGH,MEDIUM --format json --output trivy-vulns.json .
```
- For each vulnerability found, record: CVE ID, CVSS score, severity (Critical/High/Medium/Low), affected component, affected version range, fixed in version, description, whether a fix is available.
- Identify dependencies with multiple vulnerabilities (concentration risk).
- Prioritize by severity: Critical (immediate action required), High (action within 1 week), Medium (action within 1 month), Low (review next cycle).
- Check if the vulnerability is reachable from the application code (not just in the dependency tree). Use call graph analysis if available.
- For dependencies where no fix is available: assess mitigation options (WAF rules, input sanitization, feature disabling).

### Step 4: Unused Dependency Detection
Identify dependencies that are declared but never imported or used in code.
```
# JavaScript/TypeScript
npx depcheck --json > unused-deps.json

# Or manually
npx madge --json src/ > module-graph.json
# Then cross-reference imports against package.json dependencies

# Python
pip install pipreqs
pipreqs --mode import .

# Rust
cargo +nightly udeps --json > unused-deps.json

# .NET (manual - check .csproj vs. actual usings)
# Use Roslyn analyzers: RS0016, RS0035
```
- Categorize unused dependencies:
  - **Completely unused**: package is in manifest but never imported anywhere.
  - **Dev-only but in production dependencies**: testing tools listed as production deps.
  - **Used only in one file**: consider if the dependency is worth the cost for limited usage.
  - **Replaced by language/stdlib features**: e.g., lodash replaceable by native Array methods.
- Calculate the **unused dependency ratio**: (unused deps / total deps) * 100. Target: <5%.
- For each unused dependency: recommend removal. Assess removal risk (is it imported indirectly?).
- Flag development dependencies (devDependencies) that are used in build/production scripts.

### Step 5: Duplicate and Conflicting Dependency Detection
Identify duplicate packages at different versions and version conflicts.
```
# Node
npm dedupe --dry-run
npm ls --all | Select-String -Pattern "UNMET|INVALID|PEER"

# .NET
# Check packages.lock.json for duplicate entries with different versions

# Go
go mod why -m <package>

# General
# Use dependency tree analysis to find multiple versions of the same package
```
- For each duplicate: record package name, versions present, number of occurrences, which dependents require each version.
- Categorize duplication severity:
  - **Critical**: conflicting major versions of the same package (different APIs, cannot dedupe)
  - **High**: minor version differences (risk of behavior differences, bundle bloat)
  - **Medium**: patch version differences (minor risk, should dedupe)
  - **Low**: pre-release/tag variations
- Flag peer dependency warnings (package expects a specific version of another package).
- Flag unmet peer dependencies.
- Estimate bundle size impact of duplicates (can add MBs to frontend bundles).

### Step 6: License Compliance Audit
Verify all dependencies use licenses compatible with the project's distribution model.
```
# Node
npx license-checker --json --production --out license-report.json

# Python
pip-licenses --format=json --output-file=license-report.json

# .NET
# Use dotnet-project-licenses tool
dotnet-project-licenses -i . -o license-report.txt

# General purpose
# Use FOSSA or Snyk for comprehensive license scanning
```
- Classify each dependency's license:
  - **Permissive**: MIT, Apache 2.0, BSD, ISC (generally safe)
  - **Weak Copyleft**: LGPL, MPL (may have requirements for derivative works)
  - **Strong Copyleft**: GPL, AGPL (may require source disclosure of the whole project)
  - **Restricted**: proprietary, no license, custom (requires legal review)
- For each restricted/copyleft license, assess:
  - Is the dependency statically or dynamically linked?
  - Is the project distributed (making it subject to copyleft terms)?
  - Is the dependency used internally only (not distributed)?
  - Are there attribution requirements?
- Flag dependencies without a declared license (unlicensed = cannot use).
- Flag dependencies with licenses explicitly blacklisted by company policy.
- Generate a license compatibility matrix: verify all licenses are compatible with the project's primary license.
- Calculate license risk score: (restricted deps / total deps) * 100 + (unlicensed deps / total deps) * 200.

### Step 7: Dependency Size and Impact Analysis
Evaluate the cost of each dependency in terms of bundle size and install time.
```
# Node: package size
npx cost-of-modules --less --no-color

# Analyze per-package contribution to bundle
npx webpack-bundle-analyzer build/stats.json

# General: install size
du -sh node_modules/
du -sh ~/.nuget/packages/
du -sh vendor/bundle/
```
- For each dependency, record:
  - Install size (disk space)
  - Number of files installed
  - Bundle contribution (for frontend packages)
  - Install time (affects CI/CD pipeline speed)
- Flag dependencies >10MB install size (investigate if all that code is needed).
- Flag dependencies that contribute >100KB to the frontend bundle.
- Compare against lighter alternatives (e.g., dayjs vs. moment.js, zod vs. joi).
- Calculate **dependency weight score**: total install size / LOC of project code. High ratio = heavy dependency burden.

### Step 8: Maintenance and Health Assessment
Evaluate the long-term viability and maintenance status of each dependency.
- For each dependency (or at least top-level dependencies), assess:
  - **Maintainer count**: packages with single maintainers are bus-factor risks
  - **Commit frequency**: how often is the package updated? >6 months without activity = red flag
  - **Issue resolution time**: average time to close issues
  - **Release frequency**: how often are new versions published?
  - **Test coverage**: does the package have tests? (check CI badges or test directories)
  - **Documentation**: is there a README, API docs, changelog?
  - **Community size**: GitHub stars, download count, contributors
  - **Security response**: how quickly do maintainers respond to security disclosures?
- Sources for health data:
  - GitHub API (commits, issues, releases, contributors)
  - Libraries.io API
  - npmjs.com package page
  - NuGet.org package page
- Flag dependencies with health concerns:
  - **Abandoned**: no commits in >2 years, no response to issues
  - **Solo-maintained**: single contributor, no bus factor
  - **Inactive**: >6 months since last release, open issues piling up
  - **Immature**: recently released, few downloads, minimal testing
- Assign a **health score** (1-10) to each top-level dependency. Score <5 = replacement candidate.

### Step 9: Overlap and Redundancy Analysis
Identify dependencies that provide overlapping functionality.
- **Functional overlap detection**:
  - Multiple date libraries? (moment, dayjs, date-fns, luxon)
  - Multiple utility libraries? (lodash, underscore, ramda)
  - Multiple HTTP clients? (axios, fetch, got, superagent)
  - Multiple validation libraries? (joi, yup, zod, validator)
  - Multiple testing frameworks? (jest, mocha, jasmine)
- For each overlap:
  - Are both needed, or can one be eliminated?
  - What is the bundle size cost of keeping both?
  - What is the maintenance cost of keeping both?
  - Can the team standardize on one?
- Recommend consolidation: pick one library per functional area, plan migration.

### Step 10: Report Generation and Update Planning
Compile all findings and create a dependency management plan.
- **Dependency health scorecard**:
  - Total dependency count (production + dev + transitive)
  - Vulnerable dependency count and severity breakdown
  - Outdated dependency count and gap breakdown
  - Unused dependency count and removal candidates
  - Duplicate count and deduplication candidates
  - License compliance status (pass/fail per dependency)
  - Dependency weight (total install size)
  - Overall dependency health score (1-10)
- **Findings by severity**:
  - **Critical** (immediate): known vulnerability with active exploit, GPL dependency conflicting with project license, malicious package detected
  - **High** (1 week): unpatched vulnerability (no fix yet), deprecated dependency still in use, dependency with sole maintainer
  - **Medium** (1 month): major version outdated, unused dependency, license compliance gap (attribution missing)
  - **Low** (next quarter): minor version outdated, infrequently updated but stable, bundle size optimization
- **Update plan**:
  - For each upgrade, assess: major/minor/patch, breaking changes, migration effort, test requirements
  - Batch non-breaking updates together (minor + patch)
  - Plan major updates individually with migration testing
  - Schedule updates: critical (immediate), high (next sprint), medium (within 2 sprints), low (backlog)
- Create tracking items for each prioritized action.
- Save report as `dependency-review-YYYY-MM-DD.md`.
- Archive raw dependency data in `dependency-review-artifacts/`.

## Verification Steps
- All direct and transitive dependencies are inventoried and documented
- Vulnerability scan completes without errors and all findings are categorized
- Each dependency's license is identified and assessed for compatibility
- Unused dependencies are confirmed by cross-referencing manifest with actual imports
- Duplicate dependencies are identified with root cause (which dependency requires which version)
- Update plan includes timelines, risk assessment, and rollback plan for each change

## Expected Deliverables
- `dependency-review-YYYY-MM-DD.md` — comprehensive dependency review report
- Dependency inventory (CSV/JSON with name, version, license, depth, purpose)
- Vulnerability report with CVSS scores and remediation recommendations
- License compliance report with flagged dependencies
- Unused and duplicate dependency removal candidates
- Dependency update plan with prioritized actions and migration notes

## Success Criteria
- Every dependency (direct and transitive) is identified and documented
- All vulnerabilities are assessed and prioritized
- License compliance is verified for all dependencies
- Unused dependencies are identified with removal recommendations
- Duplicate dependencies are cataloged with deduplication recommendations
- Update plan includes timeline, effort estimates, and risk assessment for each change
- Overall dependency health score is calculated and trended

## Failure Recovery
- If vulnerability scanning times out on large dependency trees: run with depth limit (direct deps first, then top-level transitive)
- If license scanning tool misses uncommon licenses: manually check the package's LICENSE file or README
- If unused dependency detection produces false positives: verify by searching for the package name in source code, removing, and running tests
- If conflicting peer dependencies prevent updates: use overrides (npm: overrides, yarn: resolutions, dotnet: binding redirects) and document the decision
- If a dependency is abandoned but critical: fork and maintain internally, or find and migrate to an alternative
- If the organization does not have an approved license list: create one during this review based on legal team input

## Related SOPs
- `security-audit.md` — Vulnerability-focused dependency assessment
- `audit.md` — Full codebase audit (includes dependency overview)
- `performance-review.md` — Bundle size analysis (dependency weight impact)
- `release-audit.md` — Dependency checks as part of release readiness
- `code-review.md` — Review guidelines for new dependency additions in PRs
