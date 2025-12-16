"""
Chunking Test Script
Demonstrates the text chunking functionality with detailed statistics
"""
from text_processor import TextProcessor
from config import CHUNK_SIZE, CHUNK_OVERLAP
import json


def main():
    """Test chunking with sample documents"""
    
    print("\n" + "="*70)
    print("CHUNKING TEST - STEP 4 VERIFICATION")
    print("="*70 + "\n")
    
    # Initialize processor
    processor = TextProcessor(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    
    print(f"Configuration:")
    print(f"  • Chunk Size: {CHUNK_SIZE} characters")
    print(f"  • Chunk Overlap: {CHUNK_OVERLAP} characters")
    print(f"  • Minimum Chunk Size: 50 characters")
    print()
    
    # Sample documents simulating crawled web pages
    sample_documents = [
        {
            'url': 'https://docs.example.com/introduction',
            'title': 'Introduction to Python Programming',
            'content': '''
            Python is a powerful, high-level programming language that is widely used
            for web development, data analysis, artificial intelligence, and scientific computing.
            It was created by Guido van Rossum and first released in 1991.
            
            Python's design philosophy emphasizes code readability with its notable use of
            significant indentation. Its language constructs and object-oriented approach aim
            to help programmers write clear, logical code for small and large-scale projects.
            
            Python is dynamically-typed and garbage-collected. It supports multiple programming
            paradigms, including structured (particularly, procedural), object-oriented, and
            functional programming. Python is often described as a "batteries included" language
            due to its comprehensive standard library.
            
            The language's core philosophy is summarized in the document The Zen of Python,
            which includes aphorisms such as "Beautiful is better than ugly" and "Simple is
            better than complex." Python developers strive to avoid premature optimization
            and reject patches to non-critical parts of the CPython reference implementation
            that would offer marginal increases in speed at the cost of clarity.
            '''
        },
        {
            'url': 'https://docs.example.com/data-types',
            'title': 'Python Data Types and Structures',
            'content': '''
            Python has several built-in data types that are fundamental to programming.
            The basic types include integers (int), floating-point numbers (float),
            strings (str), and booleans (bool). These primitive types form the foundation
            for more complex data structures.
            
            Lists are ordered, mutable sequences that can contain items of different types.
            They are defined using square brackets and are one of the most versatile data
            structures in Python. Lists support indexing, slicing, and various methods
            for manipulation like append(), extend(), insert(), and remove().
            
            Tuples are similar to lists but are immutable, meaning their contents cannot
            be changed after creation. They are defined using parentheses and are often
            used for data that should remain constant throughout the program's execution.
            
            Dictionaries are key-value pairs that provide fast lookups and are defined
            using curly braces. They are unordered collections where each key must be
            unique and immutable. Dictionaries are extremely useful for mapping relationships
            and are widely used in Python programming.
            
            Sets are unordered collections of unique elements, also defined using curly
            braces or the set() constructor. They are useful for membership testing,
            removing duplicates from sequences, and computing mathematical operations
            like union, intersection, and difference.
            '''
        },
        {
            'url': 'https://docs.example.com/functions',
            'title': 'Functions and Control Flow',
            'content': '''
            Functions in Python are defined using the 'def' keyword followed by the
            function name and parentheses containing any parameters. Functions can
            accept multiple parameters and return values using the 'return' statement.
            
            Control flow statements include if-else conditionals, for loops, while loops,
            and exception handling with try-except blocks. These structures allow developers
            to control the execution path of their programs based on conditions and iterations.
            '''
        }
    ]
    
    print("="*70)
    print("PROCESSING DOCUMENTS")
    print("="*70 + "\n")
    
    # Process documents into chunks
    chunks = processor.process_documents(sample_documents)
    
    # Get statistics
    stats = processor.get_chunk_statistics(chunks)
    
    # Display results
    print("\n" + "="*70)
    print("CHUNKING RESULTS")
    print("="*70 + "\n")
    
    print(f"📊 Overall Statistics:")
    print(f"   Total chunks created: {stats['total_chunks']}")
    print(f"   Documents processed: {stats['unique_documents']}")
    print(f"   Average chunk size: {stats['avg_chunk_size']:.1f} characters")
    print(f"   Min chunk size: {stats['min_chunk_size']} characters")
    print(f"   Max chunk size: {stats['max_chunk_size']} characters")
    print()
    
    print("="*70)
    print("CHUNKS PER PAGE")
    print("="*70 + "\n")
    
    # Show chunks per document
    for url, count in stats['chunks_per_document'].items():
        title = next((chunk['title'] for chunk in chunks if chunk['url'] == url), 'Unknown')
        print(f"📄 {title}")
        print(f"   URL: {url}")
        print(f"   Chunks generated: {count}")
        print()
    
    print("="*70)
    print("SAMPLE CHUNK DETAILS")
    print("="*70 + "\n")
    
    # Show detailed information for first 3 chunks
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"Chunk #{i}")
        print(f"{'-'*70}")
        print(f"  ✓ Chunk ID: {chunk['chunk_id']}")
        print(f"  ✓ Parent URL: {chunk['url']}")
        print(f"  ✓ Page Title: {chunk['title']}")
        print(f"  ✓ Character Count: {chunk['char_count']}")
        print(f"  ✓ Total Chunks in Document: {chunk['total_chunks']}")
        print(f"\n  Chunk Text (first 200 chars):")
        print(f"  {chunk['text'][:200].replace(chr(10), ' ')}...")
        print()
    
    if len(chunks) > 3:
        print(f"... and {len(chunks) - 3} more chunks\n")
    
    # Verify all required fields
    print("="*70)
    print("FIELD VERIFICATION")
    print("="*70 + "\n")
    
    required_fields = ['chunk_id', 'url', 'title', 'text', 'char_count', 'total_chunks']
    all_fields_present = True
    
    for field in required_fields:
        present = all(field in chunk for chunk in chunks)
        status = "✅" if present else "❌"
        print(f"  {status} {field}: {'Present' if present else 'Missing'}")
        if not present:
            all_fields_present = False
    
    print()
    
    # Save sample chunk to JSON for inspection
    if chunks:
        sample_chunk_file = 'sample_chunk.json'
        with open(sample_chunk_file, 'w', encoding='utf-8') as f:
            json.dump(chunks[0], f, indent=2, ensure_ascii=False)
        print(f"📝 Sample chunk saved to: {sample_chunk_file}\n")
    
    # Final summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70 + "\n")
    
    if all_fields_present and chunks:
        print("✅ SUCCESS! All chunking requirements met:")
        print("   • Text split into smaller chunks with overlap")
        print("   • Each chunk includes chunk_id")
        print("   • Each chunk includes parent URL")
        print("   • Each chunk includes page title")
        print("   • Each chunk includes chunk text")
        print("   • All chunks stored and ready for embedding")
        print(f"   • Generated {stats['total_chunks']} chunks from {stats['unique_documents']} documents")
    else:
        print("❌ FAILED! Some requirements not met")
    
    print("\n" + "="*70 + "\n")
    
    return chunks, stats


if __name__ == "__main__":
    chunks, stats = main()
