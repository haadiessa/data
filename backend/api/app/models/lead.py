from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    address = Column(String)
    city = Column(String, index=True)
    phone = Column(String)
    website = Column(String, unique=True, index=True, nullable=True) # Unique Domain protection
    maps_link = Column(String, unique=True, index=True, nullable=True) # Unique Maps protection
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    leads = relationship("Lead", back_populates="business", cascade="all, delete-orphan")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    
    # 4. Owner / CEO Info
    name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    profile_url = Column(String, nullable=True)
    
    # 3. Email Info
    email = Column(String, unique=True, index=True) # Unique Email protection
    email_status = Column(String) # VERIFIED, RISKY, INVALID
    email_score = Column(Integer)
    status_reason = Column(String, nullable=True)
    
    # 6. Lead Scoring
    lead_score = Column(Integer, default=0) # 0-100 total score
    
    # Discovery Meta
    phone = Column(String, nullable=True) # Direct contact phone
    social_links = Column(String, nullable=True) # JSON string of social links
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    business = relationship("Business", back_populates="leads")
