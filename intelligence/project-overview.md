# Project Overview

## Vision
To become the definitive platform that empowers cross-functional teams to ship high-quality software with measurable confidence by consolidating institutional knowledge, enforcing consistency, and eliminating tribal knowledge dependencies.

## Mission
Provide a living intelligence layer that captures, connects, and surfaces every critical artifact — architecture decisions, business rules, bug history, workflow maps, API contracts, and database schemas — so that any team member or AI agent can onboard, contribute, and audit with full context in minutes instead of weeks.

## Problem Statement
Software teams lose 30-50% of their velocity to knowledge fragmentation. Requirements live in Jira. Architecture decisions vanish after Slack threads. Business rules are buried in test cases. Bug fixes get forgotten. Onboarding takes months. AI agents hallucinate because they lack grounded context. This project solves all of that with a single, maintainable, version-controlled intelligence layer.

## Target Users
1. **Software Engineers** — need to understand architecture, find relevant code, and avoid breaking business rules.
2. **AI Coding Agents** — need grounded context to generate correct, consistent code that respects existing decisions.
3. **Technical Leads** — need to enforce architectural decisions and track technical debt.
4. **Product Managers** — need to verify that features align with business rules and domain concepts.
5. **QA Engineers** — need to understand failure patterns and verify bug fixes.
6. **DevOps Engineers** — need deployment workflows and infrastructure context.
7. **New Hires** — need accelerated onboarding through comprehensive documentation.

## Core Features
1. **Project Overview** — executive summary with vision, metrics, and status.
2. **Architecture Documentation** — system context, patterns, technology decisions, module boundaries.
3. **Business Rules Catalog** — every rule with ID, description, category, enforcement point, last verified.
4. **Domain Knowledge Base** — entities, relationships, terminology, mental model of the business domain.
5. **Workflow Maps** — all workflows with triggers, steps, outputs, failure points.
6. **Decision Log** — all Architecture Decision Records in chronological order.
7. **Technical Debt Registry** — each debt item with area, description, cost, effort, priority.
8. **Failure Documentation** — post-mortems with root cause, symptoms, fix, prevention.
9. **Bug Tracker** — known bugs with severity, workaround, fix ETA.
10. **Feature Catalog** — every feature with files, dependencies, APIs, DB objects, tests.
11. **API Catalog** — every endpoint with method, path, auth, request, response, errors.
12. **Database Catalog** — every object with columns, relationships, indexes.

## Key Metrics
1. **Coverage** — % of codebase entities documented in the intelligence layer.
2. **Freshness** — average days since each document was last verified.
3. **Adoption** — number of PRs that reference intelligence-layer documents.
4. **Onboarding Time** — days for a new engineer to ship their first PR.
5. **Bug Recurrence Rate** — % of bugs that are regressions of previously fixed issues.
6. **Decision Compliance** — % of code changes that respect documented ADRs.
7. **Agent Accuracy** — correctness rate of AI-generated code when grounded against this layer.

## Current Status
- **Phase**: Initial creation of all catalog files.
- **Completion**: 0% — all documents are stubs awaiting population.
- **Next Milestone**: Populate all 17 documents with real project data.
- **Owner**: Platform / Infrastructure team.
- **Repository**: project-intelligence-layer (this directory).

## File Inventory
| # | File | Purpose | Lines | Status |
|---|------|---------|-------|--------|
| 1 | intelligence/project-overview.md | Executive summary | 100+ | Created |
| 2 | intelligence/architecture.md | System architecture | 100+ | Created |
| 3 | intelligence/business-rules.md | Business rules catalog | 100+ | Created |
| 4 | intelligence/domain-knowledge.md | Domain concepts | 100+ | Created |
| 5 | intelligence/workflow-map.md | Workflow maps | 100+ | Created |
| 6 | intelligence/decision-log.md | Architecture decisions | 100+ | Created |
| 7 | intelligence/technical-debt.md | Technical debt items | 100+ | Created |
| 8 | intelligence/known-failures.md | Documented failures | 100+ | Created |
| 9 | intelligence/known-bugs.md | Known bugs | 100+ | Created |
| 10 | intelligence/feature-catalog.md | Feature registry | 100+ | Created |
| 11 | intelligence/api-catalog.md | API endpoints | 100+ | Created |
| 12 | intelligence/database-catalog.md | Database objects | 100+ | Created |
| 13 | daily-checklist.md | Daily agent tasks | 80+ | Created |
| 14 | weekly-checklist.md | Weekly agent tasks | 80+ | Created |
| 15 | monthly-checklist.md | Monthly agent tasks | 80+ | Created |
| 16 | pre-release-checklist.md | Pre-release tasks | 80+ | Created |
| 17 | post-release-checklist.md | Post-release tasks | 80+ | Created |

## Maintenance Guidelines
1. Every document must be updated when its subject matter changes.
2. PRs that modify code must include intelligence-layer updates where applicable.
3. Automated CI checks should verify coverage and freshness.
4. AI agents MUST read relevant intelligence documents before generating code.
5. Documents should be reviewed quarterly for accuracy.
