"""
Notification Service
Finds matching users for new jobs and sends email notifications
"""

from typing import List, Dict
import logging
from app.services.database import get_firebase_service
from app.services.ai_matcher import get_matcher
from app.services.pinecone_service import get_pinecone_service
from app.services.email_service import get_email_service

logger = logging.getLogger(__name__)

class NotificationService:
    """Handle job match notifications"""
    
    def __init__(self):
        self.firebase = get_firebase_service()
        self.matcher = get_matcher()
        self.pinecone = get_pinecone_service()
        self.email_service = get_email_service()
        
        # Minimum match score to notify (%)
        self.min_match_score = 70
    
    def notify_matching_users_for_job(self, job_data: Dict, job_id: str) -> Dict:
        """
        Find users matching a new job and send email notifications
        
        Args:
            job_data: Job details dict
            job_id: Job ID in database
        
        Returns:
            Stats about notifications sent
        """
        
        logger.info(f"🔔 Finding matching users for job: {job_data.get('title')}")
        
        stats = {
            "job_id": job_id,
            "job_title": job_data.get('title'),
            "users_matched": 0,
            "emails_sent": 0,
            "emails_failed": 0,
            "matched_users": []
        }
        
        try:
            # Step 1: Create job embedding (for searching users)
            job_embedding = self.matcher.create_job_embedding(job_data, for_search=True)
            
            # Step 2: Find matching users in Pinecone
            matching_users = self.pinecone.find_matching_users(
                job_embedding=job_embedding,
                top_k=50  # Max 50 users per job notification
            )
            
            if not matching_users:
                logger.info("⚠️ No matching users found in Pinecone")
                return stats
            
            logger.info(f"📊 Found {len(matching_users)} potential matches in Pinecone")
            
            # Step 3: Filter by minimum score and send emails
            for match in matching_users:
                user_id = match['id']
                score = match['score']
                
                # Skip low matches
                if score < self.min_match_score:
                    continue
                
                stats["users_matched"] += 1
                
                # Get full user details from Firebase
                user = self.firebase.get_user(user_id)
                
                if not user:
                    logger.warning(f"⚠️ User {user_id} not found in Firebase")
                    continue
                
                # Check if user has email
                user_email = user.get('email')
                if not user_email:
                    continue
                
                user_name = user.get('full_name', 'User')
                
                # Calculate skill gaps
                skill_gaps = self.matcher.find_skill_gaps(
                    user.get('skills', []),
                    job_data.get('required_skills', [])
                )
                
                # Send email notification
                try:
                    success = self.email_service.send_job_match_notification(
                        user_email=user_email,
                        user_name=user_name,
                        job=job_data,
                        match_score=score,
                        skill_gaps=skill_gaps
                    )
                    
                    if success:
                        stats["emails_sent"] += 1
                        stats["matched_users"].append({
                            "user_id": user_id,
                            "email": user_email,
                            "score": round(score, 2)
                        })
                        logger.info(f"✅ Email sent to {user_email} (Score: {score:.1f}%)")
                    else:
                        stats["emails_failed"] += 1
                        
                except Exception as e:
                    logger.error(f"❌ Failed to send email to {user_email}: {e}")
                    stats["emails_failed"] += 1
            
            logger.info(f"🎉 Notification complete: {stats['emails_sent']} emails sent")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Notification error: {e}")
            return stats
    
    def notify_user_for_new_matches(self, user_id: str, min_score: float = 70) -> Dict:
        """
        Find new matching jobs for a user and send digest email
        
        Args:
            user_id: User ID
            min_score: Minimum match score
        
        Returns:
            Stats about notification
        """
        
        logger.info(f"🔔 Finding new matches for user: {user_id}")
        
        stats = {
            "user_id": user_id,
            "jobs_matched": 0,
            "email_sent": False
        }
        
        try:
            # Get user
            user = self.firebase.get_user(user_id)
            if not user:
                logger.warning(f"⚠️ User {user_id} not found")
                return stats
            
            # Create user embedding
            user_embedding = self.matcher.create_user_embedding(user, for_search=True)
            
            # Find matching jobs in Pinecone
            matching_jobs = self.pinecone.find_matching_jobs(
                user_embedding=user_embedding,
                top_k=10
            )
            
            if not matching_jobs:
                logger.info("⚠️ No matching jobs found")
                return stats
            
            # Filter by score and get full job details
            jobs_to_notify = []
            
            for match in matching_jobs:
                if match['score'] >= min_score:
                    job = self.firebase.get_job(match['id'])
                    if job:
                        jobs_to_notify.append({
                            'job': job,
                            'match_score': match['score']
                        })
            
            if not jobs_to_notify:
                logger.info("⚠️ No jobs above minimum score")
                return stats
            
            stats["jobs_matched"] = len(jobs_to_notify)
            
            # Send digest email
            success = self.email_service.send_multiple_job_matches(
                user_email=user.get('email'),
                user_name=user.get('full_name', 'User'),
                jobs=jobs_to_notify
            )
            
            stats["email_sent"] = success
            
            if success:
                logger.info(f"✅ Digest email sent to {user.get('email')}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return stats


# Global instance
notification_service_instance = None

def get_notification_service() -> NotificationService:
    """Get or create notification service instance"""
    global notification_service_instance
    if notification_service_instance is None:
        notification_service_instance = NotificationService()
    return notification_service_instance