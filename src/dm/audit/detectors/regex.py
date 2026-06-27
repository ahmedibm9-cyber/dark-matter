import re
from ..models import Finding


def _content(ev: dict) -> str:
    return ev.get("payload", {}).get("content_preview", "")


def _path(ev: dict) -> str:
    return ev.get("payload", {}).get("relative_path", "") or ev.get("relative_path", "")


def hardcoded_secrets(graph, evidence: list) -> list:
    findings = []
    pattern = re.compile(
        r'(?:password|passwd|pwd|secret|api_key|apikey|api\.key|token|auth_token|'
        r'access_key|secret_key|private_key|connection_string)'
        r'\s*[:=]\s*["\'][^"\']+["\']',
        re.IGNORECASE
    )
    skips = {"example", "test", "placeholder", "your_"}
    for ev in evidence:
        fp = _path(ev)
        content = _content(ev)
        for m in pattern.finditer(content):
            val = m.group(0)
            if any(s in val.lower() for s in skips):
                continue
            findings.append(Finding(
                rule_id="DM-REGEX-001",
                severity="high",
                file=fp,
                line=content[:m.start()].count("\n") + 1,
                description="Hardcoded credential detected",
                confidence=0.85,
                suggested_fix="Move to environment variable or secrets manager",
            ))
    return findings


def sql_injection(graph, evidence: list) -> list:
    findings = []
    patterns = [
        re.compile(r'(?:execute|query|cursor\.execute|raw_query|db\.execute)\s*\(\s*[f"\'][^)]*\{'),
        re.compile(r'(?:WHERE|SELECT|INSERT|UPDATE|DELETE)\s+.*?(?:\+|\.format\(|%\(|%s|f["\'])', re.IGNORECASE),
        re.compile(r'["\']\s*\+\s*[\w_]+\s*\+\s*["\']'),
    ]
    for ev in evidence:
        fp = _path(ev)
        content = _content(ev)
        ext = ev.get("payload", {}).get("extension", "")
        if ext not in (".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".php"):
            continue
        for p in patterns:
            for m in p.finditer(content):
                findings.append(Finding(
                    rule_id="DM-REGEX-002",
                    severity="high",
                    file=fp,
                    line=content[:m.start()].count("\n") + 1,
                    description="Potential SQL injection: string formatting in query",
                    confidence=0.75,
                    suggested_fix="Use parameterized queries instead of string formatting",
                ))
    return findings


def empty_catch(graph, evidence: list) -> list:
    findings = []
    patterns = [
        re.compile(r'except\s*\w*(?:\s+as\s+\w+)?\s*:\s*\n\s*(?:pass|#|$|\n)', re.MULTILINE),
        re.compile(r'catch\s*\([^)]*\)\s*\{\s*(?:\/\/.*)?\s*\}', re.MULTILINE),
        re.compile(r'catch\s*\{[^}]*\}'),
    ]
    for ev in evidence:
        fp = _path(ev)
        content = _content(ev)
        for p in patterns:
            for m in p.finditer(content):
                findings.append(Finding(
                    rule_id="DM-REGEX-003",
                    severity="medium",
                    file=fp,
                    line=content[:m.start()].count("\n") + 1,
                    description="Empty exception handler",
                    confidence=0.8,
                    suggested_fix="Log the exception or handle it appropriately",
                    fix_strategy={"action": "comment_out", "line": content[:m.start()].count("\n") + 1},
                ))
    return findings


def console_log(graph, evidence: list) -> list:
    findings = []
    patterns = [
        re.compile(r'\bconsole\.(?:log|warn|error|debug|info)\s*\('),
        re.compile(r'\bprint\s*\('),
    ]
    for ev in evidence:
        fp = _path(ev)
        ext = ev.get("payload", {}).get("extension", "")
        if ext not in (".js", ".ts", ".jsx", ".tsx"):
            if ext not in (".py",) and ext != ".js":
                continue
        content = _content(ev)
        lc = ev.get("payload", {}).get("line_count", 1)
        for p in patterns:
            for m in p.finditer(content):
                findings.append(Finding(
                    rule_id="DM-REGEX-004",
                    severity="low",
                    file=fp,
                    line=content[:m.start()].count("\n") + 1,
                    description=f"Debug {m.group(0).split('(')[0]} statement",
                    confidence=0.6,
                    suggested_fix="Remove before production, or use proper logging framework",
                    fix_strategy={"action": "comment_out", "line": content[:m.start()].count("\n") + 1},
                ))
    return findings


def eval_usage(graph, evidence: list) -> list:
    findings = []
    # ponytail: negative lookbehind excludes re.compile, ast.literal_eval, etc.
    pattern = re.compile(r'(?<!\.)\b(?:eval|exec|compile)\s*\(')
    for ev in evidence:
        fp = _path(ev)
        content = _content(ev)
        for m in pattern.finditer(content):
            line = content[:m.start()].count("\n") + 1
            findings.append(Finding(
                rule_id="DM-REGEX-005",
                severity="high",
                file=fp,
                line=line,
                description=f"Dynamic code execution: {m.group(0).rstrip('(')}()",
                confidence=0.85,
                suggested_fix="Replace with safer alternative (ast.literal_eval, importlib, etc.)",
            ))
    return findings


def todo_without_ticket(graph, evidence: list) -> list:
    findings = []
    # ponytail: require # or // prefix so string literals like "TODO Density" are not matched
    pattern = re.compile(r'(?:#|//)\s*\b(TODO|FIXME|HACK)\b\s*(?::?\s*)([^\n]*)', re.IGNORECASE)
    ticket_pattern = re.compile(r'(?:#\d+|JIRA-\d+|GH-\d+|DM-\d+|TASK-\d+|PROJ-\d+)', re.IGNORECASE)
    for ev in evidence:
        fp = _path(ev)
        content = _content(ev)
        for m in pattern.finditer(content):
            rest = m.group(2)
            if not ticket_pattern.search(rest):
                findings.append(Finding(
                    rule_id="DM-REGEX-006",
                    severity="info",
                    file=fp,
                    line=content[:m.start()].count("\n") + 1,
                    description=f"{m.group(1).upper()} without ticket reference: {rest.strip()[:40]}",
                    confidence=0.5,
                    suggested_fix="Add ticket/issue reference (e.g., #123, PROJ-456)",
                ))
    return findings


def insecure_compare(graph, evidence: list) -> list:
    findings = []
    pattern = re.compile(r'(?:password|token|secret|hash|hmac|signature)\s*(?:!=|==)\s*[\w"\']+', re.IGNORECASE)
    for ev in evidence:
        fp = _path(ev)
        content = _content(ev)
        for m in pattern.finditer(content):
            findings.append(Finding(
                rule_id="DM-REGEX-007",
                severity="low",
                file=fp,
                line=content[:m.start()].count("\n") + 1,
                description=f"Insecure comparison: {m.group(0)[:50]}",
                confidence=0.4,
                suggested_fix="Use constant-time comparison (hmac.compare_digest, timingSafeEqual)",
            ))
    return findings
