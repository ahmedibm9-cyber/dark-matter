import yaml
from pathlib import Path


def load_rules(rules_dir: str = None) -> list[dict]:
    if not rules_dir:
        return []
    p = Path(rules_dir)
    if not p.exists():
        return []
    rules = []
    for f in sorted(p.glob("*.yaml")):
        with open(f) as fh:
            rules.extend(yaml.safe_load(fh) or [])
    return rules
