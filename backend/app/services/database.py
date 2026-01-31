"""
Firebase Database Service
Handles all Firestore operations for jobs, internships, users
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class FirebaseService:
    """Firebase Firestore database operations"""
    
    def __init__(self):
        """Initialize Firebase connection"""
        
        # Check multiple possible env variable names
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH") or os.getenv("FIREBASE_CRED_PATH")
        
        logger.info(f"🔥 Looking for Firebase credentials at: {cred_path}")
        
        if not cred_path:
            logger.warning("⚠️ Firebase credentials path not found in .env")
            self.db = None
            return
        
        if not os.path.exists(cred_path):
            logger.warning(f"⚠️ Firebase credentials file not found: {cred_path}")
            self.db = None
            return
        
        try:
            # Initialize Firebase (only once)
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("✅ Firebase initialized successfully!")
            
            self.db = firestore.client()
            logger.info("✅ Firestore client ready!")
            
        except Exception as e:
            logger.error(f"❌ Firebase initialization error: {e}")
            self.db = None
    
    # ========================================
    # USER OPERATIONS
    # ========================================
    
    def create_user(self, user_data: Dict) -> Optional[str]:
        """Create new user in Firestore"""
        
        if not self.db:
            logger.error("❌ Database not initialized")
            return None
        
        try:
            # Add timestamps
            user_data['created_at'] = datetime.utcnow()
            user_data['updated_at'] = datetime.utcnow()
            
            # Create document
            doc_ref = self.db.collection('users').add(user_data)
            user_id = doc_ref[1].id
            
            logger.info(f"✅ User created: {user_id}")
            return user_id
            
        except Exception as e:
            logger.error(f"❌ Error creating user: {e}")
            return None
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        
        if not self.db:
            return None
        
        try:
            doc = self.db.collection('users').document(user_id).get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        
        if not self.db:
            return None
        
        try:
            query = self.db.collection('users').where('email', '==', email).limit(1)
            docs = list(query.stream())
            
            if docs:
                data = docs[0].to_dict()
                data['id'] = docs[0].id
                return data
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting user by email: {e}")
            return None
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user profile"""
        
        if not self.db:
            return False
        
        try:
            updates['updated_at'] = datetime.utcnow()
            
            self.db.collection('users').document(user_id).update(updates)
            logger.info(f"✅ User updated: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating user: {e}")
            return False
    
    def get_all_users(self, limit: int = 100) -> List[Dict]:
        """Get all users"""
        
        if not self.db:
            return []
        
        try:
            query = self.db.collection('users').limit(limit)
            docs = query.stream()
            
            users = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                users.append(data)
            
            return users
            
        except Exception as e:
            logger.error(f"❌ Error getting users: {e}")
            return []
    
    # ========================================
    # JOB OPERATIONS
    # ========================================
    
    def create_job(self, job_data: Dict) -> Optional[str]:
        """Create new job in Firestore"""
        
        if not self.db:
            logger.error("❌ Database not initialized")
            return None
        
        try:
            # Add timestamps
            job_data['created_at'] = datetime.utcnow()
            job_data['updated_at'] = datetime.utcnow()
            job_data['is_active'] = job_data.get('is_active', True)
            
            # Create document
            doc_ref = self.db.collection('jobs').add(job_data)
            job_id = doc_ref[1].id
            
            logger.info(f"✅ Job created: {job_id}")
            return job_id
            
        except Exception as e:
            logger.error(f"❌ Error creating job: {e}")
            return None
    
    def get_job(self, job_id: str) -> Optional[Dict]:
        """Get job by ID"""
        
        if not self.db:
            return None
        
        try:
            doc = self.db.collection('jobs').document(job_id).get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting job: {e}")
            return None
    
    def get_all_jobs(self, limit: int = 100, is_active: bool = True) -> List[Dict]:
        """Get all jobs with optional filters"""
        
        if not self.db:
            return []
        
        try:
            query = self.db.collection('jobs')
            
            if is_active:
                query = query.where('is_active', '==', True)
            
            query = query.order_by('created_at', direction=firestore.Query.DESCENDING)
            query = query.limit(limit)
            
            docs = query.stream()
            
            jobs = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                jobs.append(data)
            
            return jobs
            
        except Exception as e:
            logger.error(f"❌ Error getting jobs: {e}")
            return []
    
    def update_job(self, job_id: str, updates: Dict) -> bool:
        """Update job posting"""
        
        if not self.db:
            return False
        
        try:
            updates['updated_at'] = datetime.utcnow()
            
            self.db.collection('jobs').document(job_id).update(updates)
            logger.info(f"✅ Job updated: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating job: {e}")
            return False
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job posting"""
        
        if not self.db:
            return False
        
        try:
            self.db.collection('jobs').document(job_id).delete()
            logger.info(f"✅ Job deleted: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting job: {e}")
            return False
    
    def check_job_exists(self, title: str, company: str) -> bool:
        """Check if job already exists (avoid duplicates)"""
        
        if not self.db:
            return False
        
        try:
            query = self.db.collection('jobs')\
                .where('title', '==', title)\
                .where('company', '==', company)\
                .limit(1)
            
            docs = list(query.stream())
            return len(docs) > 0
            
        except Exception as e:
            logger.error(f"❌ Error checking job exists: {e}")
            return False
    
    # ========================================
    # INTERNSHIP OPERATIONS
    # ========================================
    
    def create_internship(self, internship_data: Dict) -> Optional[str]:
        """Create new internship in Firestore"""
        
        if not self.db:
            logger.error("❌ Database not initialized")
            return None
        
        try:
            # Add timestamps
            internship_data['created_at'] = datetime.utcnow()
            internship_data['updated_at'] = datetime.utcnow()
            internship_data['is_active'] = True
            
            # Create document
            doc_ref = self.db.collection('internships').add(internship_data)
            internship_id = doc_ref[1].id
            
            logger.info(f"✅ Internship created: {internship_id}")
            return internship_id
            
        except Exception as e:
            logger.error(f"❌ Error creating internship: {e}")
            return None
    
    def get_internship(self, internship_id: str) -> Optional[Dict]:
        """Get internship by ID"""
        
        if not self.db:
            return None
        
        try:
            doc = self.db.collection('internships').document(internship_id).get()
            
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting internship: {e}")
            return None
    
    def get_all_internships(self, limit: int = 100, is_active: bool = True) -> List[Dict]:
        """Get all internships"""
        
        if not self.db:
            return []
        
        try:
            query = self.db.collection('internships')
            
            if is_active:
                query = query.where('is_active', '==', True)
            
            query = query.order_by('created_at', direction=firestore.Query.DESCENDING)
            query = query.limit(limit)
            
            docs = query.stream()
            
            internships = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                internships.append(data)
            
            return internships
            
        except Exception as e:
            logger.error(f"❌ Error getting internships: {e}")
            return []
    
    def update_internship(self, internship_id: str, updates: Dict) -> bool:
        """Update internship"""
        
        if not self.db:
            return False
        
        try:
            updates['updated_at'] = datetime.utcnow()
            
            self.db.collection('internships').document(internship_id).update(updates)
            logger.info(f"✅ Internship updated: {internship_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating internship: {e}")
            return False
    
    def delete_internship(self, internship_id: str) -> bool:
        """Delete internship"""
        
        if not self.db:
            return False
        
        try:
            self.db.collection('internships').document(internship_id).delete()
            logger.info(f"✅ Internship deleted: {internship_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting internship: {e}")
            return False
    
    def check_internship_exists(self, title: str, company: str) -> bool:
        """Check if internship already exists"""
        
        if not self.db:
            return False
        
        try:
            query = self.db.collection('internships')\
                .where('title', '==', title)\
                .where('company', '==', company)\
                .limit(1)
            
            docs = list(query.stream())
            return len(docs) > 0
            
        except Exception as e:
            logger.error(f"❌ Error checking internship: {e}")
            return False
    
    # ========================================
    # APPLICATION OPERATIONS
    # ========================================
    
    def create_application(self, application_data: Dict) -> Optional[str]:
        """Create job/internship application"""
        
        if not self.db:
            return None
        
        try:
            application_data['created_at'] = datetime.utcnow()
            application_data['status'] = application_data.get('status', 'applied')
            
            doc_ref = self.db.collection('applications').add(application_data)
            return doc_ref[1].id
            
        except Exception as e:
            logger.error(f"❌ Error creating application: {e}")
            return None
    
    def get_user_applications(self, user_id: str) -> List[Dict]:
        """Get all applications for a user"""
        
        if not self.db:
            return []
        
        try:
            query = self.db.collection('applications')\
                .where('user_id', '==', user_id)\
                .order_by('created_at', direction=firestore.Query.DESCENDING)
            
            docs = query.stream()
            
            applications = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                applications.append(data)
            
            return applications
            
        except Exception as e:
            logger.error(f"❌ Error getting applications: {e}")
            return []
    
    def update_application_status(self, application_id: str, status: str, rejection_reason: str = None) -> bool:
        """Update application status (applied, interview, rejected, accepted)"""
        
        if not self.db:
            return False
        
        try:
            updates = {
                'status': status,
                'updated_at': datetime.utcnow()
            }
            
            if rejection_reason:
                updates['rejection_reason'] = rejection_reason
            
            self.db.collection('applications').document(application_id).update(updates)
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating application: {e}")
            return False
    
    # ========================================
    # STATISTICS
    # ========================================
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        
        if not self.db:
            return {}
        
        try:
            # Count documents in each collection
            users_count = len(list(self.db.collection('users').limit(1000).stream()))
            jobs_count = len(list(self.db.collection('jobs').where('is_active', '==', True).limit(1000).stream()))
            internships_count = len(list(self.db.collection('internships').where('is_active', '==', True).limit(1000).stream()))
            applications_count = len(list(self.db.collection('applications').limit(1000).stream()))
            
            return {
                'total_users': users_count,
                'total_jobs': jobs_count,
                'total_internships': internships_count,
                'total_applications': applications_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting statistics: {e}")
            return {}


# ========================================
# GLOBAL INSTANCE
# ========================================

firebase_instance = None

def get_firebase_service() -> FirebaseService:
    """Get or create Firebase service instance"""
    global firebase_instance
    if firebase_instance is None:
        firebase_instance = FirebaseService()
    return firebase_instance

def init_db():
    """Initialize database (called on startup)"""
    service = get_firebase_service()
    if service.db:
        logger.info("✅ Database connection verified")
    else:
        logger.warning("⚠️ Database not available")
    return service