# AI Agent Workflow SOP

> **Standard Operating Procedure** for AI agents executing tasks within the Project Intelligence Layer.
> **Version:** 1.0.0
> **Applies to:** All AI agents (code gen, review, analysis, testing, documentation)
> **Prerequisites:** AI Constitution compliance, task assignment with clear scope

---

## Overview

This document defines the standard operating procedure for AI agents from the moment a task is received to the moment the result is delivered. Every agent MUST follow these phases in order. Skipping phases or reordering them invalidates the workflow guarantee.

```
RECEIVE → EXPLORE → PLAN → IMPLEMENT → VERIFY → DOCUMENT → DELIVER
```

Each phase has defined quality gates. No phase is complete until its gates pass.

---

## PHASE 1: RECEIVE

**Purpose:** Fully understand what is being asked before any action is taken. This phase ensures the agent and the requester share a correct, complete, and unambiguous understanding of the task.

**Steps:**
1. **Parse task description.** Read the task input thoroughly. Identify: the problem to solve, the expected outcome, the affected system, the priority level, and any explicit constraints.
2. **Identify task type.** Categorize the task:
   - `feature` — new functionality
   - `bugfix` — defect resolution
   - `refactor` — structural improvement without behavior change
   - `docs` — documentation creation or update
   - `config` — configuration change
   - `test` — test creation or update
   - `research` — investigation without code change
3. **Identify scope boundaries.** Extract explicit scope inclusions and exclusions. If none are stated, infer from the task description and flag any ambiguity.
4. **Identify constraints.** Look for: deadline, environment constraints (OS, runtime version), compatibility requirements, performance targets, security requirements.
5. **Identify implicit prerequisites.** Check if the task depends on prior tasks, architectural decisions, or external dependencies that are not yet in place.
6. **Ask clarifying questions.** If the task has ANY ambiguity — incomplete acceptance criteria, unclear scope, missing constraints — raise a clarifying question before proceeding. Do NOT fill gaps with assumptions.
7. **Confirm readiness.** Summarize the parsed task back to the requester or log it in the task tracker. Proceed only after confirmation.

**Expected outputs:**
- Parsed task summary with type, scope, and constraints
- List of clarifying questions (if any) with answers
- Explicit statement of readiness to proceed

**Quality gates:**
- [ ] Task type is identified and explicitly stated
- [ ] Scope boundaries are documented
- [ ] All ambiguities are resolved (no open questions)
- [ ] Implicit dependencies are identified

---

## PHASE 2: EXPLORE

**Purpose:** Build a comprehensive mental model of the affected codebase, its structure, its conventions, and the specific code paths that the task touches. This phase prevents blind changes.

**Steps:**
1. **Navigate to the relevant code area.** Use the task scope to identify the target directory, module, or service.
2. **Read the primary file(s).** Read every file listed in the task scope in full.
3. **Trace imports and dependencies.** For each primary file, read all local imports (skip stdlib and third-party unless the change directly uses them). Build a dependency map.
4. **Read tests.** Read the existing tests for the affected module. Tests reveal expected behavior, edge cases, and design intent better than any other documentation.
5. **Read configuration files.** Read any configuration files that govern the affected module (`appsettings.json`, `.env`, `.yaml`, `Dockerfile`, etc.).
6. **Read documentation.** Read any README, ADR, API spec, or wiki page that relates to the task.
7. **Identify code conventions.** Note naming conventions, error handling style, design patterns, test patterns, and comment style used in the area.
8. **Identify risks.** Based on the code review, identify any risks the change might introduce (see Constitution Rule 5).
9. **Map workflows.** Identify user-facing workflows that touch the affected code (see Constitution Rule 4).

**Expected outputs:**
- Dependency map of affected files
- Summary of code conventions observed
- Risk assessment (initial)
- Workflow map
- Impact analysis (preliminary)

**Quality gates:**
- [ ] All primary files are read in full
- [ ] All local imports are read and understood
- [ ] Existing tests are read and understood
- [ ] Code conventions are identified and noted
- [ ] Risk assessment is started

---

## PHASE 3: PLAN

**Purpose:** Design the solution before writing any code. Planning surfaces tradeoffs, validates approaches, and creates the blueprint for implementation. This phase produces artifacts that enable review and rollback.

**Steps:**
1. **Design the solution.** Based on the exploration phase, design an approach that satisfies all acceptance criteria. Consider at least three alternatives (see Constitution Rule 25).
2. **Identify affected files.** Enumerate every file that will need to change: source code, tests, configuration, documentation, migration scripts.
3. **Document alternatives.** For each alternative considered, document: approach, pros, cons, and reason for rejection.
4. **Document risks.** Using the risk assessment from Phase 2, finalize the risk document. Include severity and mitigation for each risk.
5. **Create rollback plan.** For each change, define the rollback procedure (see Constitution Rule 6).
6. **Check for backward compatibility.** If the change breaks backward compatibility, design a migration plan (see Constitution Rule 23).
7. **Estimate effort.** Provide a rough estimate of files changed, lines added/modified/deleted, and test count.
8. **Submit plan for review.** If the task is significant (>5 files changed, or risk level > Medium), submit the plan for human review before implementation.

**Expected outputs:**
- Solution design document
- Alternatives analysis
- Risk assessment (final)
- Rollback plan
- Migration plan (if needed)
- Affected files list
- Effort estimate

**Quality gates:**
- [ ] At least two alternatives are documented with rejection reasons
- [ ] Rollback plan exists for every change
- [ ] Risk assessment is complete with mitigations
- [ ] Affected files list is exhaustive
- [ ] Migration plan exists if backward compatibility is broken
- [ ] Plan approved (if review is required)

---

## PHASE 4: IMPLEMENT

**Purpose:** Execute the planned changes surgically, with minimal deviation from the plan. Each change is a deliberate, verified operation.

**Steps:**
1. **Re-read the target file.** Before editing, read the target file again (even if read in Phase 2). Files may have changed or scrolling context may have been lost.
2. **Make one logical change at a time.** Do not batch multiple unrelated changes into a single edit. Each edit should address exactly one logical modification.
3. **Verify each change.** After each edit:
   - Re-read the modified region to confirm correctness.
   - Check that the code compiles (if possible).
   - Check that existing tests in the affected module still pass.
4. **Maintain code style.** Ensure all edits match the established style of the surrounding code (see Constitution Rule 13).
5. **Scope discipline.** Do NOT modify files outside the planned scope (see Constitution Rule 12).
6. **Commit discipline.** If using version control, commit each logical change with a descriptive message that references the task ID and explains what was changed and why.
7. **Treat warnings as errors.** Do not introduce new compiler warnings, linter warnings, or analyzer warnings.

**Expected outputs:**
- Modified source files
- Modified test files
- Modified configuration files
- Modified documentation files
- Migration scripts (if applicable)
- Commit history (if applicable)

**Quality gates:**
- [ ] Each change is verified independently
- [ ] Code matches surrounding style
- [ ] No files outside scope are modified
- [ ] No new warnings introduced
- [ ] Each logical change has a descriptive commit message

---

## PHASE 5: VERIFY

**Purpose:** Exhaustively verify that the change is correct, complete, and safe. This phase is the primary quality assurance gate before delivery.

**Steps:**
1. **Run the build.** Execute the project build command. Confirm zero errors, zero warnings.
2. **Run the linter.** Execute the linter with the strictest project configuration. Confirm zero violations.
3. **Run existing tests.** Execute the full existing test suite. Confirm zero regressions (see Constitution Rule 10).
4. **Write and run new tests.** For each new or changed behavior, write unit/integration tests. Run them and confirm all pass.
5. **Verify edge cases.** Check null, empty, boundary, and error states (see Constitution Rule 9).
6. **Verify acceptance criteria.** Walk through every acceptance criterion from the task definition and confirm each is met (see Constitution Rule 8).
7. **Verify security.** Perform security review (see Constitution Rule 19).
8. **Verify performance.** Assess performance impact (see Constitution Rule 20).
9. **Verify regression.** Confirm that existing behavior is preserved (see Constitution Rule 10).
10. **Verify database migrations.** If migrations exist, test both `up` and `down` (see Constitution Rule 24).
11. **Verify documentation.** Confirm documentation is updated and accurate (see Constitution Rule 7).

**Expected outputs:**
- Build output (success)
- Lint output (zero violations)
- Test results (all pass)
- Security review findings
- Performance assessment
- Acceptance criteria verification matrix
- Migration test results

**Quality gates:**
- [ ] Build passes with zero errors and zero warnings
- [ ] Lint passes with zero violations
- [ ] All existing tests pass (zero regressions)
- [ ] New tests pass and cover acceptance criteria
- [ ] Edge cases are verified
- [ ] Security review completed with no unresolved findings
- [ ] Performance assessment completed with no regressions
- [ ] Migration `up` and `down` tested successfully

---

## PHASE 6: DOCUMENT

**Purpose:** Ensure that all knowledge generated during the task is captured in permanent, findable form. Documentation is the bridge between this task and all future work.

**Steps:**
1. **Update changelog.** Add an entry to `CHANGELOG.md` (see Constitution Rule 15).
2. **Update README / user docs.** If the change affects user-facing behavior, update the relevant documentation.
3. **Update API specs.** If the change affects an API endpoint, update OpenAPI/Swagger specs.
4. **Update ADRs.** If the change represents or implies an architectural decision, create or update an ADR.
5. **Document configuration changes.** If configuration values are added or changed, update the config reference documentation.
6. **Update the task plan.** If the plan diverged from the original during implementation, update the plan document to reflect reality.
7. **Create handoff summary (if session > 1 hour).** Write a handoff document covering completed items, pending items, decisions, risks, and open questions (see Constitution Rule 16).

**Expected outputs:**
- Updated `CHANGELOG.md`
- Updated user documentation
- Updated API specifications
- Updated or new ADRs
- Updated configuration documentation
- Handoff summary (if applicable)

**Quality gates:**
- [ ] Changelog entry is present and follows format
- [ ] User-facing docs are updated and accurate
- [ ] API specs are updated (if API changed)
- [ ] ADR exists for any architectural decisions
- [ ] Config docs are updated (if config changed)
- [ ] Handoff summary exists (if session > 1 hour)

---

## PHASE 7: DELIVER

**Purpose:** Present the completed work to the requester or system in a clear, complete, and actionable format. The delivery should enable immediate use, review, or further action.

**Steps:**
1. **Summarize what was done.** One-paragraph description of the implemented change, referencing the task ID.
2. **Summarize what was learned.** Any insights, surprises, or discoveries made during implementation that are relevant to future work.
3. **Summarize what remains.** Any follow-up tasks, deferred work, or known limitations.
4. **Provide artifact locations.** File paths, commit hashes, PR numbers, or links to all created or modified artifacts.
5. **Provide verification evidence.** Test results, build outputs, lint results — link to or attach the output logs.
6. **Provide rollback instructions.** Concise rollback procedure for operators.
7. **Confirm all quality gates passed.** Explicit statement confirming each phase's quality gates are met.
8. **Hand off.** Mark the task as complete in the task tracker. Attach all artifacts.

**Expected outputs:**
- Delivery summary (what was done, learned, remains)
- Artifact locations
- Verification evidence
- Rollback instructions
- Quality gate confirmation

**Quality gates:**
- [ ] Delivery summary is complete and clear
- [ ] All artifact locations are provided
- [ ] Verification evidence is attached
- [ ] Rollback instructions are included
- [ ] All Phase 1-7 quality gates are confirmed passing
- [ ] Task is marked complete

---

## Workflow Diagram

```
                    ┌─────────────┐
                    │  RECEIVE    │
                    │  (clarify)  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  EXPLORE    │
                    │  (read all) │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   PLAN      │
                    │  (design)   │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐  ┌─────▼──────┐  ┌─────▼──────┐
    │ IMPLEMENT   │  │  VERIFY    │  │ DOCUMENT   │
    │ (change)    │◄─┤ (quality)  │◄─┤ (record)   │
    └──────┬──────┘  └─────┬──────┘  └─────┬──────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                    ┌──────▼──────┐
                    │  DELIVER    │
                    │  (handoff)  │
                    └─────────────┘
```

## Quality Gate Summary Table

| Phase     | Gate                                                         |
|-----------|--------------------------------------------------------------|
| RECEIVE   | Task parsed, scope clear, no ambiguities                     |
| EXPLORE   | All files read, dependencies mapped, conventions noted       |
| PLAN      | Alternatives analyzed, risks assessed, rollback planned      |
| IMPLEMENT | Surgical changes, style matched, scope respected             |
| VERIFY    | Build/lint/tests pass, security/perf reviewed, criteria met  |
| DOCUMENT  | Changelog/docs/ADRs updated, handoff written                 |
| DELIVER   | Summary complete, evidence attached, task closed             |

---

## Exception Handling

If any phase gate fails:
1. **Record the failure.** Document what gate failed and why.
2. **Return to the appropriate phase.** Do NOT skip forward to delivery.
   - Failed RECEIVE gate → return to Phase 1
   - Failed EXPLORE gate → return to Phase 2
   - Failed PLAN gate → return to Phase 3
   - Failed IMPLEMENT gate → return to Phase 4
   - Failed VERIFY gate → return to Phase 4 or Phase 5 depending on cause
   - Failed DOCUMENT gate → return to Phase 6
   - Failed DELIVER gate → return to Phase 7
3. **Address the root cause.** Fix the underlying issue, not the symptom.
4. **Re-verify.** Re-run the gate that failed before proceeding.

---

## Appendix: Quick Reference Card

```
1. RECEIVE  → "Do I understand exactly what to do?"
2. EXPLORE  → "Have I read everything I need to read?"
3. PLAN     → "Is my solution designed, analyzed, and reviewed?"
4. IMPLEMENT→ "Is each change correct, scoped, and styled?"
5. VERIFY   → "Does everything still work? Is it complete?"
6. DOCUMENT → "Is everything recorded for the future?"
7. DELIVER  → "Is the result presented clearly and completely?"
```
