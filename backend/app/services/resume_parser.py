"""
Resume Parser Service
Extracts skills, experience, and other info from PDF resumes
"""

import PyPDF2
import re
from typing import Dict, List
import os
import logging

logger = logging.getLogger(__name__)

class ResumeParser:
    """Parse resume and extract information"""
    
    def __init__(self):
        # Common tech skill keywords
        self.skill_keywords = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'nodejs', 'express', 'django', 'flask', 'fastapi',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab',
            'machine learning', 'deep learning', 'ai', 'artificial intelligence',
            'data science', 'data analysis', 'pandas', 'numpy', 'tensorflow', 'pytorch',
            'html', 'css', 'bootstrap', 'tailwind', 'sass', 'scss',
            'git', 'github', 'bitbucket', 'jira', 'agile', 'scrum',
            'rest api', 'graphql', 'microservices', 'api',
            'c++', 'c#', 'go', 'golang', 'rust', 'php', 'ruby', 'kotlin', 'swift',
            'spring', 'hibernate', 'next.js', 'vue.js', 'angular.js',
            'firebase', 'mongodb', 'dynamodb', 'elasticsearch',
            'linux', 'unix', 'bash', 'shell scripting',
            'ci/cd', 'devops', 'terraform', 'ansible',
            'figma', 'photoshop', 'ui/ux', 'design',
            'testing', 'jest', 'mocha', 'pytest', 'selenium',
            'excel', 'powerpoint', 'tableau', 'power bi'
        ]
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Extracted text as string
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            logger.info(f"✅ Extracted {len(text)} characters from PDF")
            return text
            
        except Exception as e:
            logger.error(f"❌ Error reading PDF: {e}")
            return ""
    
    def extract_email(self, text: str) -> str:
        """
        Extract email from text
        
        Args:
            text: Resume text
        
        Returns:
            Email address or empty string
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        if emails:
            logger.debug(f"✅ Email found: {emails[0]}")
            return emails[0]
        
        return ""
    
    def extract_phone(self, text: str) -> str:
        """
        Extract phone number from text
        
        Args:
            text: Resume text
        
        Returns:
            Phone number or empty string
        """
        # Indian phone patterns
        phone_patterns = [
            r'\+91[\s-]?\d{10}',  # +91 1234567890
            r'\d{10}',  # 1234567890
            r'\d{5}[\s-]?\d{5}',  # 12345 67890
            r'\(\d{3}\)[\s-]?\d{3}[\s-]?\d{4}'  # (123) 456-7890
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                logger.debug(f"✅ Phone found: {phones[0]}")
                return phones[0]
        
        return ""
    
    def extract_skills(self, text: str) -> List[str]:
        """
        Extract technical skills from text
        
        Args:
            text: Resume text
        
        Returns:
            List of found skills
        """
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.skill_keywords:
            # Match whole word or with common variations
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                # Capitalize properly
                found_skills.append(skill.title())
        
        # Remove duplicates and sort
        found_skills = sorted(list(set(found_skills)))
        
        logger.info(f"✅ Found {len(found_skills)} skills")
        return found_skills
    
    def extract_experience(self, text: str) -> str:
        """
        Try to determine experience level from text
        
        Args:
            text: Resume text
        
        Returns:
            'entry', 'mid', or 'senior'
        """
        text_lower = text.lower()
        
        # Senior level indicators
        senior_keywords = [
            'senior', 'lead', 'principal', 'architect', 'manager',
            '7+ years', '8+ years', '10+ years', '5-7 years',
            'team lead', 'tech lead'
        ]
        
        # Mid level indicators
        mid_keywords = [
            'mid-level', 'intermediate', 
            '3+ years', '4+ years', '5+ years',
            '2-4 years', '3-5 years'
        ]
        
        # Entry level indicators
        entry_keywords = [
            'entry', 'junior', 'fresher', 'graduate',
            'internship', 'trainee', '0-2 years', '1 year'
        ]
        
        # Check for senior
        for keyword in senior_keywords:
            if keyword in text_lower:
                logger.debug(f"✅ Experience: Senior (found '{keyword}')")
                return 'senior'
        
        # Check for mid
        for keyword in mid_keywords:
            if keyword in text_lower:
                logger.debug(f"✅ Experience: Mid (found '{keyword}')")
                return 'mid'
        
        # Check for entry
        for keyword in entry_keywords:
            if keyword in text_lower:
                logger.debug(f"✅ Experience: Entry (found '{keyword}')")
                return 'entry'
        
        # Default to entry
        logger.debug("✅ Experience: Entry (default)")
        return 'entry'
    
    def extract_education(self, text: str) -> List[str]:
        """
        Extract education qualifications
        
        Args:
            text: Resume text
        
        Returns:
            List of degrees/qualifications
        """
        text_lower = text.lower()
        
        education_keywords = [
            'b.tech', 'btech', 'bachelor of technology',
            'b.e', 'bachelor of engineering',
            'bca', 'bachelor of computer application',
            'm.tech', 'mtech', 'master of technology',
            'm.e', 'master of engineering',
            'mca', 'master of computer application',
            'bsc', 'bachelor of science',
            'msc', 'master of science',
            'mba', 'master of business administration',
            'phd', 'doctorate'
        ]
        
        found_education = []
        for edu in education_keywords:
            if edu in text_lower:
                found_education.append(edu.upper())
        
        return list(set(found_education))
    
    def parse_resume(self, file_path: str) -> Dict:
        """
        Main function to parse resume and extract all information
        
        Args:
            file_path: Path to resume PDF
        
        Returns:
            Dictionary with extracted information
        """
        
        if not os.path.exists(file_path):
            logger.error(f"❌ File not found: {file_path}")
            return {"error": "File not found"}
        
        # Extract text
        text = self.extract_text_from_pdf(file_path)
        
        if not text:
            logger.error("❌ Could not extract text from PDF")
            return {"error": "Could not extract text from PDF"}
        
        # Parse information
        parsed_data = {
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "skills": self.extract_skills(text),
            "experience_level": self.extract_experience(text),
            "education": self.extract_education(text),
            "raw_text_preview": text[:500]  # First 500 chars for preview
        }
        
        logger.info("✅ Resume parsed successfully")
        logger.info(f"   - Email: {parsed_data['email']}")
        logger.info(f"   - Skills: {len(parsed_data['skills'])} found")
        logger.info(f"   - Experience: {parsed_data['experience_level']}")
        
        return parsed_data


# Global instance
parser_instance = None

def get_resume_parser() -> ResumeParser:
    """Get or create parser instance"""
    global parser_instance
    if parser_instance is None:
        parser_instance = ResumeParser()
    return parser_instance