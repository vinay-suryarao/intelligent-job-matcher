"""
Chat Routes
AI chat interface for user queries
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import logging

from app.services.database import get_firebase_service
from app.services.chat_service import get_chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

# ========================================
# REQUEST/RESPONSE MODELS
# ========================================

class ChatMessage(BaseModel):
    user_id: str
    message: str
    messages: list = []  # Optional chat history

class ChatResponse(BaseModel):
    response: str
    context: dict = {}

# ========================================
# ENDPOINTS
# ========================================

@router.post("/message", response_model=ChatResponse)
async def send_message(chat: ChatMessage):
    """
    Process chat message and return AI response
    
    - Understands user intent (rejection, jobs, skills, etc.)
    - Fetches relevant data
    - Generates personalized response
    """
    
    logger.info(f"💬 Chat message from user {chat.user_id}: {chat.message[:50]}...")
    
    firebase = get_firebase_service()
    
    # Get user
    user = firebase.get_user(chat.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prepare user data
    user_data = {
        "id": user.get("id"),
        "full_name": user.get("full_name", "User"),
        "email": user.get("email"),
        "skills": user.get("skills", []),
        "experience_level": user.get("experience_level", "entry"),
        "interests": user.get("interests", ""),
        "career_goals": user.get("career_goals", ""),
        "total_applications": 0
    }
    
    # Get user's applications
    applications = firebase.get_user_applications(chat.user_id)
    user_data["total_applications"] = len(applications)
    
    # Get rejections
    rejections_data = []
    for app in applications:
        if app.get("status") == "rejected":
            # Get rejection details
            rejections = firebase.get_user_rejections(chat.user_id)
            for rejection in rejections:
                if rejection.get("application_id") == app.get("id"):
                    rejections_data.append({
                        "job_id": app.get("job_id"),
                        "internship_id": app.get("internship_id"),
                        "skill_gaps": rejection.get("skill_gaps", []),
                        "reason": rejection.get("reason"),
                        "job_experience_required": "mid"  # Simplified
                    })
    
    # Get top missing skills
    all_skill_gaps = []
    for rejection in rejections_data:
        all_skill_gaps.extend(rejection.get("skill_gaps", []))
    
    from collections import Counter
    skill_counter = Counter(all_skill_gaps)
    top_missing_skills = [skill for skill, _ in skill_counter.most_common(5)]
    
    # Prepare context
    context = {
        "rejections": rejections_data,
        "matched_jobs": [],  # Could fetch from matching service
        "total_applications": len(applications),
        "top_missing_skills": top_missing_skills
    }
    
    # Get chat service and process
    chat_service = get_chat_service()
    response_text = chat_service.process_message(
        chat.message,
        user_data,
        context,
        chat.messages
    )
    
    logger.info(f"✅ Chat response generated")
    
    return {
        "response": response_text,
        "context": context
    }


@router.get("/history/{user_id}")
async def get_chat_history(user_id: str):
    """
    Get chat history for user
    
    (Optional feature - not implemented in MVP)
    """
    
    firebase = get_firebase_service()
    
    # Verify user exists
    user = firebase.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Return empty for now
    return {
        "user_id": user_id,
        "messages": [],
        "note": "Chat history feature coming soon"
    }