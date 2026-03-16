import re

class DataExtractor:
    """
    Extracts Data from raw crawled text mapping to step 2 requirements.
    """
    
    # Regex Patterns
    EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    # Basic phone regex (imperfect due to global formats, but catches most US/UK)
    PHONE_REGEX = r"\(?\b[0-9]{3}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}\b"
    
    def extract_emails(self, text: str) -> list:
        emails = re.findall(self.EMAIL_REGEX, text)
        return list(set([e.lower() for e in emails]))
        
    def extract_phones(self, text: str) -> list:
        phones = re.findall(self.PHONE_REGEX, text)
        return list(set(phones))
