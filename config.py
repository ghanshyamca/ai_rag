"""
Configuration settings for the RAG Q&A Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Crawling Configuration
TARGET_URL = os.getenv("TARGET_URL", "https://docs.python.org/3/")
MAX_PAGES = int(os.getenv("MAX_PAGES", "50"))
CRAWL_DELAY = float(os.getenv("CRAWL_DELAY", "1.0"))  # Delay between requests in seconds

# Text Processing Configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Vector Database Configuration
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "website_docs")

# Embedding Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

# LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))

# Retrieval Configuration
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
