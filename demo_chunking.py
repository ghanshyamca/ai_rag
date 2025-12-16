"""
Chunking Demo - Visual Demonstration of Step 4
Shows exactly what happens when text is chunked
"""

def demo_chunking():
    """Visual demonstration of the chunking process"""
    
    print("\n" + "="*70)
    print("STEP 4: TEXT CHUNKING DEMONSTRATION")
    print("="*70 + "\n")
    
    # Sample long text
    sample_text = """
    Python is a high-level, interpreted programming language created by Guido van Rossum.
    It was first released in 1991 and has since become one of the most popular programming
    languages in the world. Python emphasizes code readability with its notable use of
    significant indentation.
    
    The language supports multiple programming paradigms including object-oriented,
    imperative, and functional programming. Python is dynamically typed and features
    automatic memory management. Its comprehensive standard library is often described
    as having "batteries included."
    
    Python is widely used in web development, data science, artificial intelligence,
    scientific computing, automation, and many other fields. Popular frameworks include
    Django and Flask for web development, NumPy and Pandas for data analysis, and
    TensorFlow and PyTorch for machine learning.
    """
    
    sample_text = " ".join(sample_text.split())  # Clean whitespace
    
    print("ORIGINAL TEXT:")
    print("-" * 70)
    print(f"Length: {len(sample_text)} characters")
    print(f"\n{sample_text}\n")
    print("-" * 70)
    
    # Chunking configuration
    chunk_size = 200
    overlap = 50
    
    print(f"\nCHUNKING CONFIGURATION:")
    print(f"  Chunk Size: {chunk_size} characters")
    print(f"  Overlap: {overlap} characters")
    print()
    
    # Simple chunking algorithm
    chunks = []
    start = 0
    text_length = len(sample_text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        
        # Try to find sentence boundary
        if end < text_length:
            chunk_text = sample_text[start:end]
            last_period = chunk_text.rfind('. ')
            if last_period != -1 and last_period > chunk_size // 2:
                end = start + last_period + 2  # Include period and space
        
        chunk = sample_text[start:end].strip()
        chunks.append({
            'chunk_id': len(chunks),
            'start_pos': start,
            'end_pos': end,
            'text': chunk,
            'length': len(chunk)
        })
        
        if end >= text_length:
            break
        
        start = end - overlap
    
    # Display chunks
    print("="*70)
    print(f"RESULTING CHUNKS: {len(chunks)} chunks created")
    print("="*70 + "\n")
    
    for chunk in chunks:
        print(f"Chunk #{chunk['chunk_id']}:")
        print(f"  Position: chars {chunk['start_pos']}-{chunk['end_pos']}")
        print(f"  Length: {chunk['length']} characters")
        print(f"  Text: \"{chunk['text']}\"")
        print()
    
    # Show overlap
    if len(chunks) > 1:
        print("="*70)
        print("OVERLAP DEMONSTRATION")
        print("="*70 + "\n")
        
        chunk0_end = chunks[0]['text'][-overlap:]
        chunk1_start = chunks[1]['text'][:overlap]
        
        print(f"End of Chunk 0 (last {overlap} chars):")
        print(f'  "...{chunk0_end}"')
        print()
        print(f"Start of Chunk 1 (first {overlap} chars):")
        print(f'  "{chunk1_start}..."')
        print()
        
        if chunk0_end in chunks[1]['text']:
            print("✅ Overlap preserved! Context maintained across chunks.")
        
    # Show metadata structure
    print("\n" + "="*70)
    print("CHUNK METADATA STRUCTURE")
    print("="*70 + "\n")
    
    print("In the actual implementation, each chunk includes:")
    print("""
    {
        'chunk_id': 0,              # ← Sequential ID
        'url': 'https://...',       # ← Parent URL
        'title': 'Page Title',      # ← Page title  
        'text': 'chunk content',    # ← Chunk text
        'total_chunks': 5,          # ← Total chunks in document
        'char_count': 987           # ← Length
    }
    """)
    
    print("="*70)
    print("KEY BENEFITS OF CHUNKING")
    print("="*70 + "\n")
    
    print("✅ 1. Manageable Size")
    print("   - Large documents split into digestible pieces")
    print("   - Fits within embedding model limits")
    print()
    
    print("✅ 2. Context Preservation")
    print("   - Overlap ensures no information loss")
    print("   - Related content stays together")
    print()
    
    print("✅ 3. Better Retrieval")
    print("   - More precise matching of user queries")
    print("   - Smaller chunks = more focused results")
    print()
    
    print("✅ 4. Complete Metadata")
    print("   - Know where each chunk came from")
    print("   - Track position within original document")
    print()
    
    print("="*70)
    print("TESTING THE IMPLEMENTATION")
    print("="*70 + "\n")
    
    print("Run these commands to test chunking:")
    print()
    print("  1. Test with sample data:")
    print("     python test_chunking.py")
    print()
    print("  2. Test text processor directly:")
    print("     python text_processor.py")
    print()
    print("  3. Run full pipeline:")
    print("     python main.py")
    print()
    
    print("="*70 + "\n")


if __name__ == "__main__":
    demo_chunking()
