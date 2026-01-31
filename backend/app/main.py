"""
FastAPI Main Application
Entry point for Intelligent Job Matcher API
With Background Scheduler for Real-time Job Scraping
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========================================
# INITIALIZE FASTAPI APP
# ========================================

app = FastAPI(
    title="Intelligent Job & Internship Matcher API",
    description="""
    🎯 **AI-Powered Job Matching System**
    
    ### Problem Statement Solution:
    Students and job seekers often apply blindly to dozens of roles without understanding 
    skill fit, leading to rejections and frustration. This API solves that problem by:
    
    - 🤖 **Semantic AI Matching** - Not keyword-based, understands context
    - 📊 **Rejection Prediction** - Know rejection probability BEFORE applying
    - 📚 **Skill Gap Analysis** - Identify exactly what skills you need
    - 💬 **AI Chat Assistant** - Get personalized career guidance
    - 📈 **Statistical Insights** - Data-driven application strategy
    - 🔄 **Real-time Job Scraping** - Automatic every 2 hours
    
    ### Features:
    - ✅ Job & Internship Matching (Separate tabs)
    - ✅ Resume Auto-parsing (PDF upload)
    - ✅ Real-time Job Scraping (Adzuna + JSearch APIs)
    - ✅ Rejection Analysis & Recommendations
    - ✅ Email Notifications for new matches
    - ✅ Background Scheduler for continuous scraping
    
    ### Tech Stack:
    - **Backend:** FastAPI + Python
    - **AI/ML:** Sentence Transformers (Semantic matching)
    - **Database:** Firebase Firestore (NoSQL)
    - **Vector DB:** Pinecone (Fast similarity search)
    - **Job APIs:** Adzuna + JSearch
    - **Scheduler:** APScheduler
    
    ---
    **Built for Hackathon 2026** 🚀
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ========================================
# CORS MIDDLEWARE
# ========================================

# Get allowed origins from environment
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"✅ CORS enabled for: {allowed_origins}")

# ========================================
# REQUEST LOGGING MIDDLEWARE
# ========================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    
    start_time = time.time()
    
    # Log request
    logger.info(f"➡️  {request.method} {request.url.path}")
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(f"⬅️  {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}s")
        
        return response
    except Exception as e:
        logger.error(f"❌ Unhandled exception: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "message": str(e),
                "path": request.url.path
            }
        )

# ========================================
# EXCEPTION HANDLERS
# ========================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc),
            "path": request.url.path
        }
    )

# ========================================
# STARTUP EVENT
# ========================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    
    logger.info("=" * 60)
    logger.info("🚀 STARTING INTELLIGENT JOB MATCHER API")
    logger.info("=" * 60)
    
    # Initialize database
    logger.info("📊 Initializing Firebase database...")
    try:
        from app.services.database import init_db
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.warning("⚠️  API will run in limited mode")
    
    # Preload AI model
    logger.info("🤖 Loading BAAI High-Accuracy AI Model...")
    logger.info("   📥 First time download may take 2-3 minutes...")
    try:
        from app.services.ai_matcher import get_matcher
        matcher = get_matcher()
        logger.info("✅ BAAI AI model loaded successfully!")
        logger.info(f"   Model: {os.getenv('EMBEDDING_MODEL', 'BAAI/bge-base-en-v1.5')}")
        logger.info(f"   Dimensions: 768 (High Accuracy)")
    except Exception as e:
        logger.error(f"❌ AI model loading failed: {e}")
    
    # Check Pinecone connection
    logger.info("🔢 Checking Pinecone connection...")
    try:
        from app.services.pinecone_service import get_pinecone_service
        pinecone = get_pinecone_service()
        
        if pinecone.index:
            stats = pinecone.get_index_stats()
            logger.info(f"✅ Pinecone connected - {stats.get('total_vectors', 0)} vectors indexed")
        else:
            logger.warning("⚠️  Pinecone not configured - Vector search disabled")
    except Exception as e:
        logger.error(f"❌ Pinecone connection failed: {e}")
    
    # Check job scrapers
    logger.info("🔍 Checking job scrapers...")
    try:
        from app.scrapers import get_unified_scraper
        scraper = get_unified_scraper()
        logger.info("✅ Job scrapers ready (Adzuna + JSearch)")
    except Exception as e:
        logger.error(f"❌ Scraper initialization failed: {e}")
    
    # 🔥 START BACKGROUND SCHEDULER
    logger.info("⏰ Starting background scheduler...")
    try:
        from app.services.scheduler_service import start_scheduler
        start_scheduler()
        logger.info("✅ Background scheduler started")
        logger.info("   🔄 Auto-scraping: Every 2 hours")
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}")
        logger.warning("⚠️  Manual scraping still available at /api/jobs/scrape-jobs")
    
    logger.info("=" * 60)
    logger.info("🎯 API IS READY!")
    logger.info(f"📝 Documentation: http://localhost:8000/docs")
    logger.info(f"🔄 ReDoc: http://localhost:8000/redoc")
    logger.info(f"⏰ Auto-scraping: Every 2 hours")
    logger.info("=" * 60)

# ========================================
# SHUTDOWN EVENT
# ========================================

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    
    logger.info("=" * 60)
    logger.info("🛑 SHUTTING DOWN API")
    logger.info("=" * 60)
    
    # Stop scheduler
    try:
        from app.services.scheduler_service import stop_scheduler
        stop_scheduler()
        logger.info("✅ Scheduler stopped")
    except Exception as e:
        logger.error(f"❌ Error stopping scheduler: {e}")
    
    logger.info("✅ Cleanup complete")
    logger.info("👋 Goodbye!")

# ========================================
# INCLUDE ROUTERS
# ========================================

from app.routes import auth, users, jobs, internships, matching, chat, statistics

# Authentication routes
app.include_router(auth.router)
logger.info("✅ Auth routes loaded")

# User routes
app.include_router(users.router)
logger.info("✅ User routes loaded")

# Job routes
app.include_router(jobs.router)
logger.info("✅ Job routes loaded")

# Internship routes
app.include_router(internships.router)
logger.info("✅ Internship routes loaded")

# Matching routes
app.include_router(matching.router)
logger.info("✅ Matching routes loaded")

# Chat routes
app.include_router(chat.router)
logger.info("✅ Chat routes loaded")

# Statistics routes
app.include_router(statistics.router)
logger.info("✅ Statistics routes loaded")

# ========================================
# ROOT ENDPOINTS
# ========================================

@app.get("/", tags=["root"])
async def root():
    """
    API Root - Health check and information
    """
    return {
        "message": "Intelligent Job & Internship Matcher API",
        "status": "running",
        "version": "2.0.0",
        "description": "AI-powered job matching system using semantic understanding",
        "features": [
            "🤖 Semantic Job Matching (NOT keyword-based)",
            "📊 Rejection Probability Prediction",
            "📚 Skill Gap Analysis",
            "💬 AI Chat Assistant",
            "📈 Statistical Insights",
            "📄 Resume Auto-parsing",
            "🔄 Real-time Job Scraping (Every 2 hours)",
            "✉️ Email Notifications"
        ],
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "auth": "/api/auth",
            "users": "/api/users",
            "jobs": "/api/jobs",
            "internships": "/api/internships",
            "matching": "/api/matching",
            "chat": "/api/chat",
            "statistics": "/api/statistics"
        },
        "tech_stack": {
            "backend": "FastAPI + Python 3.11",
            "ai_ml": "BAAI/bge-base-en-v1.5 (768 dimensions)",
            "database": "Firebase Firestore (NoSQL)",
            "vector_db": "Pinecone",
            "job_apis": "Adzuna + JSearch",
            "scheduler": "APScheduler"
        }
    }


@app.get("/health", tags=["root"])
async def health_check():
    """
    Detailed health check
    
    - Checks database connection
    - Checks AI model status
    - Checks Pinecone connection
    - Checks scheduler status
    - Returns system status
    """
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {}
    }
    
    # Check database
    try:
        from app.services.database import get_firebase_service
        firebase = get_firebase_service()
        
        if firebase.db:
            health_status["components"]["database"] = {
                "status": "connected",
                "type": "Firebase Firestore"
            }
        else:
            health_status["components"]["database"] = {
                "status": "disconnected",
                "type": "Firebase Firestore"
            }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check AI model
    try:
        from app.services.ai_matcher import get_matcher
        matcher = get_matcher()
        
        health_status["components"]["ai_model"] = {
            "status": "loaded",
            "model": os.getenv("EMBEDDING_MODEL", "BAAI/bge-base-en-v1.5")
        }
    except Exception as e:
        health_status["components"]["ai_model"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check Pinecone
    try:
        from app.services.pinecone_service import get_pinecone_service
        pinecone = get_pinecone_service()
        
        if pinecone.index:
            stats = pinecone.get_index_stats()
            health_status["components"]["pinecone"] = {
                "status": "connected",
                "vectors": stats.get("total_vectors", 0)
            }
        else:
            health_status["components"]["pinecone"] = {
                "status": "not_configured"
            }
    except Exception as e:
        health_status["components"]["pinecone"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check job scrapers
    try:
        from app.scrapers import get_unified_scraper
        scraper = get_unified_scraper()
        
        health_status["components"]["scrapers"] = {
            "status": "ready",
            "sources": ["Adzuna", "JSearch"]
        }
    except Exception as e:
        health_status["components"]["scrapers"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check scheduler
    try:
        from app.services.scheduler_service import get_scheduler
        scheduler = get_scheduler()
        
        if scheduler and scheduler.running:
            jobs = scheduler.get_jobs()
            next_run = None
            for job in jobs:
                if job.next_run_time:
                    next_run = str(job.next_run_time)
                    break
            
            health_status["components"]["scheduler"] = {
                "status": "running",
                "jobs_scheduled": len(jobs),
                "next_scrape": next_run
            }
        else:
            health_status["components"]["scheduler"] = {
                "status": "not_running"
            }
    except Exception as e:
        health_status["components"]["scheduler"] = {
            "status": "error",
            "error": str(e)
        }
    
    return health_status


@app.get("/version", tags=["root"])
async def get_version():
    """Get API version information"""
    
    return {
        "version": "2.0.0",
        "release_date": "2026-01-30",
        "python_version": "3.11+",
        "fastapi_version": "0.109.0",
        "features_added": [
            "Dual API integration (Adzuna + JSearch)",
            "Firebase + Pinecone database",
            "BAAI Semantic matching engine (768 dim)",
            "Rejection analyzer",
            "AI chat interface",
            "Statistical dashboard",
            "Background scheduler (auto-scraping)",
            "Email notifications"
        ]
    }


@app.get("/api-stats", tags=["root"])
async def get_api_stats():
    """Get API usage statistics"""
    
    try:
        from app.services.database import get_firebase_service
        firebase = get_firebase_service()
        
        # Get counts
        jobs = firebase.get_all_jobs(limit=1000)
        internships = firebase.get_all_internships(limit=1000)
        
        return {
            "total_jobs": len(jobs),
            "total_internships": len(internships),
            "active_jobs": sum(1 for j in jobs if j.get("is_active")),
            "active_internships": sum(1 for i in internships if i.get("is_active")),
            "job_sources": {
                "adzuna": sum(1 for j in jobs if j.get("source") == "adzuna"),
                "jsearch": sum(1 for j in jobs if j.get("source") == "jsearch"),
                "manual": sum(1 for j in jobs if j.get("source") == "manual")
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Stats unavailable"
        }


# ========================================
# RUN SERVER (for development)
# ========================================

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    logger.info(f"🚀 Starting server on {host}:{port}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )