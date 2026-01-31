"""
Authentication Routes - Using hashlib (No bcrypt issues)
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import hashlib
import secrets
import logging

from app.services.database import get_firebase_service

router = APIRouter(prefix="/api/auth", tags=["authentication"])
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ========================================
# MODELS
# ========================================

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ========================================
# PASSWORD FUNCTIONS (Using hashlib - NO bcrypt issues!)
# ========================================

def hash_password(password: str) -> str:
    """Hash password using SHA256 + salt"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${password_hash}"

def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        if "$" not in stored_hash:
            return False
        salt, password_hash = stored_hash.split("$", 1)
        new_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return new_hash == password_hash
    except Exception as e:
        logger.error(f"Password verify error: {e}")
        return False

def create_token(user_id: str) -> str:
    """Create JWT token"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {"sub": user_id, "exp": expire}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# ========================================
# ENDPOINTS
# ========================================

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register new user"""
    
    logger.info(f"📝 Registering: {user_data.email}")
    
    firebase = get_firebase_service()
    
    # Check if exists
    existing = firebase.get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password (using hashlib - no 72 byte limit!)
    hashed = hash_password(user_data.password)
    
    # Create user
    new_user = {
        "email": user_data.email,
        "password": hashed,
        "full_name": user_data.full_name,
        "skills": [],
        "experience_level": "entry",
        "interests": "",
        "career_goals": "",
        "is_active": True
    }
    
    user_id = firebase.create_user(new_user)
    
    if not user_id:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    token = create_token(user_id)
    
    logger.info(f"✅ Registered: {user_id}")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user_id,
        "user_data": {
            "email": user_data.email,
            "full_name": user_data.full_name,
            "skills": []
        }
    }


@router.post("/login")
async def login(credentials: UserLogin):
    """Login user"""
    
    logger.info(f"🔐 Login: {credentials.email}")
    
    firebase = get_firebase_service()
    
    user = firebase.get_user_by_email(credentials.email)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    stored_password = user.get("password", "")
    
    if not verify_password(credentials.password, stored_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"])
    
    logger.info(f"✅ Logged in: {user['id']}")
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user["id"],
        "user_data": {
            "email": user["email"],
            "full_name": user.get("full_name", ""),
            "skills": user.get("skills", [])
        }
    }


@router.post("/upload-resume/{user_id}")
async def upload_resume(user_id: str, file: UploadFile = File(...)):
    """Upload and parse resume"""
    
    logger.info(f"📄 Resume upload: {user_id}")
    
    firebase = get_firebase_service()
    
    user = firebase.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")
    
    # Create upload directory
    upload_dir = "uploads/resumes"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = f"{upload_dir}/{user_id}_{file.filename}"
    
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info(f"✅ File saved: {file_path}")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")
    
    # Parse resume
    try:
        from app.services.resume_parser import get_resume_parser
        parser = get_resume_parser()
        parsed = parser.parse_resume(file_path)
        
        # Update user
        updates = {
            "skills": parsed.get("skills", []),
            "experience_level": parsed.get("experience_level", "entry"),
            "resume_url": file_path
        }
        firebase.update_user(user_id, updates)
        
        # Create embedding
        try:
            from app.services.ai_matcher import get_matcher
            from app.services.pinecone_service import get_pinecone_service
            
            matcher = get_matcher()
            pinecone = get_pinecone_service()
            
            updated_user = firebase.get_user(user_id)
            user_embedding = matcher.create_user_embedding(updated_user)
            
            pinecone.upsert_user_embedding(
                user_id=user_id,
                embedding=user_embedding,
                metadata={
                    "user_id": user_id,
                    "skills": updates["skills"],
                    "type": "user"
                }
            )
            logger.info("✅ User embedding created")
        except Exception as e:
            logger.warning(f"⚠️ Embedding error: {e}")
        
        return {
            "message": "Resume uploaded successfully",
            "parsed_data": parsed,
            "file_path": file_path
        }
        
    except Exception as e:
        logger.error(f"⚠️ Parse error: {e}")
        return {
            "message": "Resume uploaded (parsing failed)",
            "file_path": file_path
        }


@router.get("/verify-token/{token}")
async def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"valid": True, "user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset email via Firebase"""
    
    logger.info(f"🔑 Password reset request: {request.email}")
    
    firebase = get_firebase_service()
    
    # Check if user exists
    user = firebase.get_user_by_email(request.email)
    
    if not user:
        # Return success anyway to prevent email enumeration
        logger.info(f"⚠️ User not found for reset: {request.email}")
        return {"message": "If an account exists with this email, a password reset link will be sent."}
    
    try:
        # Use Firebase Admin SDK to send password reset email
        import firebase_admin
        from firebase_admin import auth as firebase_auth
        
        # Generate password reset link
        reset_link = firebase_auth.generate_password_reset_link(request.email)
        
        # Send email via email service
        try:
            from app.services.email_service import get_email_service
            email_service = get_email_service()
            
            await email_service.send_password_reset_email(
                to_email=request.email,
                reset_link=reset_link,
                user_name=user.get("full_name", "User")
            )
            logger.info(f"✅ Password reset email sent: {request.email}")
        except Exception as e:
            logger.warning(f"⚠️ Email service error: {e}")
            # Still return success since link was generated
        
        return {"message": "If an account exists with this email, a password reset link will be sent."}
        
    except Exception as e:
        logger.error(f"❌ Password reset error: {e}")
        # Return success message to prevent email enumeration
        return {"message": "If an account exists with this email, a password reset link will be sent."}