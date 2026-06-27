def compile_markdown(graph_state: dict, output_path: str):
    # ponytail: plain markdown with no templating engine. Switch to Jinja2 if report needs HTML/pagination.
    lines = []
    lines.append("# Repository Intelligence Report")
    lines.append("")
    lines.append(f"> Generated: {graph_state.get('generated_at', 'unknown')}")
    lines.append(f"> Graph Version: {graph_state.get('graph_version', 'unknown')}")
    lines.append("")

    # FileMap
    repo = graph_state.get("repo_node", {})
    if repo:
        lines.append("## Repository")
        lines.append(f"- **Name:** {repo.get('name', 'unknown')}")
        lines.append(f"- **Root:** {repo.get('properties', {}).get('root_path', 'unknown')}")
        lines.append("")

    files = graph_state.get("files", [])
    if files:
        lines.append("## Files")
        lines.append("")
        lines.append("| File | Lines | Language |")
        lines.append("|------|-------|----------|")
        for f in files:
            props = f.get("properties", {})
            lines.append(f"| {props.get('relative_path', f['name'])} | {props.get('line_count', '?')} | {props.get('extension', '')} |")
        lines.append("")

    # Facts
    facts = graph_state.get("facts", [])
    if facts:
        lines.append("## Inferred Facts")
        lines.append("")
        for f in facts:
            lines.append(f"- **{f['statement']}** (confidence: {f.get('confidence', '?')})")
            lines.append(f"  - Rule: {f.get('rule_id', '?')}")
            lines.append(f"  - Evidence: {', '.join(f.get('evidence_refs', []))}")
        lines.append("")

    # Verifications
    verifications = graph_state.get("verifications", [])
    if verifications:
        lines.append("## Verifications")
        lines.append("")
        for v in verifications:
            lines.append(f"- **{v['claim']}**: {v['result']} (confidence: {v.get('confidence', '?')})")
        lines.append("")

    # Statistics
    lines.append("## Statistics")
    lines.append("")
    lines.append(f"- Files discovered: {len(files)}")
    lines.append(f"- Facts inferred: {len(facts)}")
    lines.append(f"- Verifications recorded: {len(verifications)}")

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path
