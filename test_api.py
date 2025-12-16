"""
Test script to verify the RAG Q&A Bot API
"""
import requests
import json
import time
from typing import Dict, Any

# API Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def print_separator():
    """Print a separator line"""
    print("\n" + "="*70 + "\n")


def print_response(response: requests.Response):
    """Pretty print API response"""
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)


def test_root():
    """Test root endpoint"""
    print("Testing: GET /")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=TIMEOUT)
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_health():
    """Test health check endpoint"""
    print("Testing: GET /health")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('vector_store_count', 0) == 0:
                print("\n⚠️  WARNING: Vector store is empty!")
                print("Run 'python main.py' to build the knowledge base first.")
                return False
            return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_stats():
    """Test statistics endpoint"""
    print("Testing: GET /stats")
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=TIMEOUT)
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_ask_question(question: str, top_k: int = 5):
    """Test ask endpoint with a question"""
    print(f"Testing: POST /ask")
    print(f"Question: {question}")
    
    try:
        payload = {
            "question": question,
            "top_k": top_k
        }
        
        response = requests.post(
            f"{BASE_URL}/ask",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"\n✅ Answer generated successfully!")
                print(f"Number of sources: {len(data.get('sources', []))}")
                return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def run_all_tests():
    """Run all API tests"""
    print("""
    ╔═══════════════════════════════════════════════╗
    ║     RAG Q&A Bot API - Test Suite             ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    results = {}
    
    # Test 1: Root endpoint
    print_separator()
    results['root'] = test_root()
    
    # Test 2: Health check
    print_separator()
    results['health'] = test_health()
    
    # If health check fails due to empty store, stop here
    if not results['health']:
        print_separator()
        print("\n❌ Cannot continue tests - knowledge base is empty")
        print("Please run: python main.py")
        return
    
    # Test 3: Statistics
    print_separator()
    results['stats'] = test_stats()
    
    # Test 4-7: Ask questions
    questions = [
        "What is Python used for?",
        "How do I install Python?",
        "What are the main features of Python?",
        "How do I create a virtual environment?"
    ]
    
    for i, question in enumerate(questions):
        print_separator()
        time.sleep(1)  # Rate limiting
        results[f'question_{i+1}'] = test_ask_question(question)
    
    # Print summary
    print_separator()
    print("TEST SUMMARY")
    print_separator()
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")


if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to API server")
        print("Please start the server first: python api.py")
        print("Or: uvicorn api:app --reload")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
    
    run_all_tests()
