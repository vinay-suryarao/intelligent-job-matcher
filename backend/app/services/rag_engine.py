import os
import logging
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

# Singleton instances
_qa_chain = None
_retriever = None

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_qa_chain():
    """Get or initialize the QA chain components"""
    global _qa_chain, _retriever
    
    if _qa_chain and _retriever:
        return _qa_chain, _retriever
        
    try:
        logger.info("🤖 Initializing RAG Engine...")
        
        # 1. Setup Gemini/Groq LLM
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            logger.error("❌ GROQ_API_KEY not found in environment variables")
            return None, None
            
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=groq_api_key,
            temperature=0.3
        )
        
        # 2. Setup Embeddings (Must match what we used for indexing)
        logger.info("📥 Loading Embedding Model (BAAI)...")
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
        
        # 3. Connect to Pinecone Memory
        index_name = os.getenv("PINECONE_INDEX_NAME", "job-matcher")
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        
        if not pinecone_api_key:
            logger.error("❌ PINECONE_API_KEY not found")
            return None, None
            
        vectorstore = PineconeVectorStore(
            index_name=index_name, 
            embedding=embeddings,
            pinecone_api_key=pinecone_api_key
        )
        
        # 4. Create RAG Prompt
        prompt_template = """
        You are an Intelligent Career Coach & Consultant.
        Your goal is to help candidates find the right jobs and improve their skills.
        
        Strictly follow these rules:
        1. **Format your answer using Markdown.** Use bolding for key terms and headers for sections.
        2. Use the Context (Job Descriptions/Resumes) provided below to answer.
        3. If you find a skill gap, be honest but encouraging. Suggest specific topics to learn.
        4. If asking for interview prep, provide technical questions based on the JD.
        5. Don't hallucinate jobs. Only use what's in the context.
        6. **ALWAYS** provide the "APPLY LINK" if available in the context.
        7. Use bullet points for lists to make it readable.
        8. If the user greets you (hi, hello) or asks general questions, answer logically and politely even if not in the context.
        9. Keep greetings short and professional.
        
        Context:
        {context}
        
        Chat History:
        {chat_history}
        
        Question:
        {question}
        
        Answer:
        """
        
        PROMPT = PromptTemplate(
            template=prompt_template, 
            input_variables=["context", "question", "chat_history"]
        )
        
        # 5. Create Manual Retrieval Chain (LCEL)
        _retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        _qa_chain = (
            PROMPT
            | llm
            | StrOutputParser()
        )
        
        logger.info("✅ RAG Engine initialized successfully")
        return _qa_chain, _retriever
        
    except Exception as e:
        logger.error(f"❌ Error initializing RAG Engine: {e}")
        return None, None

def format_chat_history(history: list) -> str:
    """Format chat history into a string"""
    if not history:
        return "No previous history."
    
    formatted = []
    for msg in history:
        role = msg.get("role", "unknown").title()
        content = msg.get("content", "")
        formatted.append(f"{role}: {content}")
        
    # Limit to last 10 messages to save tokens
    return "\n".join(formatted[-10:])

def ask_career_coach(query: str, chat_history: list = [], context: dict = None):
    """
    Main function to ask specific career questions.
    """
    chain, retriever = get_qa_chain()
    
    if not chain:
        return {
            "error": "RAG engine not initialized"
        }
    
    try:
        # 1. Retrieve docs manually
        docs = retriever.invoke(query)
        context_str = format_docs(docs)
        
        # 2. Format history
        history_str = format_chat_history(chat_history)

        # 3. Invoke generation chain
        response_text = chain.invoke({
            "context": context_str, 
            "question": query,
            "chat_history": history_str
        })
        
        return {
            "answer": response_text,
            "source_docs": [doc.page_content for doc in docs]
        }
    except Exception as e:
        logger.error(f"❌ RAG Query Error: {e}")
        return {"error": str(e)}
