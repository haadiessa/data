import google.generativeai as genai
import json
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class GeminiBrain:
    """
    Core Intelligence Engine powered by Gemini 1.5 Flash.
    Processes raw business data to extract leads, emails, and roles.
    """
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def process_business_data(self, business_name: str, website: str, raw_text: str) -> Dict[str, Any]:
        """
        Step B & C: Use Gemini to analyze raw data and extract key info.
        """
        prompt = f"""
        You are acting as the Core Intelligence Engine for a Lead Generation Website.
        Analyze the following raw text scraped from a website belonging to '{business_name}' ({website}).
        
        EXTRACT the following information in JSON format:
        1. "email": The most likely professional email address.
        2. "email_status": Mark as "VERIFIED" if the email looks highly specific, or "RISKY" if it's a generic one or guessed.
        3. "decision_maker_name": Identify the Owner, CEO, or Founder if mentioned.
        4. "decision_maker_role": Their specific title (e.g., Owner, CEO, Managing Director).
        5. "lead_score": Assign a score (0-100) based on how complete and valuable this lead is.
        
        RULES:
        - If no email is found, suggest a common pattern based on the domain (e.g., info@domain.com or contact@domain.com) and mark as "RISKY".
        - Ensure "decision_maker_name" and "decision_maker_role" are null if not found.
        - The response MUST be a valid JSON object only.

        RAW TEXT:
        {raw_text[:8000]} 
        """

        try:
            response = self.model.generate_content(prompt)
            # Assuming the response is a JSON string
            text_response = response.text.strip()
            # Clean up potential markdown code blocks
            if text_response.startswith("```json"):
                text_response = text_response.split("```json")[1].split("```")[0].strip()
            elif text_response.startswith("```"):
                text_response = text_response.split("```")[1].split("```")[0].strip()
            
            data = json.loads(text_response)
            return data
        except Exception as e:
            if "quota" in str(e).lower():
                return {
                    "error": "Daily Limit Reached - Please try again tomorrow.",
                    "email": None,
                    "email_status": "RISKY",
                    "decision_maker_name": None,
                    "decision_maker_role": None,
                    "lead_score": 0
                }
            logger.error(f"Gemini API Error: {e}")
            return {
                "error": str(e),
                "email": None,
                "email_status": "RISKY",
                "decision_maker_name": None,
                "decision_maker_role": None,
                "lead_score": 0
            }

brain_service = GeminiBrain(api_key="AIzaSyD7SDfIk_qXRe0FVtTELQsds26kvQzUf94")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, help="Business name or query to test")
    args = parser.parse_args()
    
    if args.test:
        print(f"--- [DEBUG] Testing Gemini Brain CLI ---")
        print(f"Input Query: {args.test}")
        
        # Mocking raw scraped text for the test
        mock_text = f"""
        Welcome to {args.test} Solutions.
        As a leading company in Pakistan, we specialize in high-end software development.
        Contact our team at hello@{args.test.lower().replace(' ', '')}.com for inquiries.
        Our CEO, Javed Iqbal, will be happy to discuss potential partnerships.
        Visit us at our Lahore office.
        """
        
        result = brain_service.process_business_data(args.test, f"https://{args.test.lower().replace(' ', '')}.com", mock_text)
        print("\n[RESULT FROM GEMINI]:")
        print(json.dumps(result, indent=2))
