from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import engine, Base, get_db
from app.models import Business, Lead
from pydantic import BaseModel
import uuid

# Create tables for local development automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Lead Gen & Sales Intelligence API")

class SearchRequest(BaseModel):
    niche: str
    location: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Lead Generation API is running."}

@app.post("/api/leads/search")
def start_lead_search(req: SearchRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Endpoint to trigger the asynchronous Lead Discovery Engine.
    For production, this would dispatch to Celery. For MVP simplicity with background tasks:
    """
    job_id = str(uuid.uuid4())
    
    # In a real app we dispatch `celery_app.send_task(...)`
    # Here, we simulate appending to background tasks
    # background_tasks.add_task(run_discovery_engine, req.niche, req.location, job_id)
    
    return {"job_id": job_id, "status": "Search started", "niche": req.niche, "location": req.location}

from fastapi.responses import Response
from app.services.exporter.export_service import ExportService

@app.get("/api/leads")
def get_leads(db: Session = Depends(get_db)):
    """
    Query leads from the database, sorted by Lead Score (Rule 6)
    """
    leads = db.query(Lead).order_by(Lead.lead_score.desc()).limit(100).all()
    
    result = []
    for lead in leads:
        business = lead.business
        result.append({
            "company_name": business.name if business else None,
            "website": business.website if business else None,
            "name": lead.name,
            "role": lead.role,
            "profile_url": lead.profile_url,
            "email": lead.email,
            "email_status": lead.email_status,
            "verified_score": lead.email_score,
            "lead_score": lead.lead_score,
            "phone": lead.phone or (business.phone if business else None)
        })
        
    return {"data": result}

@app.get("/api/leads/export")
def export_leads(db: Session = Depends(get_db)):
    """
    Export all leads to CSV format.
    """
    data_response = get_leads(db)
    leads = data_response["data"]
    
    exporter = ExportService()
    csv_content = exporter.export_csv(leads)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_export.csv"}
    )
