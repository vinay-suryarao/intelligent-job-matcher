"""
Statistics Service
Calculate detailed analytics for user dashboard
Provides rejection analysis, skill gaps, timeline data, and recommendations
"""

from typing import Dict, List
from collections import Counter
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StatisticsService:
    """Calculate comprehensive statistics for user dashboard"""
    
    def get_user_statistics(self, user_id: str, firebase_db) -> Dict:
        """
        Get comprehensive statistics for user
        
        Args:
            user_id: User identifier
            firebase_db: Firebase service instance
        
        Returns:
            Complete statistics dictionary
        """
        
        logger.info(f"📊 Calculating statistics for user {user_id}")
        
        # Get user data
        user = firebase_db.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        # Get all applications
        applications = firebase_db.get_user_applications(user_id)
        
        # Get rejections
        rejections = firebase_db.get_user_rejections(user_id)
        
        # Separate by type
        job_apps = [app for app in applications if app.get('application_type') == 'job']
        internship_apps = [app for app in applications if app.get('application_type') == 'internship']
        
        # Calculate statistics
        stats = {
            "overview": self._calculate_overview(applications),
            "jobs": self._calculate_type_stats(job_apps),
            "internships": self._calculate_type_stats(internship_apps),
            "rejection_analysis": self._analyze_rejections(rejections, user),
            "skill_gaps": self._analyze_skill_gaps(rejections),
            "timeline": self._get_timeline_data(applications),
            "recommendations": self._generate_recommendations(user, applications, rejections),
            "performance_metrics": self._calculate_performance_metrics(applications)
        }
        
        logger.info("✅ Statistics calculated successfully")
        return stats
    
    def _calculate_overview(self, applications: List[Dict]) -> Dict:
        """Calculate overview statistics"""
        
        total = len(applications)
        if total == 0:
            return {
                "total_applications": 0,
                "success_rate": 0,
                "rejection_rate": 0,
                "pending": 0,
                "rejected": 0,
                "accepted": 0,
                "interview": 0
            }
        
        # Count by status
        rejected = sum(1 for app in applications if app.get('status') == 'rejected')
        accepted = sum(1 for app in applications if app.get('status') == 'accepted')
        pending = sum(1 for app in applications if app.get('status') == 'applied')
        interview = sum(1 for app in applications if app.get('status') == 'interview')
        
        return {
            "total_applications": total,
            "success_rate": round((accepted / total) * 100, 1) if total > 0 else 0,
            "rejection_rate": round((rejected / total) * 100, 1) if total > 0 else 0,
            "pending": pending,
            "rejected": rejected,
            "accepted": accepted,
            "interview": interview
        }
    
    def _calculate_type_stats(self, applications: List[Dict]) -> Dict:
        """Calculate stats for jobs or internships"""
        
        total = len(applications)
        if total == 0:
            return {
                "total": 0,
                "avg_match_score": 0,
                "avg_rejection_prob": 0,
                "best_match_score": 0
            }
        
        total_match_score = sum(app.get('match_score', 0) for app in applications)
        total_rejection_prob = sum(app.get('rejection_probability', 0) for app in applications)
        
        match_scores = [app.get('match_score', 0) for app in applications if app.get('match_score')]
        best_match = max(match_scores) if match_scores else 0
        
        return {
            "total": total,
            "avg_match_score": round(total_match_score / total, 1) if total > 0 else 0,
            "avg_rejection_prob": round(total_rejection_prob / total, 1) if total > 0 else 0,
            "best_match_score": round(best_match, 1)
        }
    
    def _analyze_rejections(self, rejections: List[Dict], user: Dict) -> Dict:
        """Detailed rejection analysis"""
        
        if not rejections:
            return {
                "total": 0,
                "reasons": {},
                "top_reason": None,
                "trend": "No data",
                "recent_count": 0
            }
        
        # Count reasons
        reasons = Counter([r.get('reason', 'unknown') for r in rejections if r.get('reason')])
        
        # Trend analysis (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_rejections = []
        
        for r in rejections:
            created_at = r.get('created_at')
            if created_at:
                # Handle both timestamp and datetime objects
                if hasattr(created_at, 'timestamp'):
                    rejection_date = created_at
                else:
                    rejection_date = created_at
                
                if rejection_date >= thirty_days_ago:
                    recent_rejections.append(r)
        
        # Determine trend
        if len(recent_rejections) < len(rejections) / 2:
            trend = "Improving"
        elif len(recent_rejections) > len(rejections) / 2:
            trend = "Needs Attention"
        else:
            trend = "Stable"
        
        return {
            "total": len(rejections),
            "reasons": dict(reasons),
            "top_reason": reasons.most_common(1)[0][0] if reasons else None,
            "trend": trend,
            "recent_count": len(recent_rejections),
            "improvement_tips": self._get_improvement_tips(reasons.most_common(1)[0][0] if reasons else None)
        }
    
    def _analyze_skill_gaps(self, rejections: List[Dict]) -> Dict:
        """Analyze missing skills across all rejections"""
        
        all_gaps = []
        for rejection in rejections:
            skill_gaps = rejection.get('skill_gaps', [])
            if skill_gaps:
                all_gaps.extend(skill_gaps)
        
        if not all_gaps:
            return {
                "total_unique_gaps": 0,
                "top_missing_skills": [],
                "learning_priority": []
            }
        
        # Count frequency
        gap_counter = Counter(all_gaps)
        top_gaps = gap_counter.most_common(10)
        
        # Priority based on frequency
        priority = []
        for skill, count in top_gaps[:5]:
            if count >= 3:
                priority_level = "High"
            elif count >= 2:
                priority_level = "Medium"
            else:
                priority_level = "Low"
            
            priority.append({
                "skill": skill,
                "frequency": count,
                "priority": priority_level,
                "jobs_unlocked": count  # Number of jobs this skill appears in
            })
        
        return {
            "total_unique_gaps": len(set(all_gaps)),
            "top_missing_skills": [skill for skill, _ in top_gaps],
            "learning_priority": priority,
            "skill_distribution": dict(top_gaps)
        }
    
    def _get_timeline_data(self, applications: List[Dict]) -> List[Dict]:
        """Get application timeline for last 30 days"""
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Filter recent applications
        recent_apps = []
        for app in applications:
            applied_date = app.get('applied_at')
            if applied_date:
                # Handle both timestamp and datetime
                if hasattr(applied_date, 'timestamp'):
                    app_date = applied_date
                else:
                    app_date = applied_date
                
                if app_date >= thirty_days_ago:
                    recent_apps.append(app)
        
        # Group by date
        timeline = {}
        for app in recent_apps:
            applied_date = app.get('applied_at')
            if applied_date:
                date_key = applied_date.strftime('%Y-%m-%d') if hasattr(applied_date, 'strftime') else str(applied_date)[:10]
                
                if date_key not in timeline:
                    timeline[date_key] = {
                        "date": date_key,
                        "applications": 0,
                        "rejections": 0,
                        "acceptances": 0
                    }
                
                timeline[date_key]["applications"] += 1
                
                if app.get('status') == 'rejected':
                    timeline[date_key]["rejections"] += 1
                elif app.get('status') == 'accepted':
                    timeline[date_key]["acceptances"] += 1
        
        # Convert to sorted list
        timeline_list = sorted(timeline.values(), key=lambda x: x['date'])
        
        return timeline_list
    
    def _generate_recommendations(
        self, 
        user: Dict, 
        applications: List[Dict],
        rejections: List[Dict]
    ) -> List[str]:
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Check application count
        if len(applications) < 5:
            recommendations.append("📊 Apply to more positions to improve your chances (target: 10-15 applications)")
        
        # Check rejection rate
        if applications:
            rejection_rate = len(rejections) / len(applications) * 100
            
            if rejection_rate > 70:
                recommendations.append("🎯 Focus on positions with 80%+ match score to reduce rejections")
                recommendations.append("📚 Learn the top 3 missing skills to unlock more opportunities")
            elif rejection_rate > 50:
                recommendations.append("✨ Improve your resume to highlight relevant skills")
                recommendations.append("💼 Consider applying to mid-level roles if you have experience")
            elif rejection_rate < 30:
                recommendations.append("✅ You're doing great! Keep applying consistently")
        
        # Check skill gaps
        skill_gaps = self._analyze_skill_gaps(rejections)
        if skill_gaps['top_missing_skills']:
            top_skill = skill_gaps['top_missing_skills'][0]
            count = skill_gaps['skill_distribution'].get(top_skill, 0)
            recommendations.append(f"💡 Priority: Learn {top_skill} - appears in {count} rejections")
        
        # Add time-based recommendation
        recommendations.append("⏰ Best time to apply: Tuesday-Thursday, 9-11 AM")
        
        # Add motivation
        if rejection_rate > 60:
            recommendations.append("💪 Don't give up! Average person applies to 50+ jobs before success")
        
        return recommendations
    
    def _calculate_performance_metrics(self, applications: List[Dict]) -> Dict:
        """Calculate performance metrics over time"""
        
        if not applications:
            return {
                "response_rate": 0,
                "interview_conversion": 0,
                "average_time_to_response": "N/A"
            }
        
        # Response rate (apps that got any response)
        responded = sum(1 for app in applications if app.get('status') != 'applied')
        response_rate = (responded / len(applications)) * 100 if applications else 0
        
        # Interview conversion (interviews / total apps)
        interviews = sum(1 for app in applications if app.get('status') == 'interview')
        interview_conversion = (interviews / len(applications)) * 100 if applications else 0
        
        return {
            "response_rate": round(response_rate, 1),
            "interview_conversion": round(interview_conversion, 1),
            "average_time_to_response": "3-7 days",  # Placeholder
            "total_companies_applied": len(set(app.get('job', {}).get('company', '') for app in applications))
        }
    
    def _get_improvement_tips(self, top_reason: str) -> List[str]:
        """Get specific improvement tips based on rejection reason"""
        
        tips_map = {
            "skill_gap": [
                "Enroll in online courses for missing skills",
                "Build portfolio projects demonstrating skills",
                "Contribute to open source projects"
            ],
            "experience_gap": [
                "Apply to entry-level positions",
                "Highlight relevant projects and internships",
                "Consider contract roles to gain experience"
            ],
            "overqualified": [
                "Target senior-level positions",
                "Apply to larger companies with bigger budgets",
                "Negotiate for appropriate compensation"
            ],
            "location_mismatch": [
                "Focus on remote opportunities",
                "Update location preferences",
                "Consider relocation if possible"
            ]
        }
        
        return tips_map.get(top_reason, ["Keep applying and stay consistent"])


# Global instance
stats_service_instance = None

def get_statistics_service() -> StatisticsService:
    """Get or create statistics service instance"""
    global stats_service_instance
    if stats_service_instance is None:
        stats_service_instance = StatisticsService()
    return stats_service_instance