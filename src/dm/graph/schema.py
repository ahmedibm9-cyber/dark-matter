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


@dataclass
class Edge:
    source_id: str
    target_id: str
    kind: str
    properties: dict = field(default_factory=dict)
    evidence_refs: list = field(default_factory=list)
    created: datetime = field(default_factory=datetime.utcnow)
    modified: datetime = field(default_factory=datetime.utcnow)
