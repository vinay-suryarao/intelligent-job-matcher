
try:
    from langchain.chains.retrieval_qa.base import RetrievalQA
    print("SUCCESS: Found RetrievalQA in langchain.chains.retrieval_qa.base")
except ImportError as e:
    print(f"FAILED deep base: {e}")

try:
    import langchain.chains.retrieval_qa
    print("SUCCESS: imported langchain.chains.retrieval_qa")
except ImportError as e:
    print(f"FAILED deep pkg: {e}")
