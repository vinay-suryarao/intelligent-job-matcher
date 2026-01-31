"""
Direct test - bypassing API
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("="*50)
print("DIRECT JOB CREATION TEST")
print("="*50)

# Test 1: Database service
print("\n1. Testing database service...")
try:
    from app.services.database import get_firebase_service
    firebase = get_firebase_service()
    
    if firebase.db:
        print("   ✅ Database connected!")
    else:
        print("   ❌ Database is None!")
        exit(1)
        
except Exception as e:
    print(f"   ❌ Database error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 2: Create job directly
print("\n2. Creating test job...")
try:
    job_data = {
        "title": "Test Python Developer",
        "company": "Test Corp",
        "description": "This is a test job",
        "required_skills": ["Python", "Django"],
        "experience_required": "mid",
        "location": "Bangalore",
        "job_type": "remote",
        "source": "manual",
        "is_active": True
    }
    
    job_id = firebase.create_job(job_data)
    
    if job_id:
        print(f"   ✅ Job created! ID: {job_id}")
    else:
        print("   ❌ Job creation returned None!")
        
except Exception as e:
    print(f"   ❌ Job creation error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: AI Matcher
print("\n3. Testing AI Matcher...")
try:
    from app.services.ai_matcher import get_matcher
    matcher = get_matcher()
    print("   ✅ AI Matcher loaded!")
except Exception as e:
    print(f"   ❌ AI Matcher error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Pinecone
print("\n4. Testing Pinecone...")
try:
    from app.services.pinecone_service import get_pinecone_service
    pinecone = get_pinecone_service()
    
    if pinecone.index:
        print("   ✅ Pinecone connected!")
    else:
        print("   ⚠��� Pinecone not configured (optional)")
except Exception as e:
    print(f"   ⚠️ Pinecone error: {e}")

print("\n" + "="*50)
print("TEST COMPLETE!")
print("="*50)