# AI Agent Performance Optimization

> Deep analysis of what degrades AI agent performance and how to fix it.
> Covers context loss, hallucination, inconsistent code generation, and incomplete implementations.

---

## Context Loss Root Causes

### 1. Long Conversations Without Summaries

- **Root Cause:** AI conversations accumulate tokens. At ~8K tokens, the oldest messages start being truncated. At ~16K, significant context is lost. Without summaries, the AI forgets earlier decisions, task goals, and explored alternatives.
- **Impact:** High — causes rework, inconsistent decisions, wasted time re-exploring.
- **Current Defense:** None. Context is allowed to grow until failure.
- **Improved Defense:** Implement rolling summaries every 10 messages. Each summary captures: decisions made, files changed, current task status, next steps. Summaries are themselves summarized when exceeding 5.
- **Implementation:**
  1. Create summary template with required sections
  2. After every 10 AI messages, generate summary in `.opencode/memory/checkpoints/`
  3. After 5 checkpoints, summarize the summaries
  4. On session start, load latest summary + checkpoint files
  5. AI reads summary before any tool use

### 2. Missing Reference Documents

- **Root Cause:** The AI doesn't know which documents exist or where to find them. When it needs architecture context, API docs, or coding standards, it either doesn't look or wastes time searching.
- **Impact:** High — leads to incorrect assumptions, non-standard code, architectural drift.
- **Current Defense:** Ad-hoc reading of docs when the user remembers to request it.
- **Improved Defense:** Create a `docs/quick-reference/` directory with one-page summaries of all key documents. Each summary includes: exact file path, key information, common commands, and cross-references.
- **Implementation:**
  1. Audit all project documents and identify knowledge domains
  2. Create one quick-reference file per domain (< 50 lines each)
  3. Create `INDEX.md` with domain-to-file mapping
  4. AI loads relevant quick-reference based on task type
  5. Quick-refs are maintained as part of documentation updates

### 3. Scattered Context

- **Root Cause:** Information about the current project state is spread across multiple files: git status shows files, terminal shows last command, error messages are in the scrollback, the task description is in the prompt. The AI must piece together a complete picture from fragments.
- **Impact:** High — the AI makes decisions based on incomplete information.
- **Current Defense:** None. The AI must manually gather context from multiple sources.
- **Improved Defense:** Create a single "current state" document at `current-state.md` that gets overwritten each session. Contains: active branch, changed files, recent errors, last command, next task.
- **Implementation:**
  1. Create `current-state.md` with structured sections
  2. Update before every significant action (run command, edit file)
  3. AI reads this first on session start
  4. AI updates it as state changes
  5. Keep under 30 lines

### 4. No Checkpoints

- **Root Cause:** When a session ends (due to context limit, crash, or manual stop), all in-progress work context is lost. The next session starts from zero, requiring re-exploration of the same space.
- **Impact:** Medium — significant rework, frustration, lost time.
- **Current Defense:** None. Sessions are isolated with no memory.
- **Improved Defense:** Create milestone summary files at key points: task start, task completion, and every 15 minutes of active work. Store in `.opencode/memory/checkpoints/`.
- **Implementation:**
  1. Define checkpoint data structure (task, progress, decisions, blockers)
  2. After each completed subtask, write a checkpoint
  3. After every 15 min of work, auto-write checkpoint
  4. On session resume, load latest checkpoint
  5. Prune checkpoints older than 30 days

### 5. No Handoff Protocol

- **Root Cause:** When work moves between AI agents or sessions, there's no structured handoff. The receiving agent has no idea what was done, what was decided, or what comes next.
- **Impact:** High — causes duplicate work, contradictory decisions, broken implementations.
- **Current Defense:** Manual handoff via copy-paste by the user.
- **Improved Defense:** Implement agent-handoff-template.md with required sections: context, decisions, completed work, pending items, known issues, file changes. Agents are trained to emit handoffs when context exceeds 80% of limit.
- **Implementation:**
  1. Create handoff template at `docs/agent-handoff-template.md`
  2. Create `handoff.sh` script that generates a handoff file
  3. Train AI to use handoff protocol proactively
  4. Store in `.opencode/handoffs/` with timestamps
  5. Validate handoff completeness with a schema check

---

## Hallucination Root Causes

### 1. Assuming Instead of Verifying

- **Root Cause:** AI generates code or makes statements based on what it *thinks* the codebase contains, rather than reading the actual files. This is the #1 source of hallucination.
- **Impact:** Critical — generates broken code, incorrect documentation, bad decisions.
- **Current Defense:** None. AI is not required to read before writing.
- **Improved Defense:** Mandatory "read first, then write" policy. Before any edit, the AI must read the file. Implement a pre-write hook that checks if the target file was read in the last 5 messages.
- **Implementation:**
  1. Add to task template: "Read relevant files first"
  2. Create pre-write validation hook
  3. Log violations for review
  4. Update AI instructions to emphasize this rule
  5. Track compliance rate over time

### 2. Missing Ground Truth

- **Root Cause:** The AI is asked to verify something but isn't given the exact command to run and expected output. It guesses whether something works.
- **Impact:** High — false confidence in broken implementations.
- **Current Defense:** Ad-hoc by the user if they remember to provide exact commands.
- **Improved Defense:** Every task must include: exact commands to run for verification, expected output (or output pattern), and what constitutes success/failure.
- **Implementation:**
  1. Add "Verification Commands" section to all task templates
  2. Specify: command, expected output, pass/fail criteria
  3. AI runs verification before marking task complete
  4. Log verification results for audit
  5. Failed verifications trigger task reassessment

### 3. Ambiguous Requirements

- **Root Cause:** The task description is vague: "improve error handling" without specifying which errors, "add tests" without specifying which cases. The AI fills gaps with assumptions.
- **Impact:** High — generates incorrect or incomplete implementations.
- **Current Defense:** User clarifies via follow-up messages (wasteful).
- **Improved Defense:** Use structured task templates with explicit sections: objective, inputs, acceptance criteria, non-goals. Every requirement must be specific and testable.
- **Implementation:**
  1. Design task template with ambiguity-reducing fields
  2. Create `tasks/templates/` with templates per task type
  3. AI fills template at task start, user reviews
  4. Requirements must include measurable success criteria
  5. Non-goals are explicitly stated to prevent scope creep

### 4. Outdated Knowledge

- **Root Cause:** The AI has a knowledge cutoff and doesn't know about API changes, library updates, or new patterns. It generates code using old APIs or patterns that don't exist anymore.
- **Impact:** Medium — generates code that uses deprecated APIs, fails to compile.
- **Current Defense:** The user corrects the AI mid-conversation (wasteful).
- **Improved Defense:** Pin all dependency versions in lock files. Create `docs/api-changes.md` that tracks all API changes with dates. AI reads this before touching any dependency.
- **Implementation:**
  1. Pin all dependency versions in lock files
  2. Create API change log document
  3. Add version-aware prompts: "Using v2.3.1 of library X"
  4. CI check for unpinned dependencies
  5. Update API change log as part of PR process

### 5. Pattern Hallucination

- **Root Cause:** The AI generates code using patterns that it knows from training data but that don't exist in the project. The resulting code doesn't match the project's conventions.
- **Impact:** Medium — generates code that doesn't fit the codebase, requires rework.
- **Current Defense:** Code review catches it, but requires rework.
- **Improved Defense:** Provide exact code examples from the codebase. Create a pattern library with real examples. AI must reference it before generating new code.
- **Implementation:**
  1. Identify top 15 recurring patterns in the codebase
  2. Document each with intent, structure, and codebase example
  3. Store in `docs/patterns/`
  4. AI reads relevant pattern before generating similar code
  5. New patterns discovered during review are added to the library

---

## Inconsistent Code Generation

### 1. No Style Guide Reference

- **Root Cause:** AI generates code in whatever style it "thinks" is correct, which may not match the project's established style (naming, file structure, imports, formatting).
- **Impact:** Medium — inconsistent code, increased review burden.
- **Current Defense:** Linters catch some issues, but many style problems pass lint.
- **Improved Defense:** AI must read `docs/coding-standards.md` before generating any code. The guide must include: naming conventions, file organization, import style, error handling patterns, test conventions.
- **Implementation:**
  1. Create comprehensive coding standards document
  2. Include exact code examples from the codebase
  3. Cover all languages/frameworks used
  4. AI reads before first code generation in each session
  5. Review and update quarterly

### 2. No Pattern Library

- **Root Cause:** Without documented patterns, the AI invents its own solutions for common problems. These solutions vary in quality and consistency.
- **Impact:** Medium — inconsistent implementations, varying quality.
- **Current Defense:** Code review catches major issues.
- **Improved Defense:** Create a pattern library documenting recurring solutions with codebase examples. Include: when to use, when not to use, trade-offs.
- **Implementation:**
  1. Document 15+ patterns with codebase examples
  2. Organize by category (architectural, design, testing, error handling)
  3. AI reads relevant pattern before implementing
  4. Patterns are reviewed and added during code review
  5. Outdated patterns are deprecated explicitly

### 3. No Context About Existing Code

- **Root Cause:** The AI is told "edit service.ts" but isn't shown the file contents. It generates code based on assumptions about what the file contains.
- **Impact:** High — generates code that doesn't integrate with existing code.
- **Current Defense:** User provides file excerpts manually (inconsistent).
- **Improved Defense:** Always provide file excerpts (not just paths) when asking AI to work on files. Auto-gather script provides excerpts for recently changed files.
- **Implementation:**
  1. AI reads target files before editing (enforced)
  2. Context gathering script includes file excerpts
  3. For PRs: provide diff + surrounding context
  4. For new files: provide similar existing files as reference
  5. AI summarizes what it read to confirm understanding

### 4. Task Too Large

- **Root Cause:** Large tasks exceed the AI's ability to plan and execute coherently. The AI loses track of what's been done, what remains, and how pieces fit together.
- **Impact:** High — incomplete implementations, integration issues, quality degradation.
- **Current Defense:** User splits tasks manually (if they remember).
- **Improved Defense:** Break large tasks into smaller, verifiable steps. Each step has: objective, files to touch, verification criteria. Steps are executed sequentially with checkpoints.
- **Implementation:**
  1. AI analyzes task and proposes sub-tasks
  2. Each sub-task is independently verifiable
  3. Sub-tasks are executed in order with dependency tracking
  4. After each sub-task: verify, checkpoint, summarize
  5. If a sub-task fails, it's re-planned before proceeding

### 5. No Verification Criteria

- **Root Cause:** Tasks lack success criteria. The AI doesn't know when it's done or what "done" looks like. It stops when it thinks the task is complete, often prematurely.
- **Impact:** High — incomplete implementations, iterations, rework.
- **Current Defense:** User reviews and requests fixes (slow).
- **Improved Defense:** Every task must define success criteria upfront. Criteria must be: specific (what exactly should work), measurable (how to verify), testable (can be checked automatically).
- **Implementation:**
  1. Add "Success Criteria" as mandatory task template section
  2. Each criterion is a single sentence with verification method
  3. AI checks off criteria as they're met
  4. All criteria must be met before task is complete
  5. Track criteria pass rate over time

---

## Incomplete Implementations

### 1. Missing Edge Cases

- **Root Cause:** AI implements the happy path but ignores edge cases: empty states, boundary values, concurrent access, network failures, rate limits, etc.
- **Impact:** High — production bugs, emergency fixes.
- **Current Defense:** Code review catches some edge cases.
- **Improved Defense:** Edge case checklist in `verification-engine.md`. AI reads checklist and addresses each item before completing implementation.
- **Implementation:**
  1. Compile 20+ edge cases from past bugs
  2. Categorize: input, state, concurrency, boundary, error, security
  3. Embed checklist in verification engine doc
  4. AI checks off each item with code or explanation
  5. New edge cases discovered are added to checklist

### 2. Missing Error Handling

- **Root Cause:** AI generates code that assumes success: no try/catch, no error propagation, no user-facing error messages, no recovery strategies.
- **Impact:** High — crashes, poor user experience, silent failures.
- **Current Defense:** Code review catches some, but many slip through.
- **Improved Defense:** Error handling template and requirements in coding standards. AI must include error handling in every code generation. Validate with grep-based CI checks.
- **Implementation:**
  1. Document error handling patterns per layer
  2. Create error handling template (try, catch, log, recover, report)
  3. Add error handling to task template requirements
  4. CI checks for common error handling patterns
  5. Track error handling coverage per module

### 3. Missing Tests

- **Root Cause:** Test generation is seen as optional or separate from implementation. AI completes the code and stops without creating tests.
- **Impact:** High — untested code, regression risk, coverage degradation.
- **Current Defense:** PR review requires tests (if the reviewer checks).
- **Improved Defense:** Test requirements in task template. AI must generate tests as part of implementation. CI validates test requirements are met.
- **Implementation:**
  1. Add "Test Requirements" to task template (types, coverage, scenarios)
  2. AI generates tests matching existing patterns
  3. CI runs tests and validates coverage thresholds
  4. Missing tests block PR merge
  5. Track test coverage per module

### 4. Missing Documentation

- **Root Cause:** Documentation is treated as a separate activity. AI finishes code and doesn't update README, API docs, changelog, or inline comments.
- **Impact:** Medium — stale documentation, knowledge loss, onboarding friction.
- **Current Defense:** Manual documentation updates (often forgotten).
- **Improved Defense:** Documentation requirements in task template. AI updates docs as part of implementation. CI checks for doc changes matching code changes.
- **Implementation:**
  1. Add "Documentation Requirements" to task template
  2. AI updates relevant docs during implementation
  3. CI validates docs are updated when code changes
  4. Track documentation freshness score
  5. Documentation debt is tracked and reviewed monthly

### 5. Missing Security Considerations

- **Root Cause:** Security is not top-of-mind during implementation. AI generates code with: missing input validation, hardcoded secrets, insufficient authorization, data exposure.
- **Impact:** Critical — security vulnerabilities, compliance violations.
- **Current Defense:** Security review (if any) happens late in the process.
- **Improved Defense:** Security checklist in task template. AI addresses each item during implementation. Security scanning in CI catches what slips through.
- **Implementation:**
  1. Create security checklist: input validation, auth, data exposure, injection, secrets
  2. Embed in every task template
  3. AI checks off each item with code or explanation
  4. CI runs SAST scanning
  5. Security exceptions require documented approval

---

## System-Level Recommendations

### Monitoring and Metrics

Track the following metrics to measure AI performance improvement over time:
- **Context Loss Events:** Number of times context is lost (measured by checkpoint gaps)
- **Hallucination Rate:** Incorrect statements or code per 1000 lines generated
- **First-Pass Success Rate:** Percentage of tasks completed correctly first time
- **Iteration Cycles:** Average number of back-and-forth cycles per task
- **Bug Introduction Rate:** Bugs introduced per 1000 lines of AI-generated code
- **Time to Complete:** Average task completion time (trending down)

### Defenses Summary Matrix

| Threat | Defense | Detection Method | Recovery |
|--------|---------|-----------------|----------|
| Context Loss | Rolling summaries, checkpoints | Gap analysis | Load latest checkpoint |
| Hallucination | Read-first policy | Pre-write hooks | Verify against source |
| Inconsistent code | Pattern library, style guide | CI lint, review | Auto-format, review |
| Incomplete impl | Checklists, templates | CI checks, review | Re-open task |

### Implementation Priority

1. **Week 1:** Rolling summaries, Read-first policy, Edge case checklist
2. **Week 2:** Quick-reference docs, Current state document, Task templates
3. **Week 3-4:** Pattern library, Handoff protocol, Security checklist
4. **Month 2:** Verification criteria, Error handling template, Test requirements
5. **Month 3:** Context gathering script, Auto-checkpoints, Monitoring

---

*End of AI Performance Optimization Analysis.*
