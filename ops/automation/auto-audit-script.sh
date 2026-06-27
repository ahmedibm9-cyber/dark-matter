#!/usr/bin/env bash
# =============================================================================
# auto-audit-script.sh — Automated Daily Audit Runner
# Runs every morning at 06:00 UTC via cron. Checks every quality gate then
# writes a timestamped report into ops/audits/reports/.
# =============================================================================
set -euo pipefail
IFS=$'\n\t'

readonly VERSION="1.0.0"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
readonly REPORT_DIR="$PROJECT_ROOT/ops/audits/reports"
readonly TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
readonly REPORT_FILE="$REPORT_DIR/audit_$TIMESTAMP.md"
readonly TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT

# ---------------------------------------------------------------------------
# Color / formatting helpers (no-op if not a terminal)
# ---------------------------------------------------------------------------
if [ -t 1 ]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
  CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; NC=''
fi

pass()  { echo -e "  ${GREEN}✓${NC} $1"; }
warn()  { echo -e "  ${YELLOW}⚠${NC} $1"; }
fail()  { echo -e "  ${RED}✗${NC} $1"; }
info()  { echo -e "  ${CYAN}→${NC} $1"; }
header(){ echo -e "\n${BOLD}$1${NC}"; }

FAILURES=0
WARNINGS=0

# ---------------------------------------------------------------------------
# 1. check_dependencies — run dependency audit
# ---------------------------------------------------------------------------
check_dependencies() {
  header "Dependency Audit"
  local fail_count=0

  if [ -f "$PROJECT_ROOT/package.json" ]; then
    info "Running npm audit..."
    cd "$PROJECT_ROOT"
    local audit_out
    audit_out=$(npm audit --audit-level=high 2>&1 || true)
    local high_crit
    high_crit=$(echo "$audit_out" | grep -cE "high|critical" || true)
    if [ "$high_crit" -gt 0 ]; then
      fail "npm audit found $high_crit high/critical vulnerabilities"
      fail_count=$((fail_count + 1))
    else
      pass "npm audit passed"
    fi

    info "Checking for outdated packages..."
    local outdated
    outdated=$(npm outdated --long 2>&1 | tail -n +2 | head -20 || true)
    if [ -n "$outdated" ]; then
      warn "Outdated packages detected (see report)"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi

  if [ -f "$PROJECT_ROOT/go.mod" ]; then
    info "Running go mod tidy check..."
    cd "$PROJECT_ROOT"
    if ! go mod tidy -v 2>&1; then
      fail "go mod tidy failed"
      fail_count=$((fail_count + 1))
    else
      pass "go modules tidy"
    fi
  fi

  if [ -f "$PROJECT_ROOT/Cargo.toml" ]; then
    info "Running cargo audit..."
    if command -v cargo-audit &>/dev/null; then
      if ! cargo audit 2>&1; then
        fail "cargo audit found issues"
        fail_count=$((fail_count + 1))
      else
        pass "cargo audit passed"
      fi
    else
      warn "cargo-audit not installed; skipping"
    fi
  fi

  if [ -f "$PROJECT_ROOT/requirements.txt" ] || [ -f "$PROJECT_ROOT/Pipfile" ]; then
    info "Running pip audit (safety)..."
    if command -v safety &>/dev/null; then
      if ! safety check 2>&1; then
        fail "safety check found vulnerabilities"
        fail_count=$((fail_count + 1))
      else
        pass "safety check passed"
      fi
    else
      warn "safety not installed; skipping"
    fi
  fi

  FAILURES=$((FAILURES + fail_count))
  [ "$fail_count" -eq 0 ] && pass "All dependency checks passed"
}

# ---------------------------------------------------------------------------
# 2. check_tests — run test suite, report failures
# ---------------------------------------------------------------------------
check_tests() {
  header "Test Suite"
  local fail_count=0

  if [ -f "$PROJECT_ROOT/package.json" ]; then
    local test_scripts
    test_scripts=$(node -p "const p=require('./package.json'); Object.keys(p.scripts||{}).filter(s=>/^test/.test(s)).join(' ')" 2>/dev/null || echo "")
    if echo "$test_scripts" | grep -qw "test"; then
      info "Running npm test..."
      cd "$PROJECT_ROOT"
      if ! npm test 2>&1; then
        fail "npm test returned non-zero exit code"
        fail_count=$((fail_count + 1))
      else
        pass "npm test passed"
      fi
    fi
    if echo "$test_scripts" | grep -qw "test:integration"; then
      info "Running integration tests..."
      cd "$PROJECT_ROOT"
      if ! npm run test:integration 2>&1; then
        warn "integration tests failed"
        WARNINGS=$((WARNINGS + 1))
      else
        pass "integration tests passed"
      fi
    fi
  fi

  if [ -f "$PROJECT_ROOT/Makefile" ]; then
    if grep -q "^test" "$PROJECT_ROOT/Makefile" 2>/dev/null; then
      info "Running make test..."
      cd "$PROJECT_ROOT"
      if ! make test 2>&1; then
        fail "make test failed"
        fail_count=$((fail_count + 1))
      else
        pass "make test passed"
      fi
    fi
  fi

  local test_dirs
  test_dirs=$(find "$PROJECT_ROOT" -type d -name "__pycache__" -prune -o -type d -name "tests" -print 2>/dev/null | head -5)
  if [ -n "$test_dirs" ] && [ -f "$PROJECT_ROOT/pyproject.toml" ] || [ -f "$PROJECT_ROOT/setup.py" ]; then
    info "Running pytest..."
    cd "$PROJECT_ROOT"
    if command -v pytest &>/dev/null; then
      if ! pytest --tb=short -q 2>&1; then
        fail "pytest failed"
        fail_count=$((fail_count + 1))
      else
        pass "pytest passed"
      fi
    fi
  fi

  FAILURES=$((FAILURES + fail_count))
  [ "$fail_count" -eq 0 ] && pass "All test suites passed"
}

# ---------------------------------------------------------------------------
# 3. check_coverage — check coverage thresholds
# ---------------------------------------------------------------------------
check_coverage() {
  header "Code Coverage"
  local fail_count=0
  local threshold=80

  if [ -f "$PROJECT_ROOT/package.json" ]; then
    local cover_scripts
    cover_scripts=$(node -p "const p=require('./package.json'); Object.keys(p.scripts||{}).filter(s=>/^(cover|coverage|test:coverage)/.test(s)).join(' ')" 2>/dev/null || echo "")
    if [ -n "$cover_scripts" ]; then
      local first_script
      first_script=$(echo "$cover_scripts" | awk '{print $1}')
      info "Running $first_script..."
      cd "$PROJECT_ROOT"
      npm run "$first_script" 2>&1 || true

      local lcov_file="$PROJECT_ROOT/coverage/lcov.info"
      local json_summary="$PROJECT_ROOT/coverage/coverage-summary.json"
      if [ -f "$json_summary" ]; then
        local pct
        pct=$(node -p "const j=require('$json_summary'); (j.total.lines.pct || 0).toFixed(1)" 2>/dev/null || echo "0")
        info "Line coverage: ${pct}% (threshold: ${threshold}%)"
        if (( $(echo "$pct < $threshold" | bc -l) )); then
          fail "Coverage ${pct}% below threshold ${threshold}%"
          fail_count=$((fail_count + 1))
        else
          pass "Coverage meets threshold"
        fi
      elif [ -f "$lcov_file" ]; then
        warn "lcov.info found but no summary; install nyc for JSON output"
      else
        warn "No coverage report found"
      fi
    else
      warn "No coverage script defined in package.json"
    fi
  fi

  if [ -f "$PROJECT_ROOT/pyproject.toml" ] || [ -f "$PROJECT_ROOT/.coveragerc" ]; then
    if command -v coverage &>/dev/null; then
      info "Running coverage report..."
      cd "$PROJECT_ROOT"
      coverage report --fail-under="$threshold" 2>&1 || true
      local cov_pct
      cov_pct=$(coverage report 2>/dev/null | tail -1 | awk '{print $NF}' | tr -d '%')
      if [ -n "$cov_pct" ] && [ "$cov_pct" != "TOTAL" ]; then
        if (( $(echo "$cov_pct < $threshold" | bc -l) )); then
          fail "Coverage ${cov_pct}% below threshold ${threshold}%"
          fail_count=$((fail_count + 1))
        fi
      fi
    fi
  fi

  FAILURES=$((FAILURES + fail_count))
  [ "$fail_count" -eq 0 ] && pass "Coverage checks passed"
}

# ---------------------------------------------------------------------------
# 4. check_todos — count new TODO / FIXME / HACK
# ---------------------------------------------------------------------------
check_todos() {
  header "TODO / FIXME / HACK Audit"
  local threshold=30

  local todo_count hack_count fixme_count
  todo_count=$(grep -r "TODO" "$PROJECT_ROOT/src" "$PROJECT_ROOT/app" "$PROJECT_ROOT/lib" 2>/dev/null | grep -v node_modules | grep -v ".next" | wc -l || true)
  fixme_count=$(grep -r "FIXME" "$PROJECT_ROOT/src" "$PROJECT_ROOT/app" "$PROJECT_ROOT/lib" 2>/dev/null | grep -v node_modules | grep -v ".next" | wc -l || true)
  hack_count=$(grep -r "HACK" "$PROJECT_ROOT/src" "$PROJECT_ROOT/app" "$PROJECT_ROOT/lib" 2>/dev/null | grep -v node_modules | grep -v ".next" | wc -l || true)
  local total=$((todo_count + fixme_count + hack_count))

  info "TODOs: $todo_count | FIXMEs: $fixme_count | HACKs: $hack_count | Total: $total"
  if [ "$total" -gt "$threshold" ]; then
    warn "Total annotations ($total) exceeds threshold ($threshold)"
    WARNINGS=$((WARNINGS + 1))
  else
    pass "Annotation count under threshold"
  fi

  local git_ref="HEAD"
  if git -C "$PROJECT_ROOT" rev-parse --git-dir &>/dev/null; then
    local new_todos
    new_todos=$(git -C "$PROJECT_ROOT" diff HEAD~1 --name-only 2>/dev/null | xargs grep -l "TODO\|FIXME\|HACK" 2>/dev/null | wc -l || true)
    if [ "$new_todos" -gt 0 ]; then
      warn "$new_todos files with new annotations introduced"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
}

# ---------------------------------------------------------------------------
# 5. check_secrets — scan for hardcoded secrets
# ---------------------------------------------------------------------------
check_secrets() {
  header "Secrets Scan"

  if command -v git &>/dev/null && git -C "$PROJECT_ROOT" rev-parse --git-dir &>/dev/null; then
    if command -v gitleaks &>/dev/null; then
      info "Running gitleaks..."
      cd "$PROJECT_ROOT"
      if ! gitleaks detect --no-git --verbose 2>&1; then
        fail "gitleaks found potential secrets"
        FAILURES=$((FAILURES + 1))
      else
        pass "gitleaks passed"
      fi
    elif command -v trufflehog &>/dev/null; then
      info "Running trufflehog..."
      cd "$PROJECT_ROOT"
      if ! trufflehog filesystem . 2>&1; then
        fail "trufflehog found potential secrets"
        FAILURES=$((FAILURES + 1))
      else
        pass "trufflehog passed"
      fi
    elif command -v secret-detector &>/dev/null; then
      info "Running secret-detector..."
      if ! secret-detector 2>&1; then
        fail "secret-detector found issues"
        FAILURES=$((FAILURES + 1))
      else
        pass "secret-detector passed"
      fi
    else
      warn "No secret scanner installed (gitleaks/trufflehog/secret-detector)"
    fi
  else
    warn "Not a git repository; skipping secret scan"
  fi

  info "Scanning for common secret patterns..."
  local secret_patterns=('AKIA[0-9A-Z]{16}' 'sk-[A-Za-z0-9]{32,}' 'ghp_[A-Za-z0-9]{36}' 'gho_[A-Za-z0-9]{36}' 'xox[baprs]-' '-----BEGIN.*PRIVATE KEY-----')
  local found=0
  for pattern in "${secret_patterns[@]}"; do
    local matches
    matches=$(grep -rn "$pattern" "$PROJECT_ROOT/src" "$PROJECT_ROOT/app" "$PROJECT_ROOT/config" 2>/dev/null | grep -v node_modules | grep -v ".next" | grep -v "\.git" || true)
    if [ -n "$matches" ]; then
      warn "Potential secret pattern found: $pattern"
      found=$((found + 1))
    fi
  done
  [ "$found" -eq 0 ] && pass "No secret patterns detected"
}

# ---------------------------------------------------------------------------
# 6. check_lint — run linter
# ---------------------------------------------------------------------------
check_lint() {
  header "Lint Check"
  local fail_count=0

  if [ -f "$PROJECT_ROOT/package.json" ]; then
    local lint_scripts
    lint_scripts=$(node -p "const p=require('./package.json'); Object.keys(p.scripts||{}).filter(s=>/^lint/.test(s)).join(' ')" 2>/dev/null || echo "")
    if echo "$lint_scripts" | grep -qw "lint"; then
      info "Running npm run lint..."
      cd "$PROJECT_ROOT"
      if ! npm run lint 2>&1; then
        fail "Lint failed"
        fail_count=$((fail_count + 1))
      else
        pass "Lint passed"
      fi
    fi
  fi

  if [ -f "$PROJECT_ROOT/.eslintrc.js" ] || [ -f "$PROJECT_ROOT/.eslintrc.json" ] || [ -f "$PROJECT_ROOT/.eslintrc" ]; then
    if command -v eslint &>/dev/null; then
      info "Running ESLint..."
      cd "$PROJECT_ROOT"
      if ! eslint . --max-warnings=30 2>&1; then
        fail "ESLint found violations"
        fail_count=$((fail_count + 1))
      else
        pass "ESLint passed"
      fi
    fi
  fi

  if [ -f "$PROJECT_ROOT/.ruff.toml" ] || [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
    if command -v ruff &>/dev/null; then
      info "Running ruff..."
      cd "$PROJECT_ROOT"
      if ! ruff check . 2>&1; then
        fail "ruff found violations"
        fail_count=$((fail_count + 1))
      else
        pass "ruff passed"
      fi
    fi
  fi

  FAILURES=$((FAILURES + fail_count))
  [ "$fail_count" -eq 0 ] && pass "All lint checks passed"
}

# ---------------------------------------------------------------------------
# 7. check_build — verify build
# ---------------------------------------------------------------------------
check_build() {
  header "Build Verification"
  local fail_count=0

  if [ -f "$PROJECT_ROOT/package.json" ]; then
    local build_scripts
    build_scripts=$(node -p "const p=require('./package.json'); Object.keys(p.scripts||{}).filter(s=>/^build/.test(s)).join(' ')" 2>/dev/null || echo "")
    if echo "$build_scripts" | grep -qw "build"; then
      info "Running npm run build..."
      cd "$PROJECT_ROOT"
      if ! npm run build 2>&1; then
        fail "Build failed"
        fail_count=$((fail_count + 1))
      else
        pass "Build succeeded"
      fi
    else
      warn "No build script found"
    fi
  fi

  if [ -f "$PROJECT_ROOT/Dockerfile" ]; then
    info "Validating Dockerfile..."
    if command -v docker &>/dev/null; then
      if ! docker build -t audit-check --quiet "$PROJECT_ROOT" 2>&1; then
        fail "Docker build failed"
        fail_count=$((fail_count + 1))
      else
        pass "Docker build succeeded"
      fi
    fi
  fi

  if [ -f "$PROJECT_ROOT/Makefile" ]; then
    if grep -q "^build" "$PROJECT_ROOT/Makefile" 2>/dev/null; then
      info "Running make build..."
      cd "$PROJECT_ROOT"
      if ! make build 2>&1; then
        fail "make build failed"
        fail_count=$((fail_count + 1))
      else
        pass "make build succeeded"
      fi
    fi
  fi

  FAILURES=$((FAILURES + fail_count))
  [ "$fail_count" -eq 0 ] && pass "All builds passed"
}

# ---------------------------------------------------------------------------
# 8. check_docs_freshness — check doc last-modified dates
# ---------------------------------------------------------------------------
check_docs_freshness() {
  header "Documentation Freshness"
  local max_age_days=30
  local stale_count=0

  local doc_dirs
  doc_dirs=$(find "$PROJECT_ROOT" -type d -name "docs" 2>/dev/null | head -5)
  if [ -z "$doc_dirs" ]; then
    warn "No docs directory found"
    return
  fi

  for doc_dir in $doc_dirs; do
    while IFS= read -r -d '' file; do
      local mod_epoch last_modified age_days
      mod_epoch=$(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file" 2>/dev/null || echo "0")
      last_modified=$(date -d @"$mod_epoch" +%s 2>/dev/null || echo "0")
      local now
      now=$(date +%s)
      age_days=$(( (now - last_modified) / 86400 ))
      if [ "$age_days" -gt "$max_age_days" ]; then
        warn "$(basename "$file") last modified $age_days days ago"
        stale_count=$((stale_count + 1))
      fi
    done < <(find "$doc_dir" -name "*.md" -type f -print0 2>/dev/null)
  done

  if [ "$stale_count" -gt 0 ]; then
    warn "$stale_count documentation files are stale (>$max_age_days days)"
    WARNINGS=$((WARNINGS + 1))
  else
    pass "All documentation files are fresh"
  fi
}

# ---------------------------------------------------------------------------
# 9. report_generation — generate summary report
# ---------------------------------------------------------------------------
report_generation() {
  header "Report Generation"

  mkdir -p "$REPORT_DIR"

  local score
  local total_checks=8
  local passed_checks=$((total_checks - FAILURES))
  score=$((passed_checks * 100 / total_checks))

  cat > "$REPORT_FILE" <<REPORT
# Automated Audit Report

**Date:** $(date '+%Y-%m-%d %H:%M:%S UTC')
**Script Version:** $VERSION
**Status:** $([ "$FAILURES" -eq 0 ] && echo "✅ PASSED" || echo "❌ FAILED")

## Summary

| Metric | Value |
|--------|-------|
| Checks Failed | $FAILURES |
| Warnings | $WARNINGS |
| Score | ${score}% |
| Threshold | 75% |

## Detail

REPORT

  if [ -f "$PROJECT_ROOT/package.json" ]; then
    echo "**Node:** $(node -v 2>/dev/null || echo 'N/A')" >> "$REPORT_FILE"
    echo "**npm:** $(npm -v 2>/dev/null || echo 'N/A')" >> "$REPORT_FILE"
  fi
  echo "**OS:** $(uname -a 2>/dev/null || echo 'N/A')" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"

  echo "## Results by Check" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"

  local checks=(
    "Dependency Audit"
    "Test Suite"
    "Code Coverage"
    "TODO/FIXME/HACK Audit"
    "Secrets Scan"
    "Lint Check"
    "Build Verification"
    "Documentation Freshness"
  )

  local outcomes=("")
  [ "$FAILURES" -gt 0 ] || outcomes+=("✅ Passed")

  for check_name in "${checks[@]}"; do
    echo "- $check_name: ✅ Checked" >> "$REPORT_FILE"
  done

  echo "" >> "$REPORT_FILE"

  if [ "$FAILURES" -gt 0 ]; then
    echo "## 🔴 Failed Checks" >> "$REPORT_FILE"
    echo "Review the log output above for details on each failure." >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
  fi

  if [ "$WARNINGS" -gt 0 ]; then
    echo "## 🟡 Warnings" >> "$REPORT_FILE"
    echo "$WARNINGS warning(s) were raised that did not fail the audit." >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
  fi

  echo "---" >> "$REPORT_FILE"
  echo "_Generated by auto-audit-script.sh v$VERSION_" >> "$REPORT_FILE"

  info "Report written to $REPORT_FILE"
  pass "Report generated"
}

# ---------------------------------------------------------------------------
# Main execution flow
# ---------------------------------------------------------------------------
main() {
  echo ""
  echo "=============================================="
  echo "  Project Intelligence — Auto Audit v$VERSION"
  echo "  $(date)"
  echo "=============================================="

  cd "$PROJECT_ROOT"

  check_dependencies
  check_tests
  check_coverage
  check_todos
  check_secrets
  check_lint
  check_build
  check_docs_freshness
  report_generation

  echo ""
  echo "=============================================="
  echo "  Audit Complete"
  echo "  Failures: $FAILURES  |  Warnings: $WARNINGS"
  echo "=============================================="

  if [ "$FAILURES" -gt 0 ]; then
    exit 1
  elif [ "$WARNINGS" -gt 0 ]; then
    exit 0
  else
    exit 0
  fi
}

main
