# RAG Q&A Support Bot

A Question & Answer support bot built with Retrieval Augmented Generation (RAG) that crawls websites, generates embeddings, and answers questions based only on the crawled content.

## 🚀 Features

- **Web Crawling**: Automatically crawls website pages and extracts clean text content (POST /crawl)
- **Text Processing**: Cleans and chunks text with configurable overlap for optimal context
- **Vector Embeddings**: Generates embeddings using OpenAI's text-embedding-ada-002
- **Vector Database**: Stores embeddings in ChromaDB for efficient similarity search
- **RAG Pipeline**: Retrieves relevant context and generates accurate answers using GPT-3.5-turbo
- **REST API**: Full FastAPI server with crawling and Q&A endpoints
- **Configurable**: Environment-based configuration for flexibility
- **Well-Tested**: Comprehensive test suites and demo scripts

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for web crawling

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd ai_rag
```

2. **Create a virtual environment**:
```bash
python -m venv venv
```

3. **Activate the virtual environment**:
- Windows:
  ```bash
  .\venv\Scripts\activate
  ```
- Linux/Mac:
  ```bash
  source venv/bin/activate
  ```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

5. **Set up environment variables**:
```bash
cp .env.example .env
```

Edit `.env` file and add your configuration:
```env
OPENAI_API_KEY=your_openai_api_key_here
TARGET_URL=https://docs.python.org/3/
MAX_PAGES=50
```

## 📖 Usage

### Quick Start (All-in-One API)

**Step 1: Start the API Server**
```bash
python api.py
```

The API will be available at `http://localhost:8000`
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Step 2: Build Knowledge Base via API**
```bash
curl -X POST "http://localhost:8000/crawl" \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "https://docs.python.org/3/",
    "max_pages": 10,
    "crawl_delay": 1.0
  }'
```

**Step 3: Ask Questions via API**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I install Python?",
    "top_k": 5
  }'
```

### Alternative: CLI-based Knowledge Building

If you prefer to build the knowledge base via command line:

```bash
# Build knowledge base
python main.py

# Then start API server
python api.py
```

### Testing

**PowerShell**:
```powershell
.\test_api.ps1
```

**Python**:
```bash
python demo_api.py
```

**Postman**: Import `postman_collection.json`

## 📡 API Endpoints

### `POST /crawl` ⭐
Crawl a website and build the knowledge base.

**Request**:
```json
{
  "base_url": "https://docs.python.org/3/",
  "max_pages": 10,
  "crawl_delay": 1.0
}
```

**Response**:
```json
{
  "success": true,
  "message": "Crawling completed successfully...",
  "pages_crawled": 10,
  "chunks_created": 87,
  "embeddings_generated": 87,
  "total_time": 45.23
}
```

**Pipeline**: Crawl → Extract → Chunk → Embed → Index

---

### `POST /ask` ⭐
Ask a question using RAG (Retrieval-Augmented Generation).

**Request**:
```json
{
  "question": "How do I install Python?",
  "top_k": 5
}
```

**Response**:
```json
{
  "success": true,
  "answer": "To install Python, visit python.org and download...",
  "sources": [
    {
      "title": "Python Setup and Usage",
      "url": "https://docs.python.org/3/using/index.html",
      "relevance_score": 0.8542
    }
  ]
}
```

**Pipeline**: Retrieve → Generate → Respond

---

### `GET /health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "vector_store_count": 87,
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

---

### `GET /stats`
Get detailed statistics.

**Response**:
```json
{
  "total_documents": 87,
  "collection_name": "rag_documents",
  "embedding_model": "text-embedding-ada-002",
  "embedding_dimensions": 1536,
  "llm_model": "gpt-3.5-turbo",
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "is_crawling": false,
  "last_crawl": "2024-01-15T09:25:30.456789"
}
```

---

### `GET /crawl/status`
Check if a crawl is in progress.

**Response**:
```json
{
  "is_crawling": false,
  "last_crawl_time": "2024-01-15T09:25:30.456789",
  "last_result": {
    "success": true,
    "pages_crawled": 10,
    "chunks_created": 87
  }
}
```

---

### `GET /`
Root endpoint with API information.
---

## 🧪 Testing

### Test Scripts

**PowerShell**:
```powershell
.\test_api.ps1
```

**Python Demo**:
```bash
python demo_api.py
```

**Postman**: Import `postman_collection.json`

### Manual Testing with curl

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Crawl Website**:
```bash
curl -X POST "http://localhost:8000/crawl" \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "https://docs.python.org/3/",
    "max_pages": 5,
    "crawl_delay": 1.0
  }'
```

**Ask Question**:
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I install Python?",
    "top_k": 5
  }'
```

**Check Stats**:
```bash
curl http://localhost:8000/stats
```

## ⚙️ Configuration

Edit the `.env` file to customize behavior:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `TARGET_URL` | Website to crawl | `https://docs.python.org/3/` |
| `MAX_PAGES` | Maximum pages to crawl | `50` |
| `CRAWL_DELAY` | Delay between requests (seconds) | `1.0` |
| `CHUNK_SIZE` | Text chunk size in characters | `1000` |
| `CHUNK_OVERLAP` | Overlap between chunks | `200` |
| `EMBEDDING_MODEL` | OpenAI embedding model | `text-embedding-ada-002` |
| `LLM_MODEL` | OpenAI chat model | `gpt-3.5-turbo` |
| `TOP_K_RESULTS` | Number of contexts to retrieve | `5` |
| `API_PORT` | API server port | `8000` |

## 📁 Project Structure

```
ai_rag/
├── api.py                      # FastAPI REST API server
├── config.py                   # Configuration management
├── crawler.py                  # Web crawler implementation
├── text_processor.py           # Text cleaning and chunking
├── vector_store.py             # Vector database operations
├── rag_pipeline.py             # RAG workflow (retrieve + generate)
├── main.py                     # CLI knowledge base builder
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── Test Scripts:
│   ├── test_api.ps1           # PowerShell API tests
│   ├── test_api.py            # Python API tests (legacy)
│   ├── demo_api.py            # Interactive API demo
│   ├── demo_rag.py            # RAG pipeline demo
│   ├── demo_chunking.py       # Chunking demo
│   ├── demo_embeddings.py     # Embeddings demo
│   ├── test_rag.py            # RAG tests
│   ├── test_chunking.py       # Chunking tests
│   └── test_embeddings.py     # Embeddings tests
│
├── Documentation:
│   ├── STEP5_EMBEDDINGS_COMPLETE.md      # Step 5 docs
│   ├── STEP5_QUICK_REFERENCE.txt         # Step 5 reference
│   ├── STEP5_COMPLETION_SUMMARY.md       # Step 5 summary
│   ├── STEP6_RAG_COMPLETE.md             # Step 6 docs
│   ├── STEP6_QUICK_REFERENCE.txt         # Step 6 reference
│   ├── STEP6_COMPLETION_SUMMARY.md       # Step 6 summary
│   ├── STEP7_API_COMPLETE.md             # Step 7 docs (API)
│   ├── STEP7_QUICK_REFERENCE.txt         # Step 7 reference
│   ├── STEP7_COMPLETION_SUMMARY.md       # Step 7 summary
│   ├── PROJECT_SUMMARY.md                # Project overview
│   ├── QUICKSTART.md                     # Quick start guide
│   └── SUBMISSION.md                     # Submission checklist
│
└── postman_collection.json     # Postman API collection
```

## 🔄 RAG Workflow

1. **Crawling**: Web pages are crawled and text is extracted
2. **Chunking**: Text is split into overlapping chunks
3. **Embedding**: Each chunk is converted to a vector embedding
4. **Storage**: Embeddings are stored in ChromaDB
5. **Retrieval**: User question is embedded and similar chunks are retrieved
6. **Generation**: LLM generates answer using retrieved context

## 🐛 Troubleshooting

**Vector store is empty**:
- Run `python main.py` to build the knowledge base first

**OpenAI API errors**:
- Verify your API key in `.env`
- Check your API quota and billing

**Crawling issues**:
- Check internet connection
- Verify the target URL is accessible
- Adjust `CRAWL_DELAY` if getting rate limited

**Import errors**:
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## 📝 Example Questions

Try these questions after crawling Python documentation:

- "What is Python used for?"
- "How do I install Python?"
- "What are Python's main features?"
- "How do I create a virtual environment?"
- "What is pip?"
- "How do I write a function in Python?"
- "What are decorators?"

## 📚 Documentation

### Complete Step-by-Step Guides
- **STEP5_EMBEDDINGS_COMPLETE.md** - Embeddings and vector storage
- **STEP6_RAG_COMPLETE.md** - Retrieval and answer generation  
- **STEP7_API_COMPLETE.md** - REST API implementation

### Quick References (ASCII Art)
- **STEP5_QUICK_REFERENCE.txt** - Embeddings quick ref
- **STEP6_QUICK_REFERENCE.txt** - RAG quick ref
- **STEP7_QUICK_REFERENCE.txt** - API quick ref

### Interactive Demos
- **demo_embeddings.py** - Embeddings demo
- **demo_chunking.py** - Text chunking demo
- **demo_rag.py** - RAG pipeline demo
- **demo_api.py** - API usage demo

### Test Suites
- **test_embeddings.py** - Embeddings tests
- **test_chunking.py** - Chunking tests
- **test_rag.py** - RAG pipeline tests (5 questions)
- **test_api.ps1** - API endpoint tests

## 🚀 Advanced Usage

### Test Individual Components

**Test Embeddings**:
```bash
python test_embeddings.py
```

**Test Chunking**:
```bash
python test_chunking.py
```

**Test RAG Pipeline**:
```bash
python test_rag.py
```

**Test API**:
```powershell
.\test_api.ps1
```

### Run Interactive Demos

**Embeddings Demo**:
```bash
python demo_embeddings.py
```

**Chunking Demo**:
```bash
python demo_chunking.py
```

**RAG Demo**:
```bash
python demo_rag.py
```

**API Demo**:
```bash
python demo_api.py
```

### Custom Crawling via API

```bash
curl -X POST "http://localhost:8000/crawl" \
  -H "Content-Type: application/json" \
  -d '{
    "base_url": "https://your-website.com",
    "max_pages": 20,
    "crawl_delay": 1.5
  }'
```

### Custom Crawling via CLI

Modify `.env`:
```env
TARGET_URL=https://your-website.com
MAX_PAGES=100
CRAWL_DELAY=2.0
```

Then run:
```bash
python main.py --force
```

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions, please open an issue on the GitHub repository.

---

**Built with ❤️ using Python, FastAPI, OpenAI, and ChromaDB**
