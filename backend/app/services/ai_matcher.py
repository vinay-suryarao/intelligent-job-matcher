"""
AI Semantic Matching Engine
Uses BAAI/bge-base-en-v1.5 for HIGH ACCURACY semantic matching
768 dimensions - Better than MiniLM for job matching
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Tuple, Optional
import logging
import os

logger = logging.getLogger(__name__)

class IntelligentMatcher:
    """AI-powered semantic job matching using BAAI model (High Accuracy)"""
    
    def __init__(self, model_name: str = 'BAAI/bge-base-en-v1.5'):
        """
        Initialize the AI matcher with BAAI high-accuracy model
        
        Args:
            model_name: BAAI model for better semantic understanding
                       'BAAI/bge-base-en-v1.5' - 768 dimensions, HIGH accuracy
        """
        try:
            logger.info(f"🤖 Loading BAAI High-Accuracy Model: {model_name}")
            logger.info("📥 First time download may take a few minutes...")
            self.model = SentenceTransformer(model_name)
            logger.info("✅ BAAI Model loaded successfully!")
            logger.info(f"   Model dimensions: 768 (High Accuracy)")
        except Exception as e:
            logger.error(f"❌ Failed to load BAAI model: {e}")
            raise
    
    def _get_embedding(self, text: str, is_query: bool = False) -> np.ndarray:
        """
        Create embedding using BAAI model
        
        IMPORTANT: BAAI model uses instruction prefix for queries
        - is_query=True: For searching (user profile matching)
        - is_query=False: For storing (job/resume indexing)
        
        Args:
            text: Text to embed
            is_query: True if searching, False if storing
        
        Returns:
            768-dimensional numpy array (normalized)
        """
        try:
            if is_query:
                # BAAI instruction for search queries
                instruction = "Represent this sentence for searching relevant passages: "
                text = instruction + text
            
            # Normalize embeddings for better cosine similarity
            embedding = self.model.encode(text, normalize_embeddings=True)
            return embedding
            
        except Exception as e:
            logger.error(f"❌ Embedding error: {e}")
            raise
    
    def create_user_embedding(self, user_data: Dict, for_search: bool = True) -> np.ndarray:
        """
        Convert user profile to semantic vector
        
        Args:
            user_data: User profile dict with skills, experience, etc.
            for_search: True for searching jobs, False for storing
        
        Returns:
            768-dimensional numpy array
        """
        
        # Build comprehensive profile text
        skills = user_data.get('skills', [])
        if isinstance(skills, list):
            skills_text = ', '.join(skills)
        else:
            skills_text = str(skills)
        
        profile_text = f"""
        Professional Profile:
        Skills: {skills_text}
        Experience Level: {user_data.get('experience_level', 'entry')}
        Interests: {user_data.get('interests', 'software development')}
        Career Goals: {user_data.get('career_goals', 'grow as developer')}
        Education: {', '.join(user_data.get('education', []))}
        """
        
        try:
            embedding = self._get_embedding(profile_text.strip(), is_query=for_search)
            logger.debug(f"✅ User embedding created: shape {embedding.shape}")
            return embedding
        except Exception as e:
            logger.error(f"❌ Error creating user embedding: {e}")
            raise
    
    def create_job_embedding(self, job_data: Dict, for_search: bool = False) -> np.ndarray:
        """
        Convert job posting to semantic vector
        
        Args:
            job_data: Job dict with title, description, skills
            for_search: False for storing (default), True for searching
        
        Returns:
            768-dimensional numpy array
        """
        
        # Build comprehensive job text
        required_skills = job_data.get('required_skills', [])
        if isinstance(required_skills, list):
            skills_text = ', '.join(required_skills)
        else:
            skills_text = str(required_skills)
        
        # Limit description length for better embedding
        description = job_data.get('description', '')[:1000]
        
        job_text = f"""
        Job Position: {job_data.get('title', '')}
        Company: {job_data.get('company', '')}
        Job Description: {description}
        Required Skills: {skills_text}
        Experience Required: {job_data.get('experience_required', 'entry')}
        Location: {job_data.get('location', 'India')}
        Job Type: {job_data.get('job_type', 'remote')}
        """
        
        try:
            embedding = self._get_embedding(job_text.strip(), is_query=for_search)
            logger.debug(f"✅ Job embedding created: shape {embedding.shape}")
            return embedding
        except Exception as e:
            logger.error(f"❌ Error creating job embedding: {e}")
            raise
    
    def create_resume_embedding(self, resume_text: str, skills: List[str], for_search: bool = False) -> np.ndarray:
        """
        Convert resume to semantic vector
        
        Args:
            resume_text: Full resume text
            skills: Extracted skills list
            for_search: False for storing
        
        Returns:
            768-dimensional numpy array
        """
        
        # Combine resume text with skills for better context
        combined_text = f"""
        Resume:
        {resume_text[:2000]}
        
        Key Skills: {', '.join(skills)}
        """
        
        try:
            embedding = self._get_embedding(combined_text.strip(), is_query=for_search)
            logger.debug(f"✅ Resume embedding created")
            return embedding
        except Exception as e:
            logger.error(f"❌ Error creating resume embedding: {e}")
            raise
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Note: BAAI embeddings are already normalized, so dot product = cosine similarity
        
        Args:
            embedding1: First vector (768-dim)
            embedding2: Second vector (768-dim)
        
        Returns:
            Similarity score (0-100%)
        """
        
        try:
            # Since embeddings are normalized, dot product = cosine similarity
            similarity = np.dot(embedding1, embedding2)
            
            # Convert to percentage (0-100)
            score = float(similarity * 100)
            
            # Clamp to valid range
            score = max(0, min(100, score))
            
            logger.debug(f"✅ Similarity calculated: {score:.2f}%")
            return score
            
        except Exception as e:
            logger.error(f"❌ Error calculating similarity: {e}")
            return 0.0
    
    def find_skill_gaps(self, user_skills: List[str], required_skills: List[str]) -> List[str]:
        """
        Identify missing skills using SEMANTIC similarity
        (NOT just keyword matching - understands "Python" ≈ "Python3")
        
        Args:
            user_skills: List of user's skills
            required_skills: List of required skills for job
        
        Returns:
            List of missing skills
        """
        
        if not user_skills or not required_skills:
            return required_skills if required_skills else []
        
        try:
            # Create embeddings for all skills
            user_skill_embeddings = [
                self._get_embedding(skill, is_query=True) 
                for skill in user_skills
            ]
            
            required_skill_embeddings = [
                self._get_embedding(skill, is_query=False) 
                for skill in required_skills
            ]
            
            gaps = []
            threshold = 0.65  # Higher threshold for BAAI model (more accurate)
            
            for i, req_skill in enumerate(required_skills):
                req_embedding = required_skill_embeddings[i]
                
                # Calculate similarity with all user skills
                max_similarity = 0
                for user_embedding in user_skill_embeddings:
                    sim = np.dot(user_embedding, req_embedding)
                    max_similarity = max(max_similarity, sim)
                
                # If no user skill is similar enough, it's a gap
                if max_similarity < threshold:
                    gaps.append(req_skill)
            
            logger.debug(f"✅ Skill gaps identified: {len(gaps)} out of {len(required_skills)}")
            return gaps
            
        except Exception as e:
            logger.error(f"❌ Error finding skill gaps: {e}")
            return required_skills
    
    def generate_match_reasoning(
        self, 
        user_data: Dict, 
        job_data: Dict, 
        score: float, 
        skill_gaps: List[str]
    ) -> str:
        """
        Generate human-readable explanation for the match
        
        Args:
            user_data: User profile
            job_data: Job posting
            score: Match score (0-100)
            skill_gaps: List of missing skills
        
        Returns:
            Formatted reasoning text
        """
        
        try:
            # Find matching skills
            user_skills = set(s.lower() for s in user_data.get('skills', []))
            required_skills = set(s.lower() for s in job_data.get('required_skills', []))
            matching_skills = user_skills.intersection(required_skills)
            
            # Build reasoning parts
            reasoning_parts = [
                f"🎯 Match Score: {score:.1f}% (BAAI High-Accuracy Model)",
                "",
            ]
            
            # Matching skills
            if matching_skills:
                reasoning_parts.append(f"✅ Strong Match: {', '.join(matching_skills)}")
            else:
                reasoning_parts.append("✅ Semantic analysis found transferable skills")
            
            # Skill gaps
            if skill_gaps:
                reasoning_parts.append(f"\n⚠️ Skills to Develop: {', '.join(skill_gaps[:5])}")
                if len(skill_gaps) > 5:
                    reasoning_parts.append(f"   ... and {len(skill_gaps) - 5} more")
            else:
                reasoning_parts.append("\n✅ All required skills covered!")
            
            # Experience level match
            user_exp = user_data.get('experience_level', '').lower()
            job_exp = job_data.get('experience_required', '').lower()
            
            if user_exp == job_exp:
                reasoning_parts.append(f"\n👔 Experience Level: Perfect match ({job_exp})")
            else:
                reasoning_parts.append(f"\n👔 Experience: {job_exp} required, you have {user_exp}")
            
            # Recommendation based on BAAI's accurate scoring
            if score >= 85:
                reasoning_parts.append("\n🚀 Recommendation: Excellent match - Apply now!")
            elif score >= 70:
                reasoning_parts.append("\n📚 Recommendation: Strong fit - Apply with confidence")
            elif score >= 55:
                reasoning_parts.append("\n💡 Recommendation: Consider applying with a good cover letter")
            else:
                reasoning_parts.append("\n📖 Recommendation: Build missing skills first")
            
            return "\n".join(reasoning_parts)
            
        except Exception as e:
            logger.error(f"❌ Error generating reasoning: {e}")
            return f"Match Score: {score:.1f}%"
    
    def rank_matches(
        self, 
        user_data: Dict, 
        jobs: List[Dict],
        top_k: int = 20
    ) -> List[Dict]:
        """
        Rank jobs by match score using BAAI embeddings
        
        Args:
            user_data: User profile
            jobs: List of job postings
            top_k: Number of top results to return
        
        Returns:
            Ranked list of matches with scores and reasoning
        """
        
        try:
            # Create user embedding once (for searching)
            user_embedding = self.create_user_embedding(user_data, for_search=True)
            
            matches = []
            
            for job in jobs:
                # Skip jobs in rejection history
                rejection_history = user_data.get('rejection_history', [])
                if isinstance(rejection_history, list) and job.get('id') in rejection_history:
                    continue
                
                # Create job embedding (for matching against)
                job_embedding = self.create_job_embedding(job, for_search=False)
                
                # Calculate similarity
                score = self.calculate_similarity(user_embedding, job_embedding)
                
                # Only include decent matches (50%+ with BAAI is meaningful)
                if score >= 50:
                    # Find skill gaps
                    skill_gaps = self.find_skill_gaps(
                        user_data.get('skills', []),
                        job.get('required_skills', [])
                    )
                    
                    # Generate reasoning
                    reasoning = self.generate_match_reasoning(
                        user_data, job, score, skill_gaps
                    )
                    
                    # Calculate rejection probability
                    rejection_prob = self._calculate_rejection_probability(
                        score, len(skill_gaps), user_data, job
                    )
                    
                    matches.append({
                        'job': job,
                        'match_score': round(score, 2),
                        'rejection_probability': rejection_prob,
                        'rejection_risk': self._get_risk_level(rejection_prob),
                        'skill_gaps': skill_gaps,
                        'reasoning': reasoning,
                        'recommended_action': self._get_action(score, rejection_prob),
                        'ai_model': 'BAAI/bge-base-en-v1.5'
                    })
            
            # Sort by score descending
            matches.sort(key=lambda x: x['match_score'], reverse=True)
            
            logger.info(f"✅ Ranked {len(matches)} matches using BAAI model, returning top {top_k}")
            
            return matches[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Error ranking matches: {e}")
            return []
    
    def _calculate_rejection_probability(
        self, 
        match_score: float, 
        skill_gap_count: int,
        user_data: Dict,
        job_data: Dict
    ) -> float:
        """
        Calculate probability of rejection based on BAAI scores
        
        Note: BAAI gives more accurate scores, so we adjust thresholds
        """
        
        # Base calculation from match score (BAAI is more accurate)
        if match_score >= 85:
            score_penalty = 5  # Very low penalty for high BAAI scores
        elif match_score >= 70:
            score_penalty = 15
        elif match_score >= 55:
            score_penalty = 30
        else:
            score_penalty = (100 - match_score) * 0.5
        
        # Skill gap penalty
        skill_gap_penalty = min(skill_gap_count * 8, 45)  # Max 45%
        
        # Experience mismatch penalty
        exp_levels = {'entry': 1, 'mid': 2, 'senior': 3}
        user_level = exp_levels.get(user_data.get('experience_level', 'entry'), 1)
        job_level = exp_levels.get(job_data.get('experience_required', 'entry'), 1)
        exp_gap = abs(user_level - job_level) * 12  # 12% per level gap
        
        # Total probability (capped at 95%)
        total = min(score_penalty + skill_gap_penalty + exp_gap, 95)
        
        return round(total, 1)
    
    def _get_risk_level(self, rejection_prob: float) -> str:
        """Get risk level label"""
        if rejection_prob < 25:
            return "Low"
        elif rejection_prob < 50:
            return "Medium"
        else:
            return "High"
    
    def _get_action(self, score: float, rejection_prob: float) -> str:
        """Get recommended action based on BAAI scores"""
        if score >= 85 and rejection_prob < 25:
            return "Apply Now - Excellent Match!"
        elif score >= 75 and rejection_prob < 40:
            return "Strongly Consider Applying"
        elif score >= 65 and rejection_prob < 55:
            return "Apply with Portfolio"
        elif score >= 55:
            return "Consider After Skill Improvement"
        else:
            return "Build Skills First"


# Global instance
matcher_instance = None

def get_matcher() -> IntelligentMatcher:
    """Get or create matcher instance with BAAI model"""
    global matcher_instance
    if matcher_instance is None:
        model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
        matcher_instance = IntelligentMatcher(model_name)
    return matcher_instance