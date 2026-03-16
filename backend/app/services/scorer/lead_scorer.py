from typing import Dict, Any

class LeadScorer:
    """
    Lead Scoring Engine (Rule 6)
    Assign score 0–100 per lead based on attributes.
    """
    def generate_score(self, lead_data: Dict[str, Any]) -> int:
        score = 0
        
        # Verified Email (+40)
        if lead_data.get("email_status") == "VERIFIED":
            score += 40
        elif lead_data.get("email_status") == "RISKY":
            score += 15 # partial points for risky

        # Valid Website (+20)
        if lead_data.get("website"):
            score += 20
            
        # Owner Found (+25)
        if lead_data.get("role") and lead_data.get("name"):
            score += 25
            
        # Phone Available (+10)
        if lead_data.get("phone"):
            score += 10
            
        # Social Media Presence (+5)
        if lead_data.get("social_links") or lead_data.get("profile_url"):
            score += 5
            
        return min(score, 100)
