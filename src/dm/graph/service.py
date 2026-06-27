from datetime import datetime
from pathlib import Path
from .schema import Node, Edge


class GraphService:
    """Canonical gateway for all graph mutations and queries."""

    def __init__(self, store):
        self._store = store

    # --- Evidence ---
    def add_evidence(self, evidence: dict) -> dict:
        result = self._store.store_evidence(evidence)
        self._store.append_event({
            "kind": "EVIDENCE_INGESTED",
            "entity_id": result["id"],
            "entity_kind": "EVIDENCE",
            "payload": {"evidence_kind": evidence.get("kind"), "source": evidence.get("source")},
        })
        return result

    def get_evidence(self, eid: str) -> dict:
        return self._store.get_evidence(eid)

    def find_evidence(self, kind: str = None) -> list:
        return self._store.find_evidence(kind)

    def known_path_hashes(self) -> dict:
        return self._store.known_path_hashes()

    def events(self, after_seq: int = 0) -> list:
        return self._store.get_events(after_seq)

    # --- Nodes ---
    def add_node(self, kind: str, name: str, properties: dict = None,
                 evidence_refs: list = None) -> dict:
        node = Node(
            id=self._store.next_id(kind),
            kind=kind,
            name=name,
            properties=properties or {},
            evidence_refs=evidence_refs or [],
        )
        result = self._store.create_node(node)
        if result.get("success"):
            self._store.append_event({
                "kind": "NODE_CREATED",
                "entity_id": node.id,
                "entity_kind": kind,
                "payload": {"name": name},
            })
            return {"node": node.__dict__, "id": node.id}
        return result

    def add_node_with_id(self, node_id: str, kind: str, name: str,
                         properties: dict = None, evidence_refs: list = None) -> dict:
        node = Node(
            id=node_id,
            kind=kind,
            name=name,
            properties=properties or {},
            evidence_refs=evidence_refs or [],
        )
        result = self._store.create_node(node)
        return {"node": node.__dict__, "created": result.get("success", False), "id": node.id}

    def get_node(self, nid: str) -> dict:
        return self._store.get_node(nid)

    def get_nodes_by_kind(self, kind: str) -> list:
        return self._store.get_nodes_by_kind(kind)

    # --- Edges ---
    def add_edge(self, source_id: str, target_id: str, kind: str,
                 evidence_refs: list = None) -> dict:
        edge = Edge(
            source_id=source_id,
            target_id=target_id,
            kind=kind,
            evidence_refs=evidence_refs or [],
        )
        result = self._store.create_edge(edge)
        return {"edge": edge.__dict__, "created": result.get("success", False)}

    def get_edges(self, kind: str = None) -> list:
        return self._store.get_edges(kind)

    def get_neighbors(self, nid: str) -> list:
        return self._store.get_neighbors(nid)

    # --- Convenience ---
    def query(self, **filters) -> list:
        # ponytail: linear scan over all JSON files, no index. Fine for <10K files.
        results = []
        for kind_dir in self._store.nodes_dir.iterdir():
            if not kind_dir.is_dir():
                continue
            for f in kind_dir.glob("*.json"):
                import json
                node = json.loads(f.read_text())
                match = True
                for k, v in filters.items():
                    if k == "kind":
                        if node.get("kind") != v:
                            match = False
                    elif k in node.get("properties", {}):
                        if node["properties"][k] != v:
                            match = False
                    elif k in node:
                        if node[k] != v:
                            match = False
                    else:
                        match = False
                if match:
                    results.append(node)
        return results
