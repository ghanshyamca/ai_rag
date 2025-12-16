"""
Step 5 Test - Embedding Generation and Vector Database
Tests the complete embedding pipeline with ChromaDB
"""
from vector_store import VectorStore
from text_processor import TextProcessor
from config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    TOP_K_RESULTS,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_embedding_generation():
    """Test Step 5: Embedding Generation and Vector Database"""
    
    print("\n" + "="*70)
    print("STEP 5 TEST - EMBEDDING GENERATION AND VECTOR DATABASE")
    print("="*70 + "\n")
    
    # Check API key
    if not OPENAI_API_KEY:
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        print("\nPlease set your OpenAI API key in .env file:")
        print("  OPENAI_API_KEY=your_api_key_here")
        return
    
    print("Configuration:")
    print(f"  • Embedding Model: {EMBEDDING_MODEL}")
    print(f"  • Vector Database: ChromaDB")
    print(f"  • Persist Directory: {CHROMA_PERSIST_DIR}")
    print(f"  • Collection Name: {COLLECTION_NAME}")
    print(f"  • Top K Results: {TOP_K_RESULTS}")
    print()
    
    # Step 1: Create sample documents
    print("="*70)
    print("STEP 1: CREATING SAMPLE DOCUMENTS")
    print("="*70 + "\n")
    
    sample_documents = [
        {
            'url': 'https://docs.python.org/getting-started',
            'title': 'Getting Started with Python',
            'content': '''
            Python is a high-level, interpreted programming language known for its simplicity
            and readability. To get started with Python, you first need to install it on your
            system. You can download Python from the official website at python.org.
            
            After installation, you can verify that Python is installed by opening a terminal
            or command prompt and typing "python --version" or "python3 --version". This will
            display the installed Python version.
            
            Python comes with a package manager called pip, which allows you to install
            third-party libraries and packages. To check if pip is installed, type
            "pip --version" in your terminal.
            '''
        },
        {
            'url': 'https://docs.python.org/data-types',
            'title': 'Python Data Types',
            'content': '''
            Python has several built-in data types. The most common ones are:
            
            Numbers: Python supports integers (int), floating-point numbers (float), and
            complex numbers. You can perform arithmetic operations on these types.
            
            Strings: Text data is represented using strings (str). Strings are immutable
            sequences of characters enclosed in quotes. You can use single, double, or
            triple quotes for strings.
            
            Lists: Lists are ordered, mutable collections that can contain items of
            different types. They are defined using square brackets []. Lists support
            indexing, slicing, and various methods like append(), extend(), and remove().
            
            Dictionaries: Dictionaries are key-value pairs defined using curly braces {}.
            They provide fast lookups and are widely used for mapping relationships.
            '''
        },
        {
            'url': 'https://docs.python.org/functions',
            'title': 'Python Functions',
            'content': '''
            Functions in Python are defined using the def keyword. They allow you to
            encapsulate reusable code. A function can accept parameters and return values.
            
            Here's a basic function syntax:
            def function_name(parameters):
                # function body
                return result
            
            Functions can have default parameter values, accept variable number of arguments,
            and support keyword arguments. Python also supports lambda functions for creating
            small anonymous functions.
            
            Functions are first-class objects in Python, meaning they can be assigned to
            variables, passed as arguments, and returned from other functions.
            '''
        },
        {
            'url': 'https://docs.python.org/modules',
            'title': 'Python Modules and Packages',
            'content': '''
            Modules are Python files containing definitions and statements. They help organize
            code into reusable components. You can import modules using the import statement.
            
            The Python Standard Library includes many useful modules like os for operating
            system operations, sys for system-specific parameters, datetime for date and time
            operations, and json for working with JSON data.
            
            Packages are collections of modules organized in directories. A package must
            contain a special __init__.py file. You can import specific modules from packages
            using from package import module syntax.
            
            Third-party packages can be installed using pip. Popular packages include NumPy
            for numerical computing, Pandas for data analysis, and Requests for HTTP requests.
            '''
        },
        {
            'url': 'https://docs.python.org/error-handling',
            'title': 'Error Handling in Python',
            'content': '''
            Python uses exceptions to handle errors. The try-except block is used to catch
            and handle exceptions. This prevents your program from crashing when errors occur.
            
            Basic syntax:
            try:
                # code that might raise an exception
            except ExceptionType:
                # handle the exception
            
            You can catch multiple exception types, use else clause for code that runs when
            no exception occurs, and finally clause for cleanup code that always executes.
            
            Common exceptions include ValueError, TypeError, KeyError, IndexError, and
            FileNotFoundError. You can also create custom exceptions by defining classes
            that inherit from the Exception class.
            '''
        }
    ]
    
    print(f"Created {len(sample_documents)} sample documents")
    for doc in sample_documents:
        print(f"  • {doc['title']}")
    print()
    
    # Step 2: Process documents into chunks
    print("="*70)
    print("STEP 2: PROCESSING DOCUMENTS INTO CHUNKS")
    print("="*70 + "\n")
    
    processor = TextProcessor(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = processor.process_documents(sample_documents)
    
    stats = processor.get_chunk_statistics(chunks)
    print(f"\nChunk Statistics:")
    print(f"  • Total chunks: {stats['total_chunks']}")
    print(f"  • Average chunk size: {stats['avg_chunk_size']:.0f} chars")
    print(f"  • Documents processed: {stats['unique_documents']}")
    print()
    
    # Step 3: Initialize Vector Store
    print("="*70)
    print("STEP 3: INITIALIZING VECTOR STORE")
    print("="*70 + "\n")
    
    try:
        vector_store = VectorStore(
            persist_directory=CHROMA_PERSIST_DIR,
            collection_name=COLLECTION_NAME,
            openai_api_key=OPENAI_API_KEY,
            embedding_model=EMBEDDING_MODEL
        )
        
        print(f"✓ Vector store initialized")
        print(f"  Current collection size: {vector_store.get_collection_count()}\n")
        
    except Exception as e:
        print(f"❌ ERROR initializing vector store: {str(e)}")
        return
    
    # Step 4: Generate embeddings and store
    print("="*70)
    print("STEP 4: GENERATING EMBEDDINGS AND STORING IN DATABASE")
    print("="*70 + "\n")
    
    print("This will:")
    print("  1. Generate embeddings for each chunk using OpenAI API")
    print("  2. Insert embeddings and metadata into ChromaDB")
    print("  3. Persist the database to disk\n")
    
    try:
        # Clear existing data for clean test
        if vector_store.get_collection_count() > 0:
            response = input("Collection has existing data. Clear it? (y/n): ")
            if response.lower() == 'y':
                vector_store.clear_collection()
                print("✓ Collection cleared\n")
        
        # Add documents
        vector_store.add_documents(chunks, batch_size=10)
        
        print(f"✓ Successfully stored {vector_store.get_collection_count()} chunks in vector database")
        print()
        
    except Exception as e:
        print(f"❌ ERROR during embedding generation: {str(e)}")
        if "api_key" in str(e).lower():
            print("\nPlease check your OPENAI_API_KEY is valid")
        return
    
    # Step 5: Test similarity search
    print("="*70)
    print("STEP 5: TESTING SIMILARITY SEARCH")
    print("="*70 + "\n")
    
    test_queries = [
        "How do I install Python?",
        "What are the different data types in Python?",
        "How do I create a function?",
        "How do I handle errors in Python?"
    ]
    
    for query_num, test_query in enumerate(test_queries, 1):
        print(f"\n{'─'*70}")
        print(f"Test Query {query_num}: '{test_query}'")
        print(f"{'─'*70}\n")
        
        try:
            results = vector_store.search(test_query, top_k=3)
            
            if results['count'] == 0:
                print("⚠ No results found")
                continue
            
            print(f"Found {results['count']} relevant chunks:\n")
            
            for i, (doc, metadata, similarity) in enumerate(zip(
                results['documents'],
                results['metadatas'],
                results['similarities']
            ), 1):
                print(f"Result {i}:")
                print(f"  Similarity Score: {similarity:.4f} ({similarity*100:.2f}%)")
                print(f"  Title: {metadata['title']}")
                print(f"  URL: {metadata['url']}")
                print(f"  Chunk: {metadata['chunk_id']}/{metadata['total_chunks']}")
                print(f"\n  Content Preview (first 200 chars):")
                print(f"  {doc[:200].replace(chr(10), ' ')}...")
                print()
            
            # Check relevance
            top_similarity = results['similarities'][0]
            if top_similarity > 0.7:
                print(f"✓ Retrieval is RELEVANT (similarity: {top_similarity:.4f})")
            elif top_similarity > 0.5:
                print(f"⚠ Retrieval is MODERATELY RELEVANT (similarity: {top_similarity:.4f})")
                print("  Consider adjusting chunk size or improving text cleaning")
            else:
                print(f"❌ Retrieval is NOT RELEVANT (similarity: {top_similarity:.4f})")
                print("  RECOMMENDATION: Adjust chunk size or improve text cleaning")
            
        except Exception as e:
            print(f"❌ ERROR during search: {str(e)}")
    
    # Step 6: Summary and recommendations
    print("\n" + "="*70)
    print("STEP 5 VERIFICATION SUMMARY")
    print("="*70 + "\n")
    
    print("✅ Completed Tasks:")
    print(f"  ✓ Embedding model selected: {EMBEDDING_MODEL}")
    print(f"  ✓ Generated embeddings for {stats['total_chunks']} chunks")
    print(f"  ✓ Vector database selected: ChromaDB")
    print(f"  ✓ Embeddings and metadata stored in vector store")
    print(f"  ✓ Tested {len(test_queries)} similarity searches")
    print()
    
    print("📊 Database Information:")
    print(f"  • Collection: {COLLECTION_NAME}")
    print(f"  • Total vectors: {vector_store.get_collection_count()}")
    print(f"  • Persist directory: {CHROMA_PERSIST_DIR}")
    print(f"  • Embedding dimension: 1536 (text-embedding-ada-002)")
    print()
    
    print("💡 Recommendations:")
    print("  • If retrieval is not relevant, try:")
    print("    - Adjusting CHUNK_SIZE (current: {})".format(CHUNK_SIZE))
    print("    - Adjusting CHUNK_OVERLAP (current: {})".format(CHUNK_OVERLAP))
    print("    - Improving text cleaning in text_processor.py")
    print("    - Using more specific queries")
    print()
    
    print("🎯 Next Step:")
    print("  Step 6: Implement retrieval mechanism and Q&A endpoint")
    print()
    
    print("="*70 + "\n")


if __name__ == "__main__":
    test_embedding_generation()
