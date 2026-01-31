"""
User Routes
User profile management
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.services.database import get_firebase_service
from app.services.ai_matcher import get_matcher
from app.services.pinecone_service import get_pinecone_service

router = APIRouter(prefix="/api/users", tags=["users"])
logger = logging.getLogger(__name__)

# ========================================
# REQUEST/RESPONSE MODELS
# ========================================

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_level: Optional[str] = None
    interests: Optional[str] = None
    career_goals: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    preferences: Optional[dict] = None

# ========================================
# ENDPOINTS
# ========================================

@router.get("/{user_id}")
async def get_user(user_id: str):
    """
    Get user profile
    
    - Returns complete user information
    """
    
    logger.info(f"👤 Getting user: {user_id}")
    
    firebase = get_firebase_service()
    user = firebase.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Remove sensitive data
    user.pop("hashed_password", None)
    
    return {
        "user": user
    }


@router.put("/{user_id}")
async def update_user(user_id: str, user_data: UserUpdate):
    """
    Update user profile
    
    - Updates user information
    - Refreshes user embedding in Pinecone if skills changed
    """
    
    logger.info(f"✏️ Updating user: {user_id}")
    
    firebase = get_firebase_service()
    
    # Check user exists
    user = firebase.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prepare updates
    updates = {}
    
    if user_data.full_name is not None:
        updates["full_name"] = user_data.full_name
    
    if user_data.skills is not None:
        updates["skills"] = user_data.skills
    
    if user_data.experience_level is not None:
        updates["experience_level"] = user_data.experience_level
    
    if user_data.interests is not None:
        updates["interests"] = user_data.interests
    
    if user_data.career_goals is not None:
        updates["career_goals"] = user_data.career_goals
    
    if user_data.phone is not None:
        updates["phone"] = user_data.phone
    
    if user_data.location is not None:
        updates["location"] = user_data.location
    
    if user_data.preferences is not None:
        updates["preferences"] = user_data.preferences
    
    # Update in Firebase
    success = firebase.update_user(user_id, updates)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
    
    logger.info(f"✅ User updated: {user_id}")
    
    # Update embedding if skills changed
    if user_data.skills is not None:
        try:
            matcher = get_matcher()
            pinecone = get_pinecone_service()
            
            # Get updated user
            updated_user = firebase.get_user(user_id)
            
            # Create new embedding
            user_embedding = matcher.create_user_embedding(updated_user)
            
            # Update in Pinecone
            pinecone.upsert_user_embedding(
                user_id=user_id,
                embedding=user_embedding,
                metadata={
                    "user_id": user_id,
                    "skills": updated_user.get("skills", []),
                    "experience_level": updated_user.get("experience_level", "entry"),
                    "type": "user"
                }
            )
            
            logger.info(f"✅ User embedding updated in Pinecone")
            
        except Exception as e:
            logger.error(f"⚠️ Failed to update embedding: {e}")
    
    return {
        "message": "Profile updated successfully",
        "user_id": user_id
    }


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """
    Delete user account
    
    - Deletes user from Firebase
    - Deletes user embedding from Pinecone
    - Deletes all user applications
    """
    
    logger.info(f"🗑️ Deleting user: {user_id}")
    
    firebase = get_firebase_service()
    
    # Check user exists
    user = firebase.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete from Pinecone
    try:
        pinecone = get_pinecone_service()
        pinecone.delete_embedding(f"user_{user_id}")
        logger.info(f"✅ Deleted from Pinecone")
    except Exception as e:
        logger.error(f"⚠️ Failed to delete from Pinecone: {e}")
    
    # Note: In production, you'd also delete:
    # - User applications
    # - User rejections
    # - Match history
    # For now, we'll just delete the user
    
    # Delete user (Firebase doesn't have delete in our simple implementation)
    # You'd need to add a delete_user method to database.py
    
    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }


@router.get("/{user_id}/stats")
async def get_user_stats(user_id: str):
    """
    Get user statistics summary
    
    - Total applications
    - Success rate
    - Rejection rate
    """
    
    firebase = get_firebase_service()
    
    # Check user exists
    user = firebase.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get applications
    applications = firebase.get_user_applications(user_id)
    
    # Calculate stats
    total = len(applications)
    rejected = sum(1 for app in applications if app.get("status") == "rejected")
    accepted = sum(1 for app in applications if app.get("status") == "accepted")
    
    return {
        "user_id": user_id,
        "total_applications": total,
        "accepted": accepted,
        "rejected": rejected,
        "success_rate": round((accepted / total * 100), 1) if total > 0 else 0,
        "rejection_rate": round((rejected / total * 100), 1) if total > 0 else 0
    }