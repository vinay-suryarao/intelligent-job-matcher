
try:
    from langchain_community.chains import RetrievalQA
    print("SUCCESS: Found RetrievalQA in langchain_community.chains")
except ImportError as e:
    print(f"FAILED community: {e}")

try:
    from langchain.chains import RetrievalQA
    print("SUCCESS: Found RetrievalQA in langchain.chains")
except ImportError as e:
    print(f"FAILED langchain: {e}")

import langchain
print(f"Langchain file: {langchain.__file__}")
