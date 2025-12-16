"""
FastAPI application for Q&A endpoint
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from vector_store import VectorStore
from rag_pipeline import RAGPipeline
from config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    MAX_TOKENS,
    TOP_K_RESULTS
)
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Q&A Bot API",
    description="Question answering API using Retrieval Augmented Generation",
    version="1.0.0"
)

# Initialize components
vector_store = None
rag_pipeline = None


class QuestionRequest(BaseModel):
    """Request model for questions"""
    question: str = Field(..., min_length=1, description="The question to answer")
    top_k: Optional[int] = Field(
        default=TOP_K_RESULTS,
        ge=1,
        le=10,
        description="Number of context documents to retrieve"
    )


class Source(BaseModel):
    """Source document model"""
    title: str
    url: str
    relevance_score: float


class AnswerResponse(BaseModel):
    """Response model for answers"""
    question: str
    answer: str
    sources: List[Source]
    success: bool
    num_contexts_used: Optional[int] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    vector_store_count: int


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global vector_store, rag_pipeline
    
    logger.info("Initializing RAG components...")
    
    try:
        # Initialize vector store
        vector_store = VectorStore(
            persist_directory=CHROMA_PERSIST_DIR,
            collection_name=COLLECTION_NAME,
            openai_api_key=OPENAI_API_KEY,
            embedding_model=EMBEDDING_MODEL
        )
        
        # Check if vector store has data
        count = vector_store.get_collection_count()
        if count == 0:
            logger.warning("Vector store is empty! Please run main.py to build the knowledge base first.")
        else:
            logger.info(f"Vector store loaded with {count} documents")
        
        # Initialize RAG pipeline
        rag_pipeline = RAGPipeline(
            vector_store=vector_store,
            openai_api_key=OPENAI_API_KEY,
            llm_model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=MAX_TOKENS,
            top_k=TOP_K_RESULTS
        )
        
        logger.info("RAG components initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing components: {str(e)}")
        raise


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Q&A Bot API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    count = vector_store.get_collection_count()
    
    return {
        "status": "healthy" if count > 0 else "no_data",
        "vector_store_count": count
    }


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question and get an answer based on the knowledge base
    
    Args:
        request: Question request with question text and optional top_k
        
    Returns:
        Answer with sources
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    if vector_store.get_collection_count() == 0:
        raise HTTPException(
            status_code=503,
            detail="Knowledge base is empty. Please run main.py to build it first."
        )
    
    try:
        # Update top_k if provided
        original_top_k = rag_pipeline.top_k
        if request.top_k:
            rag_pipeline.top_k = request.top_k
        
        # Generate answer
        result = rag_pipeline.generate_answer(request.question)
        
        # Restore original top_k
        rag_pipeline.top_k = original_top_k
        
        return {
            "question": request.question,
            "answer": result['answer'],
            "sources": result['sources'],
            "success": result['success'],
            "num_contexts_used": result.get('num_contexts_used')
        }
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=Dict)
async def get_stats():
    """Get statistics about the knowledge base"""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    return {
        "total_documents": vector_store.get_collection_count(),
        "collection_name": COLLECTION_NAME,
        "embedding_model": EMBEDDING_MODEL,
        "llm_model": LLM_MODEL
    }


if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    
    print("""
    ╔═══════════════════════════════════════════════╗
    ║       RAG Q&A Bot API Server                  ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not found. Please set it in .env file")
        exit(1)
    
    uvicorn.run(
        "api:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
