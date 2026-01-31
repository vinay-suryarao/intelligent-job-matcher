"""
Internship Scraper Service
Scrapes internships from various sources
(Can be extended with Internshala API, AngelList, etc.)
"""

import requests
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class InternshipScraper:
    """
    Scrape internships from various sources
    
    Note: Most internship sites don't have free APIs
    This is a template that can be extended with:
    - Internshala API (paid)
    - AngelList API
    - Manual scraping with Selenium
    - Or use JSearch API with internship filter
    """
    
    def __init__(self):
        self.jsearch_api_key = os.getenv("JSEARCH_API_KEY")
        self.base_url = "https://jsearch.p.rapidapi.com/search"
        self.headers = {
            "X-RapidAPI-Key": self.jsearch_api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
    
    def search_internships_jsearch(
        self,
        keywords: str = "software development intern",
        location: str = "India",
        results_per_page: int = 50,
        page: int = 1
    ) -> List[Dict]:
        """
        Search internships using JSearch API (Google Jobs)
        
        Args:
            keywords: Search keywords
            location: Location
            results_per_page: Number of results
            page: Page number
        
        Returns:
            List of internship dicts
        """
        
        if not self.jsearch_api_key:
            logger.error("⚠️ JSearch API key not found in .env")
            return []
        
        # Build query with "intern" keyword
        query = f"{keywords} in {location}"
        
        params = {
            "query": query,
            "page": str(page),
            "num_pages": "1",
            "date_posted": "month",
            "employment_types": "INTERN"  # Filter for internships only
        }
        
        try:
            logger.info(f"🔍 Searching internships: {keywords}")
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' not in data:
                    logger.warning("⚠️ No internships found")
                    return []
                
                internships = []
                for item in data.get('data', [])[:results_per_page]:
                    parsed_internship = {
                        "title": item.get('job_title', ''),
                        "company": item.get('employer_name', 'Unknown'),
                        "description": item.get('job_description', ''),
                        "location": item.get('job_city', location),
                        "stipend_min": None,  # Not available in free tier
                        "stipend_max": None,
                        "url": item.get('job_apply_link', ''),
                        "created": item.get('job_posted_at_datetime_utc', ''),
                        "internship_type": self._extract_internship_type(item.get('job_description', '')),
                        "required_skills": self._extract_skills(item.get('job_description', '')),
                        "duration_months": self._extract_duration(item.get('job_description', '')),
                        "education_required": self._extract_education(item.get('job_description', '')),
                        "year_of_study": self._extract_year(item.get('job_description', '')),
                        "source": "jsearch",
                        "category": "Technology"
                    }
                    internships.append(parsed_internship)
                
                logger.info(f"✅ JSearch: Fetched {len(internships)} internships")
                return internships
            
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
    
    def search_internships_manual(
        self,
        keywords_list: List[str] = None
    ) -> List[Dict]:
        """
        Manually create sample internships (for demo/testing)
        
        In production, this would be replaced with actual API calls
        """
        
        if keywords_list is None:
            keywords_list = [
                "software development",
                "data science",
                "web development",
                "machine learning"
            ]
        
        sample_internships = [
            {
                "title": "Software Development Intern",
                "company": "TechStartup India",
                "description": """
                We're looking for a motivated software development intern to join our team.
                
                Responsibilities:
                - Build web applications using React and Node.js
                - Write clean, maintainable code
                - Collaborate with senior developers
                - Participate in code reviews
                
                Requirements:
                - Knowledge of JavaScript, React
                - Basic understanding of Git
                - Pursuing B.Tech/B.E in Computer Science
                
                What you'll learn:
                - Full-stack development
                - Agile methodology
                - Professional coding practices
                """,
                "location": "Remote",
                "stipend_min": 10000,
                "stipend_max": 20000,
                "url": "https://example.com/apply",
                "created": "2026-01-25",
                "internship_type": "remote",
                "required_skills": ["JavaScript", "React", "Node.js", "Git"],
                "duration_months": 6,
                "education_required": "pursuing",
                "year_of_study": "any",
                "source": "manual",
                "category": "Technology"
            },
            {
                "title": "Data Science Intern",
                "company": "AI Solutions Ltd",
                "description": """
                Seeking a data science intern passionate about machine learning.
                
                What you'll do:
                - Work on real ML projects
                - Data analysis and visualization
                - Build predictive models
                - Present findings to team
                
                Requirements:
                - Python, Pandas, NumPy
                - Basic ML knowledge
                - Statistics background
                - Any year of study
                
                Perks:
                - Work with experienced data scientists
                - Access to premium tools
                - Certificate on completion
                """,
                "location": "Bangalore, India",
                "stipend_min": 15000,
                "stipend_max": 25000,
                "url": "https://example.com/apply",
                "created": "2026-01-26",
                "internship_type": "hybrid",
                "required_skills": ["Python", "Machine Learning", "Pandas", "Data Analysis"],
                "duration_months": 3,
                "education_required": "pursuing",
                "year_of_study": "3rd",
                "source": "manual",
                "category": "Data Science"
            },
            {
                "title": "Frontend Development Intern",
                "company": "WebTech Solutions",
                "description": """
                Looking for frontend developers to build amazing user interfaces.
                
                Responsibilities:
                - Develop responsive web pages
                - Implement designs using React
                - Work with REST APIs
                - Bug fixing and testing
                
                Skills needed:
                - HTML, CSS, JavaScript
                - React.js basics
                - UI/UX awareness
                - Problem-solving skills
                
                Duration: 6 months
                Stipend: ₹12,000 - ₹18,000/month
                """,
                "location": "Mumbai, India",
                "stipend_min": 12000,
                "stipend_max": 18000,
                "url": "https://example.com/apply",
                "created": "2026-01-27",
                "internship_type": "onsite",
                "required_skills": ["HTML", "CSS", "JavaScript", "React"],
                "duration_months": 6,
                "education_required": "pursuing",
                "year_of_study": "2nd",
                "source": "manual",
                "category": "Web Development"
            },
            {
                "title": "Backend Development Intern",
                "company": "CloudNine Tech",
                "description": """
                Backend intern needed for building scalable APIs.
                
                Work on:
                - REST API development
                - Database design
                - Cloud deployment
                - Performance optimization
                
                Requirements:
                - Python or Node.js
                - SQL basics
                - Understanding of APIs
                - Final year students preferred
                
                Benefits:
                - Mentorship from senior engineers
                - Real production experience
                - Potential full-time conversion
                """,
                "location": "Remote",
                "stipend_min": 15000,
                "stipend_max": 22000,
                "url": "https://example.com/apply",
                "created": "2026-01-28",
                "internship_type": "remote",
                "required_skills": ["Python", "FastAPI", "SQL", "REST API"],
                "duration_months": 6,
                "education_required": "pursuing",
                "year_of_study": "4th",
                "source": "manual",
                "category": "Backend Development"
            },
            {
                "title": "Mobile App Development Intern",
                "company": "AppMakers Inc",
                "description": """
                Mobile development internship for Android/iOS apps.
                
                What you'll learn:
                - Mobile app architecture
                - React Native development
                - API integration
                - Publishing apps
                
                Requirements:
                - JavaScript knowledge
                - React basics helpful
                - Mobile development interest
                - Any year welcome
                
                Stipend: ₹10,000 - ₹20,000
                Duration: 3-6 months
                """,
                "location": "Pune, India",
                "stipend_min": 10000,
                "stipend_max": 20000,
                "url": "https://example.com/apply",
                "created": "2026-01-29",
                "internship_type": "hybrid",
                "required_skills": ["JavaScript", "React Native", "Mobile Development"],
                "duration_months": 6,
                "education_required": "pursuing",
                "year_of_study": "any",
                "source": "manual",
                "category": "Mobile Development"
            }
        ]
        
        logger.info(f"✅ Generated {len(sample_internships)} sample internships")
        return sample_internships
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extract skills from description"""
        if not description:
            return []
        
        description_lower = description.lower()
        
        skill_keywords = [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue',
            'node.js', 'nodejs', 'express', 'django', 'flask', 'fastapi',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'aws', 'azure', 'docker', 'kubernetes',
            'machine learning', 'deep learning', 'ai', 'data science',
            'html', 'css', 'bootstrap', 'tailwind',
            'git', 'github', 'jira', 'agile',
            'rest api', 'graphql', 'react native', 'flutter',
            'pandas', 'numpy', 'tensorflow', 'pytorch'
        ]
        
        found_skills = []
        for skill in skill_keywords:
            if skill in description_lower:
                found_skills.append(skill.title())
        
        return list(set(found_skills))
    
    def _extract_duration(self, description: str) -> int:
        """Extract internship duration in months"""
        if not description:
            return 6  # Default
        
        description_lower = description.lower()
        
        # Look for duration patterns
        if '3 month' in description_lower or '3-month' in description_lower:
            return 3
        elif '6 month' in description_lower or '6-month' in description_lower:
            return 6
        elif '12 month' in description_lower or '1 year' in description_lower:
            return 12
        else:
            return 6  # Default 6 months
    
    def _extract_education(self, description: str) -> str:
        """Extract education requirement"""
        if not description:
            return "pursuing"
        
        description_lower = description.lower()
        
        if 'graduated' in description_lower or 'degree holder' in description_lower:
            return "graduated"
        else:
            return "pursuing"
    
    def _extract_year(self, description: str) -> str:
        """Extract year of study"""
        if not description:
            return "any"
        
        description_lower = description.lower()
        
        if 'final year' in description_lower or '4th year' in description_lower:
            return "4th"
        elif '3rd year' in description_lower or 'third year' in description_lower:
            return "3rd"
        elif '2nd year' in description_lower or 'second year' in description_lower:
            return "2nd"
        elif '1st year' in description_lower or 'first year' in description_lower:
            return "1st"
        else:
            return "any"
    
    def _extract_internship_type(self, description: str) -> str:
        """Determine internship type"""
        if not description:
            return "onsite"
        
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['remote', 'work from home', 'wfh']):
            return 'remote'
        elif 'hybrid' in description_lower:
            return 'hybrid'
        else:
            return 'onsite'


# Global instance
internship_scraper_instance = None

def get_internship_scraper() -> InternshipScraper:
    """Get or create internship scraper instance"""
    global internship_scraper_instance
    if internship_scraper_instance is None:
        internship_scraper_instance = InternshipScraper()
    return internship_scraper_instance