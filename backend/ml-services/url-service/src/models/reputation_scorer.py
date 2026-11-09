"""Heuristic domain reputation scorer"""
from typing import Dict


class ReputationScorer:
    """Score a domain from 0 (very bad) to 100 (very good) using simple signals."""

    def calculate_score(self, domain_analysis: Dict) -> Dict:
        score = 80.0

        patterns = domain_analysis.get("suspicious_patterns", []) or []
        keyword_hits = [p for p in patterns if str(p).startswith("suspicious_keyword_")]
        score -= 10.0 * len(keyword_hits)
        if "excessive_hyphens" in patterns:
            score -= 10.0
        if "non_ascii_characters" in patterns:
            score -= 20.0
        if "excessive_length" in patterns:
            score -= 10.0

        if domain_analysis.get("has_numbers"):
            score -= 5.0
        if domain_analysis.get("is_ip_address"):
            score -= 30.0
        if domain_analysis.get("character_entropy", 0.0) > 3.8:
            score -= 10.0
        if domain_analysis.get("subdomain_count", 0) > 3:
            score -= 10.0

        age_days = domain_analysis.get("age_days")
        if age_days is not None:
            if age_days < 30:
                score -= 25.0
            elif age_days < 180:
                score -= 10.0
            elif age_days > 730:
                score += 10.0

        if "has_valid_ssl" in domain_analysis:
            score += 5.0 if domain_analysis["has_valid_ssl"] else -10.0
        if "has_dns" in domain_analysis and not domain_analysis["has_dns"]:
            score -= 20.0

        score = max(0.0, min(100.0, score))

        if score >= 70:
            risk_level = "low"
        elif score >= 50:
            risk_level = "medium"
        elif score >= 30:
            risk_level = "high"
        else:
            risk_level = "critical"

        return {"reputation_score": round(score, 1), "risk_level": risk_level}
