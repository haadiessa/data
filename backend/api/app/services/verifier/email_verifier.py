import re
import dns.resolver
import smtplib
from typing import Dict, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DISPOSABLE_DOMAINS = {
    "tempmail.com", "mailinator.com", "10minutemail.com", 
    "guerrillamail.com", "yopmail.com"
} # In production, this should be loaded from a larger database or API

class EmailVerifier:
    """
    Advanced Multi-Layer Email Verification System
    """
    def __init__(self):
        # RFC 5322 compliant regex for basic format validation
        self.email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def verify_format(self, email: str) -> bool:
        """1. Format Validation: Verify RFC 5322 standard and basic syntax."""
        return bool(self.email_regex.match(email))

    def check_domain_and_mx(self, domain: str) -> Tuple[bool, list]:
        """2 & 3. Domain Validation and MX Record Check."""
        try:
            records = dns.resolver.resolve(domain, 'MX')
            # Sort by preference
            mx_records = sorted(records, key=lambda rec: rec.preference)
            mx_hosts = [str(record.exchange).rstrip('.') for record in mx_records]
            return True, mx_hosts
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout, Exception) as e:
            logger.debug(f"MX lookup failed for {domain}: {e}")
            return False, []

    def check_disposable(self, domain: str) -> bool:
        """5. Disposable Email Detection."""
        return domain.lower() in DISPOSABLE_DOMAINS

    def check_smtp_and_catchall(self, domain: str, mx_record: str, email: str) -> Tuple[bool, bool, str]:
        """
        4 & 5. SMTP Verification and Catch-All Detection
        Returns: (is_deliverable, is_catchall, detailed_reason)
        """
        try:
            # Perform non-intrusive SMTP handshake
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_record)
            server.helo()
            server.mail('verify_ping@leadgenic.com')
            
            # Catch-all Check: Try a random, likely invalid email string
            code_catchall, _ = server.rcpt(f"catchall_test_invalid_89231@{domain}")
            is_catchall = (code_catchall == 250)

            # Actual Email Delivery Check
            code_real, resp_real = server.rcpt(email)
            is_deliverable = (code_real == 250)
            
            server.quit()
            
            if is_catchall:
                return True, True, "Domain accepts all emails (Catch-All)"
            
            if is_deliverable:
                return True, False, "Passed all SMTP checks"
            else:
                return False, False, f"SMTP rejected mailbox. Code: {code_real}"
                
        except smtplib.SMTPServerDisconnected:
            return False, False, "SMTP Server Disconnected unexpectedly"
        except Exception as e:
            logger.debug(f"SMTP check failed for {email} via {mx_record}: {e}")
            # If we error out on SMTP, we treat it as inconclusive/risky instead of strictly valid
            return False, False, "SMTP Check Failed. Server unreachable or blocked."


    def verify_email(self, email: str) -> Dict[str, Any]:
        """
        Main Multi-Layer Verification Pipeline
        Output Classifications: VERIFIED, RISKY, INVALID
        """
        email = email.lower().strip()
        
        # Layer 1: Format Check
        if not self.verify_format(email):
            return {"email": email, "status": "INVALID", "score": 0, "reason": "Invalid email format"}
            
        domain = email.split('@')[1]
        
        # Layer 2: Disposable Check
        if self.check_disposable(domain):
            return {"email": email, "status": "INVALID", "score": 10, "reason": "Disposable email provider detected"}

        # Layer 3: DNS & MX Check
        has_mx, mx_records = self.check_domain_and_mx(domain)
        if not has_mx or not mx_records:
            return {"email": email, "status": "INVALID", "score": 20, "reason": "Domain has no valid MX records"}

        # Layer 4 & 5: SMTP Delivery & Catch-All verification
        # Loop through MX records if the first one fails connection
        for mx_record in mx_records:
            try:
                is_deliverable, is_catchall, reason = self.check_smtp_and_catchall(domain, mx_record, email)
                
                # If we successfully tested it
                if is_catchall:
                    return {"email": email, "status": "RISKY", "score": 60, "reason": "Catch-all domain configuration"}

                if is_deliverable:
                    return {"email": email, "status": "VERIFIED", "score": 100, "reason": "Deliverable and verified"}
                else:
                    return {"email": email, "status": "INVALID", "score": 40, "reason": reason}
                    
            except Exception:
                continue # Retry next MX record (Multi-layer re-verification fallback)

        # If all MX records were exhausted without a clear deliverable success (block/timeout)
        return {"email": email, "status": "RISKY", "score": 50, "reason": "SMTP verification inconclusive (possible greylisting)"}

