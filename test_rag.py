"""
Step 6 Test - RAG Pipeline (Retrieval and Answer Generation)
Tests the complete question-answering system
"""
from rag_pipeline import RAGPipeline
from vector_store import VectorStore
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
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_rag_pipeline():
    """Test the complete RAG pipeline with sample questions"""
    
    print("\n" + "="*70)
    print("STEP 6 TEST - RAG PIPELINE (RETRIEVAL + ANSWER GENERATION)")
    print("="*70 + "\n")
    
    # Check API key
    if not OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        print("\nPlease set your OpenAI API key in .env file:")
        print("  OPENAI_API_KEY=your_api_key_here")
        return
    
    print("Configuration:")
    print(f"  • Embedding Model: {EMBEDDING_MODEL}")
    print(f"  • LLM Model: {LLM_MODEL}")
    print(f"  • Temperature: {LLM_TEMPERATURE}")
    print(f"  • Max Tokens: {MAX_TOKENS}")
    print(f"  • Top K Results: {TOP_K_RESULTS}")
    print(f"  • Vector DB: ChromaDB ({COLLECTION_NAME})")
    print()
    
    # Step 1: Initialize components
    print("="*70)
    print("STEP 1: INITIALIZING RAG PIPELINE")
    print("="*70 + "\n")
    
    try:
        # Initialize vector store
        vector_store = VectorStore(
            persist_directory=CHROMA_PERSIST_DIR,
            collection_name=COLLECTION_NAME,
            openai_api_key=OPENAI_API_KEY,
            embedding_model=EMBEDDING_MODEL
        )
        
        collection_size = vector_store.get_collection_count()
        print(f"✓ Vector store initialized")
        print(f"  Collection size: {collection_size} chunks")
        
        if collection_size == 0:
            print("\n⚠ WARNING: Vector store is empty!")
            print("  Please run one of the following first:")
            print("    - python main.py (to crawl and build knowledge base)")
            print("    - python test_embeddings.py (to add sample documents)")
            return
        
        print()
        
        # Initialize RAG pipeline
        rag = RAGPipeline(
            vector_store=vector_store,
            openai_api_key=OPENAI_API_KEY,
            llm_model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=MAX_TOKENS,
            top_k=TOP_K_RESULTS
        )
        
        print("✓ RAG pipeline initialized")
        print()
        
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize: {str(e)}")
        return
    
    # Step 2: Test retrieval function
    print("="*70)
    print("STEP 2: TESTING RETRIEVAL FUNCTION")
    print("="*70 + "\n")
    
    test_query = "How do I install Python?"
    
    print(f"Query: '{test_query}'")
    print()
    
    try:
        retrieval_results = rag.retrieve(test_query, top_k=3)
        
        if retrieval_results['count'] > 0:
            print(f"✓ Retrieved {retrieval_results['count']} chunks in {retrieval_results['retrieval_time']:.3f}s")
            print()
            
            for i, (doc, metadata, similarity) in enumerate(zip(
                retrieval_results['documents'],
                retrieval_results['metadatas'],
                retrieval_results['similarities']
            ), 1):
                print(f"Chunk {i}:")
                print(f"  Title: {metadata['title']}")
                print(f"  URL: {metadata['url']}")
                print(f"  Relevance: {similarity:.4f} ({similarity*100:.1f}%)")
                print(f"  Preview: {doc[:150].replace(chr(10), ' ')}...")
                print()
            
            # Evaluate retrieval quality
            avg_similarity = sum(retrieval_results['similarities']) / len(retrieval_results['similarities'])
            print(f"Average relevance: {avg_similarity:.4f}")
            
            if avg_similarity > 0.7:
                print("✓ Retrieval quality: EXCELLENT")
            elif avg_similarity > 0.5:
                print("⚠ Retrieval quality: GOOD (consider tuning)")
            else:
                print("❌ Retrieval quality: POOR (needs tuning)")
            
            print()
        else:
            print("❌ No results found")
            print()
            
    except Exception as e:
        print(f"❌ ERROR during retrieval: {str(e)}")
        return
    
    # Step 3: Test answer generation with multiple questions
    print("="*70)
    print("STEP 3: TESTING ANSWER GENERATION")
    print("="*70 + "\n")
    
    # Test questions related to the knowledge base
    # Adjust these based on your actual crawled content
    test_questions = [
        "How do I install Python?",
        "What are the main features of Python?",
        "How do I create a function in Python?",
        "What data types does Python support?",
        "How do I handle errors in Python?"
    ]
    
    print(f"Testing {len(test_questions)} questions...\n")
    
    results_summary = []
    
    for idx, question in enumerate(test_questions, 1):
        print("─" * 70)
        print(f"Question {idx}: {question}")
        print("─" * 70)
        
        try:
            result = rag.generate_answer(question)
            
            if result['success']:
                # Display answer
                print(f"\n✓ Answer generated successfully\n")
                print(f"Answer:")
                print(f"{result['answer']}\n")
                
                # Display timing
                print(f"Performance:")
                print(f"  • Retrieval time: {result['retrieval_time']:.3f}s")
                print(f"  • Generation time: {result['generation_time']:.3f}s")
                print(f"  • Total time: {result['total_time']:.3f}s")
                print()
                
                # Display sources
                print(f"Sources ({len(result['sources'])} unique):")
                for i, source in enumerate(result['sources'], 1):
                    print(f"  {i}. {source['title']}")
                    print(f"     URL: {source['url']}")
                    print(f"     Relevance: {source['relevance_score']:.4f}")
                print()
                
                # Evaluate answer quality
                answer_length = len(result['answer'])
                has_sources = len(result['sources']) > 0
                
                quality = "GOOD"
                if answer_length < 50:
                    quality = "TOO SHORT"
                elif "don't have enough information" in result['answer'].lower():
                    quality = "NO ANSWER FOUND"
                elif not has_sources:
                    quality = "NO SOURCES"
                
                print(f"Quality Assessment: {quality}")
                
                results_summary.append({
                    'question': question,
                    'success': True,
                    'quality': quality,
                    'num_sources': len(result['sources']),
                    'total_time': result['total_time']
                })
                
            else:
                print(f"\n❌ Failed to generate answer")
                print(f"Error: {result.get('error', 'Unknown error')}")
                
                results_summary.append({
                    'question': question,
                    'success': False,
                    'quality': 'FAILED',
                    'num_sources': 0,
                    'total_time': result.get('total_time', 0)
                })
            
            print()
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}\n")
            results_summary.append({
                'question': question,
                'success': False,
                'quality': 'ERROR',
                'num_sources': 0,
                'total_time': 0
            })
    
    # Step 4: Summary
    print("="*70)
    print("STEP 6 VERIFICATION SUMMARY")
    print("="*70 + "\n")
    
    successful = sum(1 for r in results_summary if r['success'])
    total = len(results_summary)
    avg_time = sum(r['total_time'] for r in results_summary) / total if total > 0 else 0
    
    print(f"📊 Test Results:")
    print(f"  • Questions tested: {total}")
    print(f"  • Successful answers: {successful}/{total} ({successful/total*100:.0f}%)")
    print(f"  • Average response time: {avg_time:.3f}s")
    print()
    
    print(f"✅ Completed Tasks:")
    print(f"  ✓ Built retrieval function (embeds query, fetches chunks)")
    print(f"  ✓ Built answer generation function (LLM with context)")
    print(f"  ✓ Answers generated from context only")
    print(f"  ✓ Sources returned with URLs and relevance scores")
    print(f"  ✓ Tested with {total} questions")
    print()
    
    print(f"📋 Question Results:")
    for i, r in enumerate(results_summary, 1):
        status = "✓" if r['success'] else "✗"
        print(f"  {status} Q{i}: {r['question'][:50]}...")
        print(f"     Quality: {r['quality']}, Sources: {r['num_sources']}, Time: {r['total_time']:.2f}s")
    print()
    
    if successful == total:
        print("🎉 All tests passed! RAG pipeline is working correctly.")
    elif successful > 0:
        print(f"⚠ {total - successful} test(s) failed. Review the errors above.")
    else:
        print("❌ All tests failed. Check your configuration and data.")
    
    print()
    
    print("💡 Recommendations:")
    print("  • If answers are too generic, try reducing temperature")
    print("  • If answers are too short, increase MAX_TOKENS")
    print("  • If retrieval is poor, adjust CHUNK_SIZE or TOP_K_RESULTS")
    print("  • If no sources found, verify vector store has data")
    print()
    
    print("🎯 Next Step:")
    print("  Step 7: Build FastAPI server for the Q&A system")
    print()
    
    print("="*70 + "\n")
    
    return results_summary


def test_retrieval_only():
    """Quick test of just the retrieval function"""
    
    print("\n" + "="*70)
    print("QUICK RETRIEVAL TEST")
    print("="*70 + "\n")
    
    vector_store = VectorStore(
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name=COLLECTION_NAME,
        openai_api_key=OPENAI_API_KEY,
        embedding_model=EMBEDDING_MODEL
    )
    
    rag = RAGPipeline(
        vector_store=vector_store,
        openai_api_key=OPENAI_API_KEY,
        llm_model=LLM_MODEL,
        top_k=5
    )
    
    test_queries = [
        "How to install?",
        "What is Python used for?",
        "How to write a function?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = rag.retrieve(query, top_k=3)
        
        if results['count'] > 0:
            print(f"  Found {results['count']} chunks")
            print(f"  Top relevance: {results['similarities'][0]:.3f}")
            print(f"  Source: {results['metadatas'][0]['title']}")
        else:
            print("  No results found")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        test_retrieval_only()
    else:
        test_rag_pipeline()
