"""
Statistics Routes
User analytics and insights
"""

from fastapi import APIRouter, HTTPException, status
import logging

from app.services.database import get_firebase_service

router = APIRouter(prefix="/api/statistics", tags=["statistics"])
logger = logging.getLogger(__name__)

# ========================================
# STATIC ROUTES FIRST (before dynamic {user_id})
# ========================================

@router.get("/overview")
async def get_overview_statistics():
    """
    Get general platform statistics (no auth required)
    """
    
    logger.info("📊 Getting overview statistics")
    
    firebase = get_firebase_service()
    
    try:
        # Get all jobs (simple query without ordering to avoid index requirement)
        all_jobs = []
        if firebase.db:
            docs = firebase.db.collection('jobs').limit(1000).stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                all_jobs.append(data)
        
        # Get all internships (simple query)
        all_internships = []
        if firebase.db:
            docs = firebase.db.collection('internships').limit(500).stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                all_internships.append(data)
        
        # Count by source
        job_sources = {"adzuna": 0, "jsearch": 0, "manual": 0}
        for job in all_jobs:
            source = str(job.get("source", "manual")).lower()
            if "adzuna" in source:
                job_sources["adzuna"] += 1
            elif "jsearch" in source:
                job_sources["jsearch"] += 1
            else:
                job_sources["manual"] += 1
        
        logger.info(f"✅ Found {len(all_jobs)} jobs, {len(all_internships)} internships")
        
        return {
            "total_jobs": len(all_jobs),
            "total_internships": len(all_internships),
            "job_sources": job_sources
        }
        
    except Exception as e:
        logger.error(f"❌ Statistics error: {e}")
        return {
            "total_jobs": 0,
            "total_internships": 0,
            "job_sources": {"adzuna": 0, "jsearch": 0, "manual": 0},
            "error": str(e)
        }


@router.get("/user/{user_id}")
async def get_user_statistics(user_id: str):
    """
    Get user-specific statistics for dashboard
    """
    
    logger.info(f"📊 Getting user stats for: {user_id}")
    
    firebase = get_firebase_service()
    
    user = firebase.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user's applications (simple query)
    applications = []
    try:
        if firebase.db:
            docs = firebase.db.collection('applications').where('user_id', '==', user_id).limit(100).stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                applications.append(data)
    except Exception as e:
        logger.error(f"Error getting applications: {e}")
    
    # Calculate stats
    total_apps = len(applications)
    accepted = sum(1 for app in applications if app.get("status") == "accepted")
    rejected = sum(1 for app in applications if app.get("status") == "rejected")
    pending = total_apps - accepted - rejected
    
    return {
        "user_id": user_id,
        "skills_count": len(user.get("skills", [])),
        "skills": user.get("skills", []),
        "experience_level": user.get("experience_level", "entry"),
        "total_applications": total_apps,
        "accepted": accepted,
        "rejected": rejected,
        "pending": pending,
        "success_rate": round((accepted / total_apps * 100), 1) if total_apps > 0 else 0
    }


@router.get("/skills-analysis/{user_id}")
async def get_skills_analysis(user_id: str):
    """
    Get detailed skills analysis for user
    """
    
    logger.info(f"🔍 Skills analysis for: {user_id}")
    
    firebase = get_firebase_service()
    
    user = firebase.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_skills = set(s.lower() for s in user.get("skills", []))
    
    # Get all jobs (simple query)
    all_jobs = []
    if firebase.db:
        docs = firebase.db.collection('jobs').limit(500).stream()
        for doc in docs:
            data = doc.to_dict()
            all_jobs.append(data)
    
    # Find skill demand
    skill_demand = {}
    for job in all_jobs:
        for skill in job.get("required_skills", []):
            skill_lower = skill.lower()
            skill_demand[skill_lower] = skill_demand.get(skill_lower, 0) + 1
    
    # Top demanded skills
    top_skills = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)[:20]
    
    # Skills user has that are in demand
    matched_skills = [s for s, _ in top_skills if s in user_skills]
    
    # Skills user is missing
    missing_skills = [s for s, _ in top_skills if s not in user_skills][:10]
    
    return {
        "user_id": user_id,
        "user_skills": list(user_skills),
        "top_demanded_skills": [{"skill": s, "count": c} for s, c in top_skills],
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_match_percentage": round(len(matched_skills) / len(top_skills) * 100, 1) if top_skills else 0
    }
