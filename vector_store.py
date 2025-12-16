"""
Vector Store Module
Handles embedding generation and vector database operations
"""
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    """
    Manages embeddings and vector database operations using ChromaDB
    """
    
    def __init__(
        self,
        persist_directory: str,
        collection_name: str,
        openai_api_key: str,
        embedding_model: str = "text-embedding-ada-002"
    ):
        """
        Initialize the vector store
        
        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection
            openai_api_key: OpenAI API key
            embedding_model: OpenAI embedding model to use
        """
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.embedding_model = embedding_model
        
        # Initialize ChromaDB
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Initialized vector store with collection: {collection_name}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a text using OpenAI API
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Truncate text if too long (max 8191 tokens for ada-002)
            max_chars = 8000  # Conservative limit
            if len(text) > max_chars:
                logger.warning(f"Text truncated from {len(text)} to {max_chars} chars")
                text = text[:max_chars]
            
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Truncate texts if too long
            max_chars = 8000
            truncated_texts = []
            for text in texts:
                if len(text) > max_chars:
                    truncated_texts.append(text[:max_chars])
                else:
                    truncated_texts.append(text)
            
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=truncated_texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    def add_documents(self, chunks: List[Dict[str, str]], batch_size: int = 100):
        """
        Add documents to the vector store
        
        Args:
            chunks: List of chunk dictionaries with 'text' and metadata
            batch_size: Number of documents to process at once
        """
        if not chunks:
            logger.warning("No chunks to add")
            return
        
        total_chunks = len(chunks)
        logger.info(f"\n{'='*60}")
        logger.info(f"ADDING DOCUMENTS TO VECTOR STORE")
        logger.info(f"{'='*60}")
        logger.info(f"Total chunks: {total_chunks}")
        logger.info(f"Batch size: {batch_size}")
        logger.info(f"Embedding model: {self.embedding_model}")
        logger.info(f"{'='*60}\n")
        
        import time
        start_time = time.time()
        total_batches = (total_chunks - 1) // batch_size + 1
        
        for i in range(0, total_chunks, batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            # Prepare data
            texts = [chunk['text'] for chunk in batch]
            ids = [f"{chunk['url']}_{chunk['chunk_id']}" for chunk in batch]
            metadatas = [
                {
                    'url': chunk['url'],
                    'title': chunk['title'],
                    'chunk_id': str(chunk['chunk_id']),
                    'total_chunks': str(chunk['total_chunks']),
                    'char_count': str(chunk.get('char_count', len(chunk['text'])))
                }
                for chunk in batch
            ]
            
            # Generate embeddings
            logger.info(f"[Batch {batch_num}/{total_batches}] Generating embeddings for {len(batch)} chunks...")
            batch_start = time.time()
            
            try:
                embeddings = self.generate_embeddings_batch(texts)
                batch_time = time.time() - batch_start
                
                # Add to collection
                self.collection.add(
                    embeddings=embeddings,
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                
                processed = min(i + batch_size, total_chunks)
                logger.info(f"[Batch {batch_num}/{total_batches}] ✓ Added {len(batch)} chunks in {batch_time:.2f}s (Progress: {processed}/{total_chunks})")
                
            except Exception as e:
                logger.error(f"[Batch {batch_num}/{total_batches}] ✗ Error: {str(e)}")
                raise
        
        total_time = time.time() - start_time
        logger.info(f"\n{'='*60}")
        logger.info(f"EMBEDDING GENERATION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Total chunks processed: {total_chunks}")
        logger.info(f"Total time: {total_time:.2f}s")
        logger.info(f"Average time per chunk: {total_time/total_chunks:.3f}s")
        logger.info(f"Collection size: {self.get_collection_count()}")
        logger.info(f"{'='*60}\n")
    
    def search(self, query: str, top_k: int = 5) -> Dict:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            Dictionary with results including documents, metadata, and similarity scores
        """
        try:
            # Generate query embedding
            logger.debug(f"Generating embedding for query: {query[:100]}...")
            query_embedding = self.generate_embedding(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results with similarity scores (convert distance to similarity)
            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            distances = results['distances'][0] if results['distances'] else []
            
            # Convert cosine distance to similarity score (1 - distance)
            similarities = [1 - dist for dist in distances]
            
            formatted_results = {
                'query': query,
                'documents': documents,
                'metadatas': metadatas,
                'distances': distances,
                'similarities': similarities,
                'count': len(documents)
            }
            
            logger.debug(f"Found {len(documents)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            raise
    
    def get_collection_count(self) -> int:
        """
        Get the number of documents in the collection
        
        Returns:
            Number of documents
        """
        return self.collection.count()
    
    def clear_collection(self):
        """
        Clear all documents from the collection
        """
        # Delete and recreate collection
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Cleared collection")


if __name__ == "__main__":
    # Test the vector store
    from config import (
        CHROMA_PERSIST_DIR,
        COLLECTION_NAME,
        OPENAI_API_KEY,
        EMBEDDING_MODEL,
        TOP_K_RESULTS
    )
    
    # Initialize vector store
    vector_store = VectorStore(
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name=COLLECTION_NAME,
        openai_api_key=OPENAI_API_KEY,
        embedding_model=EMBEDDING_MODEL
    )
    
    print(f"\nCollection count: {vector_store.get_collection_count()}")
    
    # Test search if collection has data
    if vector_store.get_collection_count() > 0:
        test_query = "How do I install Python?"
        results = vector_store.search(test_query, top_k=TOP_K_RESULTS)
        
        print(f"\nSearch results for: '{test_query}'")
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'],
            results['metadatas'],
            results['distances']
        )):
            print(f"\nResult {i+1} (distance: {distance:.4f}):")
            print(f"Title: {metadata['title']}")
            print(f"URL: {metadata['url']}")
            print(f"Content: {doc[:200]}...")
