from pathlib import Path
from .models import Finding

def apply_fix(finding: Finding, repo_root: str = ".") -> bool:
    strat = finding.fix_strategy
    if not strat:
        return False
    fpath = Path(repo_root) / finding.file
    if not fpath.exists():
        return False
    try:
        content = fpath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False
    action = strat.get("action")
    new_content = None
    if action == "comment_out":
        lines = content.splitlines(keepends=True)
        line_idx = strat.get("line", finding.line or 1) - 1
        if 0 <= line_idx < len(lines):
            stripped = lines[line_idx].rstrip("\n\r")
            if not stripped.strip().startswith("//") and not stripped.strip().startswith("#"):
                comment = "#" if finding.file.endswith(".py") else "//"
                lines[line_idx] = f"{comment} {stripped}\n"
                new_content = "".join(lines)
    elif action == "remove_line":
        lines = content.splitlines(keepends=True)
        line_idx = strat.get("line", finding.line or 1) - 1
        if 0 <= line_idx < len(lines):
            lines.pop(line_idx)
            new_content = "".join(lines)
    elif action == "replace_text":
        old = strat.get("old", "")
        new = strat.get("new", "")
        if old in content:
            new_content = content.replace(old, new, 1)
    elif action == "replace_line":
        lines = content.splitlines(keepends=True)
        line_idx = strat.get("line", finding.line or 1) - 1
        if 0 <= line_idx < len(lines):
            lines[line_idx] = strat.get("new", lines[line_idx])
            new_content = "".join(lines)
    if new_content is not None and new_content != content:
        try:
            fpath.write_text(new_content, encoding="utf-8")
            return True
        except Exception:
            return False
    return False


def apply_all(findings: list, repo_root: str = ".") -> tuple:
    fixed = 0
    failed = 0
    for f in findings:
        if apply_fix(f, repo_root):
            fixed += 1
        elif f.fix_strategy:
            failed += 1
    return fixed, failed
