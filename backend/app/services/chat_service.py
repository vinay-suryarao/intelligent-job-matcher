"""
AI Chat Service
Handles conversational interactions with users
Provides rejection analysis, job recommendations, and guidance
"""

from typing import Dict, List
from app.services.rejection_analyzer import get_rejection_analyzer
from app.services.rag_engine import ask_career_coach
import logging
import json

logger = logging.getLogger(__name__)

class ChatService:
    """Handle chat interactions with users"""
    
    def __init__(self):
        self.rejection_analyzer = get_rejection_analyzer()
    
    def process_message(
        self, 
        message: str, 
        user_data: Dict, 
        context: Dict = {},
        chat_history: List[Dict] = []
    ) -> str:
        """
        Process user message and generate AI response
        
        Args:
            message: User's chat message
            user_data: User profile and history
            context: Additional context (rejections, jobs, etc.)
            chat_history: Previous chat messages
        
        Returns:
            AI response text
        """
        
        message_lower = message.lower()
        
        logger.info(f"💬 Processing message: {message[:50]}...")
        
        # 1. Specialized Handlers (Logic-based)
        # Rejection analysis query
        if any(word in message_lower for word in ['reject', 'rejection', 'why', 'failed', 'denied']):
            return self._handle_rejection_query(user_data, context)
        
        # Job recommendation query
        elif any(word in message_lower for word in ['job', 'apply', 'recommend', 'suggest', 'find']):
            # We can let RAG handle this too if it has job context, 
            # but let's keep the structured response for now as a base
            # return self._handle_job_query(user_data, context)
            pass # Fall through to RAG for better natural language responses
            
        # 2. RAG Engine (AI-based)
        try:
            # Enrich context for RAG
            rag_context = f"""
            User Profile:
            - Name: {user_data.get('full_name')}
            - Skills: {', '.join(user_data.get('skills', []))}
            - Experience: {user_data.get('experience_level')}
            - Interests: {user_data.get('interests')}
            
            Available Jobs (Top Matches):
            {self._format_jobs_for_context(context.get('matched_jobs', [])[:5])}
            
            General Context:
            - This user is using the Intelligent Job Matcher platform.
            """
            
            response = ask_career_coach(message, chat_history, rag_context)
            
            if response and "answer" in response and not response.get("error"):
                logger.info("✅ RAG Engine provided response")
                return response["answer"]
            elif response.get("error"):
                logger.warning(f"⚠️ RAG Engine error: {response.get('error')}")
                # Fallback to logic-based handlers
        except Exception as e:
            logger.error(f"❌ Error invoking RAG Engine: {e}")
            # Fallback continues below
            
        # 3. Fallback Handlers (if RAG fails or for specific keywords)
        
        # Skill improvement query
        if any(word in message_lower for word in ['skill', 'learn', 'improve', 'study', 'course']):
             return self._handle_skill_query(user_data, context)
        
        # Resume query
        elif any(word in message_lower for word in ['resume', 'cv', 'profile', 'update']):
            return self._handle_resume_query(user_data)
        
        # Salary/compensation query
        elif any(word in message_lower for word in ['salary', 'pay', 'compensation', 'package']):
            return self._handle_salary_query(user_data)
        
        # Motivation/encouragement
        elif any(word in message_lower for word in ['sad', 'depressed', 'frustrated', 'tired', 'give up']):
            return self._handle_motivation_query(user_data)
        
        # General greeting
        # elif any(word in message_lower for word in ['hi', 'hello', 'hey', 'start']):
        #     return self._handle_greeting(user_data)
        
        # Help query
        elif any(word in message_lower for word in ['help', 'what can you', 'features']):
            return self._handle_help_query()
        
        # Default response
        else:
            return self._handle_default_query()
    
    def _format_jobs_for_context(self, jobs: List[Dict]) -> str:
        """Format jobs list for AI context"""
        if not jobs:
            return "No specific job matches found yet."
            
        formatted = ""
        for job in jobs:
            formatted += f"- {job.get('title')} at {job.get('company')} ({job.get('location')})\n"
            formatted += f"  Skills: {', '.join(job.get('skills_required', []))}\n"
            formatted += f"  Match Score: {job.get('match_score')}%\n"
            
        return formatted

    def _handle_rejection_query(self, user_data: Dict, context: Dict) -> str:
        """Handle rejection analysis queries"""
        
        rejections = context.get('rejections', [])
        
        if not rejections:
            return """
✅ **Good news!** You haven't been rejected yet.

**Tips to avoid rejections:**
• Apply to jobs with 80%+ match score
• Focus on positions matching your experience level
• Ensure your skills align with requirements

Would you like me to find high-match jobs for you?
            """.strip()
        
        # Analyze rejections
        analysis = self.rejection_analyzer.analyze_user_rejections(user_data, rejections)
        
        response = f"""
📊 **Your Rejection Analysis:**

**Summary:**
• Total Rejections: {analysis['total_rejections']}
• Rejection Rate: {analysis['rejection_rate']}%
• Main Issue: **{analysis['top_reason'].replace('_', ' ').title()}** ({analysis['top_reason_percentage']}%)

"""
        
        # Add missing skills if applicable
        if analysis['top_missing_skills']:
            response += f"""
⚠️ **Skills You're Missing:**
{self._format_list(analysis['top_missing_skills'][:5])}

"""
        
        # Add suggestions
        response += f"""
💡 **What You Should Do:**
{self._format_list(analysis['suggestions'][:5])}

**Trend:** {analysis['trend']}

Ready to turn this around? I can help you find jobs where you WON'T get rejected! 💪
        """
        
        return response.strip()
    
    def _handle_job_query(self, user_data: Dict, context: Dict) -> str:
        """Handle job recommendation queries"""
        # Kept for reference or fallback
        matched_jobs = context.get('matched_jobs', [])
        
        if not matched_jobs:
            return f"""
🔍 **Finding jobs for you...**

Based on your profile:
• Skills: {', '.join(user_data.get('skills', [])[:5])}
• Experience: {user_data.get('experience_level', 'Entry').title()}

I'll search for roles where your **rejection probability is LOW**.

Go to the Jobs tab to see your personalized matches! 🎯
            """.strip()
        
        # Show top 3 jobs
        top_jobs = matched_jobs[:3]
        
        response = f"""
🎯 **Found {len(matched_jobs)} jobs for you!**

**Top 3 Recommendations:**

"""
        
        for i, job in enumerate(top_jobs, 1):
            response += f"""
**{i}. {job.get('title')}** at {job.get('company')}
   • Match Score: {job.get('match_score', 0)}%
   • Rejection Risk: {job.get('rejection_risk', 'Low')} 🟢
   • Location: {job.get('location', 'Remote')}
   
"""
        
        response += "\n📋 Check the Jobs tab for all matches!"
        
        return response.strip()
    
    def _handle_skill_query(self, user_data: Dict, context: Dict) -> str:
        """Handle skill learning queries"""
        
        missing_skills = context.get('top_missing_skills', [])
        
        if not missing_skills:
            # Default high-demand skills
            missing_skills = ['React', 'Docker', 'AWS', 'Python', 'Node.js']
        
        response = f"""
📚 **Skills You Should Learn:**

**High Priority:**
{self._format_list(missing_skills[:5])}

**Free Learning Resources:**
• pure code - Web Development
• Coursera - Python, Data Science
• YouTube - Coding tutorials

**Time Investment:**
• 2-3 hours daily
• Build projects

Learning these will increase your job match rate significantly! 📈
        """.strip()
        
        return response
    
    def _handle_resume_query(self, user_data: Dict) -> str:
        """Handle resume-related queries"""
        
        skills = user_data.get('skills', [])
        
        if not skills:
            return """
📄 **Upload Your Resume**

I noticed you haven't uploaded a resume yet.

**Why upload?**
✅ Auto-extract your skills
✅ Better job matching
✅ Faster profile setup

Go to Profile → Upload Resume to get started!
            """.strip()
        
        response = f"""
📄 **Your Profile Summary:**

**Skills:** {', '.join(skills[:10])}
**Experience Level:** {user_data.get('experience_level', 'Entry').title()}

💡 **Resume Optimization Tips:**

1. **Add More Skills**
   • Include tools, frameworks, and soft skills

2. **Quantify Achievements**
   • "Improved performance by 30%"

3. **Keep It Updated**
   • Add recent projects

Want me to analyze which skills to add for better matches?
        """.strip()
        
        return response
    
    def _handle_salary_query(self, user_data: Dict) -> str:
        """Handle salary/compensation queries"""
        
        experience = user_data.get('experience_level', 'entry')
        
        # Rough salary ranges (India, Tech)
        salary_ranges = {
            'entry': '₹3-6 LPA',
            'mid': '₹8-15 LPA',
            'senior': '₹18-30+ LPA'
        }
        
        expected_range = salary_ranges.get(experience, '₹3-6 LPA')
        
        return f"""
💰 **Salary Insights:**

**Your Experience Level:** {experience.title()}
**Expected Range:** {expected_range}

**Negotiation Tips:**
1. Research First
2. Highlight Value
3. Be Flexible
4. Don't Rush

**Pro Tip:** Companies with 80%+ match scores are more likely to offer competitive packages!
        """.strip()
    
    def _handle_motivation_query(self, user_data: Dict) -> str:
        """Handle motivation/encouragement queries"""
        
        return """
💪 **You've Got This!**

I know job hunting is tough, but don't give up!

**Remember:**
• Every rejection is a learning opportunity
• Even top engineers faced 10+ rejections

**Success Stories:**
• Applied to 50 jobs → Got 3 offers
• Learned new skill → Match rate jumped 60%

**Next Steps:**
1. Take a 15-minute break
2. Apply to 3 HIGH-MATCH jobs today

**Your dream job is waiting - let's find it together!** 🚀
        """.strip()
    
    def _handle_greeting(self, user_data: Dict) -> str:
        """Handle greeting messages"""
        
        name = user_data.get('full_name', 'there')
        
        return f"""
👋 **Hi {name}!**

I'm your AI Job Matcher - here to help you land your dream job!

**What I can do:**

1️⃣ **Rejection Analysis** 
   → "Why am I getting rejected?"

2️⃣ **Smart Job Matching**
   → "Show me jobs regarding Python"

3️⃣ **Skill Recommendations**
   → "What skills should I learn?"

4️⃣ **Career Guidance**
   → "How do I negotiate salary?"

**What would you like help with today?** 🎯
        """.strip()
    
    def _handle_help_query(self) -> str:
        """Handle help queries"""
        
        return """
🤖 **I'm Your AI Career Assistant!**

**I can help you with:**

📊 **Rejection Analysis**
• Understand why you're getting rejected

🎯 **Smart Job Matching**
• Find jobs with HIGH match scores

📚 **Learning Recommendations**
• Identify skills to learn

💼 **Career Guidance**
• Resume optimization tips

**Just ask me anything!**
        """.strip()
    
    def _handle_default_query(self) -> str:
        """Default response for unrecognized queries"""
        
        return """
🤔 **I can help you with:**

• 📊 **Rejection Analysis**
• 🎯 **Job Recommendations**
• 📚 **Skill Suggestions**
• 📄 **Resume Help**

**Try asking me one of these questions!**
        """.strip()
    
    def _format_list(self, items: List[str]) -> str:
        """Format list items with bullets"""
        return '\n'.join([f"• {item}" for item in items])


# Global instance
chat_service_instance = None

def get_chat_service() -> ChatService:
    """Get or create chat service instance"""
    global chat_service_instance
    if chat_service_instance is None:
        chat_service_instance = ChatService()
    return chat_service_instance