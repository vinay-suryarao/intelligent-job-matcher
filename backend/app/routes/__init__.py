"""
Routes Package
All API endpoints
"""

from app.routes import auth, users, jobs, internships, matching, chat, statistics

__all__ = [
    'auth',
    'users',
    'jobs',
    'internships',
    'matching',
    'chat',
    'statistics'
]