import re
from pathlib import Path
from ..models import Finding

CODE_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".rs", ".go", ".java", ".kt", ".cs", ".c", ".cpp", ".h", ".hpp", ".rb", ".php", ".swift"}


def _parse_imports(content: str, ext: str) -> set:
    imports = set()
    if ext == ".py":
        for m in re.finditer(r'(?:^|\n)\s*(?:import |from )(\S+)', content):
            imports.add(m.group(1).split(".")[0])
    elif ext in (".js", ".ts", ".jsx", ".tsx"):
        for m in re.finditer(r"(?:require\(['\"])([^'\"]+)(?:['\"]\))", content):
            imports.add(m.group(1))
        for m in re.finditer(r"(?:^|\n)\s*import\s+(?:\S+\s+from\s+)?['\"]([^'\"]+)['\"]", content):
            imports.add(m.group(1))
    elif ext in (".rs",):
        for m in re.finditer(r"(?:^|\n)\s*use\s+(\S+)", content):
            imports.add(m.group(1).split("::")[0])
    elif ext in (".go",):
        for m in re.finditer(r'(?:^|\n)\s*import\s+"([^"]+)"', content):
            imports.add(m.group(1).split("/")[-1])
    elif ext in (".java", ".kt"):
        for m in re.finditer(r"(?:^|\n)\s*import\s+(\S+?)(?:\.\*)?;", content):
            imports.add(m.group(1).split(".")[-1])
    elif ext == ".cs":
        for m in re.finditer(r"(?:^|\n)\s*using\s+(\S+?);", content):
            imports.add(m.group(1).split(".")[-1])
    elif ext in (".c", ".cpp", ".h", ".hpp"):
        for m in re.finditer(r'#include\s+[<"]([^>"]+)[>"]', content):
            imports.add(m.group(1).split("/")[-1].split(".")[0])
    return {i for i in imports if i not in ("", "self", "__future__")}


CODE_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".rs", ".go", ".java", ".kt", ".cs", ".c", ".cpp", ".h", ".hpp", ".rb", ".php", ".swift"}


def orphan_files(graph, evidence) -> list:
    findings = []
    files = graph.get_nodes_by_kind("FILE")
    # deduplicate: keep one FILE node per relative path
    seen = {}
    for f in files:
        fp = f.get("properties", {}).get("relative_path", f["name"])
        if fp not in seen:
            seen[fp] = f
    files = list(seen.values())

    edges = graph.get_edges("CONTAINS")
    repo_id = None
    for e in edges:
        repo_id = e["source_id"]
        break
    if not repo_id:
        return []

    file_ids = {f["id"] for f in files}
    all_edges = graph.get_edges()
    import_targets = set()
    for e in all_edges:
        if e["kind"] != "CONTAINS" and e["target_id"] in file_ids and e["source_id"] != repo_id:
            import_targets.add(e["target_id"])
        if e["kind"] != "CONTAINS" and e["source_id"] in file_ids:
            import_targets.add(e["target_id"])
    # fallback: parse imports from content_preview
    if not import_targets:
        ev_map = {}
        for ev in evidence:
            rp = ev.get("payload", {}).get("relative_path", "")
            if rp:
                ev_map[rp] = ev
        for f in files:
            fp = f.get("properties", {}).get("relative_path", f["name"])
            ext = f.get("properties", {}).get("extension", "")
            if ext not in CODE_EXTS:
                continue
            if fp in ev_map:
                preview = ev_map[fp].get("payload", {}).get("content_preview", "")
                imported = _parse_imports(preview, ext)
                if imported:
                    import_targets.add(f["id"])
    for f in files:
        fp = f.get("properties", {}).get("relative_path", f["name"])
        ext = f.get("properties", {}).get("extension", "")
        if ext not in CODE_EXTS:
            continue
        if f["id"] not in import_targets and f["id"] != repo_id:
            findings.append(Finding(
                rule_id="DM-STRUCT-001",
                severity="medium",
                file=fp,
                line=None,
                description=f"File is not imported by any other file in the project",
                confidence=0.8,
                suggested_fix="Verify file is needed; if dead code, consider removing",
            ))
    return findings


def bloated_files(graph, evidence) -> list:
    findings = []
    files = graph.get_nodes_by_kind("FILE")
    seen = {}
    for f in files:
        fp = f.get("properties", {}).get("relative_path", f["name"])
        if fp not in seen:
            seen[fp] = f
    files = list(seen.values())
    for f in files:
        lc = f.get("properties", {}).get("line_count", 0)
        fp = f.get("properties", {}).get("relative_path", f["name"])
        if lc > 1000:
            findings.append(Finding(
                rule_id="DM-STRUCT-002",
                severity="medium",
                file=fp,
                line=None,
                description=f"Bloated file: {lc} lines. Consider splitting into smaller modules",
                confidence=0.7,
                suggested_fix=f"Split into files of <300 lines each",
            ))
        elif lc > 500:
            findings.append(Finding(
                rule_id="DM-STRUCT-002",
                severity="low",
                file=fp,
                line=None,
                description=f"Large file: {lc} lines",
                confidence=0.5,
            ))
    return findings


def duplicate_files(graph, evidence) -> list:
    findings = []
    ev_map = {}
    for ev in evidence:
        h = ev.get("payload", {}).get("hash", "")
        rp = ev.get("payload", {}).get("relative_path", "")
        if h and rp:
            ev_map.setdefault(h, []).append(rp)
    for h, paths in ev_map.items():
        if len(paths) > 1:
            for p in paths[1:]:
                findings.append(Finding(
                    rule_id="DM-STRUCT-003",
                    severity="high",
                    file=p,
                    line=None,
                    description=f"Duplicate of {paths[0]} (same content hash)",
                    confidence=0.95,
                    suggested_fix=f"Replace with import from {paths[0]}",
                ))
    return findings


def todo_density(graph, evidence) -> list:
    findings = []
    for ev in evidence:
        preview = ev.get("payload", {}).get("content_preview", "")
        fp = ev.get("payload", {}).get("relative_path", "")
        lc = ev.get("payload", {}).get("line_count", 1)
        todos = len(re.findall(r'\b(TODO|FIXME|HACK|XXX|BUG|WORKAROUND)\b', preview, re.IGNORECASE))
        if todos > 0 and lc > 0:
            density = todos / max(lc, 1)
            if density > 0.1 and fp:
                findings.append(Finding(
                    rule_id="DM-STRUCT-004",
                    severity="low" if density < 0.3 else "medium",
                    file=fp,
                    line=None,
                    description=f"High TODO/FIXME density: {todos} markers in {lc} lines ({density:.0%})",
                    confidence=0.6,
                    suggested_fix="Resolve or ticket each TODO/FIXME",
                ))
    return findings


def missing_tests(graph, evidence) -> list:
    findings = []
    files = graph.get_nodes_by_kind("FILE")
    seen = {}
    for f in files:
        fp = f.get("properties", {}).get("relative_path", f["name"])
        if fp not in seen:
            seen[fp] = f
    files = list(seen.values())

    test_paths = set()
    source_paths = {}
    for f in files:
        fp = f.get("properties", {}).get("relative_path", f["name"])
        p = Path(fp)
        name = p.stem
        ext = p.suffix
        if "test" in name.lower() or "spec" in name.lower() or p.parent.name == "test":
            base = name.replace("test_", "").replace("_test", "").replace("_spec", "").replace("spec_", "")
            test_paths.add(base)
        elif ext in (".py", ".js", ".ts", ".rs", ".go", ".java", ".kt", ".cs"):
            parent = str(p.parent) if str(p.parent) != "." else ""
            source_paths[fp] = (parent, name, ext)
    for fp, (parent, name, ext) in source_paths.items():
        if name.startswith("test") or name.endswith("test") or "test" in name.lower():
            continue
        has_test = False
        for tn in test_paths:
            if name == tn or tn.startswith(name) or name.startswith(tn):
                has_test = True
                break
        if not has_test:
            test_candidates = [f"test_{name}{ext}", f"{name}_test{ext}",
                               f"{name}.spec{ext}", f"{name}.test{ext}"]
            found = False
            for ev in evidence:
                rp = ev.get("payload", {}).get("relative_path", "")
                for tc in test_candidates:
                    if tc.lower() in rp.lower():
                        found = True
                        break
                if found:
                    break
            if not found:
                test_dir = parent + "/test" if parent else "test"
                findings.append(Finding(
                    rule_id="DM-STRUCT-005",
                    severity="medium",
                    file=fp,
                    line=None,
                    description=f"No test file found for {name}{ext}",
                    confidence=0.7,
                    suggested_fix=f"Create in {test_dir}/: {test_candidates[0]}",
                ))
    return findings
