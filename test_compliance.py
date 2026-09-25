import os
import sys

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pytest
from fastapi.testclient import TestClient

from main import app
from services.pdf_reader import extract_text_from_pdf
from services.chunker import chunk_policy_pages
from services.embedding import generate_embedding, generate_embeddings
from services.vector_store import (
    add_policy_chunks, 
    query_policy_store, 
    reset_policy_store,
    count_chunks
)
from services.contract_reader import extract_clauses_from_text
from services.conflict_detector import analyze_clause_conflict
from services.compliance_checker import check_contract_compliance
from services.ingestion import ingest_policy_pdf

SAMPLE_CONTRACT_TEXT = """Company Customer Data Agreement

1. Data Access
Employees may access customer data whenever necessary.

2. Data Sharing
Customer information may be shared with external business partners when required for business operations.

3. Data Retention
Customer records will be retained indefinitely.

4. Data Encryption
Customer data must be encrypted using AES-256.
"""

@pytest.fixture(scope="module", autouse=True)
def setup_test_environment():
    # Make sure demo PDF is created
    from create_demo_pdf import generate_test_policy_pdf
    generate_test_policy_pdf()
    reset_policy_store()
    yield
    reset_policy_store()

# 1. PDF Extraction Test
def test_1_pdf_extraction():
    demo_pdf_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "uploads", "test_policy.pdf")
    )
    pages = extract_text_from_pdf(demo_pdf_path, "test_policy.pdf")
    assert len(pages) >= 2, "Expected at least 2 pages in test_policy.pdf"
    assert pages[0]["page"] == 1
    assert "Company Data Protection Policy" in pages[0]["text"]
    assert pages[1]["page"] == 2
    assert "Data Retention" in pages[1]["text"]

# 2. Chunking Test
def test_2_smart_chunking():
    demo_pdf_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "uploads", "test_policy.pdf")
    )
    pages = extract_text_from_pdf(demo_pdf_path, "test_policy.pdf")
    chunks = chunk_policy_pages(pages)
    
    # Sections expected: Purpose, Data Access, Data Sharing, Data Retention, Security
    titles = [c["title"] for c in chunks]
    assert any("Data Access" in t for t in titles), f"Data Access not found in {titles}"
    assert any("Data Retention" in t for t in titles), f"Data Retention not found in {titles}"
    
    # Check that chunks retain source page numbers
    for c in chunks:
        assert c["page"] in [1, 2]
        assert c["source"] == "test_policy.pdf"

# 3. Embedding Generation Test
def test_3_embedding_generation():
    emb = generate_embedding("Data Access Policy Requirement")
    assert isinstance(emb, list)
    assert len(emb) == 384, f"Expected 384 dimensions from all-MiniLM-L6-v2, got {len(emb)}"

    embs = generate_embeddings(["Test sentence 1", "Test sentence 2"])
    assert len(embs) == 2
    assert len(embs[0]) == 384

# 4. Vector Search Test
def test_4_vector_search():
    reset_policy_store()
    demo_pdf_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "uploads", "test_policy.pdf")
    )
    ingest_policy_pdf(demo_pdf_path, "test_policy.pdf")
    
    assert count_chunks() > 0

    # Query vector store for retention
    q_emb = generate_embedding("How long can customer records be retained?")
    results = query_policy_store(q_emb, n_results=2)
    assert len(results) > 0
    top_result = results[0]
    assert "Retention" in top_result["title"] or "five years" in top_result["text"]
    assert top_result["similarity"] > 0.40

# 5. Contract Extraction Test
def test_5_contract_clause_extraction():
    clauses = extract_clauses_from_text(SAMPLE_CONTRACT_TEXT, "sample_contract.txt")
    assert len(clauses) == 4, f"Expected 4 clauses, got {len(clauses)}"
    
    clause_titles = [c["title"] for c in clauses]
    assert "Data Access" in clause_titles[0]
    assert "Data Sharing" in clause_titles[1]
    assert "Data Retention" in clause_titles[2]
    assert "Data Encryption" in clause_titles[3]

# 6. Conflict Detection Test
def test_6_conflict_detection():
    # Test Data Access conflict
    clause_access = {
        "clause_id": "Clause 1",
        "title": "Data Access",
        "full_clause": "1. Data Access\nEmployees may access customer data whenever necessary.",
        "body": "Employees may access customer data whenever necessary."
    }
    policy_access = {
        "text": "2. Data Access\nEmployees may access confidential customer data only when access is required for their assigned work.",
        "page": 1,
        "source": "test_policy.pdf"
    }
    res = analyze_clause_conflict(clause_access, policy_access, similarity_score=0.85)
    assert res["status"] == "Conflict"
    assert res["risk"] == "High"
    assert res["evidence_status"] == "Explicitly Stated"
    assert res["page"] == 1

# 7. Compliance Checking Test
def test_7_full_compliance_checking():
    demo_pdf_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "uploads", "test_policy.pdf")
    )
    ingest_policy_pdf(demo_pdf_path, "test_policy.pdf")

    report = check_contract_compliance(SAMPLE_CONTRACT_TEXT, "sample_contract.txt")
    findings = report["findings"]

    # Map by clause title
    findings_by_title = {f["clause_title"]: f for f in findings}

    # 1. Data Access -> Conflict, High Risk
    access_finding = findings_by_title.get("Data Access")
    assert access_finding is not None
    assert access_finding["status"] == "Conflict"
    assert access_finding["risk"] == "High"
    assert access_finding["evidence_status"] == "Explicitly Stated"

    # 2. Data Sharing -> Conflict, High Risk
    sharing_finding = findings_by_title.get("Data Sharing")
    assert sharing_finding is not None
    assert sharing_finding["status"] == "Conflict"
    assert sharing_finding["risk"] == "High"

    # 3. Data Retention -> Conflict, High Risk
    retention_finding = findings_by_title.get("Data Retention")
    assert retention_finding is not None
    assert retention_finding["status"] == "Conflict"
    assert retention_finding["risk"] == "High"

# 8. Not Found Detection Test (AES-256)
def test_8_not_found_detection_aes256():
    demo_pdf_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "uploads", "test_policy.pdf")
    )
    ingest_policy_pdf(demo_pdf_path, "test_policy.pdf")

    report = check_contract_compliance(
        "4. Data Encryption\nCustomer data must be encrypted using AES-256.",
        "sample_contract.txt"
    )
    encryption_finding = report["findings"][0]

    # Grounding check: Must be Not Found and Unknown risk, never hallucinating policy
    assert encryption_finding["status"] == "Not Found"
    assert encryption_finding["risk"] == "Unknown"
    assert encryption_finding["evidence_status"] == "Not Found"
    assert encryption_finding["policy_evidence"] == "No relevant policy requirement found."
    assert encryption_finding["page"] == "N/A"

# 9. API Health Endpoint Test
def test_9_api_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "indexed_chunks" in data

# 10. End-to-End API Analysis Test
def test_10_api_analyze_contract():
    client = TestClient(app)
    response = client.post(
        "/analyze-contract",
        data={"contract_text": SAMPLE_CONTRACT_TEXT, "threshold": "0.55"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "findings" in data
    assert data["summary"]["total_clauses"] == 4
    assert data["summary"]["conflicts"] >= 3
    assert data["summary"]["not_found"] >= 1
