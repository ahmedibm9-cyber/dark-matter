# SOP: Documentation Review
Last Updated: 2026-06-25
Owner: Technical Writer / Tech Lead

## Purpose
Evaluate the completeness, accuracy, freshness, and usability of all project documentation. This SOP ensures that documentation serves its intended audience effectively, remains synchronized with the codebase, follows consistent formatting, and covers all critical aspects of the project including setup, usage, architecture, deployment, and contribution guidelines.

## When to Execute
- Before a public release or open-sourcing the project
- When onboarding new team members reveals documentation gaps
- After significant architectural or API changes
- Quarterly as part of ongoing documentation maintenance
- When users or contributors report documentation issues
- As part of the audit process before major milestones

## Required Inputs
- Repository access (all branches and tags)
- List of all documentation files (README, docs/, wiki pages)
- API specification files (OpenAPI/Swagger, GraphQL schema)
- Architecture Decision Records (ADRs)
- Project setup and configuration files
- CI/CD pipeline and deployment configuration
- User feedback on documentation (issues, comments, surveys)
- Previous documentation review reports

## Prerequisites
- Markdown linter (markdownlint, or similar)
- Spell checker (aspell, codespell, or IDE plugin)
- Link checker (broken-link-checker, muffet, or similar)
- API documentation viewer (Swagger UI, Stoplight, GraphQL Playground)
- README template or project documentation standard
- Access to wiki or external documentation platforms

## Procedure

### Step 1: Documentation Inventory
Catalog all documentation assets and their locations.
- Find all documentation files:
```
Get-ChildItem -Recurse -Filter "*.md"
Get-ChildItem -Recurse -Filter "*.rst"
Get-ChildItem -Recurse -Include "*.pdf", "*.docx" -ErrorAction SilentlyContinue
```
- Categorize each document into: README, Setup guides, API documentation, Architecture docs, Development guides, Deployment docs, Testing docs, Operations docs, User guides, Changelog.
- Coverage assessment: which categories are present? Score 1 point per category. Target: all 10 categories should have at least one document.
- Create a documentation map: file path -> category -> intended audience -> last updated.

### Step 2: README Audit
Evaluate the project's primary README for completeness.
- Required README sections checklist:
  - Project name and description (what problem does it solve?)
  - Badges (CI status, coverage, version, license)
  - Prerequisites (required tools, versions, accounts)
  - Installation instructions (step-by-step, copy-paste commands)
  - Quick start / Getting started (minimal working example)
  - Usage examples (common scenarios, code snippets)
  - Configuration (environment variables, config files)
  - Project structure overview (high-level directory map)
  - API documentation link or embedded reference
  - Testing instructions (how to run tests)
  - Deployment instructions or link to deployment docs
  - Contributing guidelines or link to CONTRIBUTING.md
  - License information
  - Contact / support information
  - Acknowledgments (if applicable)
- README quality scoring: 1 point per present section (max 15), 1 point per accurate non-outdated example, 1 point for formatting and readability. Target: >14 for good, >10 for acceptable.
- Common README issues: outdated installation steps, placeholder text (TODO, Coming soon), missing or broken badges, no code examples or examples that don't compile, setup instructions that don't work on clean machines.

### Step 3: API Documentation Audit
Verify API documentation completeness and accuracy.
- OpenAPI/Swagger validation: `npx swagger-cli validate openapi.yaml`
- Cross-reference code routes against documented endpoints:
```
Select-String -Pattern "\[HttpGet|\[HttpPost|\[HttpPut|\[HttpDelete|app\.(get|post|put|delete)" -Path *.cs, *.js -Recurse
```
- Verify each endpoint has: summary and description, request parameters with types and constraints, response schemas for all status codes (200, 201, 400, 401, 403, 404, 500), authentication requirements documented, example request/response payloads.
- Flag undocumented endpoints (code has it, spec doesn't).
- Flag documented endpoints that don't exist in code (spec has it, code doesn't).
- Check for: consistent error response schemas across endpoints, enum values documented, rate limits documented, deprecation notices present for deprecated endpoints.
- If client SDKs exist, verify their docs match the current API version.

### Step 4: Architecture Documentation Review
Evaluate architecture documentation for accuracy and completeness.
- Architecture Decision Records (ADRs) audit:
  - List all ADRs: `Get-ChildItem -Recurse -Filter "*adr*" -or "*decision*"`
  - For each ADR, verify it contains: title and status (proposed, accepted, deprecated, superseded), context (why was this decision needed?), decision (what was decided?), consequences (what are the trade-offs?), date and author.
  - Check that ADR statuses are accurate. Check for superseded ADRs that reference the superseding ADR.
- Architecture diagrams audit:
  - Verify diagrams exist (C4, UML, or equivalent).
  - Check diagrams match current code structure: are all services/containers shown? Are component boundaries accurate? Are data flows correctly represented?
  - Check that diagram source files (PlantUML, Mermaid, draw.io) are in version control.
- System documentation audit:
  - Does the architecture doc explain the high-level system design?
  - Are technology choices documented with rationale?
  - Are integration points with external systems documented?
  - Are security boundaries and trust zones documented?

### Step 5: Setup and Onboarding Guide Verification
Test the setup guide by following it step by step on a clean machine.
- Fresh environment setup test:
  - Start with a clean machine (VM or container).
  - Follow the setup guide exactly as written.
  - Record any deviation from the documented steps.
  - Record any missing prerequisites or steps.
  - Record any commands that fail or produce different output.
- Setup guide checklist:
  - Prerequisites are complete and version-specific.
  - Clone/download instructions are clear.
  - Dependencies install without errors.
  - Configuration steps are complete (env vars, config files).
  - Database setup is automated or clearly documented.
  - Application starts without errors.
  - Sample/smoke test verifies the app is running.
  - Troubleshooting section covers common issues.
  - Links to additional resources work.
- Onboarding time measurement: how long does it take a new developer to get a running environment? Target: <30 minutes for basic setup, <2 hours for full local environment.

### Step 6: Deployment Documentation Audit
Verify deployment documentation is current and accurate.
- Deployment runbook audit:
  - Verify the runbook contains: prerequisites (permissions, tools, access), environment-specific configuration, step-by-step deployment sequence, expected output at each step, health check commands after each step, rollback procedure with exact commands, post-deployment verification steps.
  - Cross-reference with actual CI/CD pipeline: do pipeline steps match runbook steps? Are manual gates documented where they exist? Are scripts referenced in the runbook still in the repo?
- Environment documentation:
  - Are all environments documented (dev, staging, production, DR)?
  - Does each environment have: URL, access instructions, configuration differences?
  - Are environment-specific secrets documented (where they live, not the actual values)?
  - Is infrastructure topology documented (load balancers, databases, caches)?
- Disaster recovery documentation:
  - Is the DR plan documented? Are RTO and RPO targets documented?
  - Were recovery steps tested and verified within the last quarter?

### Step 7: Code Documentation Quality Review
Evaluate inline code documentation quality.
- Public API documentation coverage:
  - Verify all public methods, classes, and interfaces have XML doc comments / JSDoc / docstrings.
  - For each documented item, check: summary describes what (not how), parameters described with purpose and valid ranges, returns described with success and failure conditions, exceptions documented.
  - Flag undocumented public APIs using automated scanning.
- Code comment quality assessment:
  - Good comments explain WHY (business logic rationale, non-obvious decisions).
  - Bad comments explain WHAT (code should be self-documenting).
  - Ugly: outdated comments that contradict the code.
  - Check for commented-out code (should be deleted, not commented).
  - Check for stale TODO/FIXME/HACK comments:
```
Select-String -Pattern "TODO|FIXME|HACK|XXX|BUG" -Path *.cs, *.js, *.ts, *.py -Recurse
```
- Documentation generation: if using DocFX, JSDoc, Sphinx, verify the generation command still works, the output is complete, and it's hosted/accessible.

### Step 8: Freshness and Maintenance Check
Audit documentation for recency and maintenance processes.
- Freshness measurement: for each .md file, check the last modified date via git:
```
git log -1 --format="%ci" -- docs/filename.md
```
- Flag files older than 6 months as stale. Flag files older than 12 months as abandoned.
- Check if documents reference deprecated features, old URLs, or EOL versions.
- Evaluate maintenance process: are documentation-only commits happening regularly? Do PRs include documentation updates for code changes? Is there a documentation review checklist in the PR template? Is documentation debt tracked in the backlog?
- Link rot check:
```
npx broken-link-checker --recursive --ordered https://docs-site.com
npx markdown-link-check **/*.md
```
- Flag all broken internal and external links. Flag redirected URLs (should update to direct URL).
- Versioning check: are docs versioned with the code? Is there a mechanism to view docs for older versions? Are migration guides present for breaking changes?

### Step 9: Formatting and Style Compliance
Check documentation for consistent formatting and style guide adherence.
- Markdown linting:
```
npx markdownlint-cli 'docs/**/*.md' --config .markdownlint.json
```
- Check for: consistent heading structure (no jumps from h1 to h3), proper list formatting (consistent indentation, ordered vs. unordered), code blocks with language specifiers, proper table formatting (alignment, separators), no trailing spaces, no missing newlines at end of files.
- Spelling and grammar:
```
npx spellchecker-cli 'docs/**/*.md' --dictionary dictionary.txt
```
- Check for: technical term consistency (microservice vs micro-service everywhere), consistent terminology (don't use API and endpoint interchangeably in the same doc), acronyms defined on first use.
- Style guide compliance: does the project have a documentation style guide? If yes, verify compliance with random sampling of 5 docs. If no, recommend adopting one (Google Developer Documentation Style Guide, Microsoft Style Guide).

### Step 10: Report Generation and Improvement Plan
Compile all findings into a structured report.
- Documentation health score across weighted dimensions:
  - Coverage (all categories present): 20%
  - README quality score: 15%
  - API doc completeness: 20%
  - Architecture doc accuracy: 15%
  - Freshness (docs updated within 6 months): 15%
  - Formatting and style compliance: 10%
  - Setup guide verifiability: 5%
- Findings by severity:
  - Critical (blocking): missing README, no API docs, setup guide doesn't work, incorrect deployment docs
  - High (breaking): outdated architecture docs, no ADRs, stale setup instructions, broken links in critical docs
  - Medium (improving): incomplete API docs, formatting issues, missing diagrams, inconsistent terminology
  - Low (polish): spelling errors, minor formatting, old but not harmful docs
- Improvement roadmap:
  - Immediate: fix setup guide, update deployment docs, fix critical broken links
  - Short-term: complete API docs, add missing ADRs, update stale docs
  - Medium-term: establish documentation review process, add style guide, automate link checking
  - Long-term: version documentation, auto-generate API docs, implement docs-as-code
- Save report as `documentation-review-YYYY-MM-DD.md`.

## Verification Steps
- README score is measured and documented (target >14/17)
- Setup guide is followed step-by-step on a clean machine and works completely
- API documentation covers all endpoints in the code (zero undocumented public endpoints)
- Architecture documentation accurately reflects the current codebase structure
- Link checker identifies zero broken links (or all known broken links are documented)
- Documentation freshness is measured with clear stale/abandoned counts

## Expected Deliverables
- `documentation-review-YYYY-MM-DD.md` — comprehensive documentation review report
- Documentation health scorecard with dimension breakdown
- Broken link inventory (if any)
- Stale/outdated documentation inventory with age
- Setup guide verification results (what worked, what didn't)
- Improvement roadmap with prioritized actions

## Success Criteria
- All documentation categories are assessed and scored
- README meets the target score (>14/17)
- All API endpoints are documented (zero undocumented public endpoints)
- Setup guide is verified working on a clean machine
- Broken links are identified and documented for repair
- Documentation health score is calculated and baseline established
- Improvement plan has prioritized, actionable items with effort estimates

## Failure Recovery
- If there are too many documentation files to review individually: stratified sampling by category (2-3 files per category)
- If setup guide testing is too time-consuming: focus on critical path (install, configure, run), document gaps for other steps
- If API documentation is auto-generated: verify the generation tool is configured correctly and the output is complete
- If link checker returns too many false positives: create a whitelist of known-unreachable-but-acceptable URLs
- If team does not have a documentation culture: focus recommendations on process changes (PR checklist, doc review) not just content fixes

## Related SOPs
- `audit.md` — Documentation assessment within full codebase audit
- `code-review.md` — Documentation standards enforced in code review
- `architecture-review.md` — Architecture documentation alignment
- `deployment-review.md` — Deployment documentation accuracy
- `release-audit.md` — Release notes and changelog review
