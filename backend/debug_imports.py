
import sys
print(f"Python: {sys.executable}")
try:
    import langchain
    print(f"LangChain version: {langchain.__version__}")
    import langchain.chains
    print("langchain.chains imported successfully")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"Error: {e}")

try:
    from langchain.chains import RetrievalQA
    print("RetrievalQA imported successfully")
except Exception as e:
    print(f"RetrievalQA import failed: {e}")
