"""
Main script to build the knowledge base
Crawls website, processes text, and stores embeddings
"""
import json
import os
from crawler import WebCrawler
from text_processor import TextProcessor
from vector_store import VectorStore
from config import (
    TARGET_URL,
    MAX_PAGES,
    CRAWL_DELAY,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    OPENAI_API_KEY,
    EMBEDDING_MODEL
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_crawled_data(data, filename="crawled_data.json"):
    """Save crawled data to JSON file"""
    os.makedirs("data", exist_ok=True)
    filepath = os.path.join("data", filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved crawled data to {filepath}")


def load_crawled_data(filename="crawled_data.json"):
    """Load crawled data from JSON file"""
    filepath = os.path.join("data", filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded crawled data from {filepath}")
        return data
    return None


def build_knowledge_base(force_recrawl=False):
    """
    Build the complete knowledge base
    
    Args:
        force_recrawl: If True, recrawl even if data exists
    """
    logger.info("Starting knowledge base construction")
    
    # Step 1: Crawl website (or load existing data)
    if force_recrawl or not os.path.exists("data/crawled_data.json"):
        logger.info(f"Step 1: Crawling website {TARGET_URL}")
        crawler = WebCrawler(
            base_url=TARGET_URL,
            max_pages=MAX_PAGES,
            delay=CRAWL_DELAY
        )
        pages_data = crawler.crawl()
        save_crawled_data(pages_data)
    else:
        logger.info("Step 1: Loading existing crawled data")
        pages_data = load_crawled_data()
    
    if not pages_data:
        logger.error("No data to process")
        return
    
    # Step 2: Process and chunk text
    logger.info("Step 2: Processing and chunking text")
    processor = TextProcessor(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = processor.process_documents(pages_data)
    
    # Display chunk statistics
    chunk_stats = processor.get_chunk_statistics(chunks)
    logger.info(f"\n{'='*60}")
    logger.info("CHUNK STATISTICS")
    logger.info(f"{'='*60}")
    logger.info(f"Total chunks: {chunk_stats['total_chunks']}")
    logger.info(f"Average chunk size: {chunk_stats['avg_chunk_size']:.0f} chars")
    logger.info(f"Min chunk size: {chunk_stats['min_chunk_size']} chars")
    logger.info(f"Max chunk size: {chunk_stats['max_chunk_size']} chars")
    logger.info(f"{'='*60}\n")
    
    # Step 3: Initialize vector store
    logger.info("Step 3: Initializing vector store")
    vector_store = VectorStore(
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name=COLLECTION_NAME,
        openai_api_key=OPENAI_API_KEY,
        embedding_model=EMBEDDING_MODEL
    )
    
    # Check if we should add documents
    existing_count = vector_store.get_collection_count()
    if existing_count > 0 and not force_recrawl:
        logger.info(f"Vector store already contains {existing_count} documents")
        response = input("Clear existing data and rebuild? (y/n): ")
        if response.lower() == 'y':
            vector_store.clear_collection()
        else:
            logger.info("Keeping existing data")
            return
    
    # Step 4: Generate embeddings and store
    logger.info("Step 4: Generating embeddings and storing in vector database")
    vector_store.add_documents(chunks)
    
    # Step 5: Test similarity search
    logger.info("Step 5: Testing similarity search")
    test_queries = [
        "How do I get started?",
        "What are the main features?",
        "How do I install this?"
    ]
    
    logger.info(f"\\n{'='*60}")
    logger.info("TESTING SIMILARITY SEARCH")
    logger.info(f"{'='*60}\\n")
    
    for query in test_queries:
        logger.info(f"Query: '{query}'")
        results = vector_store.search(query, top_k=2)
        
        if results['count'] > 0:
            top_similarity = results['similarities'][0]
            logger.info(f"  Top result: {results['metadatas'][0]['title']}")
            logger.info(f"  Similarity: {top_similarity:.4f} ({top_similarity*100:.1f}%)")
            
            if top_similarity < 0.5:
                logger.warning(f"  ⚠ Low similarity score - consider adjusting chunk size or cleaning")
        else:
            logger.warning(f"  No results found")
        logger.info("")
    
    logger.info(f"\\n{'='*60}")
    logger.info("KNOWLEDGE BASE BUILD COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Total pages crawled: {len(pages_data)}")
    logger.info(f"Total chunks created: {len(chunks)}")
    logger.info(f"Documents in vector store: {vector_store.get_collection_count()}")
    logger.info(f"{'='*60}\\n")


if __name__ == "__main__":
    import sys
    
    force_recrawl = "--force" in sys.argv or "-f" in sys.argv
    
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not found. Please set it in .env file")
        sys.exit(1)
    
    print("""
    ╔═══════════════════════════════════════════════╗
    ║   RAG Q&A Bot - Knowledge Base Builder       ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    print(f"Target URL: {TARGET_URL}")
    print(f"Max pages: {MAX_PAGES}")
    print(f"Force recrawl: {force_recrawl}\n")
    
    build_knowledge_base(force_recrawl=force_recrawl)
