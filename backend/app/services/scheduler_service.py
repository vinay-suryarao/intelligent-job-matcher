"""
Background Job Scheduler
Automatically scrapes jobs at regular intervals
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None

async def scrape_jobs_task():
    """
    Background task to scrape jobs
    Runs automatically at scheduled intervals
    """
    
    logger.info("=" * 50)
    logger.info(f"🔄 AUTO-SCRAPE STARTED: {datetime.now()}")
    logger.info("=" * 50)
    
    try:
        from app.services.database import get_firebase_service
        from app.services.ai_matcher import get_matcher
        from app.services.pinecone_service import get_pinecone_service
        from app.scrapers import get_unified_scraper
        from app.services.notification_service import get_notification_service
        
        firebase = get_firebase_service()
        matcher = get_matcher()
        pinecone = get_pinecone_service()
        scraper = get_unified_scraper()
        notification_service = get_notification_service()
        
        # Keywords to search
        keywords = [
            "python developer",
            "java developer", 
            "react developer",
            "data scientist",
            "machine learning",
            "frontend developer",
            "backend developer",
            "full stack developer",
            "devops engineer",
            "software engineer"
        ]
        
        total_stored = 0
        total_emails = 0
        
        for keyword in keywords:
            logger.info(f"🔍 Scraping: {keyword}")
            
            try:
                jobs = scraper.search_all_sources(
                    keywords=keyword,
                    location="India",
                    max_results_per_source=10
                )
                
                for job_data in jobs:
                    # Check duplicate
                    if firebase.check_job_exists(job_data["title"], job_data["company"]):
                        continue
                    
                    # Store job
                    job_id = firebase.create_job(job_data)
                    if not job_id:
                        continue
                    
                    # Create embedding
                    try:
                        job_embedding = matcher.create_job_embedding(job_data)
                        pinecone.upsert_job_embedding(
                            job_id=job_id,
                            embedding=job_embedding,
                            metadata={
                                "job_id": job_id,
                                "title": job_data["title"],
                                "company": job_data["company"],
                                "type": "job"
                            }
                        )
                    except Exception as e:
                        logger.error(f"Embedding error: {e}")
                    
                    total_stored += 1
                    
                    # Notify matching users
                    try:
                        stats = notification_service.notify_matching_users_for_job(
                            job_data=job_data,
                            job_id=job_id
                        )
                        total_emails += stats.get("emails_sent", 0)
                    except Exception as e:
                        logger.error(f"Notification error: {e}")
                
            except Exception as e:
                logger.error(f"❌ Error scraping '{keyword}': {e}")
                continue
        
        logger.info("=" * 50)
        logger.info(f"✅ AUTO-SCRAPE COMPLETE!")
        logger.info(f"   📥 New jobs stored: {total_stored}")
        logger.info(f"   📧 Emails sent: {total_emails}")
        logger.info(f"   ⏰ Next run in 6 hours")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Auto-scrape failed: {e}")


def start_scheduler():
    """Start the background scheduler"""
    global scheduler
    
    if scheduler is not None:
        logger.warning("⚠️ Scheduler already running")
        return scheduler
    
    scheduler = AsyncIOScheduler()
    
    # Add job scraping task - runs every 6 hours
    scheduler.add_job(
        scrape_jobs_task,
        trigger=IntervalTrigger(hours=6),
        id="auto_scrape_jobs",
        name="Automatic Job Scraping",
        replace_existing=True
    )
    
    # Start scheduler
    scheduler.start()
    
    logger.info("=" * 50)
    logger.info("🚀 BACKGROUND SCHEDULER STARTED!")
    logger.info("   📅 Job scraping: Every 6 hours")
    logger.info("   ⏰ First run: Now + 6 hours")
    logger.info("   💡 Use /api/jobs/scrape-jobs for immediate scrape")
    logger.info("=" * 50)
    
    return scheduler


def stop_scheduler():
    """Stop the background scheduler"""
    global scheduler
    
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("🛑 Scheduler stopped")


def get_scheduler():
    """Get scheduler instance"""
    global scheduler
    return scheduler


def trigger_immediate_scrape():
    """Trigger an immediate scrape (outside schedule)"""
    global scheduler
    
    if scheduler:
        scheduler.add_job(
            scrape_jobs_task,
            id="immediate_scrape",
            replace_existing=True
        )
        logger.info("🚀 Immediate scrape triggered!")
        return True
    return False