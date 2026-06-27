import json
import os
import hashlib
from datetime import datetime
from pathlib import Path

class JSONStore:
    def __init__(self, path: str):
        self.root = Path(path)
        self.events_dir = self.root / "events"
        self.nodes_dir = self.root / "nodes"
        self.edges_dir = self.root / "edges"
        self.evidence_dir = self.root / "evidence"
        self.verifications_dir = self.root / "verifications"
        self.rules_dir = self.root / "rules"
        self.meta_file = self.root / "meta.json"
        self._ensure_dirs()
        self._event_seq = self._load_seq()

    def _ensure_dirs(self):
        for d in [self.events_dir, self.nodes_dir, self.edges_dir,
                  self.evidence_dir, self.verifications_dir, self.rules_dir]:
            d.mkdir(parents=True, exist_ok=True)
        default_rules = self.rules_dir / "default.yaml"
        if not default_rules.exists():
            import importlib.resources as res
            try:
                rules_text = res.read_text("dm.inference", "default_rules.yaml")
                default_rules.write_text(rules_text, encoding="utf-8")
            except Exception:
                pass  # Fallback: no default rules file written

    def _load_seq(self) -> int:
        if self.meta_file.exists():
            meta = json.loads(self.meta_file.read_text())
            return meta.get("event_sequence", 0)
        return 0

    def _save_seq(self):
        self.meta_file.write_text(json.dumps({"event_sequence": self._event_seq}, indent=2))

    def known_path_hashes(self) -> dict:
        """Return dict of relative_path → content_hash for all stored evidence."""
        path_hashes = {}
        for f in self.evidence_dir.glob("*.json"):
            rec = json.loads(f.read_text())
            payload = rec.get("payload", {})
            rpath = payload.get("relative_path", "")
            chash = payload.get("hash", "")
            if rpath and chash:
                path_hashes[rpath] = chash
        return path_hashes

    def next_id(self, kind: str) -> str:
        # ponytail: file-based counter, not atomic. Fine for single-user CLI.
        prefix = kind.upper()[:8]
        meta = json.loads(self.meta_file.read_text()) if self.meta_file.exists() else {}
        counters = meta.get("id_counters", {})
        n = counters.get(prefix, 0) + 1
        counters[prefix] = n
        meta["id_counters"] = counters
        self.meta_file.write_text(json.dumps(meta, indent=2))
        return f"{prefix}-{n:05d}"

    def _kind_dir(self, kind: str) -> Path:
        d = self.nodes_dir / kind.lower()
        d.mkdir(exist_ok=True)
        return d

    # --- Evidence ---
    def store_evidence(self, evidence: dict) -> dict:
        payload = evidence.get("payload", {})
        raw = f"{evidence['kind']}{evidence['source']}{json.dumps(payload, sort_keys=True)}"
        h = hashlib.sha256(raw.encode()).hexdigest()
        existing = list(self.evidence_dir.glob(f"*_{h}.json"))
        if existing:
            eid = existing[0].stem.split("_")[0]
            return {"id": eid, "hash": h, "deduplicated": True}
        eid = evidence.get("id") or self.next_id("EVID")
        rec = {**evidence, "id": eid, "hash": h, "ingested_at": datetime.utcnow().isoformat()}
        (self.evidence_dir / f"{eid}_{h}.json").write_text(json.dumps(rec, indent=2, default=str))
        return {"id": eid, "hash": h, "deduplicated": False}

    def get_evidence(self, eid: str) -> dict:
        for f in self.evidence_dir.glob(f"{eid}_*.json"):
            return json.loads(f.read_text())
        return None

    def find_evidence(self, kind: str = None) -> list:
        results = []
        for f in self.evidence_dir.glob("*.json"):
            rec = json.loads(f.read_text())
            if kind is None or rec.get("kind") == kind:
                results.append(rec)
        return results

    # --- Nodes ---
    def create_node(self, node) -> dict:
        nd = node.__dict__.copy()
        nd["created"] = nd["created"].isoformat()
        nd["modified"] = nd["modified"].isoformat()
        nd["observed"] = nd["observed"].isoformat()
        nd["verified"] = nd["verified"].isoformat() if nd["verified"] else None
        nd["expired"] = nd["expired"].isoformat() if nd["expired"] else None
        nd["checksum"] = node.checksum()
        path = self._kind_dir(node.kind) / f"{node.id}.json"
        if path.exists():
            return {"success": False, "error": "duplicate_id"}
        path.write_text(json.dumps(nd, indent=2, default=str))
        return {"success": True, "node": nd}

    def get_node(self, nid: str) -> dict:
        for kind_dir in self.nodes_dir.iterdir():
            if kind_dir.is_dir():
                p = kind_dir / f"{nid}.json"
                if p.exists():
                    return json.loads(p.read_text())
        return None

    def get_nodes_by_kind(self, kind: str) -> list:
        d = self._kind_dir(kind)
        return [json.loads(f.read_text()) for f in d.glob("*.json")]

    # --- Edges ---
    def create_edge(self, edge) -> dict:
        ek = edge.key()
        d = self.edges_dir / edge.kind.lower()
        d.mkdir(exist_ok=True)
        fname = f"{edge.source_id}__{edge.target_id}.json"
        path = d / fname
        if path.exists():
            return {"success": False, "error": "duplicate_edge"}
        rec = edge.__dict__.copy()
        rec["created"] = rec["created"].isoformat()
        rec["modified"] = rec["modified"].isoformat()
        rec["source_id"] = edge.source_id
        rec["target_id"] = edge.target_id
        path.write_text(json.dumps(rec, indent=2, default=str))
        return {"success": True, "edge": rec}

    def get_edges(self, kind: str = None) -> list:
        results = []
        search = [self.edges_dir / kind.lower()] if kind else self.edges_dir.iterdir()
        for d in search:
            if d.is_dir():
                for f in d.glob("*.json"):
                    results.append(json.loads(f.read_text()))
        return results

    def get_neighbors(self, nid: str) -> list:
        neighbors = []
        for edge in self.get_edges():
            if edge["source_id"] == nid:
                node = self.get_node(edge["target_id"])
                if node:
                    neighbors.append({"node": node, "edge": edge, "direction": "outbound"})
            if edge["target_id"] == nid:
                node = self.get_node(edge["source_id"])
                if node:
                    neighbors.append({"node": node, "edge": edge, "direction": "inbound"})
        return neighbors

    # --- Events ---
    def append_event(self, event: dict) -> dict:
        self._event_seq += 1
        event["sequence"] = self._event_seq
        event["timestamp"] = datetime.utcnow().isoformat()
        fname = f"{self._event_seq:07d}.json"
        (self.events_dir / fname).write_text(json.dumps(event, indent=2, default=str))
        self._save_seq()
        return {"sequence": self._event_seq}

    def get_events(self, after_seq: int = 0) -> list:
        events = []
        for f in sorted(self.events_dir.glob("*.json")):
            ev = json.loads(f.read_text())
            if ev["sequence"] > after_seq:
                events.append(ev)
        return events

    # --- Verifications ---
    def store_verification(self, ver: dict) -> str:
        vid = ver.get("id") or self.next_id("VERIFY")
        ver["id"] = vid
        ver["timestamp"] = datetime.utcnow().isoformat()
        (self.verifications_dir / f"{vid}.json").write_text(json.dumps(ver, indent=2, default=str))
        return vid
