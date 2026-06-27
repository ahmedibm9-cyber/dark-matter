from datetime import datetime


def generate(graph_state: dict, output_path: str) -> str:
    findings = graph_state.get("audit_findings", {})
    all_findings = []
    for name, det_findings in findings.items():
        for f in det_findings:
            all_findings.append((name, f))

    by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    by_detector = {}
    for name, f in all_findings:
        by_severity[f.severity] = by_severity.get(f.severity, 0) + 1
        by_detector[name] = by_detector.get(name, 0) + 1

    high_count = by_severity.get("critical", 0) + by_severity.get("high", 0)
    total = len(all_findings)

    lines = []
    lines.append("# Deployability Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.utcnow().isoformat()}")
    lines.append(f"**Project:** {graph_state.get('repo_node', {}).get('name', 'unknown')}")
    lines.append(f"**Files scanned:** {len(graph_state.get('files', []))}")
    lines.append("")

    # verdict
    if high_count == 0 and total == 0:
        lines.append("## Verdict: ✅ DEPLOYABLE")
        lines.append("Zero findings. Clean bill of health.")
    elif high_count == 0:
        lines.append(f"## Verdict: ⚠️ DEPLOYABLE WITH CAVEATS")
        lines.append(f"{total} findings, all at medium or below. Review before deploy.")
    else:
        lines.append(f"## Verdict: ⛔ BLOCKED")
        lines.append(f"{high_count} critical/high issue(s) must be fixed before deploy.")
    lines.append("")

    # summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Severity | Count |")
    lines.append("|----------|-------|")
    for sev in ("critical", "high", "medium", "low", "info"):
        c = by_severity.get(sev, 0)
        if c:
            lines.append(f"| {sev} | {c} |")
    lines.append(f"| **Total** | **{total}** |")
    lines.append("")

    # by detector
    if by_detector:
        lines.append("## By Detector")
        lines.append("")
        lines.append("| Detector | Findings |")
        lines.append("|----------|----------|")
        for name, count in sorted(by_detector.items(), key=lambda x: -x[1]):
            lines.append(f"| {name} | {count} |")
        lines.append("")

    # detailed findings
    if all_findings:
        lines.append("## Detailed Findings")
        lines.append("")
        for name, f in all_findings:
            loc = f"{f.file}" + (f":{f.line}" if f.line else "")
            lines.append(f"- **[{f.severity.upper()}]** {loc}")
            lines.append(f"  - {f.description}")
            if f.suggested_fix:
                lines.append(f"  - Fix: {f.suggested_fix}")
        lines.append("")

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path
