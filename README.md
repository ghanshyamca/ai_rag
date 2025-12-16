# RAG Q&A Support Bot

A Question & Answer support bot built with Retrieval Augmented Generation (RAG) that crawls websites, generates embeddings, and answers questions based only on the crawled content.

## 🚀 Features

- **Web Crawling**: Automatically crawls website pages and extracts clean text content
- **Text Processing**: Cleans and chunks text with configurable overlap for optimal context
- **Vector Embeddings**: Generates embeddings using OpenAI's embedding models
- **Vector Database**: Stores embeddings in ChromaDB for efficient similarity search
- **RAG Pipeline**: Retrieves relevant context and generates accurate answers using GPT models
- **REST API**: FastAPI-based endpoint for easy integration
- **Configurable**: Environment-based configuration for flexibility

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

### Step 1: Build the Knowledge Base

First, crawl the website and build the vector database:

```bash
python main.py
```

This will:
1. Crawl pages from the `TARGET_URL`
2. Clean and chunk the text
3. Generate embeddings for each chunk
4. Store embeddings in ChromaDB

To force a complete rebuild:
```bash
python main.py --force
```

### Step 2: Start the API Server

```bash
python api.py
```

Or using uvicorn directly:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### Step 3: Test the API

#### Using the Interactive Docs

Navigate to `http://localhost:8000/docs` for the interactive Swagger UI.

#### Using curl

**Health Check**:
```bash
curl http://localhost:8000/health
```

**Ask a Question**:
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is Python used for?\"}"
```

**Get Statistics**:
```bash
curl http://localhost:8000/stats
```

#### Using PowerShell

**Ask a Question**:
```powershell
$headers = @{"Content-Type"="application/json"}
$body = @{question="What is Python used for?"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method Post -Headers $headers -Body $body
```

## 📡 API Endpoints

### `GET /`
Root endpoint with API information.

### `GET /health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "vector_store_count": 245
}
```

### `POST /ask`
Ask a question and get an answer.

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
  "question": "How do I install Python?",
  "answer": "To install Python, you can download it from python.org...",
  "sources": [
    {
      "title": "Python Setup and Usage",
      "url": "https://docs.python.org/3/using/index.html",
      "relevance_score": 0.89
    }
  ],
  "success": true,
  "num_contexts_used": 5
}
```

### `GET /stats`
Get knowledge base statistics.

**Response**:
```json
{
  "total_documents": 245,
  "collection_name": "website_docs",
  "embedding_model": "text-embedding-ada-002",
  "llm_model": "gpt-3.5-turbo"
}
```

## 🧪 Testing with Postman

1. **Import Collection**: Create a new collection in Postman

2. **Health Check**:
   - Method: GET
   - URL: `http://localhost:8000/health`

3. **Ask Question**:
   - Method: POST
   - URL: `http://localhost:8000/ask`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):
     ```json
     {
       "question": "What is Python?",
       "top_k": 5
     }
     ```

4. **Get Stats**:
   - Method: GET
   - URL: `http://localhost:8000/stats`

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
├── api.py                  # FastAPI application
├── config.py              # Configuration management
├── crawler.py             # Web crawler implementation
├── text_processor.py      # Text cleaning and chunking
├── vector_store.py        # Vector database operations
├── rag_pipeline.py        # RAG workflow implementation
├── main.py                # Knowledge base builder
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment file
├── .gitignore            # Git ignore rules
└── README.md             # This file
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

## 🚀 Advanced Usage

### Test Individual Components

**Test Crawler**:
```bash
python crawler.py
```

**Test Text Processor**:
```bash
python text_processor.py
```

**Test Vector Store**:
```bash
python vector_store.py
```

**Test RAG Pipeline**:
```bash
python rag_pipeline.py
```

### Custom Crawling

Modify `config.py` or `.env` to crawl different websites:

```env
TARGET_URL=https://your-website.com
MAX_PAGES=100
CRAWL_DELAY=2.0
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
