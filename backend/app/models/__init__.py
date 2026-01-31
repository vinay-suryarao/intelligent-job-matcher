"""
Models Package
Data models for reference (Not used directly with Firebase)
Firebase uses NoSQL - these models are for documentation/reference
"""

# These models define the structure of our data
# Firebase Firestore uses collections and documents (NoSQL)
# But we define these for clarity and type hints

__all__ = [
    'user',
    'job',
    'internship',
    'application',
    'rejection',
    'match_history'
]