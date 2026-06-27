# Daily Checklist — AI Agent Tasks

> Run daily at start of session. Each item has a task, commands, and verification step.

## 1. Status Check
- **Task**: Review the current state of the codebase and any active work.
- **Commands**:
  ```bash
  git status
  git log --oneline -10
  git diff --stat
  ```
- **Verification**: Confirm working branch is correct, no unexpected changes, and recent commits are understood.

## 2. Test Suite Health
- **Task**: Run the test suite to verify nothing is broken.
- **Commands**:
  ```bash
  cd apps/web && npx vitest run --reporter=verbose 2>&1 | tail -20
  cd services/api && npx vitest run --reporter=verbose 2>&1 | tail -20
  ```
- **Verification**: All tests pass. Note any new failures or flaky tests.

## 3. Dependency Scan
- **Task**: Check for known vulnerabilities in dependencies.
- **Commands**:
  ```bash
  npm audit --audit-level=high 2>&1 | tail -20
  ```
- **Verification**: No high or critical vulnerabilities. If found, create a ticket.

## 4. Recent Changes Review
- **Task**: Review recent file changes for quality issues.
- **Commands**:
  ```bash
  git diff HEAD~5 --name-only
  git diff HEAD~5 --stat
  ```
- **Verification**: Understand what changed and why. Flag any files that need intelligence-layer updates.

## 5. Intelligence Layer Freshness
- **Task**: Check if any intelligence documents are stale.
- **Commands**:
  ```bash
  git log --oneline --follow "intelligence/*.md" | head -5
  ```
- **Verification**: Intelligence docs were updated within the last 7 days. If not, schedule updates.

## 6. CI Pipeline Status
- **Task**: Verify CI is green on the main branch.
- **Commands**:
  ```bash
  gh run list --branch main --limit 3 --json conclusion,displayTitle,status
  ```
- **Verification**: Latest runs show "success" conclusion. Investigate failures immediately.

## 7. Branch Hygiene
- **Task**: Check for stale branches that need cleanup.
- **Commands**:
  ```bash
  git branch --merged main | grep -v "main\|*" | head -10
  ```
- **Verification**: Identify branches that can be deleted after confirming their work is complete.

## 8. Environment Health
- **Task**: Verify development environment is functional.
- **Commands**:
  ```bash
  curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health
  curl -s -o /dev/null -w "%{http_code}" http://localhost:4000/health
  ```
- **Verification**: Both endpoints return 200. If not, check local services.

## 9. Open Issue Review
- **Task**: Check for new or updated GitHub issues relevant to today's work.
- **Commands**:
  ```bash
  gh issue list --limit 10 --json number,title,labels,updatedAt
  ```
- **Verification**: Review any issues labeled "bug" or "high-priority" that were updated in the last 24h.

## 10. Session Goal Setting
- **Task**: Set clear goals for the current session based on priority and backlog.
- **Verification**: Document today's objectives in the session notes. Ensure alignment with active sprint goals.

## 11. Lint and Type Check
- **Task**: Run linting and type checking on the codebase.
- **Commands**:
  ```bash
  cd apps/web && npx tsc --noEmit 2>&1 | tail -10
  cd apps/web && npx eslint . --max-warnings=0 2>&1 | tail -10
  ```
- **Verification**: No type errors, no lint warnings. Record any violations for cleanup.

## 12. Commit Pending Changes
- **Task**: Before end of session, ensure all changes are committed.
- **Commands**:
  ```bash
  git status --porcelain
  ```
- **Verification**: Working tree is clean. If not, commit with descriptive message referencing relevant issues.
