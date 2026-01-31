"""
Match History Model
Stores user's job matching history for analytics
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class MatchHistory(BaseModel):
    """
    Match History Model
    
    Firestore Collection: match_history
    Document Structure:
    {
        "id": "auto-generated",
        "user_id": "user_123",
        "match_type": "job",
        "match_id": "job_456",
        "match_score": 87.5,
        "rejection_probability": 25.3,
        "skill_gaps": ["Docker"],
        "action_taken": "viewed",
        "created_at": timestamp
    }
    """
    
    id: Optional[str] = None
    
    # References
    user_id: str
    match_type: str  # "job" or "internship"
    match_id: str  # job_id or internship_id
    
    # Match Details
    match_score: float
    rejection_probability: float
    skill_gaps: List[str] = []
    
    # User Action
    action_taken: str = "viewed"  # viewed, applied, rejected, saved
    
    # Timestamp
    created_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "match_type": "job",
                "match_id": "job_456",
                "match_score": 87.5,
                "rejection_probability": 25.3,
                "skill_gaps": ["Docker"],
                "action_taken": "applied"
            }
        }