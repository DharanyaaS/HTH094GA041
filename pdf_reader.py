import os
from typing import List, Dict, Any
import pymupdf as fitz

def extract_text_from_pdf(file_path: str, filename: str = None) -> List[Dict[str, Any]]:
    """
    Extract text from a PDF file page-by-page using PyMuPDF.
    Every extracted page retains its 1-indexed page number and source filename.
    
    Returns a list of dictionaries:
    [
        {"page": 1, "text": "...", "source": "test_policy.pdf"},
        ...
    ]
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found at: {file_path}")
    
    doc_name = filename or os.path.basename(file_path)
    pages_data: List[Dict[str, Any]] = []
    
    try:
        doc = fitz.open(file_path)
        if len(doc) == 0:
            raise ValueError(f"PDF file '{doc_name}' is empty (0 pages).")
        
        for page_index in range(len(doc)):
            page = doc[page_index]
            text = page.get_text("text").strip()
            pages_data.append({
                "page": page_index + 1,
                "text": text,
                "source": doc_name
            })
            
        doc.close()
    except Exception as e:
        if isinstance(e, (FileNotFoundError, ValueError)):
            raise
        raise RuntimeError(f"Error reading PDF file '{doc_name}': {str(e)}") from e
        
    return pages_data
