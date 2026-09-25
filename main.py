import os
import shutil
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from services.ingestion import ingest_policy_pdf
from services.compliance_checker import check_contract_compliance, DEFAULT_SIMILARITY_THRESHOLD
from services.vector_store import count_chunks, get_indexed_sources, reset_policy_store

app = FastAPI(
    title="Grounded Multi-Document Compliance Assistant API",
    description="Evidence-first Legal & Corporate Governance compliance checking using RAG with ChromaDB and Sentence Transformers.",
    version="1.0.0"
)

# Enable CORS for React frontend (Vite defaults to port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ContractTextRequest(BaseModel):
    text: str
    filename: Optional[str] = "contract.txt"
    threshold: Optional[float] = DEFAULT_SIMILARITY_THRESHOLD

@app.get("/")
def root():
    return {
        "message": "Grounded Multi-Document Compliance Assistant API is running!",
        "docs": "/docs",
        "health": "/health",
        "policies": "/policies"
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint returning system status and indexed policy metrics.
    """
    chunk_count = count_chunks()
    sources = get_indexed_sources()
    return {
        "status": "healthy",
        "service": "Grounded Multi-Document Compliance Assistant",
        "indexed_chunks": chunk_count,
        "indexed_sources": sources
    }

@app.get("/policies")
def list_policies():
    """
    Returns list of all currently indexed policy documents and their chunk counts.
    """
    sources = get_indexed_sources()
    return {
        "total_documents": len(sources),
        "total_chunks": count_chunks(),
        "documents": sources
    }

@app.post("/upload-policy")
async def upload_policy(files: List[UploadFile] = File(...)):
    """
    Upload one or multiple policy PDF documents.
    Extracts text, page numbers, chunks sections, generates embeddings,
    and stores them in persistent ChromaDB.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    results = []
    errors = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            errors.append(f"'{file.filename}' is not a valid PDF file. Only .pdf files are supported.")
            continue

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        try:
            # Save uploaded PDF to uploads directory
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Ingest into vector store
            ingest_result = ingest_policy_pdf(file_path, original_filename=file.filename)
            results.append(ingest_result)
        except Exception as e:
            errors.append(f"Failed to process '{file.filename}': {str(e)}")

    if not results and errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))

    return {
        "message": f"Successfully processed {len(results)} policy document(s).",
        "processed": results,
        "errors": errors,
        "total_indexed_chunks": count_chunks()
    }

def extract_text_from_file_bytes(content_bytes: bytes, filename: str) -> str:
    lower_name = filename.lower()
    if lower_name.endswith(".pdf"):
        import pymupdf as fitz
        try:
            doc = fitz.open(stream=content_bytes, filetype="pdf")
            if len(doc) == 0:
                raise ValueError("PDF file is empty (0 pages).")
            pages = []
            for i, page in enumerate(doc):
                text = page.get_text("text").strip()
                if text:
                    pages.append(text)
            doc.close()
            combined = "\n\n".join(pages)
            if not combined.strip():
                raise ValueError("Could not extract readable text from PDF (it may contain scanned images instead of text).")
            return combined
        except Exception as e:
            raise ValueError(f"Failed to read PDF: {str(e)}")
    else:
        try:
            return content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return content_bytes.decode("latin-1", errors="ignore")

@app.post("/extract-contract-text")
async def extract_contract_text(file: UploadFile = File(...)):
    """
    Extract readable text and clauses from an uploaded .pdf or .txt contract file.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file provided.")
    content_bytes = await file.read()
    try:
        text = extract_text_from_file_bytes(content_bytes, file.filename)
        return {
            "filename": file.filename,
            "text": text,
            "char_count": len(text)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-contract")
async def analyze_contract(
    file: Optional[UploadFile] = File(None),
    contract_text: Optional[str] = Form(None),
    threshold: Optional[float] = Form(DEFAULT_SIMILARITY_THRESHOLD)
):
    """
    Analyze contract text or uploaded contract document against indexed policy documents.
    Extracts clauses, retrieves policy evidence via RAG, checks compliance & risk.
    """
    raw_content = ""
    filename = "contract.txt"

    if file is not None:
        filename = file.filename
        content_bytes = await file.read()
        try:
            raw_content = extract_text_from_file_bytes(content_bytes, filename)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    elif contract_text and contract_text.strip():
        raw_content = contract_text.strip()
    else:
        raise HTTPException(status_code=400, detail="Please upload a contract file or provide contract text.")

    if not raw_content.strip():
        raise HTTPException(status_code=400, detail="Contract text is empty.")

    try:
        report = check_contract_compliance(
            contract_text=raw_content,
            contract_filename=filename,
            threshold=threshold or DEFAULT_SIMILARITY_THRESHOLD
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/reset-policies")
def reset_policies():
    """
    Clears all indexed policy chunks from the vector database.
    """
    try:
        reset_policy_store()
        return {"status": "success", "message": "Policy store reset successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset store: {str(e)}")

@app.get("/demo-files/policy")
def get_demo_policy():
    """Returns the path or content of the sample policy PDF"""
    policy_path = os.path.join(UPLOAD_DIR, "test_policy.pdf")
    if os.path.exists(policy_path):
        return FileResponse(policy_path, media_type="application/pdf", filename="test_policy.pdf")
    raise HTTPException(status_code=404, detail="Demo policy file not generated yet.")

@app.get("/demo-files/contract")
def get_demo_contract():
    """Returns the sample contract text"""
    contract_path = os.path.join(UPLOAD_DIR, "sample_contract.txt")
    if os.path.exists(contract_path):
        with open(contract_path, "r", encoding="utf-8") as f:
            return {"filename": "sample_contract.txt", "content": f.read()}
    raise HTTPException(status_code=404, detail="Demo contract file not found.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
