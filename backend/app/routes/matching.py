"""
Matching Routes
AI-powered job matching
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.services.database import get_firebase_service
from app.services.ai_matcher import get_matcher
from app.services.pinecone_service import get_pinecone_service

router = APIRouter(prefix="/api/matching", tags=["matching"])
logger = logging.getLogger(__name__)

# ========================================
# REQUEST/RESPONSE MODELS
# ========================================

class MatchRequest(BaseModel):
    user_id: str
    match_type: str = "jobs"  # jobs or internships
    filters: Optional[dict] = {}
    top_k: int = 20

class ApplicationCreate(BaseModel):
    user_id: str
    application_type: str  # job or internship
    job_id: Optional[str] = None
    internship_id: Optional[str] = None
    match_score: float
    rejection_probability: float

# ========================================
# ENDPOINTS
# ========================================

@router.post("/matches")
async def get_matches(request: MatchRequest):
    """
    Get intelligent job/internship matches
    
    Flow:
    1. Get user from Firebase
    2. Get all jobs/internships from Firebase
    3. Use AI matcher to rank by skills
    4. Return matches with reasoning
    """
    
    logger.info(f"🎯 Getting matches for user: {request.user_id}")
    
    firebase = get_firebase_service()
    
    # Get user
    user = firebase.get_user(request.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user has skills
    if not user.get("skills"):
        return {
            "user_id": request.user_id,
            "total_matches": 0,
            "matches": [],
            "message": "Please add skills to your profile or upload resume for better matches"
        }
    
    # Get all items from Firebase (direct query - works without indexes)
    try:
        if request.match_type == "jobs":
            if firebase.db:
                docs = firebase.db.collection('jobs').limit(200).stream()
                all_items = []
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    all_items.append(data)
            else:
                all_items = []
        else:
            if firebase.db:
                docs = firebase.db.collection('internships').limit(200).stream()
                all_items = []
                for doc in docs:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    all_items.append(data)
            else:
                all_items = []
    except Exception as e:
        logger.error(f"❌ Error fetching items: {e}")
        all_items = []
    
    if not all_items:
        return {
            "user_id": request.user_id,
            "total_matches": 0,
            "matches": [],
            "message": f"No {request.match_type} found in database"
        }
    
    # Use AI matcher to rank matches
    matcher = get_matcher()
    
    # Calculate match scores for each item
    matches = []
    user_skills = set(s.lower() for s in user.get("skills", []))
    
    for item in all_items:
        item_skills = set(s.lower() for s in item.get("required_skills", []))
        
        # Calculate match score based on skill overlap
        if item_skills:
            matched_skills = user_skills.intersection(item_skills)
            missing_skills = item_skills - user_skills
            match_score = len(matched_skills) / len(item_skills) * 100
        else:
            matched_skills = set()
            missing_skills = set()
            match_score = 50  # Default if no skills specified
        
        # Calculate rejection probability
        rejection_prob = max(0, min(100, 100 - match_score + (len(missing_skills) * 5)))
        
        matches.append({
            request.match_type[:-1]: item,  # job or internship
            "match_score": round(match_score, 1),
            "rejection_probability": round(rejection_prob, 1),
            "rejection_risk": "low" if rejection_prob < 30 else "medium" if rejection_prob < 60 else "high",
            "skill_match": {
                "matched": list(matched_skills),
                "missing": list(missing_skills)
            },
            "reasoning": _generate_match_reason(match_score, list(matched_skills), list(missing_skills)),
            "recommended_action": "Apply Now!" if match_score >= 70 else "Consider Upskilling" if match_score >= 40 else "Focus on Learning"
        })
    
    # Sort by match score (highest first)
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    matches = matches[:request.top_k]
    
    logger.info(f"✅ Found {len(matches)} matches")
    
    return {
        "user_id": request.user_id,
        "match_type": request.match_type,
        "total_matches": len(matches),
        "matches": matches,
        "data_source": "AI-powered skill matching",
        "user_skills": list(user_skills)
    }


def _generate_match_reason(score, matched, missing):
    """Generate human-readable match reasoning"""
    if score >= 80:
        reason = f"Excellent match! You have {len(matched)} matching skills."
    elif score >= 60:
        reason = f"Good match with {len(matched)} skills. Learn {', '.join(missing[:3])} to improve."
    elif score >= 40:
        reason = f"Fair match. Consider learning: {', '.join(missing[:5])}"
    else:
        reason = f"This role requires skills you're still developing. Focus on: {', '.join(missing[:5])}"
    return reason


@router.post("/apply")
async def create_application(application: ApplicationCreate):
    """
    Track job/internship application
    
    - Records application in Firebase
    - Used for rejection analysis later
    """
    
    logger.info(f"📝 Recording application for user: {application.user_id}")
    
    firebase = get_firebase_service()
    
    # Verify user exists
    user = firebase.get_user(application.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify job/internship exists
    if application.application_type == "job":
        if not application.job_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="job_id required for job application"
            )
        item = firebase.get_job(application.job_id)
    else:
        if not application.internship_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="internship_id required for internship application"
            )
        item = firebase.get_internship(application.internship_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{application.application_type.title()} not found"
        )
    
    # Create application record
    app_data = {
        "user_id": application.user_id,
        "application_type": application.application_type,
        "job_id": application.job_id,
        "internship_id": application.internship_id,
        "status": "applied",
        "match_score": application.match_score,
        "rejection_probability": application.rejection_probability
    }
    
    app_id = firebase.create_application(app_data)
    
    if not app_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record application"
        )
    
    logger.info(f"✅ Application recorded: {app_id}")
    
    return {
        "message": "Application recorded successfully",
        "application_id": app_id,
        "status": "applied"
    }


@router.put("/application/{application_id}/status")
async def update_application_status(
    application_id: str,
    status: str,
    skill_gaps: Optional[List[str]] = None
):
    """
    Update application status
    
    - Updates status (applied, rejected, accepted, interview)
    - If rejected, creates rejection record for analysis
    """
    
    logger.info(f"📝 Updating application {application_id} to {status}")
    
    firebase = get_firebase_service()
    
    # Update application
    updates = {"status": status}
    success = firebase.update_application(application_id, updates)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update application"
        )
    
    # If rejected, create rejection record
    if status == "rejected":
        # Get application details (simplified - you'd fetch from Firebase)
        rejection_data = {
            "user_id": "user_id_here",  # You'd get this from application
            "application_id": application_id,
            "reason": "skill_gap" if skill_gaps else "other",
            "skill_gaps": skill_gaps or [],
            "analyzed": False
        }
        
        firebase.create_rejection(rejection_data)
        logger.info(f"✅ Rejection record created")
    
    return {
        "message": "Application status updated",
        "application_id": application_id,
        "status": status
    }


# ========================================
# HELPER FUNCTIONS
# ========================================

def _calculate_rejection_probability(
    match_score: float,
    skill_gaps: int,
    user_exp: str,
    item_exp: str
) -> float:
    """Calculate rejection probability"""
    
    score_penalty = (100 - match_score) * 0.4
    skill_gap_penalty = min(skill_gaps * 10, 50)
    
    exp_levels = {'entry': 1, 'mid': 2, 'senior': 3}
    user_level = exp_levels.get(user_exp, 1)
    item_level = exp_levels.get(item_exp, 1)
    exp_gap = abs(user_level - item_level) * 10
    
    total = min(score_penalty + skill_gap_penalty + exp_gap, 95)
    return round(total, 1)


def _get_risk_level(rejection_prob: float) -> str:
    """Get risk level label"""
    if rejection_prob < 30:
        return "Low"
    elif rejection_prob < 60:
        return "Medium"
    else:
        return "High"


def _get_recommendation(score: float, rejection_prob: float) -> str:
    """Get action recommendation"""
    if score >= 80 and rejection_prob < 30:
        return "Apply Now - Strong Match!"
    elif score >= 70 and rejection_prob < 50:
        return "Consider Applying"
    elif score >= 60:
        return "Apply with Portfolio"
    else:
        return "Build Skills First"