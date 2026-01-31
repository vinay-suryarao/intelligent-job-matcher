"""
Rejection Analyzer Service
Analyzes why user is getting rejected and provides recommendations
"""

from typing import List, Dict
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class RejectionAnalyzer:
    """Analyze rejection patterns and generate insights"""
    
    def analyze_user_rejections(
        self, 
        user_data: Dict, 
        rejections: List[Dict]
    ) -> Dict:
        """
        Analyze rejection patterns for a user
        
        Args:
            user_data: User profile dict
            rejections: List of rejection records
        
        Returns:
            Detailed analysis with recommendations
        """
        
        if not rejections:
            return {
                "total_rejections": 0,
                "analysis": "No rejections yet. Keep applying!",
                "suggestions": [
                    "Apply to more jobs matching your skills",
                    "Focus on positions with 80%+ match score",
                    "Ensure your profile is complete"
                ]
            }
        
        logger.info(f"🔍 Analyzing {len(rejections)} rejections...")
        
        # Count rejection reasons
        rejection_reasons = {
            "skill_gap": 0,
            "experience_gap": 0,
            "overqualified": 0,
            "location_mismatch": 0,
            "other": 0
        }
        
        all_missing_skills = []
        
        for rejection in rejections:
            # Categorize rejection
            reason = rejection.get('reason', 'other')
            if reason in rejection_reasons:
                rejection_reasons[reason] += 1
            else:
                rejection_reasons['other'] += 1
            
            # Collect missing skills
            skill_gaps = rejection.get('skill_gaps', [])
            if skill_gaps:
                all_missing_skills.extend(skill_gaps)
        
        # Find top reason
        top_reason = max(rejection_reasons, key=rejection_reasons.get)
        
        # Get most common missing skills
        skill_counter = Counter(all_missing_skills)
        top_missing_skills = skill_counter.most_common(10)
        
        # Generate suggestions based on analysis
        suggestions = self._generate_suggestions(
            top_reason, 
            top_missing_skills, 
            user_data
        )
        
        # Calculate rejection rate trend
        rejection_rate = len(rejections) / max(user_data.get('total_applications', 1), 1) * 100
        
        analysis_result = {
            "total_rejections": len(rejections),
            "rejection_rate": round(rejection_rate, 1),
            "rejection_breakdown": rejection_reasons,
            "top_reason": top_reason,
            "top_reason_percentage": round(
                (rejection_reasons[top_reason] / len(rejections)) * 100, 1
            ),
            "top_missing_skills": [skill for skill, count in top_missing_skills],
            "skill_frequency": {skill: count for skill, count in top_missing_skills},
            "suggestions": suggestions,
            "trend": self._analyze_trend(rejections)
        }
        
        logger.info(f"✅ Analysis complete - Top reason: {top_reason}")
        return analysis_result
    
    def _generate_suggestions(
        self, 
        top_reason: str, 
        missing_skills: List[tuple],
        user_data: Dict
    ) -> List[str]:
        """
        Generate actionable suggestions based on analysis
        
        Args:
            top_reason: Main rejection reason
            missing_skills: List of (skill, frequency) tuples
            user_data: User profile
        
        Returns:
            List of suggestion strings
        """
        
        suggestions = []
        
        if top_reason == "skill_gap":
            if missing_skills:
                top_3_skills = [skill for skill, _ in missing_skills[:3]]
                suggestions.append(
                    f"🎓 Learn these high-demand skills: {', '.join(top_3_skills)}"
                )
            
            suggestions.extend([
                "📚 Take free courses on Coursera, Udemy, or freeCodeCamp",
                "💻 Build 2-3 portfolio projects showcasing these skills",
                "📝 Update your resume to highlight relevant skills",
                "🔗 Add completed projects to your GitHub profile"
            ])
        
        elif top_reason == "experience_gap":
            suggestions.extend([
                "🔰 Focus on entry-level and junior positions",
                "🤝 Consider internships to gain experience",
                "📝 Highlight your projects and learning in resume",
                "💼 Look for companies hiring freshers",
                "🎯 Apply to startups (more flexible requirements)"
            ])
        
        elif top_reason == "overqualified":
            suggestions.extend([
                "📈 Apply for senior/lead positions",
                "💼 Look for management or architect roles",
                "🎯 Target companies with larger budgets",
                "🏢 Consider roles at bigger organizations",
                "💡 Highlight leadership experience"
            ])
        
        elif top_reason == "location_mismatch":
            suggestions.extend([
                "🌍 Focus on remote positions",
                "📍 Update your location preferences",
                "🚗 Consider relocation if possible",
                "💻 Apply to remote-first companies"
            ])
        
        else:
            suggestions.extend([
                "✅ Keep applying - consistency is key!",
                "🔍 Use our AI matching to find better-fit jobs",
                "📧 Set up email alerts for new matching jobs",
                "📊 Review your application strategy"
            ])
        
        # Add specific skill learning resources
        if missing_skills:
            top_skill = missing_skills[0][0]
            suggestions.append(
                f"🎯 Priority: Master {top_skill} (appears in {missing_skills[0][1]} rejections)"
            )
        
        return suggestions
    
    def _analyze_trend(self, rejections: List[Dict]) -> str:
        """
        Analyze if rejection rate is improving or worsening
        
        Args:
            rejections: List of rejection records
        
        Returns:
            Trend description
        """
        
        if len(rejections) < 3:
            return "Not enough data for trend analysis"
        
        # Simple trend: compare first half vs second half
        mid_point = len(rejections) // 2
        first_half = rejections[:mid_point]
        second_half = rejections[mid_point:]
        
        # If we had timestamps, we'd use those
        # For now, assume list is chronological
        
        if len(second_half) < len(first_half):
            return "Improving - Fewer recent rejections"
        elif len(second_half) > len(first_half):
            return "Worsening - More recent rejections"
        else:
            return "Stable - Consistent rejection rate"
    
    def get_recommendation_priority(self, analysis: Dict) -> List[Dict]:
        """
        Prioritize recommendations by impact
        
        Args:
            analysis: Output from analyze_user_rejections
        
        Returns:
            Prioritized list of actions
        """
        
        priorities = []
        
        # High priority: Top missing skills
        if analysis.get('top_missing_skills'):
            for skill in analysis['top_missing_skills'][:3]:
                frequency = analysis['skill_frequency'].get(skill, 0)
                priorities.append({
                    "action": f"Learn {skill}",
                    "priority": "High",
                    "impact": f"Unlocks {frequency} jobs",
                    "time_estimate": "2-4 weeks"
                })
        
        # Medium priority: Experience level adjustment
        if analysis['top_reason'] == 'experience_gap':
            priorities.append({
                "action": "Apply to entry-level positions only",
                "priority": "High",
                "impact": "40% better success rate",
                "time_estimate": "Immediate"
            })
        
        # Low priority: Profile optimization
        priorities.append({
            "action": "Update resume with keywords",
            "priority": "Medium",
            "impact": "15% better visibility",
            "time_estimate": "1-2 hours"
        })
        
        return priorities


# Global instance
analyzer_instance = None

def get_rejection_analyzer() -> RejectionAnalyzer:
    """Get or create rejection analyzer instance"""
    global analyzer_instance
    if analyzer_instance is None:
        analyzer_instance = RejectionAnalyzer()
    return analyzer_instance