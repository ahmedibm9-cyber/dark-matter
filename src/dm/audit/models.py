from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Finding:
    rule_id: str
    severity: str
    file: str
    line: Optional[int]
    description: str
    confidence: float
    suggested_fix: Optional[str] = None
    evidence_ref: Optional[str] = None
