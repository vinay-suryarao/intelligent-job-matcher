
import sys
import pkg_resources

try:
    dist = pkg_resources.get_distribution("langchain")
    print(f"LangChain Version: {dist.version}")
except Exception as e:
    print(f"Could not get version: {e}")

try:
    import langchain
    print(f"Langchain dir: {langchain.__file__}")
    print(f"Langchain contents: {dir(langchain)}")
    
    try:
        import langchain.chains
        print("langchain.chains imported")
    except ImportError:
        print("langchain.chains FAILED")

    try:
        from langchain_community.chains import RetrievalQA
        print("Found RetrievalQA in langchain_community.chains")
    except ImportError:
        pass

except ImportError as e:
    print(f"Import langchain failed: {e}")
