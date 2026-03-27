from celery import shared_task
import asyncio
from typing import Dict, Any

from app.core.database import SessionLocal
from app.services.scraper.maps_scraper import GoogleMapsScraper
from app.services.scraper.website_crawler import WebsiteCrawler
from app.services.scraper.data_extractor import DataExtractor
from app.services.verifier.email_verifier import EmailVerifier
from app.services.verifier.profile_verifier import ProfileVerifier
from app.services.scorer.lead_scorer import LeadScorer
from app.services.brain import brain_service

@shared_task(bind=True)
def run_discovery_engine(self, niche: str, location: str, job_id: str):
    """
    8. Scalable Scraping Architecture Background Job.
    Orchestrates the entire AI Lead Generation workflow.
    """
    db = SessionLocal()
    dedup = DuplicateHandler(db)
    scorer = LeadScorer()
    
    maps_scraper = GoogleMapsScraper()
    crawler = WebsiteCrawler()

    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        # Step 1: Discover Businesses
        businesses = loop.run_until_complete(maps_scraper.discover_businesses(niche, location, max_results=10))
        
        for b_data in businesses:
            business_model = dedup.save_business_deduped(b_data)
            if not business_model:
                continue
                
            website = b_data.get("website")
            if not website:
                continue
                
            # Step 2: Advanced Website Crawl
            crawl_data = loop.run_until_complete(crawler.crawl_website(website))
            raw_text = crawl_data["raw_text"]
            socials = list(crawl_data.get("social_links", []))
            
            # Step 3 & 4: Gemini Brain Processing (Email, ROI, Decision Maker)
            brain_results = brain_service.process_business_data(b_data["name"], website, raw_text)
            
            if "error" in brain_results and "Limit Reached" in brain_results["error"]:
                # You might want to log this or notify the user
                logger.warning("Gemini API Limit Reached")

            lead_payload = {
                "business_id": business_model.id,
                "name": brain_results.get("decision_maker_name"),
                "role": brain_results.get("decision_maker_role"),
                "email": brain_results.get("email"),
                "email_status": brain_results.get("email_status"),
                "email_score": 100 if brain_results.get("email_status") == "VERIFIED" else 40,
                "lead_score": brain_results.get("lead_score", 0),
                "social_links": str(socials),
                "phone": b_data.get("phone")
            }
            
            # Final scoring adjustment if needed
            if lead_payload["lead_score"] == 0:
                lead_payload["lead_score"] = scorer.generate_score(lead_payload)
            
            dedup.save_lead_deduped(lead_payload)
                
    except Exception as e:
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        raise e
    finally:
        db.close()
        
    return {"status": "Complete", "job_id": job_id}
