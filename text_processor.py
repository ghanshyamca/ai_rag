"""
Text Processing Module
Cleans and chunks text for embedding generation
"""
import re
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextProcessor:
    """
    Processes and chunks text for embedding generation
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the text processor
        
        Args:
            chunk_size: Size of each text chunk in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:\;]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            # Calculate end position
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at a sentence
            if end < text_length:
                # Look for sentence ending punctuation
                chunk_text = text[start:end]
                last_period = max(
                    chunk_text.rfind('.'),
                    chunk_text.rfind('!'),
                    chunk_text.rfind('?')
                )
                
                if last_period != -1:
                    end = start + last_period + 1
            
            chunk = text[start:end].strip()
            
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Ensure we make progress
            if start <= 0 or start >= text_length:
                break
        
        return chunks
    
    def process_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Process multiple documents into chunks with metadata
        
        Args:
            documents: List of document dictionaries with 'url', 'title', and 'content'
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        processed_chunks = []
        
        for doc in documents:
            # Clean the content
            cleaned_text = self.clean_text(doc['content'])
            
            # Skip if content is too short
            if len(cleaned_text) < 100:
                logger.warning(f"Skipping document {doc['url']} - content too short")
                continue
            
            # Create chunks
            chunks = self.chunk_text(cleaned_text)
            
            # Add metadata to each chunk
            for i, chunk in enumerate(chunks):
                processed_chunks.append({
                    'text': chunk,
                    'url': doc['url'],
                    'title': doc['title'],
                    'chunk_id': i,
                    'total_chunks': len(chunks)
                })
        
        logger.info(f"Processed {len(documents)} documents into {len(processed_chunks)} chunks")
        return processed_chunks


if __name__ == "__main__":
    # Test the text processor
    from config import CHUNK_SIZE, CHUNK_OVERLAP
    
    processor = TextProcessor(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    
    # Sample document
    sample_doc = {
        'url': 'https://example.com/test',
        'title': 'Test Document',
        'content': '''
        This is a test document with some content. It has multiple sentences.
        We want to test the chunking functionality. The processor should clean
        and split this text into appropriate chunks. This will help us understand
        how the RAG system works. We need enough text to create multiple chunks
        for testing purposes. Let's add more content here to ensure we get
        multiple chunks when processing. Each chunk should have proper metadata
        attached to it including the source URL and title.
        ''' * 10  # Repeat to get more text
    }
    
    chunks = processor.process_documents([sample_doc])
    
    print(f"\nProcessed into {len(chunks)} chunks")
    if chunks:
        print(f"\nFirst chunk:")
        print(f"Text preview: {chunks[0]['text'][:200]}...")
        print(f"Metadata: URL={chunks[0]['url']}, Chunk {chunks[0]['chunk_id']+1}/{chunks[0]['total_chunks']}")
