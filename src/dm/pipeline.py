import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

from .graph.service import GraphService
from .store.json_store import JSONStore
from .collectors import filesystem
from .inference import rules
from .verification import verifier
from .compiler import markdown, ai_package
from .audit import run_detectors, run_detectors_ponytail

DEFAULT_STORE_PATH = ".darkmatter"

class Pipeline:
    def __init__(self, repo_path: str, store_path: Optional[str] = None):
        self.repo_path = Path(repo_path)
        self.store = JSONStore(store_path or str(self.repo_path / DEFAULT_STORE_PATH))
        self.graph = GraphService(self.store)
        self.graph_version = "1.0.0"

    def run(self, incremental: bool = False, ponytail: bool = False,
            progress_cb: Optional[Callable] = None, stage_cb: Optional[Callable] = None) -> dict:
        # 1. Collect (incremental: skip files with known content hashes)
        if stage_cb:
            stage_cb("collecting")
        # ponytail: content hash skip, no binary/10MB/5K-limit checks (collector already does this)
        evidence_raw = filesystem.collect(str(self.repo_path), progress_cb)
        if incremental:
            known = self.graph.known_path_hashes()
            evidence_raw = [ev for ev in evidence_raw
                            if ev.get("payload", {}).get("hash", "")
                            != known.get(ev.get("payload", {}).get("relative_path", ""))]
        if stage_cb:
            stage_cb("storing evidence")
        # 2. Store evidence via GraphService (handles dedup + events)
        stored_evidence = []
        for ev in evidence_raw:
            result = self.graph.add_evidence(ev)
            ev["id"] = result["id"]
            ev["hash"] = result.get("hash", "")
            ev["deduplicated"] = result["deduplicated"]
            stored_evidence.append(ev)

        # 3. Create repo node (deterministic ID from repo path)
        if stage_cb:
            stage_cb("building graph")
        repo_id = f"REPO-{hashlib.sha256(str(self.repo_path.absolute()).encode()).hexdigest()[:12]}"
        repo_result = self.graph.add_node_with_id(
            node_id=repo_id,
            kind="REPOSITORY",
            name=self.repo_path.name,
            properties={"root_path": str(self.repo_path.absolute())},
            evidence_refs=[ev["id"] for ev in stored_evidence],
        )
        repo_node = repo_result["node"]

        # 4. Create file nodes + edges (deterministic: same evidence hash → same node/edge)
        # ponytail: no graph builder abstraction needed, direct loop is fine for v0.1
        file_nodes = []
        edges = []
        for ev in stored_evidence:
            ev_hash = ev.get("hash", "")
            fnode_id = f"FILE-{ev_hash[:12]}" if ev_hash else self.store.next_id("FILE")
            payload = ev.get("payload", {})
            fnode_result = self.graph.add_node_with_id(
                node_id=fnode_id,
                kind="FILE",
                name=payload.get("relative_path", "unknown"),
                properties={
                    "path": payload.get("path", ""),
                    "relative_path": payload.get("relative_path", ""),
                    "extension": payload.get("extension", ""),
                    "line_count": payload.get("line_count", 0),
                    "size_bytes": payload.get("size_bytes", 0),
                },
                evidence_refs=[ev["id"]],
            )
            fnode = fnode_result["node"]
            file_nodes.append(fnode)

            self.graph.add_edge(
                source_id=repo_node["id"],
                target_id=fnode["id"],
                kind="CONTAINS",
                evidence_refs=[ev["id"]],
            )
            edges.append({
                "source_id": repo_node["id"],
                "target_id": fnode["id"],
                "kind": "CONTAINS",
                "evidence_refs": [ev["id"]],
            })

        # 5. Inference (skip in ponytail mode)
        # ponytail: keyword-match rules are cheap but still ~O(n*m), skip when quick results matter
        facts = []
        verifications = []
        if not ponytail:
            if stage_cb:
                stage_cb("inferring facts")
            rules_dir = self.store.root / "rules" if hasattr(self.store, 'root') else None
            facts = rules.run_rules(stored_evidence, str(rules_dir) if rules_dir and rules_dir.exists() else None)
            for fact in facts:
                self.store.append_event({
                    "kind": "FACT_DERIVED",
                    "entity_id": fact.get("statement", ""),
                    "entity_kind": "FACT",
                    "payload": {"rule_id": fact.get("rule_id", "")},
                })

            # 6. Verification (skip in ponytail mode)
            if stage_cb:
                stage_cb("verifying facts")
            for fact in facts:
                relevant_evidence = [ev for ev in stored_evidence
                                     if ev["id"] in fact.get("evidence_refs", [])]
                result = verifier.verify_claim(fact["statement"], relevant_evidence)
                vid = self.store.store_verification(result)
                result["id"] = vid
                verifications.append(result)

        # 7. Audit
        if stage_cb:
            stage_cb("auditing")
        if ponytail:
            # ponytail: regex-only detectors, no graph queries needed
            audit_results = run_detectors_ponytail(stored_evidence)
        else:
            audit_results = run_detectors(self.graph, stored_evidence)
        total_findings = sum(len(v) for v in audit_results.values())

        # 8. Build graph state
        graph_state = {
            "generated_at": datetime.utcnow().isoformat(),
            "graph_version": self.graph_version,
            "repo_node": repo_node,
            "files": file_nodes,
            "edges": edges,
            "facts": facts,
            "verifications": verifications,
            "edge_count": len(edges),
            "audit_findings": audit_results,
        }

        # 9. Compile (skip in ponytail mode)
        outputs = {}
        if not ponytail:
            if stage_cb:
                stage_cb("compiling outputs")
            out_dir = self.repo_path / "output"
            out_dir.mkdir(exist_ok=True)
            md_path = str(out_dir / "repository-intelligence.md")
            markdown.compile_markdown(graph_state, md_path)
            ai_path = str(out_dir / "repository.ai")
            ai_package.compile_ai_package(graph_state, ai_path, str(self.repo_path))
            outputs = {"markdown": md_path, "ai_package": ai_path}

        return {
            "evidence_count": len(stored_evidence),
            "nodes_created": 1 + len(file_nodes),
            "edges_created": len(edges),
            "facts_derived": len(facts),
            "verifications_recorded": len(verifications),
            "audit_findings": total_findings,
            "outputs": outputs,
        }
