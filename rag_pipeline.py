"""
RAG Pipeline Module
Implements the complete Retrieval Augmented Generation workflow
"""
from openai import OpenAI
from vector_store import VectorStore
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Complete RAG pipeline for question answering
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        openai_api_key: str,
        llm_model: str = "gpt-3.5-turbo",
        temperature: float = 0,
        max_tokens: int = 500,
        top_k: int = 5
    ):
        """
        Initialize the RAG pipeline
        
        Args:
            vector_store: VectorStore instance
            openai_api_key: OpenAI API key
            llm_model: LLM model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens in response
            top_k: Number of documents to retrieve
        """
        self.vector_store = vector_store
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.llm_model = llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_k = top_k
    
    def create_prompt(self, query: str, context_docs: List[str]) -> str:
        """
        Create a prompt with context for the LLM
        
        Args:
            query: User question
            context_docs: List of relevant document chunks
            
        Returns:
            Formatted prompt
        """
        context = "\n\n".join([f"Context {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])
        
        prompt = f"""You are a helpful assistant that answers questions based only on the provided context.
If the answer cannot be found in the context, say "I don't have enough information to answer that question based on the available documentation."

Context:
{context}

Question: {query}

Answer:"""
        
        return prompt
    
    def generate_answer(self, query: str) -> Dict:
        """
        Generate an answer using RAG
        
        Args:
            query: User question
            
        Returns:
            Dictionary with answer and sources
        """
        try:
            # Step 1: Retrieve relevant documents
            logger.info(f"Processing query: {query}")
            search_results = self.vector_store.search(query, top_k=self.top_k)
            
            if not search_results['documents']:
                return {
                    'answer': "I don't have any information to answer that question.",
                    'sources': [],
                    'success': False
                }
            
            # Step 2: Create prompt with context
            prompt = self.create_prompt(query, search_results['documents'])
            
            # Step 3: Generate answer using LLM
            logger.info("Generating answer with LLM")
            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            answer = response.choices[0].message.content
            
            # Step 4: Prepare sources
            sources = []
            for metadata, distance in zip(search_results['metadatas'], search_results['distances']):
                sources.append({
                    'title': metadata['title'],
                    'url': metadata['url'],
                    'relevance_score': 1 - distance  # Convert distance to similarity
                })
            
            # Remove duplicate URLs
            seen_urls = set()
            unique_sources = []
            for source in sources:
                if source['url'] not in seen_urls:
                    seen_urls.add(source['url'])
                    unique_sources.append(source)
            
            return {
                'answer': answer,
                'sources': unique_sources,
                'success': True,
                'num_contexts_used': len(search_results['documents'])
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {
                'answer': f"An error occurred while processing your question: {str(e)}",
                'sources': [],
                'success': False
            }


if __name__ == "__main__":
    # Test the RAG pipeline
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
    
    # Initialize vector store
    vector_store = VectorStore(
        persist_directory=CHROMA_PERSIST_DIR,
        collection_name=COLLECTION_NAME,
        openai_api_key=OPENAI_API_KEY,
        embedding_model=EMBEDDING_MODEL
    )
    
    # Initialize RAG pipeline
    rag = RAGPipeline(
        vector_store=vector_store,
        openai_api_key=OPENAI_API_KEY,
        llm_model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_k=TOP_K_RESULTS
    )
    
    # Test query
    test_query = "What is Python used for?"
    result = rag.generate_answer(test_query)
    
    print(f"\nQuery: {test_query}")
    print(f"\nAnswer: {result['answer']}")
    print(f"\nSources:")
    for i, source in enumerate(result['sources']):
        print(f"{i+1}. {source['title']} ({source['url']}) - Relevance: {source['relevance_score']:.2f}")
