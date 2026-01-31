"""
Internships Routes
Internship CRUD operations
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import logging

from app.services.database import get_firebase_service
from app.services.ai_matcher import get_matcher
from app.services.pinecone_service import get_pinecone_service

router = APIRouter(prefix="/api/internships", tags=["internships"])
logger = logging.getLogger(__name__)

# ========================================
# REQUEST/RESPONSE MODELS
# ========================================

class InternshipCreate(BaseModel):
    title: str
    company: str
    description: str
    required_skills: List[str] = []
    duration_months: int = 6
    stipend_min: Optional[int] = None
    stipend_max: Optional[int] = None
    location: str = "India"
    internship_type: str = "remote"
    education_required: str = "pursuing"
    year_of_study: str = "any"
    external_url: Optional[str] = ""

# ========================================
# ENDPOINTS
# ========================================

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_internship(internship_data: InternshipCreate):
    """
    Create internship posting
    
    - Creates in Firebase
    - Generates embedding
    - Stores in Pinecone
    """
    
    logger.info(f"📝 Creating internship: {internship_data.title}")
    
    firebase = get_firebase_service()
    matcher = get_matcher()
    pinecone = get_pinecone_service()
    
    # Prepare data
    internship_dict = {
        "title": internship_data.title,
        "company": internship_data.company,
        "description": internship_data.description,
        "required_skills": internship_data.required_skills,
        "duration_months": internship_data.duration_months,
        "stipend_min": internship_data.stipend_min,
        "stipend_max": internship_data.stipend_max,
        "location": internship_data.location,
        "internship_type": internship_data.internship_type,
        "education_required": internship_data.education_required,
        "year_of_study": internship_data.year_of_study,
        "external_url": internship_data.external_url,
        "source": "manual",
        "is_active": True
    }
    
    # Create in Firebase
    internship_id = firebase.create_internship(internship_dict)
    
    if not internship_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create internship"
        )
    
    logger.info(f"✅ Internship created: {internship_id}")
    
    # Generate embedding (treat like job)
    try:
        internship_embedding = matcher.create_job_embedding(internship_dict)
        
        # Store in Pinecone
        pinecone.upsert_job_embedding(
            job_id=internship_id,
            embedding=internship_embedding,
            metadata={
                "internship_id": internship_id,
                "title": internship_data.title,
                "company": internship_data.company,
                "type": "internship",
                "source": "manual"
            }
        )
        
        logger.info(f"✅ Internship embedding created")
        
    except Exception as e:
        logger.error(f"⚠️ Failed to create embedding: {e}")
    
    return {
        "message": "Internship created successfully",
        "internship_id": internship_id
    }


@router.get("/list")
async def list_internships(
    skip: int = 0,
    limit: int = 50,
    location: Optional[str] = None,
    internship_type: Optional[str] = None
):
    """
    List all internships with filters
    """
    
    logger.info(f"📋 Listing internships")
    
    firebase = get_firebase_service()
    
    # Get all internships (simple query to avoid index issues)
    all_internships = []
    try:
        if firebase.db:
            docs = firebase.db.collection('internships').limit(200).stream()
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                all_internships.append(data)
    except Exception as e:
        logger.error(f"Error fetching internships: {e}")
    
    # Apply filters
    filtered = all_internships
    
    if location:
        filtered = [
            i for i in filtered 
            if location.lower() in i.get("location", "").lower()
        ]
    
    if internship_type:
        filtered = [
            i for i in filtered 
            if i.get("internship_type") == internship_type
        ]
    
    # Pagination
    paginated = filtered[skip:skip + limit]
    
    return {
        "total": len(filtered),
        "skip": skip,
        "limit": limit,
        "internships": paginated
    }


@router.get("/{internship_id}")
async def get_internship(internship_id: str):
    """Get single internship details"""
    
    logger.info(f"🔍 Getting internship: {internship_id}")
    
    firebase = get_firebase_service()
    internship = firebase.get_internship(internship_id)
    
    if not internship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Internship not found"
        )
    
    return {
        "internship": internship
    }