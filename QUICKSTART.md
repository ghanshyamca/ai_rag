# Quick Start Guide - RAG Q&A Support Bot

## 🚀 Quick Setup (5 minutes)

### Step 1: Environment Setup

1. **Create and activate virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```powershell
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

### Step 2: Build Knowledge Base

Run the crawler to build your knowledge base:

```powershell
python main.py
```

This will:
- ✅ Crawl the target website (default: Python docs)
- ✅ Process and chunk the text
- ✅ Generate embeddings
- ✅ Store in vector database

**Expected output**:
```
Crawled 50 pages
Processed 50 documents into 245 chunks
Knowledge base built successfully!
```

⏱️ **Time**: 5-10 minutes (depending on API speed)

### Step 3: Start the API Server

```powershell
python api.py
```

The API will start at `http://localhost:8000`

### Step 4: Test the API

#### Option A: Interactive Swagger UI
Open your browser: `http://localhost:8000/docs`

#### Option B: Using PowerShell Script
```powershell
.\test_api.ps1
```

#### Option C: Using Python Script
```powershell
python test_api.py
```

#### Option D: Manual curl/PowerShell Commands

**PowerShell**:
```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Ask a question
$body = @{question="What is Python used for?"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method Post -Body $body -ContentType "application/json"
```

**curl** (Git Bash or WSL):
```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Python used for?"}'
```

## 📝 Example Questions to Try

After building the knowledge base with Python documentation:

1. "What is Python used for?"
2. "How do I install Python?"
3. "What are Python's main features?"
4. "How do I create a virtual environment?"
5. "What is pip?"
6. "How do I import modules in Python?"

## 🎯 Expected Response Format

```json
{
  "question": "What is Python used for?",
  "answer": "Python is used for...",
  "sources": [
    {
      "title": "What is Python?",
      "url": "https://docs.python.org/3/...",
      "relevance_score": 0.89
    }
  ],
  "success": true,
  "num_contexts_used": 5
}
```

## 🔧 Troubleshooting

### Issue: "Vector store is empty"
**Solution**: Run `python main.py` first to build the knowledge base

### Issue: "OpenAI API error"
**Solution**: 
- Check your API key in `.env`
- Verify you have credits: https://platform.openai.com/account/usage

### Issue: "Module not found"
**Solution**: 
- Activate virtual environment: `.\venv\Scripts\activate`
- Reinstall: `pip install -r requirements.txt`

### Issue: "Connection refused"
**Solution**: Make sure API server is running: `python api.py`

## 🔄 Crawling Your Own Website

Edit `.env`:
```
TARGET_URL=https://your-website.com
MAX_PAGES=100
CRAWL_DELAY=2.0
```

Then rebuild:
```powershell
python main.py --force
```

## 📊 Cost Estimation

**For 50 pages (default)**:
- Embeddings: ~$0.10 (one-time)
- Queries: ~$0.002 per question

**Total for initial setup + 100 questions**: ~$0.30

## ✅ Verification Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list` shows packages)
- [ ] `.env` file created with valid API key
- [ ] Knowledge base built (`chroma_db/` folder exists)
- [ ] API server running (visit `http://localhost:8000/docs`)
- [ ] Health check returns `"status": "healthy"`
- [ ] Test question returns an answer

## 🎓 Understanding the Code

### Main Components:

1. **crawler.py** - Scrapes web pages
2. **text_processor.py** - Cleans and chunks text
3. **vector_store.py** - Manages embeddings and search
4. **rag_pipeline.py** - Combines retrieval + generation
5. **api.py** - REST API endpoints
6. **main.py** - Orchestrates the pipeline

### Data Flow:

```
Web Pages → Crawler → Text Chunks → Embeddings → Vector DB
                                                      ↓
User Question → Embedding → Similarity Search → Relevant Chunks
                                                      ↓
                                    LLM + Context → Answer
```

## 📦 What Gets Created

```
ai_rag/
├── chroma_db/          # Vector database (auto-created)
├── data/               # Crawled data cache (auto-created)
│   └── crawled_data.json
└── venv/               # Virtual environment
```

## 🚀 Next Steps

1. **Customize crawling**: Change `TARGET_URL` in `.env`
2. **Adjust chunk size**: Modify `CHUNK_SIZE` for better context
3. **Try different models**: Change `LLM_MODEL` to `gpt-4`
4. **Integrate**: Use the API in your application

## 📚 Additional Resources

- OpenAI API Docs: https://platform.openai.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- ChromaDB Docs: https://docs.trychroma.com

## 🆘 Getting Help

If you encounter issues:
1. Check the error message carefully
2. Review the troubleshooting section above
3. Check the logs in the terminal
4. Verify all prerequisites are met

---

**Happy building! 🎉**
