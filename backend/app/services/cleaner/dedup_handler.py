from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.lead import Business, Lead
import logging

logger = logging.getLogger(__name__)

class DuplicateHandler:
    """
    5. Duplicate Detection & Cleaning Engine
    """
    def __init__(self, db: Session):
        self.db = db
        
    def save_business_deduped(self, data: dict) -> Business:
        """
        Attempt to save a business safely preventing duplicates using unique domains or Maps link.
        """
        # Try finding existing by maps link or website
        existing = None
        if data.get("maps_link"):
            existing = self.db.query(Business).filter(Business.maps_link == data["maps_link"]).first()
            
        if not existing and data.get("website"):
            existing = self.db.query(Business).filter(Business.website == data["website"]).first()
            
        if existing:
            # Merge updates: Keep the most complete record
            if not existing.phone and data.get("phone"):
                existing.phone = data["phone"]
            if not existing.address and data.get("address"):
                existing.address = data["address"]
            
            self.db.commit()
            return existing
            
        # Create new if didn't exist
        new_business = Business(**data)
        self.db.add(new_business)
        try:
            self.db.commit()
            self.db.refresh(new_business)
            return new_business
        except IntegrityError:
            self.db.rollback()
            logger.warning(f"Duplicate Business detected via DB Constraint for: {data.get('name')}")
            return None

    def save_lead_deduped(self, data: dict) -> Lead:
        """
        Attempt to save a lead safely preventing duplicate emails.
        """
        if not data.get("email"):
            return None
            
        existing = self.db.query(Lead).filter(Lead.email == data["email"]).first()
        
        if existing:
            # Upgrade information if the new scraped data is more complete
            if not existing.profile_url and data.get("profile_url"):
                existing.profile_url = data["profile_url"]
            if not existing.role and data.get("role"):
                existing.role = data["role"]
                
            self.db.commit()
            return existing
            
        new_lead = Lead(**data)
        self.db.add(new_lead)
        try:
            self.db.commit()
            self.db.refresh(new_lead)
            return new_lead
        except IntegrityError:
            self.db.rollback()
            logger.warning(f"Duplicate Lead Email detected via DB Constraint: {data.get('email')}")
            return None
