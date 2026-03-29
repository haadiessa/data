from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import sys
import os

# راستے کا مسئلہ حل کرنے کے لیے
try:
    from core.database import Base
except ImportError:
    try:
        from app.core.database import Base
    except ImportError:
        # اگر کچھ بھی کام نہ کرے تو یہ بیک اپ ہے
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from core.database import Base

class Business(Base):
    __tablename__ = "businesses"
    # ورسل کے لیے سب سے اہم لائن
    __table_args__ = {'extend_existing': True} 

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    address = Column(String)
    city = Column(String, index=True)
    phone = Column(String)
    website = Column(String, unique=True, index=True, nullable=True) 
    maps_link = Column(String, unique=True, index=True, nullable=True) 
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    leads = relationship("Lead", back_populates="business", cascade="all, delete-orphan")

class Lead(Base):
    __tablename__ = "leads"
    __table_args__ = {'extend_existing': True} 

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    
    name = Column(String, nullable=True)
    role = Column(String, nullable=True)
    profile_url = Column(String, nullable=True)
    
    email = Column(String, unique=True, index=True) 
    email_status = Column(String) 
    email_score = Column(Integer)
    status_reason = Column(String, nullable=True)
    
    lead_score = Column(Integer, default=0) 
    phone = Column(String, nullable=True) 
    social_links = Column(String, nullable=True) 
    created_at = Column(DateTime, default=datetime.utcnow)

    business = relationship("Business", back_populates="leads")