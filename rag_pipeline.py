"""
RAG Pipeline Module
Implements the complete Retrieval Augmented Generation workflow

Step 6: Retrieval and Answer Generation
- Retrieval: Embeds query, fetches relevant chunks
- Answer Generation: Uses LLM with retrieved context
"""
from openai import OpenAI
from vector_store import VectorStore
from typing import Dict, List, Optional
import logging
import time

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
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> Dict:
        """
        STEP 6 - RETRIEVAL FUNCTION
        
        Retrieves relevant chunks for a user query:
        1. Embeds the user query using OpenAI embeddings
        2. Fetches top-k relevant chunks from vector store
        3. Returns chunks with metadata and relevance scores
        
        Args:
            query: User question
            top_k: Number of results to return (overrides default)
            
        Returns:
            Dictionary with:
            - documents: List of text chunks
            - metadatas: List of metadata dicts (url, title, etc.)
            - similarities: List of relevance scores (0-1)
            - query: Original query
            - retrieval_time: Time taken for retrieval
        """
        start_time = time.time()
        k = top_k if top_k is not None else self.top_k
        
        logger.info(f"Retrieving top {k} chunks for query: '{query[:50]}...'")
        
        try:
            # Use vector store's search method (which embeds query automatically)
            results = self.vector_store.search(query, top_k=k)
            
            retrieval_time = time.time() - start_time
            
            # Log retrieval results
            if results['count'] > 0:
                avg_similarity = sum(results['similarities']) / len(results['similarities'])
                logger.info(f"Retrieved {results['count']} chunks in {retrieval_time:.3f}s")
                logger.info(f"Average similarity: {avg_similarity:.3f}")
                logger.debug(f"Top result similarity: {results['similarities'][0]:.3f}")
            else:
                logger.warning("No results found for query")
            
            # Add retrieval time to results
            results['retrieval_time'] = retrieval_time
            
            return results
            
        except Exception as e:
            logger.error(f"Error during retrieval: {str(e)}")
            return {
                'query': query,
                'documents': [],
                'metadatas': [],
                'similarities': [],
                'distances': [],
                'count': 0,
                'retrieval_time': time.time() - start_time,
                'error': str(e)
            }
    
    def create_prompt(self, query: str, context_docs: List[str], metadatas: List[Dict]) -> str:
        """
        Create a prompt with context for the LLM
        
        Args:
            query: User question
            context_docs: List of relevant document chunks
            metadatas: List of metadata for each chunk
            
        Returns:
            Formatted prompt
        """
        # Build context with source attribution
        context_parts = []
        for i, (doc, meta) in enumerate(zip(context_docs, metadatas), 1):
            context_parts.append(
                f"[Source {i}: {meta['title']}]\n{doc}"
            )
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided context.

IMPORTANT INSTRUCTIONS:
- Answer the question using ONLY the information from the context below
- If the answer cannot be found in the context, respond with: "I don't have enough information to answer that question based on the available documentation."
- Be concise but complete
- Cite which sources you used by mentioning the source numbers (e.g., "According to Source 1...")
- Do not make up information or use external knowledge

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""
        
        return prompt
    
    def generate_answer(self, query: str, top_k: Optional[int] = None) -> Dict:
        """
        STEP 6 - ANSWER GENERATION FUNCTION
        
        Complete RAG workflow:
        1. Retrieve relevant chunks using retrieve()
        2. Prepare prompt with retrieved context
        3. Call language model to generate answer
        4. Instruct LLM to answer only from given context
        5. Return answer with source URLs
        
        Args:
            query: User question
            top_k: Number of chunks to retrieve (overrides default)
            
        Returns:
            Dictionary with:
            - query: Original question
            - answer: Generated answer
            - sources: List of source URLs with titles and relevance
            - retrieval_time: Time for retrieval
            - generation_time: Time for LLM generation
            - total_time: Total processing time
            - success: Whether generation succeeded
        """
        start_time = time.time()
        
        try:
            # Step 1: Retrieve relevant documents
            logger.info(f"Processing query: '{query}'")
            retrieval_results = self.retrieve(query, top_k=top_k)
            
            if retrieval_results['count'] == 0:
                return {
                    'query': query,
                    'answer': "I don't have any information to answer that question.",
                    'sources': [],
                    'retrieval_time': retrieval_results.get('retrieval_time', 0),
                    'generation_time': 0,
                    'total_time': time.time() - start_time,
                    'success': False,
                    'error': 'No relevant documents found'
                }
            
            # Step 2: Create prompt with context
            prompt = self.create_prompt(
                query, 
                retrieval_results['documents'],
                retrieval_results['metadatas']
            )
            
            # Log prompt size for debugging
            logger.debug(f"Prompt size: {len(prompt)} characters")
            
            # Step 3: Generate answer using LLM
            logger.info(f"Generating answer with {self.llm_model}")
            gen_start = time.time()
            
            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant that answers questions based strictly on provided context. Never use external knowledge."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            generation_time = time.time() - gen_start
            answer = response.choices[0].message.content.strip()
            
            logger.info(f"Answer generated in {generation_time:.3f}s")
            
            # Step 4: Prepare sources with relevance scores
            sources = []
            seen_urls = set()
            
            for metadata, similarity in zip(
                retrieval_results['metadatas'], 
                retrieval_results['similarities']
            ):
                url = metadata['url']
                
                # Avoid duplicate URLs
                if url not in seen_urls:
                    seen_urls.add(url)
                    sources.append({
                        'title': metadata['title'],
                        'url': url,
                        'relevance_score': similarity,
                        'chunk_id': metadata.get('chunk_id', 'N/A')
                    })
            
            total_time = time.time() - start_time
            
            # Log summary
            logger.info(f"Total processing time: {total_time:.3f}s")
            logger.info(f"Used {len(retrieval_results['documents'])} chunks from {len(sources)} unique sources")
            
            return {
                'query': query,
                'answer': answer,
                'sources': sources,
                'num_chunks_used': len(retrieval_results['documents']),
                'num_unique_sources': len(sources),
                'retrieval_time': retrieval_results['retrieval_time'],
                'generation_time': generation_time,
                'total_time': total_time,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            total_time = time.time() - start_time
            
            return {
                'query': query,
                'answer': f"An error occurred while processing your question: {str(e)}",
                'sources': [],
                'retrieval_time': 0,
                'generation_time': 0,
                'total_time': total_time,
                'success': False,
                'error': str(e)
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
