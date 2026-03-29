import sys
import os
import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

# --- پاتھ سیٹنگز (ورتھل کے لیے راستے درست کرنا) ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# --- امپورٹس ---
try:
    from core.database import engine, Base, get_db
    from models.lead import Business, Lead
except ImportError:
    # اگر پہلا طریقہ فیل ہو تو دوسرا راستہ
    sys.path.append(os.path.join(CURRENT_DIR, ".."))
    from core.database import engine, Base, get_db
    from models.lead import Business, Lead

# --- ڈیٹا بیس ٹیبلز بنانا (یہ لائن ٹیبلز پیدا کرے گی) ---
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Table creation error: {e}")

app = FastAPI(title="AI Lead Gen API")

# --- CORS (تاکہ آپ کی ایکسٹینشن اسے استعمال کر سکے) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    niche: str
    location: str

# --- راؤٹس (Routes) ---

@app.get("/")
def read_root():
    return {
        "status": "ok", 
        "message": "API is LIVE on Neon Database!",
        "version": "1.0.6"
    }

@app.get("/api/leads")
def get_leads(db: Session = Depends(get_db)):
    try:
        # یہاں ڈیٹا بیس سے لیڈز لانے کی کوشش
        leads = db.query(Lead).limit(50).all()
        result = []
        for lead in leads:
            biz = lead.business
            result.append({
                "id": lead.id,
                "company": biz.name if biz else "N/A",
                "email": lead.email,
                "status": lead.email_status,
                "city": biz.city if biz else "N/A"
            })
        return {"data": result}
    except Exception as e:
        # اگر ٹیبل اب بھی نہ ملے تو یہ ایرر دکھائے گا
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/leads/search")
def start_search(req: SearchRequest):
    # یہ ابھی صرف ایک فرضی جاب آئی ڈی واپس کرے گا
    return {
        "job_id": str(uuid.uuid4()), 
        "status": "started",
        "query": f"{req.niche} in {req.location}"
    }

# ورسل کے لیے ہینڈلر
handler = app