"""
Application Model
Tracks user job/internship applications
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class Application(BaseModel):
    """
    Application Tracking Model
    
    Firestore Collection: applications
    Document Structure:
    {
        "id": "auto-generated",
        "user_id": "user_123",
        "application_type": "job",
        "job_id": "job_456",
        "internship_id": null,
        "status": "applied",
        "match_score": 87.5,
        "rejection_probability": 25.3,
        "applied_at": timestamp,
        "updated_at": timestamp
    }
    """
    
    id: Optional[str] = None
    
    # References
    user_id: str
    application_type: str  # "job" or "internship"
    job_id: Optional[str] = None
    internship_id: Optional[str] = None
    
    # Status
    status: str = "applied"  # applied, rejected, accepted, interview
    
    # Match Data (at time of application)
    match_score: Optional[float] = None
    rejection_probability: Optional[float] = None
    
    # Timestamps
    applied_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "application_type": "job",
                "job_id": "job_456",
                "status": "applied",
                "match_score": 87.5,
                "rejection_probability": 25.3
            }
        }