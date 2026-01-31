"""
Job Model
Defines job posting structure in Firebase (scraped from APIs)
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class Job(BaseModel):
    """
    Job Posting Model
    
    Firestore Collection: jobs
    Document Structure:
    {
        "id": "auto-generated",
        "title": "Senior Python Developer",
        "company": "TechCorp India",
        "description": "Full job description...",
        "required_skills": ["Python", "Django", "AWS"],
        "experience_required": "mid",
        "location": "Bangalore, India",
        "job_type": "remote",
        "salary_min": 1200000,
        "salary_max": 1800000,
        "category": "Technology",
        "source": "adzuna",
        "external_url": "https://...",
        "embedding": [0.23, 0.45, ...],  # 384-dim vector (stored separately in Pinecone)
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
    experience_required: str = "entry"  # entry, mid, senior
    
    # Details
    location: str = "India"
    job_type: str = "remote"  # remote, hybrid, onsite
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    
    # Metadata
    category: str = "Technology"
    source: str = "manual"  # adzuna, jsearch, manual
    external_url: Optional[str] = ""
    
    # AI Fields (embedding stored in Pinecone)
    embedding: Optional[List[float]] = None
    
    # Status
    is_active: bool = True
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Python Backend Developer",
                "company": "TechCorp",
                "description": "We are looking for...",
                "required_skills": ["Python", "FastAPI", "PostgreSQL"],
                "experience_required": "mid",
                "location": "Bangalore",
                "job_type": "remote",
                "salary_min": 1000000,
                "salary_max": 1500000,
                "source": "adzuna"
            }
        }