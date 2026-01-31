"""
Internship Model
Defines internship posting structure in Firebase
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class Internship(BaseModel):
    """
    Internship Posting Model
    
    Firestore Collection: internships
    Document Structure:
    {
        "id": "auto-generated",
        "title": "Software Development Intern",
        "company": "StartupCo",
        "description": "Internship description...",
        "required_skills": ["Python", "Git"],
        "duration_months": 6,
        "stipend_min": 10000,
        "stipend_max": 25000,
        "location": "Remote",
        "internship_type": "remote",
        "education_required": "pursuing",
        "year_of_study": "any",
        "source": "manual",
        "external_url": "https://...",
        "is_active": true,
        "created_at": timestamp,
        "updated_at": timestamp
    }
    """
    
    id: Optional[str] = None
    
    # Basic Info
    title: str
    company: str
    description: str
    
    # Requirements
    required_skills: List[str] = []
    duration_months: Optional[int] = 6
    
    # Compensation
    stipend_min: Optional[int] = None
    stipend_max: Optional[int] = None
    
    # Details
    location: str = "India"
    internship_type: str = "remote"  # remote, hybrid, onsite
    
    # Eligibility
    education_required: str = "pursuing"  # pursuing, graduated, any
    year_of_study: str = "any"  # 1st, 2nd, 3rd, 4th, any
    
    # Metadata
    source: str = "manual"
    external_url: Optional[str] = ""
    
    # AI Fields
    embedding: Optional[List[float]] = None
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Backend Development Intern",
                "company": "StartupXYZ",
                "description": "Work on backend APIs...",
                "required_skills": ["Python", "FastAPI"],
                "duration_months": 6,
                "stipend_min": 15000,
                "stipend_max": 25000,
                "location": "Remote",
                "education_required": "pursuing",
                "year_of_study": "any"
            }
        }