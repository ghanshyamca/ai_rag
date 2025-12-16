"""
RAG Pipeline Demo - Visual Demonstration of Step 6
Shows how retrieval and answer generation work together
"""

def demo_rag():
    """Visual demonstration of the complete RAG workflow"""
    
    print("\n" + "="*70)
    print("STEP 6: RAG PIPELINE DEMONSTRATION")
    print("Retrieval Augmented Generation")
    print("="*70 + "\n")
    
    # Part 1: What is RAG?
    print("PART 1: WHAT IS RAG?")
    print("-" * 70)
    print("""
RAG (Retrieval Augmented Generation) combines:
1. RETRIEVAL - Finding relevant information from your knowledge base
2. GENERATION - Using an LLM to create accurate answers

Why RAG?
✓ Reduces hallucination (LLM making up facts)
✓ Provides source citations
✓ Uses your specific data
✓ More accurate than pure LLM
✓ More flexible than pure search
""")
    
    # Part 2: The Complete Workflow
    print("\n" + "="*70)
    print("PART 2: THE COMPLETE RAG WORKFLOW")
    print("="*70 + "\n")
    
    print("User Question: 'How do I install Python?'")
    print()
    print("Step 1: RETRIEVAL")
    print("─" * 70)
    print("""
  1a. Embed the query
      Query → OpenAI Embedding API → [0.23, -0.45, 0.78, ...]
  
  1b. Search vector database
      Find chunks with similar embeddings (cosine similarity)
  
  1c. Return top-k results
      Top 5 chunks:
      - "To install Python, visit python.org..." (similarity: 0.87)
      - "Download the installer for your OS..." (similarity: 0.72)
      - "Verify installation with python --version" (similarity: 0.68)
      - "Python can be installed via package managers" (similarity: 0.65)
      - "After installing, set up your PATH" (similarity: 0.61)
""")
    
    print("Step 2: PROMPT PREPARATION")
    print("─" * 70)
    print("""
  Build a prompt with retrieved chunks as context:
  
  ┌─────────────────────────────────────────────────────────┐
  │ System: You are a helpful assistant that answers        │
  │         questions based strictly on provided context.   │
  │                                                          │
  │ User: Answer using ONLY the context below.              │
  │                                                          │
  │ CONTEXT:                                                │
  │ [Source 1: Getting Started]                             │
  │ To install Python, visit python.org and download...     │
  │                                                          │
  │ [Source 2: Installation Guide]                          │
  │ Download the installer for your operating system...     │
  │                                                          │
  │ [Source 3: Setup Instructions]                          │
  │ Verify installation with python --version...            │
  │                                                          │
  │ QUESTION: How do I install Python?                      │
  │                                                          │
  │ ANSWER:                                                 │
  └─────────────────────────────────────────────────────────┘
""")
    
    print("Step 3: GENERATION")
    print("─" * 70)
    print("""
  Send prompt to OpenAI Chat API:
  
  API Call:
    Model: gpt-3.5-turbo
    Temperature: 0 (deterministic, factual)
    Max Tokens: 500
  
  LLM Processing:
    - Reads the context carefully
    - Identifies relevant information
    - Formulates a clear answer
    - Cites sources when possible
  
  Generated Answer:
    "To install Python, visit the official website at python.org
     and download the installer for your operating system. After
     installation, you can verify it by typing 'python --version'
     in your terminal. (Sources: Getting Started, Installation Guide)"
""")
    
    print("Step 4: RESPONSE FORMATTING")
    print("─" * 70)
    print("""
  Format the final response:
  
  {
    'query': 'How do I install Python?',
    'answer': 'To install Python, visit the official website...',
    'sources': [
      {
        'title': 'Getting Started with Python',
        'url': 'https://docs.python.org/getting-started',
        'relevance_score': 0.8742
      },
      {
        'title': 'Installation Guide',
        'url': 'https://docs.python.org/install',
        'relevance_score': 0.7234
      }
    ],
    'retrieval_time': 0.084,
    'generation_time': 1.234,
    'total_time': 1.318,
    'success': True
  }
""")
    
    # Part 3: Comparison - Before and After RAG
    print("\n" + "="*70)
    print("PART 3: WITH AND WITHOUT RAG")
    print("="*70 + "\n")
    
    print("WITHOUT RAG (Pure LLM):")
    print("─" * 70)
    print("""
  User: "How do I install your company's software?"
  LLM: "I don't have specific information about that software.
        Generally, software is installed by downloading an installer
        and following the setup wizard..."
  
  Problems:
  ✗ Generic answer
  ✗ Not specific to your software
  ✗ No source citations
  ✗ May hallucinate steps
""")
    
    print("WITH RAG:")
    print("─" * 70)
    print("""
  User: "How do I install your company's software?"
  
  RAG Process:
  1. Retrieves: Installation guide from your documentation
  2. Generates: "To install our software, download the installer
                 from downloads.company.com, run setup.exe, and
                 follow the installation wizard. System requirements
                 include Windows 10 or later..."
  
  Benefits:
  ✓ Specific to your software
  ✓ Accurate steps from your docs
  ✓ Source citation included
  ✓ No hallucination
""")
    
    # Part 4: The Key Components
    print("\n" + "="*70)
    print("PART 4: KEY COMPONENTS")
    print("="*70 + "\n")
    
    print("Component 1: RETRIEVAL FUNCTION")
    print("─" * 70)
    print("""
  def retrieve(query, top_k=5):
      # 1. Embed query
      query_embedding = openai.embeddings.create(...)
      
      # 2. Search vector DB
      results = vector_db.search(query_embedding, top_k)
      
      # 3. Return chunks + metadata
      return {
          'documents': [...],
          'metadatas': [...],
          'similarities': [0.87, 0.72, ...]
      }
  
  Key Features:
  • Automatic query embedding
  • Fast similarity search (<100ms)
  • Returns relevance scores
  • Includes source metadata
""")
    
    print("Component 2: ANSWER GENERATION FUNCTION")
    print("─" * 70)
    print("""
  def generate_answer(query):
      # 1. Retrieve relevant chunks
      chunks = retrieve(query)
      
      # 2. Build prompt with context
      prompt = create_prompt(query, chunks)
      
      # 3. Call LLM
      response = openai.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": prompt}
          ],
          temperature=0
      )
      
      # 4. Format response
      return {
          'answer': response.content,
          'sources': extract_sources(chunks),
          'success': True
      }
  
  Key Features:
  • Uses retrieved context
  • Enforces "context only" rule
  • Returns source URLs
  • Tracks performance metrics
""")
    
    # Part 5: Real-World Example
    print("\n" + "="*70)
    print("PART 5: REAL-WORLD EXAMPLE")
    print("="*70 + "\n")
    
    print("Scenario: Customer Support Chatbot")
    print("─" * 70)
    print("""
Knowledge Base: 50 pages of product documentation
Vector Store: 250 chunks with embeddings

Customer Question:
"My device won't turn on. What should I do?"

RAG Workflow:
┌──────────────────────────────────────────────────────────┐
│ 1. RETRIEVE (0.08s)                                      │
│    Top chunks:                                           │
│    • Troubleshooting Guide > Won't Power On (0.89)       │
│    • Common Issues > Power Problems (0.76)               │
│    • Getting Started > Initial Setup (0.65)              │
└──────────────────────────────────────────────────────────┘
               ↓
┌──────────────────────────────────────────────────────────┐
│ 2. GENERATE (1.2s)                                       │
│    LLM reads context and creates answer                  │
└──────────────────────────────────────────────────────────┘
               ↓
┌──────────────────────────────────────────────────────────┐
│ 3. RESPOND (Total: 1.28s)                                │
│                                                          │
│ "If your device won't turn on, try these steps:         │
│  1. Check if the battery is charged                     │
│  2. Hold the power button for 10 seconds                │
│  3. Try a different charging cable                      │
│  4. If still not working, contact support               │
│                                                          │
│ Sources:                                                 │
│ - Troubleshooting Guide (docs.company.com/troubleshoot) │
│ - Common Issues (docs.company.com/faq)"                 │
└──────────────────────────────────────────────────────────┘

Result:
✓ Accurate solution from documentation
✓ Step-by-step instructions
✓ Sources for further reading
✓ Fast response (<2 seconds)
""")
    
    # Part 6: Advantages
    print("\n" + "="*70)
    print("PART 6: WHY RAG IS POWERFUL")
    print("="*70 + "\n")
    
    print("""
✓ Accuracy
  Uses your actual documentation, not LLM's training data
  
✓ Traceability
  Every answer cites its sources
  
✓ Freshness
  Update docs → update knowledge base → new answers
  
✓ Privacy
  Your data stays in your vector database
  
✓ Cost-Effective
  No need to fine-tune expensive models
  
✓ Transparency
  Can inspect which chunks were used
  
✓ Controllability
  Limit answers to specific domains
""")
    
    # Part 7: Architecture Diagram
    print("\n" + "="*70)
    print("PART 7: COMPLETE ARCHITECTURE")
    print("="*70 + "\n")
    
    print("""
┌─────────────────────────────────────────────────────────────────┐
│                        RAG SYSTEM                               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐
│ User Query  │  "How do I install Python?"
└──────┬──────┘
       │
       ↓
┌────────────────────────────────────────────┐
│  RETRIEVAL LAYER                           │
│  ┌──────────────────────────────────────┐  │
│  │ 1. Embed Query                       │  │
│  │    OpenAI Embeddings API             │  │
│  └────────────┬─────────────────────────┘  │
│               ↓                            │
│  ┌──────────────────────────────────────┐  │
│  │ 2. Vector Search                     │  │
│  │    ChromaDB (Cosine Similarity)      │  │
│  └────────────┬─────────────────────────┘  │
│               ↓                            │
│  ┌──────────────────────────────────────┐  │
│  │ 3. Return Top-K Chunks               │  │
│  │    + Metadata + Relevance Scores     │  │
│  └────────────┬─────────────────────────┘  │
└───────────────┼────────────────────────────┘
                ↓
┌────────────────────────────────────────────┐
│  GENERATION LAYER                          │
│  ┌──────────────────────────────────────┐  │
│  │ 1. Build Prompt                      │  │
│  │    Context + Instructions + Query    │  │
│  └────────────┬─────────────────────────┘  │
│               ↓                            │
│  ┌──────────────────────────────────────┐  │
│  │ 2. Call LLM                          │  │
│  │    GPT-3.5-turbo (temp=0)            │  │
│  └────────────┬─────────────────────────┘  │
│               ↓                            │
│  ┌──────────────────────────────────────┐  │
│  │ 3. Extract Answer                    │  │
│  │    + Compile Sources                 │  │
│  └────────────┬─────────────────────────┘  │
└───────────────┼────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  RESPONSE                               │
│  {                                      │
│    answer: "To install Python...",      │
│    sources: [{title, url, score}],      │
│    time: 1.3s                           │
│  }                                      │
└─────────────────────────────────────────┘
""")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70 + "\n")
    
    print("""
RAG Pipeline = RETRIEVAL + GENERATION

✓ Step 1: Retrieve relevant chunks from vector database
✓ Step 2: Build prompt with chunks as context
✓ Step 3: Generate answer using LLM
✓ Step 4: Return answer with source citations

Benefits:
• Accurate answers from your data
• Source attribution
• Fast (<2s typical)
• No model fine-tuning needed
• Easy to update knowledge

Use Cases:
• Customer support chatbots
• Internal knowledge base search
• Documentation Q&A
• Technical support systems
• FAQ automation
""")
    
    print("="*70)
    print("TO TEST THIS IN YOUR PROJECT:")
    print("="*70)
    print()
    print("  python test_rag.py")
    print()
    print("="*70 + "\n")


if __name__ == "__main__":
    demo_rag()
