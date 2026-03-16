import csv
import json
from io import StringIO
from typing import List, Dict, Any

class ExportService:
    """
    7. Export & Download Module
    Supports exporting leads to CSV and JSON formats.
    """
    
    def export_csv(self, leads: List[Dict[str, Any]]) -> str:
        """Export leads data to CSV format as a string"""
        if not leads:
            return ""
            
        output = StringIO()
        
        # Define fields from requirements
        fieldnames = [
            "Company", "Email", "Phone", "Website", 
            "Owner", "Role", "Profile Link", 
            "Lead Score", "Verification Status"
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for lead in leads:
            writer.writerow({
                "Company": lead.get("company_name", ""),
                "Email": lead.get("email", ""),
                "Phone": lead.get("phone", ""),
                "Website": lead.get("website", ""),
                "Owner": lead.get("name", ""),
                "Role": lead.get("role", ""),
                "Profile Link": lead.get("profile_url", ""),
                "Lead Score": lead.get("lead_score", 0),
                "Verification Status": lead.get("email_status", "")
            })
            
        return output.getvalue()
        
    def export_json(self, leads: List[Dict[str, Any]]) -> str:
        """Export leads data to JSON format as a string"""
        return json.dumps(leads, indent=2)

