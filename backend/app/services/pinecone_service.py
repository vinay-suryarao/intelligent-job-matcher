"""
Pinecone Vector Database Service
Updated for BAAI model (768 dimensions)
"""

from pinecone import Pinecone
import os
from typing import List, Dict, Optional
import numpy as np
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class PineconeService:
    """Pinecone vector database operations for BAAI embeddings (768-dim)"""
    
    def __init__(self):
        """Initialize Pinecone connection"""
        
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "job-matcher")
        
        if not self.api_key:
            logger.warning("⚠️ Pinecone API key not found. Vector search disabled.")
            self.index = None
            return
        
        try:
            # Initialize Pinecone with new API
            self.pc = Pinecone(api_key=self.api_key)
            
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            index_names = [idx.name for idx in existing_indexes]
            
            if self.index_name not in index_names:
                logger.info(f"📊 Creating Pinecone index: {self.index_name}")
                logger.info("   Dimension: 768 (BAAI/bge-base-en-v1.5)")
                
                self.pc.create_index(
                    name=self.index_name,
                    dimension=768,  # BAAI model dimension (was 384 for MiniLM)
                    metric="cosine"
                )
                logger.info("✅ Index created with 768 dimensions")
            
            self.index = self.pc.Index(self.index_name)
            logger.info("✅ Pinecone initialized successfully (BAAI 768-dim)")
            
        except Exception as e:
            logger.error(f"❌ Pinecone initialization error: {e}")
            self.index = None
    
    def upsert_user_embedding(
        self, 
        user_id: str, 
        embedding: np.ndarray, 
        metadata: Dict
    ) -> bool:
        """
        Store user profile embedding (768-dim BAAI)
        
        Args:
            user_id: Unique user identifier
            embedding: 768-dim vector from BAAI model
            metadata: Additional info (skills, experience, etc.)
        
        Returns:
            Success status
        """
        
        if not self.index:
            logger.warning("⚠️ Pinecone not available")
            return False
        
        try:
            # Add type to metadata
            metadata['type'] = 'user'
            
            # Convert numpy array to list
            vector_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[
                    {
                        "id": f"user_{user_id}",
                        "values": vector_list,
                        "metadata": metadata
                    }
                ]
            )
            
            logger.debug(f"✅ User embedding stored: {user_id} (768-dim)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing user embedding: {e}")
            return False
    
    def upsert_job_embedding(
        self, 
        job_id: str, 
        embedding: np.ndarray, 
        metadata: Dict
    ) -> bool:
        """
        Store job posting embedding (768-dim BAAI)
        
        Args:
            job_id: Unique job identifier
            embedding: 768-dim vector from BAAI model
            metadata: Additional info (title, company, source)
        
        Returns:
            Success status
        """
        
        if not self.index:
            logger.warning("⚠️ Pinecone not available")
            return False
        
        try:
            # Add type to metadata
            metadata['type'] = 'job'
            
            # Convert numpy array to list
            vector_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            
            # Upsert to Pinecone
            self.index.upsert(
                vectors=[
                    {
                        "id": f"job_{job_id}",
                        "values": vector_list,
                        "metadata": metadata
                    }
                ]
            )
            
            logger.debug(f"✅ Job embedding stored: {job_id} (768-dim)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing job embedding: {e}")
            return False
    
    def upsert_resume_embedding(
        self,
        user_id: str,
        embedding: np.ndarray,
        metadata: Dict
    ) -> bool:
        """
        Store resume embedding (768-dim BAAI)
        
        Args:
            user_id: User identifier
            embedding: 768-dim vector
            metadata: Skills and other info
        
        Returns:
            Success status
        """
        
        if not self.index:
            return False
        
        try:
            metadata['type'] = 'resume'
            
            vector_list = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            
            self.index.upsert(
                vectors=[
                    {
                        "id": f"resume_{user_id}",
                        "values": vector_list,
                        "metadata": metadata
                    }
                ]
            )
            
            logger.debug(f"✅ Resume embedding stored: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing resume embedding: {e}")
            return False
    
    def find_matching_jobs(
        self, 
        user_embedding: np.ndarray, 
        top_k: int = 20,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Find jobs similar to user profile using BAAI vector search
        
        Args:
            user_embedding: User's 768-dim vector (BAAI)
            top_k: Number of results to return
            filter_dict: Optional filters (e.g., {"source": "adzuna"})
        
        Returns:
            List of matching jobs with scores
        """
        
        if not self.index:
            logger.warning("⚠️ Pinecone not available")
            return []
        
        try:
            # Build filter
            query_filter = {"type": "job"}
            if filter_dict:
                query_filter.update(filter_dict)
            
            # Convert numpy array to list
            vector_list = user_embedding.tolist() if isinstance(user_embedding, np.ndarray) else user_embedding
            
            # Query Pinecone
            results = self.index.query(
                vector=vector_list,
                top_k=top_k,
                include_metadata=True,
                filter=query_filter
            )
            
            # Parse results
            matches = []
            for match in results['matches']:
                matches.append({
                    'id': match['id'].replace('job_', ''),
                    'score': match['score'] * 100,  # Convert to percentage
                    'metadata': match.get('metadata', {})
                })
            
            logger.info(f"✅ Found {len(matches)} matching jobs (BAAI search)")
            return matches
            
        except Exception as e:
            logger.error(f"❌ Error querying Pinecone: {e}")
            return []
    
    def find_matching_users(
        self, 
        job_embedding: np.ndarray, 
        top_k: int = 20
    ) -> List[Dict]:
        """
        Find users matching a job (reverse matching)
        
        Args:
            job_embedding: Job's 768-dim vector
            top_k: Number of results
        
        Returns:
            List of matching users with scores
        """
        
        if not self.index:
            return []
        
        try:
            vector_list = job_embedding.tolist() if isinstance(job_embedding, np.ndarray) else job_embedding
            
            results = self.index.query(
                vector=vector_list,
                top_k=top_k,
                include_metadata=True,
                filter={"type": "user"}
            )
            
            matches = []
            for match in results['matches']:
                matches.append({
                    'id': match['id'].replace('user_', ''),
                    'score': match['score'] * 100,
                    'metadata': match.get('metadata', {})
                })
            
            logger.info(f"✅ Found {len(matches)} matching users")
            return matches
            
        except Exception as e:
            logger.error(f"❌ Error querying users: {e}")
            return []
    
    def find_matching_resumes(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10
    ) -> List[Dict]:
        """
        Find matching resumes for a job query
        
        Args:
            query_embedding: 768-dim query vector
            top_k: Number of results
        
        Returns:
            List of matching resumes
        """
        
        if not self.index:
            return []
        
        try:
            vector_list = query_embedding.tolist() if isinstance(query_embedding, np.ndarray) else query_embedding
            
            results = self.index.query(
                vector=vector_list,
                top_k=top_k,
                include_metadata=True,
                filter={"type": "resume"}
            )
            
            matches = []
            for match in results['matches']:
                matches.append({
                    'user_id': match['id'].replace('resume_', ''),
                    'score': match['score'] * 100,
                    'skills': match.get('metadata', {}).get('skills', '')
                })
            
            return matches
            
        except Exception as e:
            logger.error(f"❌ Error finding resumes: {e}")
            return []
    
    def delete_embedding(self, vector_id: str) -> bool:
        """
        Delete a vector from Pinecone
        
        Args:
            vector_id: ID to delete (e.g., "job_123" or "user_456")
        
        Returns:
            Success status
        """
        
        if not self.index:
            return False
        
        try:
            self.index.delete(ids=[vector_id])
            logger.debug(f"✅ Deleted embedding: {vector_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting embedding: {e}")
            return False
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the Pinecone index"""
        
        if not self.index:
            return {"error": "Pinecone not available"}
        
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.get('total_vector_count', 0),
                "dimension": 768,  # BAAI dimension
                "model": "BAAI/bge-base-en-v1.5",
                "index_fullness": stats.get('index_fullness', 0)
            }
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {"error": str(e)}


# Global instance
pinecone_instance = None

def get_pinecone_service() -> PineconeService:
    """Get or create Pinecone service instance"""
    global pinecone_instance
    if pinecone_instance is None:
        pinecone_instance = PineconeService()
    return pinecone_instance