import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
from pinecone import Pinecone

# 1. Environment Variables Load karo
load_dotenv()

print("🔄 Testing Connections...")

# --- FIREBASE CHECK ---
try:
    cred_path = os.getenv("FIREBASE_CRED_PATH")
    if not cred_path:
        raise ValueError("❌ FIREBASE_CRED_PATH .env mein missing hai!")
    
    # Check if file actually exists
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"❌ '{cred_path}' file nahi mil rahi! Location check kar.")

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    print("✅ Firebase Connected! (Auth & Firestore Ready)")
except Exception as e:
    print(f"❌ Firebase Error: {e}")

# --- PINECONE CHECK ---
try:
    pc_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    if not pc_key:
        raise ValueError("❌ PINECONE_API_KEY .env mein missing hai!")

    # Initialize Pinecone (New Syntax)
    pc = Pinecone(api_key=pc_key)
    
    # Check if index exists
    existing_indexes = [i.name for i in pc.list_indexes()]
    print(f"📊 Available Pinecone Indexes: {existing_indexes}")
    
    if index_name in existing_indexes:
        print(f"✅ Pinecone Connected! Index '{index_name}' found.")
    else:
        print(f"⚠️ Pinecone Connected, but Index '{index_name}' nahi mila. Dashboard pe naam check kar.")

except Exception as e:
    print(f"❌ Pinecone Error: {e}")