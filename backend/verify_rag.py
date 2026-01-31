
try:
    import app.services.rag_engine
    print("SUCCESS: rag_engine imported")
except ImportError as e:
    print(f"FAILED: {e}")
except Exception as e:
    print(f"ERROR: {e}")
