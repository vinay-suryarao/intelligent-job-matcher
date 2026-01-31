"""
Jobs Routes
Job CRUD operations + Job scraping trigger + Email notifications
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.services.database import get_firebase_service
from app.services.ai_matcher import get_matcher
from app.services.pinecone_service import get_pinecone_service
from app.scrapers import get_unified_scraper
from app.services.notification_service import get_notification_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
logger = logging.getLogger(__name__)

# ========================================
# REQUEST/RESPONSE MODELS
# ========================================

class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    required_skills: List[str] = []
    experience_required: str = "entry"
    location: str = "India"
    job_type: str = "remote"
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    external_url: Optional[str] = ""

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    is_active: Optional[bool] = None

class ScrapeRequest(BaseModel):
    keywords: List[str] = ["python developer", "java developer"]
    location: str = "India"
    notify_users: bool = True

# ========================================
# ENDPOINTS
# ========================================

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_job(job_data: JobCreate, notify_users: bool = True):
    """
    Manually create a job posting
    
    - Creates job in Firebase
    - Generates embedding
    - Stores in Pinecone
    - SENDS EMAIL to matching users (if notify_users=True)
    """
    
    logger.info(f"📝 Creating job: {job_data.title}")
    
    firebase = get_firebase_service()
    matcher = get_matcher()
    pinecone = get_pinecone_service()
    
    # Prepare job data
    job_dict = {
        "title": job_data.title,
        "company": job_data.company,
        "description": job_data.description,
        "required_skills": job_data.required_skills,
        "experience_required": job_data.experience_required,
        "location": job_data.location,
        "job_type": job_data.job_type,
        "salary_min": job_data.salary_min,
        "salary_max": job_data.salary_max,
        "url": job_data.external_url,
        "external_url": job_data.external_url,
        "source": "manual",
        "is_active": True
    }
    
    # Create in Firebase
    job_id = firebase.create_job(job_dict)
    
    if not job_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create job"
        )
    
    logger.info(f"✅ Job created: {job_id}")
    
    # Generate embedding
    try:
        job_embedding = matcher.create_job_embedding(job_dict)
        
        # Store in Pinecone
        pinecone.upsert_job_embedding(
            job_id=job_id,
            embedding=job_embedding,
            metadata={
                "job_id": job_id,
                "title": job_data.title,
                "company": job_data.company,
                "type": "job",
                "source": "manual"
            }
        )
        
        logger.info(f"✅ Job embedding created in Pinecone")
        
    except Exception as e:
        logger.error(f"⚠️ Failed to create embedding: {e}")
    
    # 🔔 SEND NOTIFICATIONS TO MATCHING USERS
    notification_stats = None
    if notify_users:
        try:
            notification_service = get_notification_service()
            notification_stats = notification_service.notify_matching_users_for_job(
                job_data=job_dict,
                job_id=job_id
            )
            logger.info(f"📧 Notifications sent: {notification_stats['emails_sent']}")
        except Exception as e:
            logger.error(f"⚠️ Notification error: {e}")
    
    return {
        "message": "Job created successfully",
        "job_id": job_id,
        "notifications": notification_stats
    }


@router.get("/list")
async def list_jobs(
    skip: int = 0,
    limit: int = 50,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    source: Optional[str] = None
):
    """
    List all jobs with filters
    
    - Pagination support
    - Filter by location, job_type, source
    """
    
    logger.info(f"📋 Listing jobs (skip={skip}, limit={limit})")
    
    firebase = get_firebase_service()
    
    # Get all jobs (simple query to avoid index issues)
    all_jobs = []
    try:
        if firebase.db:
            docs = firebase.db.collection('jobs').limit(200).stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                all_jobs.append(data)
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
    
    # Apply filters
    filtered_jobs = all_jobs
    
    if location:
        filtered_jobs = [
            job for job in filtered_jobs 
            if location.lower() in job.get("location", "").lower()
        ]
    
    if job_type:
        filtered_jobs = [
            job for job in filtered_jobs 
            if job.get("job_type") == job_type
        ]
    
    if source:
        filtered_jobs = [
            job for job in filtered_jobs 
            if job.get("source") == source
        ]
    
    # Pagination
    paginated_jobs = filtered_jobs[skip:skip + limit]
    
    return {
        "total": len(filtered_jobs),
        "skip": skip,
        "limit": limit,
        "jobs": paginated_jobs
    }


@router.get("/{job_id}")
async def get_job(job_id: str):
    """
    Get single job details
    
    - Returns complete job information
    """
    
    logger.info(f"🔍 Getting job: {job_id}")
    
    firebase = get_firebase_service()
    job = firebase.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return {
        "job": job
    }


@router.put("/{job_id}")
async def update_job(job_id: str, job_data: JobUpdate):
    """
    Update job posting
    
    - Updates job in Firebase
    - Re-generates embedding if description changed
    """
    
    logger.info(f"✏️ Updating job: {job_id}")
    
    firebase = get_firebase_service()
    
    # Check job exists
    job = firebase.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Prepare updates
    updates = {}
    
    if job_data.title is not None:
        updates["title"] = job_data.title
    
    if job_data.description is not None:
        updates["description"] = job_data.description
    
    if job_data.required_skills is not None:
        updates["required_skills"] = job_data.required_skills
    
    if job_data.is_active is not None:
        updates["is_active"] = job_data.is_active
    
    # Update in Firebase
    success = firebase.update_job(job_id, updates)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update job"
        )
    
    logger.info(f"✅ Job updated: {job_id}")
    
    # Re-generate embedding if description changed
    if job_data.description is not None or job_data.required_skills is not None:
        try:
            matcher = get_matcher()
            pinecone = get_pinecone_service()
            
            # Get updated job
            updated_job = firebase.get_job(job_id)
            
            # Create new embedding
            job_embedding = matcher.create_job_embedding(updated_job)
            
            # Update in Pinecone
            pinecone.upsert_job_embedding(
                job_id=job_id,
                embedding=job_embedding,
                metadata={
                    "job_id": job_id,
                    "title": updated_job.get("title"),
                    "company": updated_job.get("company"),
                    "type": "job",
                    "source": updated_job.get("source", "manual")
                }
            )
            
            logger.info(f"✅ Job embedding updated in Pinecone")
            
        except Exception as e:
            logger.error(f"⚠️ Failed to update embedding: {e}")
    
    return {
        "message": "Job updated successfully",
        "job_id": job_id
    }


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """
    Delete job posting
    
    - Deletes from Firebase
    - Deletes embedding from Pinecone
    """
    
    logger.info(f"🗑️ Deleting job: {job_id}")
    
    firebase = get_firebase_service()
    pinecone = get_pinecone_service()
    
    # Check job exists
    job = firebase.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Delete from Pinecone
    try:
        pinecone.delete_embedding(f"job_{job_id}")
        logger.info(f"✅ Deleted from Pinecone")
    except Exception as e:
        logger.error(f"⚠️ Failed to delete from Pinecone: {e}")
    
    # Delete from Firebase
    success = firebase.delete_job(job_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete job"
        )
    
    return {
        "message": "Job deleted successfully",
        "job_id": job_id
    }


@router.post("/scrape-jobs")
async def trigger_job_scraping(
    request: ScrapeRequest = None,
    background_tasks: BackgroundTasks = None
):
    """
    Manually trigger job scraping from APIs (Adzuna + JSearch)
    
    - Fetches jobs from Adzuna + JSearch APIs
    - Stores in Firebase
    - Creates embeddings in Pinecone
    - SENDS EMAIL notifications to matching users
    
    (In production, this runs automatically via Celery)
    """
    
    # Default values if no request body
    if request is None:
        keywords = ["python developer", "java developer"]
        location = "India"
        notify_users = True
    else:
        keywords = request.keywords
        location = request.location
        notify_users = request.notify_users
    
    logger.info(f"🔄 Job scraping triggered for: {keywords}")
    
    firebase = get_firebase_service()
    matcher = get_matcher()
    pinecone = get_pinecone_service()
    scraper = get_unified_scraper()
    notification_service = get_notification_service()
    
    # Fetch jobs from all sources
    all_jobs = []
    
    for keyword in keywords:
        logger.info(f"🔍 Searching: {keyword}")
        try:
            jobs = scraper.search_all_sources(
                keywords=keyword,
                location=location,
                max_results_per_source=25
            )
            all_jobs.extend(jobs)
            logger.info(f"   Found {len(jobs)} jobs for '{keyword}'")
        except Exception as e:
            logger.error(f"❌ Error scraping '{keyword}': {e}")
    
    if not all_jobs:
        logger.warning("⚠️ No jobs found from APIs")
        return {
            "message": "No jobs found or API error",
            "scraped": 0,
            "total_found": 0,
            "keywords": keywords,
            "emails_sent": 0
        }
    
    logger.info(f"📥 Total jobs fetched: {len(all_jobs)}")
    
    # Store jobs and notify users
    stored_count = 0
    skipped_count = 0
    total_emails_sent = 0
    
    for job_data in all_jobs:
        try:
            # Check if job already exists (avoid duplicates)
            if firebase.check_job_exists(job_data["title"], job_data["company"]):
                skipped_count += 1
                continue
            
            # Ensure URL field exists
            if "url" not in job_data or not job_data["url"]:
                job_data["url"] = job_data.get("external_url", "")
            
            # Store in Firebase
            job_id = firebase.create_job(job_data)
            
            if not job_id:
                logger.warning(f"⚠️ Failed to store job: {job_data['title']}")
                continue
            
            logger.info(f"💾 Stored: {job_data['title']} at {job_data['company']}")
            
            # Create embedding
            try:
                job_embedding = matcher.create_job_embedding(job_data)
                
                # Store in Pinecone
                pinecone.upsert_job_embedding(
                    job_id=job_id,
                    embedding=job_embedding,
                    metadata={
                        "job_id": job_id,
                        "title": job_data["title"],
                        "company": job_data["company"],
                        "type": "job",
                        "source": job_data.get("source", "unknown")
                    }
                )
                logger.debug(f"   📊 Embedding stored in Pinecone")
                
            except Exception as e:
                logger.error(f"⚠️ Embedding error for {job_data['title']}: {e}")
            
            stored_count += 1
            
            # 🔔 Notify matching users via email
            if notify_users:
                try:
                    stats = notification_service.notify_matching_users_for_job(
                        job_data=job_data,
                        job_id=job_id
                    )
                    emails_sent = stats.get("emails_sent", 0)
                    total_emails_sent += emails_sent
                    
                    if emails_sent > 0:
                        logger.info(f"   📧 Notified {emails_sent} users")
                        
                except Exception as e:
                    logger.error(f"⚠️ Notification error: {e}")
            
        except Exception as e:
            logger.error(f"❌ Error processing job: {e}")
            continue
    
    logger.info("=" * 50)
    logger.info(f"🎉 Job scraping complete!")
    logger.info(f"   📥 Total fetched: {len(all_jobs)}")
    logger.info(f"   💾 New jobs stored: {stored_count}")
    logger.info(f"   ⏭️  Duplicates skipped: {skipped_count}")
    logger.info(f"   📧 Emails sent: {total_emails_sent}")
    logger.info("=" * 50)
    
    return {
        "message": f"Successfully scraped and stored {stored_count} jobs",
        "scraped": stored_count,
        "total_found": len(all_jobs),
        "duplicates_skipped": skipped_count,
        "keywords": keywords,
        "location": location,
        "emails_sent": total_emails_sent,
        "sources": ["adzuna", "jsearch"]
    }


@router.post("/scrape-jobs-simple")
async def scrape_jobs_simple(
    keywords: List[str] = ["python developer"],
    location: str = "India",
    notify_users: bool = False
):
    """
    Simple job scraping endpoint (Query parameters)
    
    Easier to test from Swagger UI
    """
    
    request = ScrapeRequest(
        keywords=keywords,
        location=location,
        notify_users=notify_users
    )
    
    return await trigger_job_scraping(request)


@router.get("/sources/stats")
async def get_job_sources_stats():
    """
    Get statistics about job sources
    
    - Count by source (adzuna, jsearch, manual)
    """
    
    firebase = get_firebase_service()
    
    # Get all jobs
    all_jobs = firebase.get_all_jobs(limit=500, is_active=True)
    
    # Count by source
    sources = {}
    for job in all_jobs:
        source = job.get("source", "unknown")
        sources[source] = sources.get(source, 0) + 1
    
    # Count by job type
    job_types = {}
    for job in all_jobs:
        jtype = job.get("job_type", "unknown")
        job_types[jtype] = job_types.get(jtype, 0) + 1
    
    # Count by location
    locations = {}
    for job in all_jobs:
        loc = job.get("location", "unknown")
        # Simplify location
        if "bangalore" in loc.lower():
            loc = "Bangalore"
        elif "mumbai" in loc.lower():
            loc = "Mumbai"
        elif "delhi" in loc.lower():
            loc = "Delhi"
        elif "remote" in loc.lower():
            loc = "Remote"
        else:
            loc = "Other"
        locations[loc] = locations.get(loc, 0) + 1
    
    return {
        "total_jobs": len(all_jobs),
        "by_source": sources,
        "by_job_type": job_types,
        "by_location": locations
    }


@router.get("/search")
async def search_jobs(
    query: str,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    limit: int = 20
):
    """
    Search jobs using semantic search
    
    - Uses AI to understand search intent
    - Returns ranked results by relevance
    """
    
    logger.info(f"🔍 Semantic search: {query}")
    
    firebase = get_firebase_service()
    matcher = get_matcher()
    pinecone = get_pinecone_service()
    
    # Create search query embedding
    search_data = {
        "skills": query.split(),  # Simple tokenization
        "experience_level": "any",
        "interests": query,
        "career_goals": query
    }
    
    query_embedding = matcher.create_user_embedding(search_data, for_search=True)
    
    # Search in Pinecone
    filter_dict = {"type": "job"}
    
    results = pinecone.find_matching_jobs(
        user_embedding=query_embedding,
        top_k=limit * 2,  # Get extra for filtering
        filter_dict=filter_dict
    )
    
    if not results:
        # Fallback to Firebase search
        all_jobs = firebase.get_all_jobs(limit=100)
        return {
            "query": query,
            "total": len(all_jobs),
            "jobs": all_jobs[:limit]
        }
    
    # Get full job details
    jobs = []
    for match in results:
        job = firebase.get_job(match['id'])
        if job:
            # Apply filters
            if location and location.lower() not in job.get("location", "").lower():
                continue
            if job_type and job.get("job_type") != job_type:
                continue
            
            job['relevance_score'] = round(match['score'], 2)
            jobs.append(job)
            
            if len(jobs) >= limit:
                break
    
    return {
        "query": query,
        "total": len(jobs),
        "jobs": jobs
    }


@router.post("/test-scraper")
async def test_scraper():
    """
    Test if job scrapers are working
    
    - Tests Adzuna API
    - Tests JSearch API
    - Returns sample results
    """
    
    logger.info("🧪 Testing job scrapers...")
    
    scraper = get_unified_scraper()
    
    results = {
        "adzuna": {"status": "unknown", "jobs": 0},
        "jsearch": {"status": "unknown", "jobs": 0}
    }
    
    # Test Adzuna
    try:
        adzuna_jobs = scraper.adzuna.search_jobs(
            keywords="python",
            location="india",
            results_per_page=5
        )
        results["adzuna"] = {
            "status": "working" if adzuna_jobs else "no_results",
            "jobs": len(adzuna_jobs),
            "sample": adzuna_jobs[0] if adzuna_jobs else None
        }
    except Exception as e:
        results["adzuna"] = {"status": "error", "error": str(e)}
    
    # Test JSearch
    try:
        jsearch_jobs = scraper.jsearch.search_jobs(
            keywords="python developer",
            location="India",
            results_per_page=5
        )
        results["jsearch"] = {
            "status": "working" if jsearch_jobs else "no_results",
            "jobs": len(jsearch_jobs),
            "sample": jsearch_jobs[0] if jsearch_jobs else None
        }
    except Exception as e:
        results["jsearch"] = {"status": "error", "error": str(e)}
    
    return {
        "message": "Scraper test complete",
        "results": results
    }