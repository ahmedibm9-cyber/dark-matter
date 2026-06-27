#!/usr/bin/env python3
"""Dark Matter — Repository Intelligence Platform.

Usage:
    dm <command> [options]

Commands:
    init      Initialize Dark Matter for a repository
    start     Begin a work session
    work      Load context for a task
    scan      Update intelligence from changes
    verify    Check facts against evidence
    compile   Generate intelligence outputs
    review    Get pre-commit/pre-PR analysis
    doctor    Diagnose and fix issues
    search    Find anything in project knowledge
    explain   Understand why Dark Matter thinks something
    report    Generate deployability report for engineer handoff
    watch     Watch repo for changes, auto-audit

Run 'dm <command> --help' for more information.
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        prog="dm",
        description="Repository Intelligence Platform",
        usage="dm <command> [options]",
    )
    parser.add_argument("--version", action="version", version="Dark Matter 0.1.0")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # aether init
    init_p = subparsers.add_parser("init", help="Initialize Dark Matter for a repository")
    init_p.add_argument("path", nargs="?", default=".", help="Repository path")
    init_p.add_argument("--force", action="store_true", help="Re-initialize if exists")

    start_p = subparsers.add_parser("start", help="Begin a work session")
    start_p.add_argument("--path", default=".", help="Repository path")

    work_p = subparsers.add_parser("work", help="Load context for a task")
    work_p.add_argument("task", nargs="?", help="Task ID (e.g., TASK-044)")
    work_p.add_argument("--path", default=".", help="Repository path")

    scan_p = subparsers.add_parser("scan", help="Update intelligence from changes")
    scan_p.add_argument("--path", default=".", help="Repository path")
    scan_p.add_argument("--full", action="store_true", help="Full scan (not incremental)")
    scan_p.add_argument("-p", "--ponytail", action="store_true",
                        help="Lazy mode: skip inference, verify, compile. Just collect + audit.")

    verify_p = subparsers.add_parser("verify", help="Check facts against evidence")
    verify_p.add_argument("claim", nargs="?", help="Specific claim to verify")
    verify_p.add_argument("--path", default=".", help="Repository path")

    compile_p = subparsers.add_parser("compile", help="Generate intelligence outputs")
    compile_p.add_argument("--path", default=".", help="Repository path")
    compile_p.add_argument("--target", choices=["all", "markdown", "ai-package", "dashboard"],
                           default="all", help="Compiler target")

    review_p = subparsers.add_parser("review", help="Get pre-commit/pre-PR analysis")
    review_p.add_argument("--pr", action="store_true", help="PR review mode")
    review_p.add_argument("--release", type=str, help="Release review mode (pass version)")
    review_p.add_argument("--path", default=".", help="Repository path")

    audit_p = subparsers.add_parser("audit", help="Run bug detectors against the project")
    audit_p.add_argument("--path", default=".", help="Repository path")
    audit_p.add_argument("-p", "--ponytail", action="store_true",
                         help="Lazy mode: regex-only detectors, minimal output. ~6x faster.")
    audit_p.add_argument("--severity", choices=["critical", "high", "medium", "low", "info"],
                         help="Minimum severity to show (default: all)")
    audit_p.add_argument("--detector", help="Only run specific detector (regex match on name)")
    audit_p.add_argument("--json", action="store_true",
                         help="Output findings as JSON (machine-readable for AI agents)")
    audit_p.add_argument("--fix", action="store_true",
                         help="Auto-fix findings when possible")

    doctor_p = subparsers.add_parser("doctor", help="Diagnose and fix issues")
    doctor_p.add_argument("--fix", action="store_true", help="Auto-fix when possible")
    doctor_p.add_argument("--path", default=".", help="Repository path")

    search_p = subparsers.add_parser("search", help="Find anything in project knowledge")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--path", default=".", help="Repository path")
    search_p.add_argument("--limit", type=int, default=10, help="Max results")
    search_p.add_argument("--json", action="store_true",
                          help="Output as JSON (machine-readable for AI agents)")

    explain_p = subparsers.add_parser("explain", help="Understand why Dark Matter thinks something")
    explain_p.add_argument("claim", help="Statement to explain")
    explain_p.add_argument("--path", default=".", help="Repository path")
    explain_p.add_argument("--json", action="store_true",
                           help="Output as JSON (machine-readable for AI agents)")

    report_p = subparsers.add_parser("report", help="Generate deployability report for engineer handoff")
    report_p.add_argument("--path", default=".", help="Repository path")
    report_p.add_argument("--output", default="deployability-report.md", help="Output file path")

    watch_p = subparsers.add_parser("watch", help="Watch repo for changes, auto-audit")
    watch_p.add_argument("--path", default=".", help="Repository path")
    watch_p.add_argument("--interval", type=int, default=3, help="Poll interval in seconds")
    watch_p.add_argument("--fix", action="store_true", help="Auto-fix findings when possible")

    args = parser.parse_args()

    if not args.command:
        print("Dark Matter  v0.1  —  Repository Intelligence Platform")
        print()
        print("Quickstart:")
        print("  dm init .       Scan your project and build the knowledge graph")
        print("  dm scan         Update intelligence (incremental)")
        print("  dm compile      Generate repository.ai + markdown report")
        print("  dm verify       Check facts against evidence")
        print("  dm search <q>   Find anything in project knowledge")
        print("  dm audit        Run bug detectors")
        print("  dm doctor       Diagnose issues")
        print()
        print("Commands:")
        for cmd, desc in [("init", "Initialize DM for a repository"),
                          ("start", "Begin a work session"),
                          ("work", "Load context for a task"),
                          ("scan", "Update intelligence from changes"),
                          ("verify", "Check facts against evidence"),
                          ("compile", "Generate intelligence outputs"),
                          ("review", "Get pre-commit/pre-PR analysis"),
                          ("audit", "Run bug detectors"),
                          ("doctor", "Diagnose and fix issues"),
                          ("search", "Find anything in project knowledge"),
                          ("explain", "Understand why DM thinks something"),
                          ("report", "Generate deployability report"),
                          ("watch", "Watch repo for changes, auto-audit")]:
            print(f"  {cmd:<12} {desc}")
        print()
        print("Run 'dm <command> --help' for more details.")
        sys.exit(0)

    # Route to command handler
    commands = {
        "init": cmd_init,
        "start": cmd_start,
        "work": cmd_work,
        "scan": cmd_scan,
        "verify": cmd_verify,
        "compile": cmd_compile,
        "review": cmd_review,
        "audit": cmd_audit,
        "doctor": cmd_doctor,
        "search": cmd_search,
        "explain": cmd_explain,
        "report": cmd_report,
        "watch": cmd_watch,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


def _render_box(title: str, lines: list, indent: int = 0) -> str:
    prefix = "  " * indent
    result = [f"{prefix}--- {title} " + "-" * max(1, 40 - len(title))]
    for line in lines:
        result.append(f"{prefix}  {line}")
    return "\n".join(result)


def _check_aether(path: str) -> Path:
    repo = Path(path).resolve()
    aether_dir = repo / ".darkmatter"
    if not aether_dir.exists():
        print(f"Aether not initialized in {repo}")
        print(f"Run: dm init {repo}")
        sys.exit(1)
    return repo


def cmd_init(args):
    """Initialize Dark Matter for a repository."""
    repo = Path(args.path).resolve()
    aether_dir = repo / ".darkmatter"

    if aether_dir.exists() and not args.force:
        print(f"Aether already initialized in {repo}")
        print("Run with --force to re-initialize")
        return

    # Import and run the pipeline
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from dm.pipeline import Pipeline

    def show_progress(processed, total, skipped):
        print(f"\r  Scanning... {processed} files collected ({skipped} skipped)       ", end="", flush=True)

    def show_stage(stage):
        print(f"\r  {stage}...                                                ", flush=True)

    pipeline = Pipeline(str(repo))
    result = pipeline.run(progress_cb=show_progress, stage_cb=show_stage)
    print()

    print(f"\nDark Matter initialized.")
    print(f"\nScanning project structure...")
    print(f"  OK {result['nodes_created']} files found")
    print(f"  OK Evidence: {result['evidence_count']} records collected")
    print(f"  OK Graph: {result['nodes_created']} nodes, {result['edges_created']} edges")
    print(f"  OK Facts: {result['facts_derived']} inferred")
    print(f"  OK Verifications: {result['verifications_recorded']} recorded")
    print(f"\nRepository intelligence ready.")
    print(f"\nNext: dm start")


# ponytail: 6 of 12 CLI commands are stubs. They exist in the help text because the
# user story says "10 CLI commands", but only init/scan/compile/verify/audit are real.
def _stub(args, name):
    repo = _check_aether(args.path)
    print(f"\n'{name}' not yet implemented in v0.1.")
    print(f"Run 'dm scan' or 'dm audit' instead.\n")


def cmd_start(args):
    """Begin a work session."""
    repo = _check_aether(args.path)
    import json as _json
    from datetime import datetime
    sessions_dir = repo / ".darkmatter" / "sessions"
    sessions_dir.mkdir(exist_ok=True)
    session = {
        "session_id": datetime.utcnow().strftime("SES-%Y%m%d-%H%M%S"),
        "started": datetime.utcnow().isoformat(),
        "repo": str(repo),
    }
    (sessions_dir / "current.json").write_text(_json.dumps(session, indent=2))
    print(f"  Session {session['session_id']} started\n")


def cmd_work(args):
    """Load context for a task."""
    repo = _check_aether(args.path)
    import json as _json
    task = args.task or "unnamed"
    work_dir = repo / ".darkmatter" / "work"
    work_dir.mkdir(exist_ok=True)
    ctx = {
        "task": task,
        "set_at": __import__("datetime").datetime.utcnow().isoformat(),
    }
    (work_dir / "current.json").write_text(_json.dumps(ctx, indent=2))
    print(f"  Context set to task: {task}\n")


def cmd_scan(args):
    """Update intelligence from changes."""
    repo = _check_aether(args.path)
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from dm.pipeline import Pipeline

    # ponytail: default progress is minimal, skip boxes for one-liner
    if args.ponytail:
        def cb_progress(processed, total, skipped):
            pass
        def cb_stage(stage):
            print(f"  {stage}...")
    else:
        def cb_progress(processed, total, skipped):
            print(f"\r  Scanning... {processed} files collected ({skipped} skipped)  ", end="", flush=True)
        def cb_stage(stage):
            print(f"\r  {stage}...                                                ", flush=True)

    pipeline = Pipeline(str(repo))
    result = pipeline.run(incremental=not args.full, ponytail=args.ponytail,
                          progress_cb=cb_progress, stage_cb=cb_stage)
    print()
    if not args.ponytail:
        print(f"\nScanning...")
        print(_render_box("Collected", [f"Filesystem:  {result['evidence_count']} files scanned"]))
        print(_render_box("Inference", [f"{result['facts_derived']} facts inferred",
                                        f"{result['verifications_recorded']} verifications recorded"]))
    else:
        print(f"  {result['evidence_count']} files, {result['audit_findings']} findings")
    print(f"\nScan complete.")


def cmd_verify(args):
    """Check facts against evidence."""
    repo = _check_aether(args.path)

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from dm.store.json_store import JSONStore

    store = JSONStore(str(repo / ".darkmatter"))
    evidence_list = store.find_evidence()
    verifications = list(store.verifications_dir.glob("*.json"))

    import json
    ver_data = []
    for v in verifications:
        ver_data.append(json.loads(v.read_text()))

    print(f"\nVerification Results")
    print()
    if ver_data:
        verified = [v for v in ver_data if v.get("result") == "verified"]
        inconclusive = [v for v in ver_data if v.get("result") == "inconclusive"]
        rejected = [v for v in ver_data if v.get("result") == "rejected"]

        if verified:
            print("--- Verified " + "-" * 28)
            for v in verified[:5]:
                print(f"  {v['claim']} ({v.get('confidence', '?')})")
            if len(verified) > 5:
                print(f"  ... and {len(verified) - 5} more")
            print()

        if inconclusive:
            print("--- Inconclusive " + "-" * 25)
            for v in inconclusive[:3]:
                print(f"  {v['claim']} ({v.get('confidence', '?')})")
            if len(inconclusive) > 3:
                print(f"  ... and {len(inconclusive) - 3} more")
            print()

        print("--- Summary " + "-" * 29)
        print(f"  {len(verified)} verified")
        print(f"  {len(inconclusive)} inconclusive")
        print(f"  {len(rejected)} rejected")
        print(f"  {len(evidence_list)} evidence records")
    else:
        print("  No verifications recorded yet.")
        print("  Run: dm scan")
    print()


def cmd_compile(args):
    """Generate intelligence outputs."""
    repo = _check_aether(args.path)

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from dm.pipeline import Pipeline

    def show_stage(stage):
        print(f"  {stage}...")

    pipeline = Pipeline(str(repo))
    result = pipeline.run(stage_cb=show_stage)

    print(f"\nCompiling...")
    print()
    outputs = result.get("outputs", {})
    print(_render_box("Outputs", [
        f"OK {outputs.get('ai_package', 'N/A')}",
        f"OK {outputs.get('markdown', 'N/A')}",
    ]))
    print(f"\nCompilation complete.")
    print()


def cmd_review(args):
    """Get pre-commit/pre-PR analysis."""
    repo = _check_aether(args.path)
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from dm.pipeline import Pipeline
    from dm.audit import run_detectors_ponytail
    from dm.store.json_store import JSONStore
    import json as _json

    store = JSONStore(str(repo / ".darkmatter"))

    if args.pr:
        print(f"  PR review mode — checking {repo.name}\n")
    elif args.release:
        print(f"  Release review for {args.release} — checking {repo.name}\n")
    else:
        print(f"  Pre-commit review — checking {repo.name}\n")

    evidence = store.find_evidence()
    if not evidence:
        print("  No evidence found. Run 'dm scan' first.\n")
        return

    results = run_detectors_ponytail(evidence)
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    all_f = [(n, f) for n, fs in results.items() for f in fs]
    highs = [(n, f) for n, f in all_f if f.severity in ("critical", "high")]

    if not all_f:
        print("  ✅ No findings. Good to go.\n")
        return

    if highs:
        print(f"  ⛔ {len(highs)} blocking finding(s):\n")
        for name, f in highs:
            loc = f"{f.file}:{f.line}" if f.line else f.file
            print(f"    [{f.severity.upper()}] {loc}")
            print(f"           {f.description}")
        print(f"\n  Fix before committing. Run 'dm audit --fix' or fix manually.\n")
    else:
        print(f"  ⚠️  {len(all_f)} low/medium findings (non-blocking)\n")
        for name, f in all_f[:5]:
            loc = f"{f.file}:{f.line}" if f.line else f.file
            print(f"    {loc}  ({f.severity}) {f.description}")
        if len(all_f) > 5:
            print(f"    ... and {len(all_f) - 5} more")
        print()


def cmd_audit(args):
    """Run bug detectors against the project."""
    repo = _check_aether(args.path)
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from dm.store.json_store import JSONStore
    from dm.audit import run_detectors, run_detectors_ponytail

    store = JSONStore(str(repo / ".darkmatter"))
    evidence = store.find_evidence()

    # ponytail: skip graph queries entirely, regex-only detection
    if args.ponytail:
        results = run_detectors_ponytail(evidence)
    else:
        from dm.graph.service import GraphService
        graph = GraphService(store)
        def cb_progress(current, total):
            print(f"\r  Running detectors... {current}/{total}          ", end="", flush=True)
        print(f"\nAuditing {repo.name}...\n")
        results = run_detectors(graph, evidence, progress_cb=cb_progress)
        print()

    # auto-fix before filtering so --fix applies to everything
    if args.fix:
        from dm.audit.fixer import apply_all
        all_detected = [(n, f) for n, fs in results.items() for f in fs]
        fixed, failed = apply_all([f for _, f in all_detected], str(repo))
        if fixed or failed:
            print(f"  Auto-fixed: {fixed}, failed: {failed}\n")
        else:
            print("  No auto-fixable findings.\n")
        return

    SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    min_sev = args.severity
    detector_filter = args.detector

    all_findings = [(n, f) for n, fs in results.items()
                    for f in fs
                    if (not detector_filter or detector_filter.lower() in n.lower())
                    and (not min_sev or SEVERITY_ORDER.get(f.severity, 99) <= SEVERITY_ORDER.get(min_sev, 99))]

    by_severity = {}
    for _, f in all_findings:
        by_severity[f.severity] = by_severity.get(f.severity, 0) + 1

    if args.json:
        import json as _json
        out = {
            "findings": [
                {
                    "rule_id": f.rule_id,
                    "severity": f.severity,
                    "file": f.file,
                    "line": f.line,
                    "description": f.description,
                    "confidence": f.confidence,
                    "suggested_fix": f.suggested_fix,
                }
                for _, f in all_findings
            ],
            "summary": dict(sorted(by_severity.items())),
            "total": len(all_findings),
        }
        print(_json.dumps(out, indent=2))
        if all_findings:
            sys.exit(1)
        return

    if not all_findings:
        print("  No findings. Clean bill of health.\n")
        return

    all_findings.sort(key=lambda x: SEVERITY_ORDER.get(x[1].severity, 99))

    sev_counts = [f"{c} {s}" for s in ("critical", "high", "medium", "low", "info") if (c := by_severity.get(s))]

    # ponytail: one-liner output, no boxes
    if args.ponytail:
        print(f"  {', '.join(sev_counts)}\n")
        for name, f in all_findings:
            loc = f"{f.file}" + (f":{f.line}" if f.line else "")
            print(f"  {loc}  ({f.severity}) {f.description}")
        print(f"\n  {len(all_findings)} findings\n")
        sys.exit(1)
        return

    print(f"  Found: {', '.join(sev_counts)}\n")
    for name, f in all_findings:
        loc = f"{f.file}" + (f":{f.line}" if f.line else "")
        conf = f" ({f.confidence:.0%})" if f.confidence else ""
        print(f"  [{f.severity.upper():<8}] {loc}{conf}")
        print(f"          {f.description}")
        if f.suggested_fix:
            print(f"          => {f.suggested_fix}")
        print()
    print(f"  {len(all_findings)} total findings across {len(results)} detectors\n")
    sys.exit(1)


def cmd_doctor(args):
    """Diagnose and fix issues."""
    repo = Path(args.path).resolve()
    dm_dir = repo / ".darkmatter"

    if not dm_dir.exists():
        print(f"  Dark Matter not initialized in {repo}")
        print(f"  Run: dm init {repo}")
        return

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from dm.store.json_store import JSONStore
    import json as _json

    store = JSONStore(str(dm_dir))
    issues = []

    # check required dirs
    for name in ["events", "nodes", "edges", "evidence", "verifications", "rules"]:
        d = dm_dir / name
        if not d.exists():
            issues.append({"type": "missing_dir", "path": str(d), "fix": f"mkdir -p {d}"})

    # check for orphan edges
    all_nodes = set()
    for kind_dir in store.nodes_dir.iterdir():
        if kind_dir.is_dir():
            for f in kind_dir.glob("*.json"):
                all_nodes.add(f.stem)
    for edge_file in store.edges_dir.rglob("*.json"):
        edge = _json.loads(edge_file.read_text())
        if edge["source_id"] not in all_nodes:
            issues.append({"type": "orphan_edge", "file": str(edge_file), "detail": f"source {edge['source_id']} not found", "fix": f"rm {edge_file}"})
        if edge["target_id"] not in all_nodes:
            issues.append({"type": "orphan_edge", "file": str(edge_file), "detail": f"target {edge['target_id']} not found", "fix": f"rm {edge_file}"})

    # check evidence integrity
    for ev_file in store.evidence_dir.glob("*.json"):
        try:
            ev = _json.loads(ev_file.read_text())
            if not ev.get("payload"):
                issues.append({"type": "corrupt_evidence", "file": str(ev_file), "detail": "missing payload", "fix": f"rm {ev_file}"})
        except _json.JSONDecodeError:
            issues.append({"type": "corrupt_evidence", "file": str(ev_file), "detail": "invalid JSON", "fix": f"rm {ev_file}"})

    if args.fix:
        fixed = 0
        for issue in issues:
            if issue["type"] == "missing_dir":
                Path(issue["path"]).mkdir(parents=True, exist_ok=True)
                fixed += 1
            elif issue["type"] == "orphan_edge":
                Path(issue["file"]).unlink(missing_ok=True)
                fixed += 1
            elif issue["type"] == "corrupt_evidence":
                Path(issue["file"]).unlink(missing_ok=True)
                fixed += 1
        print(f"  Fixed {fixed} issue(s)\n")
        return

    if not issues:
        print("  Store is healthy. No issues found.\n")
        return

    print(f"  Found {len(issues)} issue(s):\n")
    for issue in issues:
        print(f"  [{issue['type']}] {issue.get('detail', issue['path'])}")
        if issue.get("fix"):
            print(f"           fix: {issue['fix']}")
    print(f"\n  Run 'dm doctor --fix' to auto-repair\n")


def cmd_search(args):
    """Find anything in project knowledge."""
    repo = _check_aether(args.path)
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from dm.store.json_store import JSONStore
    import json as _json

    store = JSONStore(str(repo / ".darkmatter"))
    evidence = store.find_evidence()
    query = args.query.lower()
    limit = args.limit
    results = []

    for ev in evidence:
        payload = ev.get("payload", {})
        preview = payload.get("content_preview", "").lower()
        rpath = payload.get("relative_path", "")
        if query in rpath.lower() or query in preview:
            results.append({
                "path": rpath,
                "file_path": payload.get("path", ""),
                "evidence_id": ev.get("id", ""),
                "confidence_weight": ev.get("confidence_weight", 0.5),
            })
        if len(results) >= limit:
            break

    if args.json:
        print(_json.dumps({"results": results, "total": len(results), "query": args.query}, indent=2))
        return

    if not results:
        print(f"  No results for '{args.query}'")
        return
    print(f"  Found {len(results)} result(s) for '{args.query}':\n")
    for r in results:
        print(f"  {r['path']}  (evidence: {r['evidence_id']})")
    print()


def cmd_explain(args):
    """Understand why Dark Matter thinks something."""
    repo = _check_aether(args.path)
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from dm.store.json_store import JSONStore
    import json as _json

    store = JSONStore(str(repo / ".darkmatter"))
    verifications = list(store.verifications_dir.glob("*.json"))
    claim = args.claim.lower()
    matches = []

    for vp in verifications:
        v = _json.loads(vp.read_text())
        if claim in v.get("claim", "").lower():
            matches.append(v)

    if args.json:
        print(_json.dumps({"claim": args.claim, "matches": matches, "total": len(matches)}, indent=2))
        return

    if not matches:
        print(f"  No explanations found for '{args.claim}'")
        print("  Run 'dm scan' first to generate facts and verifications.")
        return

    for v in matches:
        print(f"  {v['claim']}")
        print(f"    Result: {v.get('result', 'unknown')}")
        print(f"    Confidence: {v.get('confidence', '?')}")
        print(f"    Reason: {v.get('reason', 'N/A')}")
        if v.get("evidence_used"):
            print(f"    Evidence ({len(v['evidence_used'])} sources):")
            for eid in v["evidence_used"][:5]:
                ev = store.get_evidence(eid)
                if ev:
                    rp = ev.get("payload", {}).get("relative_path", eid)
                    print(f"      - {rp}")
        print()


def cmd_report(args):
    """Generate deployability report for engineer handoff."""
    repo = _check_aether(args.path)
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from dm.pipeline import Pipeline
    from dm.compiler.report import generate

    def show_stage(stage):
        print(f"  {stage}...")

    pipeline = Pipeline(str(repo))
    result = pipeline.run(stage_cb=show_stage)

    out_path = repo / args.output
    generate(result, str(out_path))
    print(f"\n  Report written to {out_path}\n")


def cmd_watch(args):
    """Watch repo for changes, auto-audit."""
    from dm.cli.watch import watch
    watch(args.path, interval=args.interval, fix=args.fix)


if __name__ == "__main__":
    main()
