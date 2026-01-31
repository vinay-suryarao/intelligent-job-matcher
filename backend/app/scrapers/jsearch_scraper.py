"""
JSearch API Integration (RapidAPI)
Free Tier: 150 requests/month
Coverage: Google for Jobs data (Indeed, LinkedIn, ZipRecruiter, etc.)
Sign up: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
"""

import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class JSearchJobScraper:
    """Scrape jobs from JSearch API (Google Jobs)"""
    
    def __init__(self):
        self.api_key = os.getenv("JSEARCH_API_KEY")
        self.base_url = "https://jsearch.p.rapidapi.com/search"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
    
    def search_jobs(
        self, 
        keywords: str = "python developer", 
        location: str = "India",
        results_per_page: int = 50,
        page: int = 1,
        employment_types: Optional[str] = None,
        date_posted: str = "month"
    ) -> List[Dict]:
        """
        Search jobs on JSearch (Google Jobs)
        
        Args:
            keywords: Job search query
            location: Location
            results_per_page: Number of results (max 50)
            page: Page number
            employment_types: FULLTIME, PARTTIME, CONTRACTOR, INTERN
            date_posted: all, today, 3days, week, month
        
        Returns:
            List of job dictionaries
        """
        
        if not self.api_key:
            logger.error("⚠️ JSearch API key not found in .env")
            return []
        
        query = f"{keywords} in {location}"
        
        params = {
            "query": query,
            "page": str(page),
            "num_pages": "1",
            "date_posted": date_posted
        }
        
        if employment_types:
            params["employment_types"] = employment_types
        
        try:
            logger.info(f"🔍 Searching JSearch for: {keywords}")
            response = requests.get(
                self.base_url, 
                headers=self.headers, 
                params=params, 
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' not in data:
                    logger.warning("⚠️ JSearch: No results found")
                    return []
                
                jobs = []
                for job in data.get('data', [])[:results_per_page]:
                    parsed_job = {
                        "title": job.get('job_title', ''),
                        "company": job.get('employer_name', 'Unknown'),
                        "description": job.get('job_description', ''),
                        "location": job.get('job_city', location),
                        "salary_min": None,  # Parse if available
                        "salary_max": None,
                        "url": job.get('job_apply_link', ''),
                        "created": job.get('job_posted_at_datetime_utc', ''),
                        "job_type": self._map_job_type(job.get('job_employment_type', '')),
                        "required_skills": self._extract_skills(job.get('job_description', '')),
                        "experience_required": self._extract_experience(job.get('job_description', '')),
                        "source": "jsearch",
                        "category": "Technology"
                    }
                    jobs.append(parsed_job)
                
                logger.info(f"✅ JSearch: Fetched {len(jobs)} jobs")
                return jobs
            
            elif response.status_code == 429:
                logger.error("❌ JSearch: Rate limit exceeded")
                return []
            
            else:
                logger.error(f"❌ JSearch API error: {response.status_code}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error("❌ JSearch: Request timeout")
            return []
        except Exception as e:
            logger.error(f"❌ JSearch error: {e}")
            return []
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from job description"""
        if not description:
            return []
        
        description_lower = description.lower()
        
        skill_keywords = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'nodejs', 'express', 'django', 'flask', 'fastapi',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins',
            'machine learning', 'deep learning', 'ai', 'data science',
            'html', 'css', 'bootstrap', 'tailwind',
            'git', 'github', 'gitlab', 'jira', 'agile', 'scrum',
            'rest api', 'graphql', 'microservices'
        ]
        
        found_skills = []
        for skill in skill_keywords:
            if skill in description_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))
    
    def _extract_experience(self, description: str) -> str:
        """Determine experience level from description"""
        if not description:
            return 'entry'
        
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['senior', '5+ years', '7+ years', 'lead', 'architect']):
            return 'senior'
        elif any(word in description_lower for word in ['mid', '2-4 years', '3+ years', 'intermediate']):
            return 'mid'
        else:
            return 'entry'
    
    def _map_job_type(self, employment_type: str) -> str:
        """Map JSearch job type to our format"""
        if not employment_type:
            return 'onsite'
        
        employment_type_lower = employment_type.lower()
        
        if 'remote' in employment_type_lower:
            return 'remote'
        elif 'hybrid' in employment_type_lower:
            return 'hybrid'
        else:
            return 'onsite'


# Global instance
jsearch_scraper_instance = None

def get_jsearch_scraper() -> JSearchJobScraper:
    """Get or create JSearch scraper instance"""
    global jsearch_scraper_instance
    if jsearch_scraper_instance is None:
        jsearch_scraper_instance = JSearchJobScraper()
    return jsearch_scraper_instance