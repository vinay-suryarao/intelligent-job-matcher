"""
User Model
Defines user profile structure in Firebase
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    """
    User Profile Model
    
    Firestore Collection: users
    Document Structure:
    {
        "id": "auto-generated",
        "email": "user@example.com",
        "hashed_password": "bcrypt_hash",
        "full_name": "John Doe",
        "skills": ["Python", "React", "AWS"],
        "experience_level": "mid",
        "interests": "Backend development, Cloud computing",
        "career_goals": "Become a senior developer",
        "education": ["B.Tech Computer Science"],
        "phone": "+91 1234567890",
        "location": "Bangalore, India",
        "resume_url": "uploads/resumes/user_123.pdf",
        "preferences": {
            "job_type": "remote",
            "locations": ["Bangalore", "Mumbai"],
            "min_salary": 800000
        },
        "rejection_history": [],
        "created_at": timestamp,
        "updated_at": timestamp
    }
    """
    
    id: Optional[str] = None
    email: EmailStr
    hashed_password: str
    full_name: str
    
    # Skills and Experience
    skills: List[str] = []
    experience_level: str = "entry"  # entry, mid, senior
    interests: Optional[str] = ""
    career_goals: Optional[str] = ""
    education: List[str] = []
    
    # Contact
    phone: Optional[str] = ""
    location: Optional[str] = ""
    
    # Resume
    resume_url: Optional[str] = ""
    
    # Preferences
    preferences: dict = {
        "job_type": "remote",  # remote, hybrid, onsite
        "locations": [],
        "min_salary": 0
    }
    
    # Tracking
    rejection_history: List[str] = []  # List of job IDs
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "hashed_password": "$2b$12$...",
                "full_name": "John Doe",
                "skills": ["Python", "Django", "React"],
                "experience_level": "mid",
                "interests": "Full-stack development",
                "career_goals": "Become a tech lead",
                "education": ["B.Tech CSE"],
                "phone": "+91 9876543210",
                "location": "Bangalore"
            }
        }