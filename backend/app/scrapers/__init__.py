"""
Unified Job & Internship Scraper
Combines Adzuna + JSearch + Internship sources
"""

from typing import List, Dict
import logging
from app.scrapers.adzuna_scraper import get_adzuna_scraper
from app.scrapers.jsearch_scraper import get_jsearch_scraper
from app.scrapers.internship_scraper import get_internship_scraper

logger = logging.getLogger(__name__)

class UnifiedJobScraper:
    """
    Unified scraper for Jobs
    Adzuna + JSearch = Maximum job coverage
    """
    
    def __init__(self):
        self.adzuna = get_adzuna_scraper()
        self.jsearch = get_jsearch_scraper()
    
    def search_all_sources(
        self,
        keywords: str = "python developer",
        location: str = "India",
        max_results_per_source: int = 50
    ) -> List[Dict]:
        """Search jobs from ALL sources (Adzuna + JSearch)"""
        
        all_jobs = []
        
        # Fetch from Adzuna
        logger.info("🔄 Fetching from Adzuna...")
        try:
            adzuna_jobs = self.adzuna.search_jobs(
                keywords=keywords,
                location=location,
                results_per_page=max_results_per_source
            )
            all_jobs.extend(adzuna_jobs)
            logger.info(f"✅ Adzuna: {len(adzuna_jobs)} jobs")
        except Exception as e:
            logger.error(f"❌ Adzuna failed: {e}")
        
        # Fetch from JSearch (Google Jobs)
        logger.info("🔄 Fetching from JSearch (Google Jobs)...")
        try:
            jsearch_jobs = self.jsearch.search_jobs(
                keywords=keywords,
                location=location,
                results_per_page=max_results_per_source
            )
            all_jobs.extend(jsearch_jobs)
            logger.info(f"✅ JSearch: {len(jsearch_jobs)} jobs")
        except Exception as e:
            logger.error(f"❌ JSearch failed: {e}")
        
        # Remove duplicates
        all_jobs = self._remove_duplicates(all_jobs)
        
        logger.info(f"🎉 Total unique jobs: {len(all_jobs)}")
        return all_jobs
    
    def search_by_keywords_list(
        self,
        keywords_list: List[str],
        location: str = "India",
        max_results_per_keyword: int = 30
    ) -> List[Dict]:
        """Search multiple keywords across all sources"""
        
        all_jobs = []
        
        for keywords in keywords_list:
            logger.info(f"🔍 Searching for: {keywords}")
            
            jobs = self.search_all_sources(
                keywords=keywords,
                location=location,
                max_results_per_source=max_results_per_keyword
            )
            
            all_jobs.extend(jobs)
        
        # Remove duplicates
        all_jobs = self._remove_duplicates(all_jobs)
        
        logger.info(f"🎉 Total unique jobs: {len(all_jobs)}")
        return all_jobs
    
    def _remove_duplicates(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs"""
        
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            title = job['title'].lower().strip()
            company = job['company'].lower().strip()
            key = (title, company)
            
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        removed = len(jobs) - len(unique_jobs)
        if removed > 0:
            logger.info(f"🧹 Removed {removed} duplicate jobs")
        
        return unique_jobs


class UnifiedInternshipScraper:
    """
    Unified scraper for Internships
    JSearch (with internship filter) + Manual samples
    """
    
    def __init__(self):
        self.internship_scraper = get_internship_scraper()
    
    def search_all_sources(
        self,
        keywords: str = "software development intern",
        location: str = "India",
        max_results: int = 50
    ) -> List[Dict]:
        """Search internships from all sources"""
        
        all_internships = []
        
        # Fetch from JSearch (with internship filter)
        logger.info("🔄 Fetching internships from JSearch...")
        try:
            jsearch_internships = self.internship_scraper.search_internships_jsearch(
                keywords=keywords,
                location=location,
                results_per_page=max_results
            )
            all_internships.extend(jsearch_internships)
            logger.info(f"✅ JSearch: {len(jsearch_internships)} internships")
        except Exception as e:
            logger.error(f"❌ JSearch failed: {e}")
        
        # If no results from API, add manual samples
        if len(all_internships) == 0:
            logger.info("⚠️ No API results, using manual samples...")
            manual_internships = self.internship_scraper.search_internships_manual()
            all_internships.extend(manual_internships)
        
        logger.info(f"🎉 Total internships: {len(all_internships)}")
        return all_internships
    
    def search_by_keywords_list(
        self,
        keywords_list: List[str],
        location: str = "India",
        max_results_per_keyword: int = 20
    ) -> List[Dict]:
        """Search multiple internship keywords"""
        
        all_internships = []
        
        for keywords in keywords_list:
            logger.info(f"🔍 Searching internships: {keywords}")
            
            internships = self.search_all_sources(
                keywords=keywords,
                location=location,
                max_results=max_results_per_keyword
            )
            
            all_internships.extend(internships)
        
        # Remove duplicates
        all_internships = self._remove_duplicates(all_internships)
        
        logger.info(f"🎉 Total unique internships: {len(all_internships)}")
        return all_internships
    
    def _remove_duplicates(self, internships: List[Dict]) -> List[Dict]:
        """Remove duplicate internships"""
        
        seen = set()
        unique_internships = []
        
        for internship in internships:
            title = internship['title'].lower().strip()
            company = internship['company'].lower().strip()
            key = (title, company)
            
            if key not in seen:
                seen.add(key)
                unique_internships.append(internship)
        
        return unique_internships


# Global instances
unified_scraper_instance = None
unified_internship_scraper_instance = None

def get_unified_scraper() -> UnifiedJobScraper:
    """Get or create unified job scraper instance"""
    global unified_scraper_instance
    if unified_scraper_instance is None:
        unified_scraper_instance = UnifiedJobScraper()
    return unified_scraper_instance

def get_unified_internship_scraper() -> UnifiedInternshipScraper:
    """Get or create unified internship scraper instance"""
    global unified_internship_scraper_instance
    if unified_internship_scraper_instance is None:
        unified_internship_scraper_instance = UnifiedInternshipScraper()
    return unified_internship_scraper_instance