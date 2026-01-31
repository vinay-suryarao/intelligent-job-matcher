import os
from dotenv import load_dotenv

load_dotenv()

print("="*50)
print("FIREBASE TEST")
print("="*50)

# Check 1: Credentials path
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
print(f"\n1. Path in .env: {cred_path}")

# Check 2: File exists?
if cred_path and os.path.exists(cred_path):
    print(f"   ✅ File exists! Size: {os.path.getsize(cred_path)} bytes")
else:
    print(f"   ❌ File NOT found!")
    print(f"   Current dir: {os.getcwd()}")
    exit(1)

# Check 3: Try Firebase
print("\n2. Testing Firebase connection...")
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    print("   ✅ Firebase connected!")
    
    # Test write
    print("\n3. Testing write...")
    db.collection('_test').document('test').set({'test': True})
    print("   ✅ Write works!")
    
    # Cleanup
    db.collection('_test').document('test').delete()
    print("   ✅ Cleanup done!")
    
    print("\n" + "="*50)
    print("🎉 FIREBASE IS WORKING!")
    print("="*50)
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()