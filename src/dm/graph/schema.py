from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Node:
    id: str
    kind: str
    name: str
    properties: dict = field(default_factory=dict)
    evidence_refs: list = field(default_factory=list)
    created: datetime = field(default_factory=datetime.utcnow)
    modified: datetime = field(default_factory=datetime.utcnow)
    observed: datetime = field(default_factory=datetime.utcnow)
    verified: Optional[datetime] = None
    expired: Optional[datetime] = None
    tags: list = field(default_factory=list)

    def checksum(self) -> str:
        import hashlib
        raw = f"{self.kind}{self.name}{sorted(self.properties.items())}{sorted(self.evidence_refs)}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

@dataclass
class Edge:
    source_id: str
    target_id: str
    kind: str
    properties: dict = field(default_factory=dict)
    evidence_refs: list = field(default_factory=list)
    created: datetime = field(default_factory=datetime.utcnow)
    modified: datetime = field(default_factory=datetime.utcnow)

    def key(self) -> tuple:
        return (self.source_id, self.target_id, self.kind)
