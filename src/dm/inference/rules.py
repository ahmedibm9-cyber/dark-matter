import re
from . import rule_loader

HARDCODED_RULES = [
    {
        "id": "RULE-0001",
        "name": "detect-framework",
        "description": "Detect web frameworks from package.json dependencies",
        "category": "semantic",
        "inputs": [{"kind": "file", "pattern": "package.json"}],
        "patterns": {
            "express": {"framework": "Express.js", "category": "backend"},
            "react": {"framework": "React", "category": "frontend"},
            "next": {"framework": "Next.js", "category": "fullstack"},
            "django": {"framework": "Django", "category": "backend"},
            "flask": {"framework": "Flask", "category": "backend"},
            "fastapi": {"framework": "FastAPI", "category": "backend"},
            "spring": {"framework": "Spring", "category": "backend"},
            "rails": {"framework": "Ruby on Rails", "category": "backend"},
            "laravel": {"framework": "Laravel", "category": "backend"},
            "vue": {"framework": "Vue.js", "category": "frontend"},
            "angular": {"framework": "Angular", "category": "frontend"},
            "svelte": {"framework": "Svelte", "category": "frontend"},
            "jsonwebtoken": {"framework": "JWT", "category": "auth"},
            "stripe": {"framework": "Stripe", "category": "payments"},
            "redis": {"framework": "Redis", "category": "cache"},
            "jest": {"framework": "Jest", "category": "testing"},
            "typescript": {"framework": "TypeScript", "category": "language"},
        },
    },
    {
        "id": "RULE-0002",
        "name": "detect-architecture-from-readme",
        "description": "Infer architecture patterns from README content",
        "category": "structural",
        "inputs": [{"kind": "file", "pattern": "README.md"}],
        "patterns": {
            "microservice": {"pattern": "microservice", "architecture": "Microservices"},
            "monolith": {"pattern": "monolith", "architecture": "Monolithic"},
            "layered": {"pattern": "layer", "architecture": "Layered"},
            "event-driven": {"pattern": "event", "architecture": "Event-Driven"},
            "serverless": {"pattern": "serverless", "architecture": "Serverless"},
        },
    },
]

def run_rules(evidence_list: list, rules_dir: str = None) -> list:
    # ponytail: keyword substring matching, no NLP/semantic. Add AST-based detection if keyword ceiling hits.
    rules = rule_loader.load_rules(rules_dir) or HARDCODED_RULES
    facts = []
    for rule in rules:
        for ev in evidence_list:
            payload = ev.get("payload", {})
            content = payload.get("content_preview", "")
            for key, info in rule.get("patterns", {}).items():
                if key.lower() in content.lower():
                    facts.append({
                        "statement": f"Uses {info.get('framework', info.get('architecture', key))}",
                        "category": rule["category"],
                        "rule_id": rule["id"],
                        "evidence_refs": [ev.get("id", "")],
                        "confidence": ev.get("confidence_weight", 0.5) * 0.9,
                        "details": info,
                    })
    return facts
