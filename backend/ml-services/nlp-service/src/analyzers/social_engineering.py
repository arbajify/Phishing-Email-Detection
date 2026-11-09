"""Social engineering indicator detection"""
import re
from typing import Dict, List


class SocialEngineeringAnalyzer:
    """Detect social engineering tactics"""
    
    def __init__(self):
        # Authority impersonation indicators
        self.authority_keywords = [
            'bank', 'paypal', 'microsoft', 'google', 'amazon', 'apple',
            'irs', 'fbi', 'police', 'government', 'tax', 'security team',
            'support team', 'administrator', 'manager', 'ceo', 'president'
        ]
        
        # Action request indicators
        self.action_keywords = [
            'click here', 'verify now', 'confirm now', 'update now',
            'download', 'install', 'login', 'sign in', 'enter your',
            'provide your', 'send us', 'call us', 'reply with'
        ]
        
        # Reward/prize indicators
        self.reward_keywords = [
            'won', 'winner', 'prize', 'reward', 'free', 'gift',
            'congratulations', 'selected', 'claim', 'bonus'
        ]
        
        # Threat indicators
        self.threat_keywords = [
            'suspend', 'close', 'terminate', 'cancel', 'delete',
            'expire', 'lock', 'block', 'restrict', 'penalty'
        ]

        # Payment-request scams (gift cards, wires, crypto)
        self.payment_patterns = [
            r'\b(buy|purchase|get|pick up|order|send)\b[^.]{0,50}\bgift ?cards?\b',
            r'\bscratch (off|the)\b',
            r'\bwire (the )?(money|transfer|funds)\b',
            r'\bwestern union\b',
            r'\bmoneygram\b',
            r'\b(bitcoin|crypto(currency)?)\b[^.]{0,40}\b(send|transfer|pay)\b',
            r'\b(send|email|text)\b[^.]{0,30}\b(photos?|pictures?)\b[^.]{0,30}\bcodes?\b',
        ]

        # Secrecy requests
        self.secrecy_patterns = [
            r'\bkeep (this|it) (confidential|secret|private|between us)\b',
            r"\b(don't|do not|dont) (tell|share|mention)\b[^.]{0,30}\b(anyone|anybody|others)\b",
        ]

        # Pretexts for why the sender cannot be contacted
        self.unavailable_patterns = [
            r"\b(can't|cannot|can not|cant) (talk|take calls?|call|speak)\b",
            r'\bin a meeting\b',
            r'\bunable to (talk|call|speak)\b',
        ]

        # Promise to pay the victim back
        self.reimburse_patterns = [
            r'\b(reimburse|pay you back|refund you)\b',
        ]

    @staticmethod
    def _count_patterns(patterns: List[str], text: str) -> int:
        return sum(1 for p in patterns if re.search(p, text))
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze social engineering indicators
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with social engineering analysis
        """
        text_lower = text.lower()
        
        # Count different tactic types
        authority_count = sum(1 for kw in self.authority_keywords if kw in text_lower)
        action_count = sum(1 for kw in self.action_keywords if kw in text_lower)
        reward_count = sum(1 for kw in self.reward_keywords if kw in text_lower)
        threat_count = sum(1 for kw in self.threat_keywords if kw in text_lower)

        payment_count = self._count_patterns(self.payment_patterns, text_lower)
        secrecy_count = self._count_patterns(self.secrecy_patterns, text_lower)
        unavailable_count = self._count_patterns(self.unavailable_patterns, text_lower)
        reimburse_count = self._count_patterns(self.reimburse_patterns, text_lower)
        
        # Detect specific tactics
        tactics = []
        
        if authority_count > 0:
            tactics.append("authority_impersonation")
        
        if action_count > 2:
            tactics.append("urgency_action_requests")
        
        if reward_count > 0:
            tactics.append("reward_baiting")
        
        if threat_count > 1:
            tactics.append("threat_tactics")

        if payment_count > 0:
            tactics.append("payment_request")

        if secrecy_count > 0:
            tactics.append("secrecy_request")

        if unavailable_count > 0:
            tactics.append("unavailable_pretext")

        if reimburse_count > 0:
            tactics.append("reimbursement_promise")
        
        # Combination tactics are highly suspicious
        if authority_count > 0 and threat_count > 0:
            tactics.append("authority_with_threat")
        
        if reward_count > 0 and action_count > 0:
            tactics.append("reward_with_urgency")

        if payment_count > 0 and (secrecy_count > 0 or unavailable_count > 0):
            tactics.append("payment_request_with_pretext")
        
        # Calculate overall social engineering score (0-100)
        se_score = min(100, (
            authority_count * 15 +
            action_count * 10 +
            reward_count * 20 +
            threat_count * 15 +
            (40 if payment_count > 0 else 0) +
            (20 if secrecy_count > 0 else 0) +
            (15 if unavailable_count > 0 else 0) +
            (10 if reimburse_count > 0 else 0)
        ))
        
        return {
            "social_engineering_score": se_score,
            "tactics_detected": tactics,
            "authority_impersonation_count": authority_count,
            "action_request_count": action_count,
            "reward_mention_count": reward_count,
            "threat_count": threat_count,
            "payment_request_count": payment_count,
            "secrecy_request_count": secrecy_count,
            "is_social_engineering": se_score > 40,
            "risk_level": "high" if se_score > 60 else ("medium" if se_score > 30 else "low")
        }
