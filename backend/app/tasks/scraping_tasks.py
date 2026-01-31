"""
Background Tasks for Job Scraping
Fetches from Adzuna + Indeed daily
"""

from celery import Celery
from app.services.database import get_firebase_service
from app.services.pinecone_service import get_pinecone_service
from app.services.ai_matcher import get_matcher
from app.scrapers import get_unified_scraper
import logging
import os

logger = logging.getLogger(__name__)

# Initialize Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery('tasks', broker=redis_url)

@celery_app.task
def scrape_and_store_jobs():
    """
    Background task: Scrape jobs from Adzuna + Indeed
    Runs daily at 2 AM
    """
    
    logger.info("🚀 Starting job scraping from ALL sources...")
    
    # Get services
    firebase = get_firebase_service()
    pinecone = get_pinecone_service()
    matcher = get_matcher()
    scraper = get_unified_scraper()
    
    # Keywords to search
    keywords_list = [
        "python developer",
        "java developer",
        "javascript developer",
        "react developer",
        "backend engineer",
        "frontend developer",
        "full stack developer",
        "data scientist",
        "data analyst",
        "machine learning engineer",
        "devops engineer"
    ]
    
    # Fetch from BOTH Adzuna + Indeed
    logger.info(f"🔍 Searching {len(keywords_list)} keywords across Adzuna + Indeed...")
    
    all_jobs = scraper.search_by_keywords_list(
        keywords_list=keywords_list,
        location="india",
        max_results_per_keyword=25  # 25 per keyword per source
    )
    
    logger.info(f"📥 Total jobs fetched: {len(all_jobs)}")
    
    # Store in Firebase + Pinecone
    total_stored = 0
    
    for job_data in all_jobs:
        try:
            # Check if job already exists
            if firebase.check_job_exists(
                title=job_data['title'],
                company=job_data['company']
            ):
                logger.debug(f"⏭️  Skipping duplicate: {job_data['title']}")
                continue
            
            # Store in Firebase
            job_id = firebase.create_job(job_data)
            
            if not job_id:
                continue
            
            logger.info(f"💾 Stored: {job_data['title']} ({job_data['source']})")
            
            # Generate embedding
            job_embedding = matcher.create_job_embedding(job_data)
            
            # Store in Pinecone
            pinecone.upsert_job_embedding(
                job_id=job_id,
                embedding=job_embedding,
                metadata={
                    'job_id': job_id,
                    'title': job_data['title'],
                    'company': job_data['company'],
                    'type': 'job',
                    'source': job_data['source']  # adzuna or indeed
                }
            )
            
            logger.debug(f"🔢 Embedding stored in Pinecone")
            
            total_stored += 1
            
        except Exception as e:
            logger.error(f"❌ Error processing job: {e}")
            continue
    
    logger.info(f"🎉 Job scraping complete!")
    logger.info(f"📊 Summary:")
    logger.info(f"   - Total fetched: {len(all_jobs)}")
    logger.info(f"   - New jobs stored: {total_stored}")
    
    return {
        'status': 'success',
        'total_fetched': len(all_jobs),
        'jobs_stored': total_stored
    }


@celery_app.task
def cleanup_old_jobs():
    """Remove jobs older than 30 days"""
    
    logger.info("🧹 Cleaning up old jobs...")
    
    firebase = get_firebase_service()
    pinecone = get_pinecone_service()
    
    old_jobs = firebase.get_old_jobs(days=30)
    
    for job in old_jobs:
        firebase.delete_job(job['id'])
        pinecone.delete_embedding(f"job_{job['id']}")
    
    logger.info(f"✅ Deleted {len(old_jobs)} old jobs")


# Schedule tasks
celery_app.conf.beat_schedule = {
    'scrape-jobs-daily': {
        'task': 'app.tasks.scraping_tasks.scrape_and_store_jobs',
        'schedule': 86400.0,  # Every 24 hours
    },
    'cleanup-old-jobs-weekly': {
        'task': 'app.tasks.scraping_tasks.cleanup_old_jobs',
        'schedule': 604800.0,  # Every 7 days
    },
}