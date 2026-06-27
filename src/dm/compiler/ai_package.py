import json
import hashlib
from datetime import datetime

def compile_ai_package(graph_state: dict, output_path: str):
    findings_raw = graph_state.get("audit_findings", {})
    findings_list = []
    for detector_name, det_findings in findings_raw.items():
        for f in det_findings:
            findings_list.append({
                "detector": detector_name,
                "rule_id": f.rule_id,
                "severity": f.severity,
                "file": f.file,
                "line": f.line,
                "description": f.description,
                "confidence": f.confidence,
                "suggested_fix": f.suggested_fix,
            })
    pkg = {
        "aether_version": "1.0.0",
        "generated_at": datetime.utcnow().isoformat(),
        "graph_version": graph_state.get("graph_version", "1.0.0"),
        "genome": {
            "nodes_count": len(graph_state.get("files", [])) + (1 if graph_state.get("repo_node") else 0),
            "edges_count": graph_state.get("edge_count", 0),
            "facts_count": len(graph_state.get("facts", [])),
            "verifications_count": len(graph_state.get("verifications", [])),
            "findings_count": len(findings_list),
            "languages": list(set(f.get("properties", {}).get("extension", "") for f in graph_state.get("files", []))),
        },
        "nodes": [],
        "edges": [],
        "facts": graph_state.get("facts", []),
        "verifications": graph_state.get("verifications", []),
        "findings": findings_list,
    }

    repo = graph_state.get("repo_node")
    if repo:
        pkg["nodes"].append({
            "id": repo["id"],
            "kind": repo["kind"],
            "name": repo["name"],
            "properties": repo["properties"],
        })

    for f in graph_state.get("files", []):
        pkg["nodes"].append({
            "id": f["id"],
            "kind": f["kind"],
            "name": f["name"],
            "properties": {k: v for k, v in f.get("properties", {}).items() if k != "content_preview"},
        })

    for e in graph_state.get("edges", []):
        pkg["edges"].append({
            "source_id": e["source_id"],
            "target_id": e["target_id"],
            "kind": e["kind"],
        })

    raw = json.dumps(pkg, indent=2, default=str)
    pkg["checksum"] = hashlib.sha256(raw.encode()).hexdigest()[:16]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pkg, f, indent=2, default=str)
    return output_path
