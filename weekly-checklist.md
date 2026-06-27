# Weekly Checklist — AI Agent Tasks

> Run every Monday. Deeper inspection than daily tasks.

## 1. Technical Debt Triage
- **Task**: Review technical-debt.md and triage new items.
- **Commands**:
  ```bash
  cat intelligence/technical-debt.md | grep -A2 "^### TDEBT"
  ```
- **Steps**:
  1. Read all open debt items.
  2. Update effort estimates if new information is available.
  3. Assign owners to unassigned items.
  4. Move HIGH-priority items <= 3 story points to active sprint.
  5. Mark resolved items as complete and archive them.
  6. Add any new debt discovered during the week.
- **Verification**: File is updated with current state. No unowned HIGH-priority items.

## 2. Code Review Backlog
- **Task**: Process the code review queue.
- **Commands**:
  ```bash
  gh pr list --review-requested "@me" --json number,title,createdAt
  gh pr list --author "@me" --json number,title,state
  ```
- **Steps**:
  1. Review all PRs assigned to you.
  2. Respond to feedback on your open PRs.
  3. Ensure each PR includes updates to intelligence-layer docs if applicable.
  4. Approve or request changes with clear rationale.
- **Verification**: No PRs pending review > 48 hours. All your PRs have recent activity.

## 3. Test Coverage Check
- **Task**: Review test coverage trends and identify gaps.
- **Commands**:
  ```bash
  npx vitest run --coverage 2>&1 | grep -E "(Statements|Branches|Functions|Lines)"
  ```
- **Steps**:
  1. Compare coverage against previous week's baseline.
  2. Identify modules with < 80% coverage.
  3. Flag newly added code without tests.
  4. Update the test coverage section in the weekly report.
- **Verification**: Coverage did not decrease. All new code has tests.

## 4. Performance Baseline
- **Task**: Run performance benchmarks and compare against baseline.
- **Commands**:
  ```bash
  # Example: run load test
  # npx artillery run tests/performance/checkout-flow.yml
  ```
- **Steps**:
  1. Run key endpoint benchmarks (products list, checkout, login).
  2. Compare p50/p95/p99 latency against last week's baseline.
  3. Check for regressions > 10%.
  4. Record baseline for next week.
- **Verification**: No regressions. If found, file a performance bug.

## 5. Security Scan
- **Task**: Run security scanning tools.
- **Commands**:
  ```bash
  npm audit --audit-level=moderate 2>&1
  ```
- **Steps**:
  1. Check npm audit for moderate+ vulnerabilities.
  2. Review any security advisories for dependencies.
  3. Check for exposed secrets in the codebase (`git diff --cached` review).
  4. Verify no hardcoded credentials in configuration files.
- **Verification**: No moderate+ vulnerabilities. No secrets in the codebase.

## 6. Business Rules Verification
- **Task**: Spot-check business rules against actual code behavior.
- **Commands**:
  ```bash
  grep -r "BR-00[0-9]" services/ --include="*.ts" | head -20
  ```
- **Steps**:
  1. Pick 3 business rules at random.
  2. Verify the enforcement point listed in business-rules.md matches actual code.
  3. Update last-verified date for checked rules.
  4. Flag any rules whose enforcement has drifted.
- **Verification**: At least 3 rules verified. All checked rules have correct enforcement points.

## 7. Known Bugs Review
- **Task**: Review known-bugs.md for status changes.
- **Commands**:
  ```bash
  cat intelligence/known-bugs.md | grep -E "(BUG-|Severity|Fix ETA)"
  ```
- **Steps**:
  1. Check if any fix ETAs have passed.
  2. Verify resolved bugs are actually fixed in code.
  3. Add any newly discovered bugs.
  4. Update severity or workaround if changed.
- **Verification**: All bugs have current information. Overdue fixes are escalated.

## 8. Intelligence Layer Consistency
- **Task**: Verify cross-references between intelligence documents are correct.
- **Commands**:
  ```bash
  grep -oE "(BR-|ADR-|TDEBT-|FAIL-|BUG-|F-)[0-9]{3}" intelligence/*.md | sort | uniq -d
  ```
- **Steps**:
  1. Ensure all referenced IDs exist in their respective files.
  2. Fix any broken cross-references.
- **Verification**: No dangling references. All IDs resolve to existing documents.
