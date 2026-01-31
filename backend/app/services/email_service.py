"""
Email Service
Send job match notifications to users
Supports Gmail, Outlook, and custom SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import os
from dotenv import load_dotenv
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

load_dotenv()
logger = logging.getLogger(__name__)

class EmailService:
    """Send email notifications to users"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.email = os.getenv("SMTP_EMAIL")
        self.password = os.getenv("SMTP_PASSWORD")
        self.app_name = os.getenv("APP_NAME", "Intelligent Job Matcher")
        
        # Thread pool for async email sending
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        if not self.email or not self.password:
            logger.warning("⚠️ Email credentials not configured")
        else:
            logger.info(f"✅ Email service ready: {self.email}")
    
    def _send_email_sync(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = ""
    ) -> bool:
        """
        Send email (synchronous - used internally)
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML body
            text_content: Plain text body (fallback)
        
        Returns:
            Success status
        """
        
        if not self.email or not self.password:
            logger.warning("⚠️ Email credentials not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.app_name} <{self.email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach both plain text and HTML
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    async def send_email_async(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = ""
    ) -> bool:
        """Send email asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._send_email_sync,
            to_email,
            subject,
            html_content,
            text_content
        )
    
    async def send_password_reset_email(
        self,
        to_email: str,
        reset_link: str,
        user_name: str = "User"
    ) -> bool:
        """
        Send password reset email
        
        Args:
            to_email: User's email
            reset_link: Password reset link
            user_name: User's name
        
        Returns:
            Success status
        """
        
        subject = "🔐 HIRESTORM - Password Reset Request"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #EAEFEF;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 0;">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #2D3E50 0%, #1a252f 100%); padding: 30px; text-align: center;">
                    <h1 style="color: #FF9F56; margin: 0; font-size: 28px; font-weight: 900; letter-spacing: -2px;">
                        HIRESTORM
                    </h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">
                        Password Reset Request
                    </p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    
                    <p style="font-size: 16px; color: #333;">
                        Hi <strong>{user_name}</strong>,
                    </p>
                    
                    <p style="font-size: 16px; color: #333;">
                        We received a request to reset your password. Click the button below to create a new password:
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" 
                           style="background: #FF9F56; color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                            🔑 Reset Password
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666;">
                        If you didn't request a password reset, you can safely ignore this email.
                    </p>
                    
                    <p style="font-size: 14px; color: #666;">
                        This link will expire in 1 hour for security reasons.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #999; text-align: center;">
                        © 2024 HIRESTORM | Your Career Partner
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Hi {user_name},
        
        We received a request to reset your password.
        
        Click this link to reset: {reset_link}
        
        If you didn't request this, please ignore this email.
        
        - HIRESTORM Team
        """
        
        return await self.send_email_async(to_email, subject, html_content, text_content)
    
    def send_job_match_notification(
        self,
        user_email: str,
        user_name: str,
        job: Dict,
        match_score: float,
        skill_gaps: List[str] = []
    ) -> bool:
        """
        Send notification about a new matching job
        
        Args:
            user_email: User's email
            user_name: User's name
            job: Job details
            match_score: Match percentage
            skill_gaps: Missing skills (if any)
        
        Returns:
            Success status
        """
        
        # Determine emoji based on match score
        if match_score >= 90:
            emoji = "🔥"
            match_text = "EXCELLENT"
        elif match_score >= 80:
            emoji = "🎯"
            match_text = "GREAT"
        elif match_score >= 70:
            emoji = "✨"
            match_text = "GOOD"
        else:
            emoji = "👍"
            match_text = "POTENTIAL"
        
        subject = f"{emoji} {match_text} Match: {job.get('title')} at {job.get('company')} ({match_score:.0f}%)"
        
        # Skills gap section
        skill_gap_html = ""
        if skill_gaps:
            skill_gap_html = f"""
            <div style="background: #FFF3CD; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <p style="margin: 0; color: #856404;">
                    <strong>⚠️ Skills to brush up:</strong> {', '.join(skill_gaps[:5])}
                </p>
            </div>
            """
        else:
            skill_gap_html = """
            <div style="background: #D4EDDA; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <p style="margin: 0; color: #155724;">
                    <strong>✅ You have all required skills!</strong>
                </p>
            </div>
            """
        
        # Salary section
        salary_html = ""
        if job.get('salary_min') or job.get('salary_max'):
            salary_min = job.get('salary_min', 'N/A')
            salary_max = job.get('salary_max', 'N/A')
            salary_html = f"""
            <p style="margin: 8px 0;">
                <strong>💰 Salary:</strong> ₹{salary_min:,} - ₹{salary_max:,}
            </p>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 0;">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">
                        {emoji} New Job Match Found!
                    </h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">
                        Based on your profile and skills
                    </p>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px;">
                    
                    <p style="font-size: 16px; color: #333;">
                        Hi <strong>{user_name}</strong>,
                    </p>
                    
                    <p style="font-size: 16px; color: #333;">
                        Great news! We found a job that matches your profile with 
                        <span style="color: #667eea; font-weight: bold;">{match_score:.0f}% compatibility</span>!
                    </p>
                    
                    <!-- Job Card -->
                    <div style="background: #f8f9fa; border-radius: 12px; padding: 20px; margin: 20px 0; border-left: 4px solid #667eea;">
                        
                        <h2 style="margin: 0 0 10px 0; color: #333; font-size: 20px;">
                            {job.get('title', 'Job Title')}
                        </h2>
                        
                        <p style="margin: 5px 0; color: #666; font-size: 16px;">
                            <strong>🏢 Company:</strong> {job.get('company', 'Company')}
                        </p>
                        
                        <p style="margin: 5px 0; color: #666; font-size: 16px;">
                            <strong>📍 Location:</strong> {job.get('location', 'India')}
                        </p>
                        
                        <p style="margin: 5px 0; color: #666; font-size: 16px;">
                            <strong>💼 Type:</strong> {job.get('job_type', 'Full-time').title()}
                        </p>
                        
                        {salary_html}
                        
                        <p style="margin: 15px 0 5px 0; color: #666; font-size: 14px;">
                            <strong>🛠️ Required Skills:</strong>
                        </p>
                        <p style="margin: 5px 0; color: #333;">
                            {', '.join(job.get('required_skills', [])[:8]) or 'Not specified'}
                        </p>
                        
                    </div>
                    
                    <!-- Match Score Badge -->
                    <div style="text-align: center; margin: 25px 0;">
                        <div style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; border-radius: 50px; font-size: 18px;">
                            <strong>Match Score: {match_score:.0f}%</strong>
                        </div>
                    </div>
                    
                    <!-- Skill Gaps -->
                    {skill_gap_html}
                    
                    <!-- CTA Button -->
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{job.get('url', '#')}" 
                           style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-size: 16px; font-weight: bold;">
                            🚀 Apply Now
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #666; margin-top: 30px;">
                        Don't wait too long - great opportunities don't last!
                    </p>
                    
                </div>
                
                <!-- Footer -->
                <div style="background: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #eee;">
                    <p style="margin: 0; color: #666; font-size: 12px;">
                        You received this email because you're registered on {self.app_name}
                    </p>
                    <p style="margin: 10px 0 0 0; color: #666; font-size: 12px;">
                        <a href="#" style="color: #667eea;">Manage Preferences</a> | 
                        <a href="#" style="color: #667eea;">Unsubscribe</a>
                    </p>
                </div>
                
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Hi {user_name},

        Great news! We found a job that matches your profile with {match_score:.0f}% compatibility!

        Job: {job.get('title')} at {job.get('company')}
        Location: {job.get('location')}
        Type: {job.get('job_type')}

        Match Score: {match_score:.0f}%
        
        Skills Gap: {', '.join(skill_gaps) if skill_gaps else 'None! You have all required skills!'}

        Apply Now: {job.get('url', 'Check our portal')}

        Best regards,
        {self.app_name} Team
        """
        
        return self._send_email_sync(user_email, subject, html_content, text_content)
    
    async def send_job_match_notification_async(
        self,
        user_email: str,
        user_name: str,
        job: Dict,
        match_score: float,
        skill_gaps: List[str] = []
    ) -> bool:
        """Send job match notification asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.send_job_match_notification,
            user_email,
            user_name,
            job,
            match_score,
            skill_gaps
        )
    
    def send_multiple_job_matches(
        self,
        user_email: str,
        user_name: str,
        jobs: List[Dict]
    ) -> bool:
        """
        Send email with multiple matching jobs (digest format)
        
        Args:
            user_email: User's email
            user_name: User's name
            jobs: List of matching jobs with scores
        
        Returns:
            Success status
        """
        
        if not jobs:
            return False
        
        subject = f"🎯 {len(jobs)} New Jobs Match Your Profile!"
        
        # Build jobs HTML
        jobs_html = ""
        for i, job_data in enumerate(jobs[:5], 1):  # Max 5 jobs per email
            job = job_data.get('job', job_data)
            score = job_data.get('match_score', 0)
            
            jobs_html += f"""
            <div style="background: #f8f9fa; border-radius: 8px; padding: 15px; margin: 15px 0; border-left: 4px solid #667eea;">
                <h3 style="margin: 0 0 8px 0; color: #333;">
                    {i}. {job.get('title', 'Job')}
                </h3>
                <p style="margin: 4px 0; color: #666;">
                    🏢 {job.get('company', 'Company')} | 📍 {job.get('location', 'India')}
                </p>
                <p style="margin: 8px 0 0 0;">
                    <span style="background: #667eea; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px;">
                        {score:.0f}% Match
                    </span>
                </p>
            </div>
            """
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; background: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background: white;">
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0;">🎯 {len(jobs)} New Job Matches!</h1>
                </div>
                
                <div style="padding: 30px;">
                    <p style="font-size: 16px; color: #333;">
                        Hi <strong>{user_name}</strong>,
                    </p>
                    
                    <p style="font-size: 16px; color: #333;">
                        We found <strong>{len(jobs)} new jobs</strong> that match your profile!
                    </p>
                    
                    {jobs_html}
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="#" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                            View All Matches
                        </a>
                    </div>
                </div>
                
                <div style="background: #f8f9fa; padding: 20px; text-align: center;">
                    <p style="margin: 0; color: #666; font-size: 12px;">
                        {self.app_name} | AI-Powered Job Matching
                    </p>
                </div>
                
            </div>
        </body>
        </html>
        """
        
        return self._send_email_sync(user_email, subject, html_content)
    
    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        
        subject = f"🎉 Welcome to {self.app_name}!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; background: #f4f4f4;">
            <div style="max-width: 600px; margin: 0 auto; background: white;">
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px; text-align: center;">
                    <h1 style="color: white; margin: 0;">Welcome Aboard! 🚀</h1>
                </div>
                
                <div style="padding: 30px;">
                    <p style="font-size: 18px; color: #333;">
                        Hi <strong>{user_name}</strong>,
                    </p>
                    
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">
                        Welcome to <strong>{self.app_name}</strong>! We're excited to help you find your dream job using AI-powered matching.
                    </p>
                    
                    <h3 style="color: #667eea;">What's Next?</h3>
                    
                    <div style="margin: 20px 0;">
                        <p style="margin: 10px 0;">📄 <strong>Upload your resume</strong> - We'll auto-extract your skills</p>
                        <p style="margin: 10px 0;">🎯 <strong>Get matched</strong> - Our AI finds the best jobs for you</p>
                        <p style="margin: 10px 0;">📊 <strong>See rejection risk</strong> - Know before you apply</p>
                        <p style="margin: 10px 0;">📧 <strong>Get alerts</strong> - New matching jobs in your inbox</p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="#" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; text-decoration: none; border-radius: 8px; font-weight: bold;">
                            Complete Your Profile
                        </a>
                    </div>
                </div>
                
            </div>
        </body>
        </html>
        """
        
        return self._send_email_sync(user_email, subject, html_content)


# Global instance
email_service_instance = None

def get_email_service() -> EmailService:
    """Get or create email service instance"""
    global email_service_instance
    if email_service_instance is None:
        email_service_instance = EmailService()
    return email_service_instance