from . import structural, regex

DETECTORS = [
    ("Structural: Orphan Files", structural.orphan_files),
    ("Structural: Bloated Files", structural.bloated_files),
    ("Structural: Duplicate Files", structural.duplicate_files),
    ("Structural: TODO Density", structural.todo_density),
    ("Structural: Missing Tests", structural.missing_tests),
    ("Regex: Hardcoded Secrets", regex.hardcoded_secrets),
    ("Regex: SQL Injection", regex.sql_injection),
    ("Regex: Empty Catch", regex.empty_catch),
    ("Regex: Console Log", regex.console_log),
    ("Regex: Eval Usage", regex.eval_usage),
    ("Regex: TODO Without Ticket", regex.todo_without_ticket),
    ("Regex: Insecure Compare", regex.insecure_compare),
]

# ponytail: regex-only detectors skip graph queries, no graph service needed
PONYTAIL_DETECTORS = [
    ("Regex: Hardcoded Secrets", regex.hardcoded_secrets),
    ("Regex: SQL Injection", regex.sql_injection),
    ("Regex: Empty Catch", regex.empty_catch),
    ("Regex: Console Log", regex.console_log),
    ("Regex: Eval Usage", regex.eval_usage),
    ("Regex: TODO Without Ticket", regex.todo_without_ticket),
    ("Regex: Insecure Compare", regex.insecure_compare),
]


def run_detectors(graph, evidence, progress_cb=None) -> dict:
    results = {}
    total = len(DETECTORS)
    for i, (name, detector) in enumerate(DETECTORS):
        try:
            findings = detector(graph, evidence)
            results[name] = findings
        except Exception:
            results[name] = []
        if progress_cb:
            progress_cb(i + 1, total)
    return results


def run_detectors_ponytail(evidence, progress_cb=None) -> dict:
    """Regex-only audit, no graph queries. ~6x faster, no structural checks."""
    results = {}
    total = len(PONYTAIL_DETECTORS)
    for i, (name, detector) in enumerate(PONYTAIL_DETECTORS):
        try:
            # ponytail: regex detectors accept (graph, evidence) but only use evidence
            findings = detector(None, evidence)
            results[name] = findings
        except Exception:
            results[name] = []
        if progress_cb:
            progress_cb(i + 1, total)
    return results
