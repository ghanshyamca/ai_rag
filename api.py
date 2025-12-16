"""
FastAPI application for RAG Q&A Bot

Step 7: REST API Endpoints
- POST /crawl: Crawl website and build knowledge base
- POST /ask: Ask questions and get answers
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl
from vector_store import VectorStore
from rag_pipeline import RAGPipeline
from crawler import WebCrawler
from text_processor import TextProcessor
from config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    MAX_TOKENS,
    TOP_K_RESULTS,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    MAX_PAGES,
    CRAWL_DELAY
)
from typing import List, Dict, Optional
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Q&A Bot API",
    description="Question answering API using Retrieval Augmented Generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
vector_store = None
rag_pipeline = None

# Track crawl status
crawl_status = {
    "is_crawling": False,
    "last_crawl": None,
    "last_result": None
}


class CrawlRequest(BaseModel):
    """Request model for crawling"""
    base_url: HttpUrl = Field(..., description="The base URL to crawl")
    max_pages: Optional[int] = Field(
        default=MAX_PAGES,
        ge=1,
        le=100,
        description="Maximum number of pages to crawl"
    )
    crawl_delay: Optional[float] = Field(
        default=CRAWL_DELAY,
        ge=0.5,
        le=5.0,
        description="Delay between requests in seconds"
    )


class CrawlResponse(BaseModel):
    """Response model for crawl endpoint"""
    success: bool
    message: str
    pages_crawled: Optional[int] = None
    chunks_created: Optional[int] = None
    embeddings_generated: Optional[int] = None
    total_time: Optional[float] = None


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


@app.post("/crawl", response_model=CrawlResponse)
async def crawl_and_index(request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    STEP 7 - POST /crawl Endpoint
    
    Crawls a website and builds the knowledge base:
    1. Run crawling (extract HTML from pages)
    2. Run extraction (clean text)
    3. Run chunking (split into chunks)
    4. Run embeddings (generate vectors)
    5. Index everything in vector store
    
    Args:
        request: Crawl request with base_url, max_pages, crawl_delay
        
    Returns:
        Success message with statistics
    """
    global vector_store, rag_pipeline, crawl_status
    
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    if crawl_status["is_crawling"]:
        raise HTTPException(
            status_code=409,
            detail="Crawl already in progress. Please wait for it to complete."
        )
    
    try:
        crawl_status["is_crawling"] = True
        start_time = time.time()
        
        logger.info(f"Starting crawl of {request.base_url}")
        
        # Step 1: Run crawling
        logger.info("Step 1/5: Crawling website...")
        crawler = WebCrawler(
            base_url=str(request.base_url),
            max_pages=request.max_pages,
            delay=request.crawl_delay
        )
        pages_data = crawler.crawl()
        
        if not pages_data:
            crawl_status["is_crawling"] = False
            return {
                "success": False,
                "message": "No pages were crawled. Please check the URL.",
                "pages_crawled": 0
            }
        
        logger.info(f"Crawled {len(pages_data)} pages")
        
        # Step 2 & 3: Run extraction and chunking
        logger.info("Step 2/5: Extracting and cleaning text...")
        logger.info("Step 3/5: Chunking text...")
        processor = TextProcessor(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        chunks = processor.process_documents(pages_data)
        
        if not chunks:
            crawl_status["is_crawling"] = False
            return {
                "success": False,
                "message": "No chunks created. Content may be too short.",
                "pages_crawled": len(pages_data),
                "chunks_created": 0
            }
        
        logger.info(f"Created {len(chunks)} chunks")
        
        # Step 4 & 5: Run embeddings and index in vector store
        logger.info("Step 4/5: Generating embeddings...")
        logger.info("Step 5/5: Indexing in vector store...")
        
        # Clear existing data
        vector_store.clear_collection()
        
        # Add new documents
        vector_store.add_documents(chunks, batch_size=100)
        
        total_time = time.time() - start_time
        
        logger.info(f"Crawl completed in {total_time:.2f}s")
        
        # Update crawl status
        crawl_status["is_crawling"] = False
        crawl_status["last_crawl"] = time.time()
        crawl_status["last_result"] = {
            "pages_crawled": len(pages_data),
            "chunks_created": len(chunks),
            "embeddings_generated": len(chunks),
            "total_time": total_time
        }
        
        return {
            "success": True,
            "message": f"Successfully crawled and indexed {len(pages_data)} pages",
            "pages_crawled": len(pages_data),
            "chunks_created": len(chunks),
            "embeddings_generated": len(chunks),
            "total_time": total_time
        }
        
    except Exception as e:
        crawl_status["is_crawling"] = False
        logger.error(f"Error during crawl: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Crawl failed: {str(e)}")


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    STEP 7 - POST /ask Endpoint
    
    Ask a question and get an answer:
    1. Run retrieval (find relevant chunks)
    2. Generate final answer (use LLM with context)
    3. Return answer text and source URLs
    
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
            detail="Knowledge base is empty. Please use POST /crawl to build it first."
        )
    
    try:
        logger.info(f"Processing question: {request.question}")
        
        # Generate answer
        result = rag_pipeline.generate_answer(
            request.question,
            top_k=request.top_k
        )
        
        if not result['success']:
            logger.warning(f"Failed to generate answer: {result.get('error', 'Unknown error')}")
        
        return {
            "question": request.question,
            "answer": result['answer'],
            "sources": result['sources'],
            "success": result['success'],
            "num_contexts_used": result.get('num_chunks_used', 0)
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
        "llm_model": LLM_MODEL,
        "is_crawling": crawl_status["is_crawling"],
        "last_crawl": crawl_status["last_result"]
    }


@app.get("/crawl/status", response_model=Dict)
async def get_crawl_status():
    """Get current crawl status"""
    return {
        "is_crawling": crawl_status["is_crawling"],
        "last_crawl_time": crawl_status["last_crawl"],
        "last_result": crawl_status["last_result"]
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
