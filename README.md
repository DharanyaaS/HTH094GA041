# Grounded Multi-Document Compliance Assistant

An evidence-first, zero-hallucination Legal & Corporate Governance contract compliance web application built with **React**, **FastAPI**, **PyMuPDF**, **Sentence Transformers (`all-MiniLM-L6-v2`)**, and **ChromaDB**.

> **Governance Notice**: This tool provides document-based compliance assistance and does not replace professional legal advice.

---

## 1. Project Architecture & Workflow

```text
Upload Policy PDFs
    ↓
PDF Text & Page Extraction (PyMuPDF)
    ↓
Smart Section Chunking (Section-based, retains Page Number & Source)
    ↓
Embedding Generation (all-MiniLM-L6-v2, 384 dimensions)
    ↓
Persistent Vector Storage (ChromaDB under backend/vector_store)
    ↓
Upload Contract Document (.txt)
    ↓
Automatic Clause Extraction (Numbered Sections / Clauses)
    ↓
Query Vector Retrieval (Cosine Similarity RAG)
    ↓
Grounding Guardrail (Relevance Threshold Check >= 0.55)
    ├── If below threshold or topic absent: Return "Not Found" (Risk: Unknown)
    └── If relevant policy exists:
            ↓
    Conflict Detection Engine (Rule & Semantic Analysis)
            ↓
    Risk Assessment (High / Medium / Low / Unknown)
            ↓
    Interactive Compliance Report & Evidence Viewer
```

---

## 2. Directory Structure

```text
C:/Compliance-AI/
├── backend/
│   ├── main.py                     # FastAPI server with CORS, endpoints, file handling
│   ├── services/
│   │   ├── pdf_reader.py           # PyMuPDF extractor preserving page numbers
│   │   ├── chunker.py              # Smart section-based chunking
│   │   ├── embedding.py            # all-MiniLM-L6-v2 embedding model wrapper
│   │   ├── vector_store.py         # Persistent ChromaDB client & similarity search
│   │   ├── ingestion.py            # End-to-end policy PDF ingestion pipeline
│   │   ├── contract_reader.py      # Automatic numbered clause extractor
│   │   ├── conflict_detector.py    # Modular conflict & risk detection engine
│   │   └── compliance_checker.py   # RAG coordinator & compliance report generator
│   ├── uploads/
│   │   ├── test_policy.pdf         # Sample Data Protection Policy PDF
│   │   └── sample_contract.txt     # Sample contract with 4 clauses
│   ├── tests/
│   │   └── test_compliance.py      # Comprehensive 10-point test suite
│   ├── create_demo_pdf.py          # Script to generate test_policy.pdf
│   ├── requirements.txt            # Python dependencies
│   └── venv/                       # Local Python virtual environment
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx          # Header with system health, index count, disclaimer
│   │   │   ├── PolicyUploader.jsx  # Multi-PDF upload, demo loader, indexed file list
│   │   │   ├── ContractInput.jsx   # Contract editor, threshold slider, analyze button
│   │   │   ├── StatsOverview.jsx   # Metrics KPI cards (Conflicts, High Risk, Not Found)
│   │   │   ├── FindingsReport.jsx  # Interactive findings table with search & filter pills
│   │   │   └── EvidenceModal.jsx   # Side-by-side evidence viewer modal
│   │   ├── App.jsx                 # Main state coordinator
│   │   ├── App.css                 # Glassmorphism & responsive stylesheet
│   │   ├── index.css               # Design tokens & color system
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## 3. Key Grounding Features

- **Evidence-First Verification**: Every finding provides the exact policy excerpt, source filename, and source page number.
- **Strict Grounding / Zero Hallucination**:
  - If a clause (such as AES-256 encryption) is not present in the uploaded policies, the system explicitly returns:
    - **Status**: `Not Found`
    - **Risk**: `Unknown`
    - **Evidence Status**: `Not Found`
    - **Policy Evidence**: `No relevant policy requirement found.`
    - **Page**: `N/A`
  - The system will **never** invent or hallucinate a policy requirement.

---

## 4. Installation & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Node.js v18+ and npm

### Backend Installation

```cmd
cd C:\Compliance-AI\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Installation

```cmd
cd C:\Compliance-AI\frontend
npm install
```

---

## 5. Running the Application

### Step 1: Start Backend Server
From `C:\Compliance-AI\backend`:
```cmd
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```
Backend API will be accessible at: `http://localhost:8000`  
Interactive Swagger Docs: `http://localhost:8000/docs`

### Step 2: Start Frontend Dev Server
In a separate terminal, from `C:\Compliance-AI\frontend`:
```cmd
npm run dev
```
Frontend will be running at: `http://localhost:5173`

---

## 6. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health, vector DB index count, indexed documents |
| `GET` | `/policies` | List all currently indexed policy documents |
| `POST` | `/upload-policy` | Upload multiple policy PDFs; extracts & indexes sections into ChromaDB |
| `POST` | `/analyze-contract` | Upload or post contract text; extracts clauses, performs RAG analysis, returns report |
| `POST` | `/reset-policies` | Clear all indexed chunks from ChromaDB |
| `GET` | `/demo-files/policy` | Download the default `test_policy.pdf` |
| `GET` | `/demo-files/contract` | Get the default `sample_contract.txt` content |

---

## 7. Running the Automated Test Suite

To run the comprehensive 10-point test suite:

```cmd
cd C:\Compliance-AI\backend
venv\Scripts\pytest -v tests/test_compliance.py
```

### Verified Tests:
1. `test_1_pdf_extraction`: Validates PyMuPDF extraction, page numbers, and text.
2. `test_2_smart_chunking`: Validates section-based chunking and page metadata retention.
3. `test_3_embedding_generation`: Validates 384-dimensional `all-MiniLM-L6-v2` embeddings.
4. `test_4_vector_search`: Validates persistent ChromaDB insertion and cosine similarity search.
5. `test_5_contract_clause_extraction`: Validates automatic parsing of numbered contract clauses.
6. `test_6_conflict_detection`: Validates Data Access conflict detection logic.
7. `test_7_full_compliance_checking`: Validates full workflow for Access, Sharing, and Retention.
8. `test_8_not_found_detection_aes256`: Validates strict "Not Found" / zero hallucination for AES-256.
9. `test_9_api_health`: Validates FastAPI `/health` endpoint response.
10. `test_10_api_analyze_contract`: Validates end-to-end API `/analyze-contract` endpoint.

---

## 8. Demo Walkthrough

1. Open `http://localhost:5173` in your browser.
2. In the **Policy Documents** card, click **Load Demo Policy** (or upload `test_policy.pdf`). The system indexes 5 sections across 2 pages into ChromaDB.
3. In the **Contract Document** card, click **Load Sample Contract**. The 4 clauses appear in the editor:
   - 1. Data Access (allows access whenever necessary)
   - 2. Data Sharing (allows external sharing without approval)
   - 3. Data Retention (retains records indefinitely)
   - 4. Data Encryption (AES-256 encryption requirement)
4. Click the prominent **Analyze Contract** button.
5. Review the **Compliance Report**:
   - **Data Access** → `Conflict` | `High Risk` | `Explicitly Stated` (Policy Page 1)
   - **Data Sharing** → `Conflict` | `High Risk` | `Explicitly Stated` (Policy Page 1)
   - **Data Retention** → `Conflict` | `High Risk` | `Explicitly Stated` (Policy Page 2)
   - **Data Encryption** → `Not Found` | `Unknown Risk` | `Not Found` (Evidence: *No relevant policy requirement found.*)
6. Click **View Evidence** on any finding to open the side-by-side comparison modal with source citation and reasoning.
