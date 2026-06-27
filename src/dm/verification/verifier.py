from datetime import datetime


def verify_claim(claim: str, evidence_list: list, threshold: float = 0.7) -> dict:
    if not evidence_list:
        return {
            "claim": claim,
            "result": "inconclusive",
            "confidence": 0.0,
            "reason": "No supporting evidence",
            "evidence_used": [],
            "evidence_missing": [],
        }

    now = datetime.utcnow()
    adjusted_weights = []
    evidence_used = []

    for ev in evidence_list:
        weight = ev.get("confidence_weight", 0.5)
        collected = ev.get("collected_at")
        if collected:
            try:
                age_days = (now - datetime.fromisoformat(collected)).total_seconds() / 86400.0
            except (ValueError, TypeError):
                age_days = 0
        else:
            age_days = 0

        ev_kind = ev.get("kind", "file")
        half_life = 30
        freshness = 0.9 ** (age_days / half_life) if half_life > 0 else 1.0
        source = ev.get("source", "filesystem")
        trust = 0.95 if source == "filesystem" else 0.50

        adjusted = weight * freshness * trust
        adjusted_weights.append(adjusted)
        evidence_used.append(ev.get("id", ""))

    # ponytail: naive product-of-complements instead of Bayesian combination.
    # This is a valid probability (no evidence can increase confidence above 1)
    # but doesn't handle dependent evidence. Upgrade to Dempster-Shafer if needed.
    product = 1.0
    for w in adjusted_weights:
        product *= (1.0 - w)
    confidence = 1.0 - product

    if confidence >= threshold:
        result = "verified"
    elif confidence >= threshold * 0.5:
        result = "inconclusive"
    else:
        result = "rejected"

    return {
        "claim": claim,
        "result": result,
        "confidence": round(confidence, 4),
        "reason": f"Computed from {len(evidence_list)} evidence sources",
        "evidence_used": evidence_used,
        "evidence_missing": [],
    }
