import os
from typing import Dict, Any, List
from .pdf_reader import extract_text_from_pdf
from .chunker import chunk_policy_pages
from .embedding import generate_embeddings
from .vector_store import add_policy_chunks

def ingest_policy_pdf(file_path: str, original_filename: str = None) -> Dict[str, Any]:
    """
    Complete ingestion pipeline for a policy PDF:
    1. Extract page-by-page text with PyMuPDF
    2. Split into smart section-based chunks with source and page metadata
    3. Generate vector embeddings using all-MiniLM-L6-v2
    4. Store in ChromaDB vector store
    """
    filename = original_filename or os.path.basename(file_path)
    
    # 1. Extract text and pages
    pages_data = extract_text_from_pdf(file_path, filename)
    if not pages_data:
        raise ValueError(f"No content extracted from policy PDF '{filename}'")

    # 2. Smart section chunking
    chunks = chunk_policy_pages(pages_data)
    if not chunks:
        raise ValueError(f"No valid sections or chunks created for '{filename}'")

    # 3. Generate embeddings
    texts_to_embed = [c["text"] for c in chunks]
    embeddings = generate_embeddings(texts_to_embed)

    # 4. Store in ChromaDB
    indexed_count = add_policy_chunks(chunks, embeddings)

    return {
        "filename": filename,
        "total_pages": len(pages_data),
        "total_chunks": indexed_count,
        "chunks": [
            {
                "chunk_id": c["chunk_id"],
                "title": c["title"],
                "page": c["page"],
                "preview": c["text"][:100] + "..." if len(c["text"]) > 100 else c["text"]
            }
            for c in chunks
        ]
    }
