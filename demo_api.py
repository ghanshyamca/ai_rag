"""
Demo: REST API Testing
Shows how to interact with the RAG Q&A Bot API

Run this after starting the API server:
    python api.py
"""

import requests
import json
from typing import Dict, Any
import time

# Configuration
BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_response(response: requests.Response):
    """Print a formatted API response"""
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)

def test_health():
    """Test GET /health endpoint"""
    print_section("1. Health Check (GET /health)")
    
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ API is healthy")
        print(f"📊 Documents in vector store: {data['vector_store_count']}")
        return data['vector_store_count'] > 0
    else:
        print("❌ Health check failed")
        return False

def test_stats():
    """Test GET /stats endpoint"""
    print_section("2. Statistics (GET /stats)")
    
    response = requests.get(f"{BASE_URL}/stats")
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Stats retrieved successfully")
        print(f"📊 Total documents: {data['total_documents']}")
        print(f"🔧 Embedding model: {data['embedding_model']}")
        print(f"🤖 LLM model: {data['llm_model']}")

def test_crawl_status():
    """Test GET /crawl/status endpoint"""
    print_section("3. Crawl Status (GET /crawl/status)")
    
    response = requests.get(f"{BASE_URL}/crawl/status")
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Crawl status retrieved")
        print(f"🔄 Crawling: {data['is_crawling']}")
        if data['last_crawl_time']:
            print(f"📅 Last crawl: {data['last_crawl_time']}")

def test_crawl(interactive: bool = True):
    """Test POST /crawl endpoint"""
    print_section("4. Crawl Website (POST /crawl)")
    
    if interactive:
        print("⚠️  This test will crawl a website and may take 30+ seconds.")
        print("⚠️  It will replace existing knowledge base data.")
        response = input("\nProceed with crawling? (yes/no): ")
        if response.lower() != 'yes':
            print("Skipping crawl test.")
            return
    
    # Crawl request
    crawl_data = {
        "base_url": "https://docs.python.org/3/",
        "max_pages": 5,
        "crawl_delay": 1.0
    }
    
    print("\nRequest:")
    print(json.dumps(crawl_data, indent=2))
    
    print("\n🔄 Crawling... (this may take a while)")
    start_time = time.time()
    
    response = requests.post(
        f"{BASE_URL}/crawl",
        json=crawl_data,
        timeout=300  # 5 minute timeout
    )
    
    elapsed_time = time.time() - start_time
    
    print_response(response)
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print(f"\n✅ Crawl completed successfully!")
            print(f"📄 Pages crawled: {data['pages_crawled']}")
            print(f"📝 Chunks created: {data['chunks_created']}")
            print(f"🔢 Embeddings generated: {data['embeddings_generated']}")
            print(f"⏱️  Total time: {data['total_time']:.2f} seconds")
            print(f"⏱️  Client time: {elapsed_time:.2f} seconds")
        else:
            print(f"\n❌ Crawl failed: {data['message']}")
    else:
        print("\n❌ Crawl request failed")

def test_ask_questions():
    """Test POST /ask endpoint with multiple questions"""
    print_section("5. Ask Questions (POST /ask)")
    
    questions = [
        "How do I install Python?",
        "What are the main features of Python?",
        "How do I create a function in Python?",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'─'*70}")
        print(f"Question {i}: {question}")
        print('─'*70)
        
        # Ask request
        ask_data = {
            "question": question,
            "top_k": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/ask",
            json=ask_data
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data['success']:
                print(f"\n✅ Answer generated successfully!\n")
                print(f"Answer:")
                print(data['answer'])
                
                print(f"\nSources ({len(data['sources'])}):")
                for j, source in enumerate(data['sources'], 1):
                    print(f"\n  {j}. {source['title']}")
                    print(f"     URL: {source['url']}")
                    print(f"     Relevance: {source['relevance_score']:.4f}")
            else:
                print(f"\n❌ Failed to generate answer")
                print(f"Message: {data['answer']}")
        else:
            print(f"\n❌ Request failed with status {response.status_code}")
            print_response(response)
        
        # Small delay between questions
        if i < len(questions):
            time.sleep(0.5)

def main():
    """Run all API tests"""
    print("\n" + "="*70)
    print("  RAG Q&A Bot API - Demo Script")
    print("="*70)
    print("\nMake sure the API server is running:")
    print("  python api.py")
    print("\nServer should be at: " + BASE_URL)
    print("="*70)
    
    try:
        # Test 1: Health check
        has_data = test_health()
        
        # Test 2: Stats
        test_stats()
        
        # Test 3: Crawl status
        test_crawl_status()
        
        # Test 4: Crawl (optional, interactive)
        if not has_data:
            print("\n⚠️  Knowledge base is empty!")
            print("You need to crawl a website to populate it.")
            test_crawl(interactive=True)
        else:
            print("\n💡 Knowledge base already has data.")
            print("Skipping crawl test (would replace existing data).")
            response = input("Do you want to crawl anyway? (yes/no): ")
            if response.lower() == 'yes':
                test_crawl(interactive=False)
        
        # Test 5: Ask questions
        test_ask_questions()
        
        # Summary
        print_section("✅ Demo Complete!")
        print("All tests completed successfully!")
        print("\nNext steps:")
        print("1. Visit http://localhost:8000/docs for interactive API docs")
        print("2. Try the PowerShell test script: .\\test_api.ps1")
        print("3. See STEP7_API_COMPLETE.md for full documentation")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print(f"Make sure the server is running at {BASE_URL}")
        print("Start it with: python api.py")
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
