from celery import Celery
import os

# Configure Celery to use Redis as the message broker
# Fallback to a local file/memory broker if Redis isn't running for easy local testing
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "leadgen_worker",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600, # Max 1 hour per huge scraping job
)

# Load tasks
celery_app.autodiscover_tasks(["app.worker.tasks"], force=True)
