"""
Adzuna Job API Integration
Free Tier: 250 calls/month
Coverage: India, Multiple sources (LinkedIn, Indeed, Monster, etc.)
"""

import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class AdzunaJobScraper:
    """Scrape jobs from Adzuna API"""
    
    def __init__(self):
        self.app_id = os.getenv("ADZUNA_APP_ID")
        self.app_key = os.getenv("ADZUNA_APP_KEY")
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        self.country = "in"  # India
    
    def search_jobs(
        self, 
        keywords: str = "python developer", 
        location: str = "india",
        results_per_page: int = 50,
        page: int = 1,
        max_days_old: int = 30
    ) -> List[Dict]:
        """
        Search jobs on Adzuna
        
        Args:
            keywords: Job search keywords (e.g., "python developer")
            location: Location (default: "india")
            results_per_page: Number of results per page (max 50)
            page: Page number (starts from 1)
            max_days_old: Maximum age of job postings in days
        
        Returns:
            List of job dictionaries
        """
        
        if not self.app_id or not self.app_key:
            logger.error("⚠️ Adzuna API credentials not found in .env")
            return []
        
        url = f"{self.base_url}/{self.country}/search/{page}"
        
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": results_per_page,
            "what": keywords,
            "where": location,
            "max_days_old": max_days_old,
            "content-type": "application/json"
        }
        
        try:
            logger.info(f"🔍 Searching Adzuna for: {keywords}")
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                jobs = []
                for job in data.get('results', []):
                    parsed_job = {
                        "title": job.get('title', ''),
                        "company": job.get('company', {}).get('display_name', 'Unknown'),
                        "description": job.get('description', ''),
                        "location": job.get('location', {}).get('display_name', 'India'),
                        "salary_min": job.get('salary_min'),
                        "salary_max": job.get('salary_max'),
                        "url": job.get('redirect_url', ''),
                        "created": job.get('created', ''),
                        "job_type": self._extract_job_type(job.get('description', '')),
                        "required_skills": self._extract_skills(job.get('description', '')),
                        "experience_required": self._extract_experience(job.get('description', '')),
                        "source": "adzuna",
                        "category": job.get('category', {}).get('label', 'Other')
                    }
                    jobs.append(parsed_job)
                
                logger.info(f"✅ Adzuna: Fetched {len(jobs)} jobs")
                return jobs
            
            elif response.status_code == 429:
                logger.error("❌ Adzuna: Rate limit exceeded")
                return []
            
            else:
                logger.error(f"❌ Adzuna API error: {response.status_code}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error("❌ Adzuna: Request timeout")
            return []
        except Exception as e:
            logger.error(f"❌ Adzuna error: {e}")
            return []
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description"""
        description_lower = description.lower()
        
        # Common tech skills
        skill_keywords = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'nodejs', 'express', 'django', 'flask', 'fastapi',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'machine learning', 'deep learning', 'ai', 'data science',
            'html', 'css', 'bootstrap', 'tailwind',
            'git', 'github', 'gitlab', 'jira', 'agile', 'scrum',
            'rest api', 'graphql', 'microservices',
            'c++', 'c#', 'go', 'rust', 'php', 'ruby', 'kotlin', 'swift'
        ]
        
        found_skills = []
        for skill in skill_keywords:
            if skill in description_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))
    
    def _extract_experience(self, description: str) -> str:
        """Determine experience level from description"""
        description_lower = description.lower()
        
        # Senior level keywords
        if any(word in description_lower for word in ['senior', '5+ years', '7+ years', '10+ years', 'lead', 'architect', 'principal']):
            return 'senior'
        
        # Mid level keywords
        elif any(word in description_lower for word in ['mid', '2-4 years', '3+ years', '2+ years', 'intermediate']):
            return 'mid'
        
        # Entry level (default)
        else:
            return 'entry'
    
    def _extract_job_type(self, description: str) -> str:
        """Determine job type (remote/hybrid/onsite)"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['remote', 'work from home', 'wfh']):
            return 'remote'
        elif any(word in description_lower for word in ['hybrid']):
            return 'hybrid'
        else:
            return 'onsite'
    
    def get_job_details(self, job_id: str) -> Optional[Dict]:
        """Get detailed information for a specific job"""
        
        if not self.app_id or not self.app_key:
            return None
        
        url = f"{self.base_url}/{self.country}/details/{job_id}"
        
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Error getting job details: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None


# Global instance
adzuna_scraper_instance = None

def get_adzuna_scraper() -> AdzunaJobScraper:
    """Get or create Adzuna scraper instance"""
    global adzuna_scraper_instance
    if adzuna_scraper_instance is None:
        adzuna_scraper_instance = AdzunaJobScraper()
    return adzuna_scraper_instance