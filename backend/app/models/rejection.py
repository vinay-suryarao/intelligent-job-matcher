"""
Rejection Model
Tracks and analyzes job rejections
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class Rejection(BaseModel):
    """
    Rejection Tracking Model
    
    Firestore Collection: rejections
    Document Structure:
    {
        "id": "auto-generated",
        "user_id": "user_123",
        "application_id": "app_789",
        "job_id": "job_456",
        "reason": "skill_gap",
        "skill_gaps": ["Docker", "AWS"],
        "analyzed": true,
        "notes": "Missing cloud computing skills",
        "created_at": timestamp
    }
    """
    
    id: Optional[str] = None
    
    # References
    user_id: str
    application_id: str
    job_id: Optional[str] = None
    internship_id: Optional[str] = None
    
    # Analysis
    reason: str  # skill_gap, experience_gap, overqualified, location_mismatch, other
    skill_gaps: List[str] = []
    
    # Tracking
    analyzed: bool = False
    notes: Optional[str] = ""
    
    # Timestamp
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "application_id": "app_789",
                "job_id": "job_456",
                "reason": "skill_gap",
                "skill_gaps": ["Docker", "Kubernetes", "AWS"],
                "analyzed": True,
                "notes": "User needs to learn DevOps tools"
            }
        }