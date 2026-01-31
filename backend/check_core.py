
try:
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import PromptTemplate
    print("SUCCESS: langchain_core works")
except ImportError as e:
    print(f"FAILED core: {e}")
