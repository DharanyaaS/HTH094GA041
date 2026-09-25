import React, { useState, useRef } from 'react';
import { 
  FileCheck, 
  UploadCloud, 
  Play, 
  RefreshCw, 
  Sliders, 
  FileCode, 
  FileText, 
  CheckCircle2, 
  AlertCircle,
  X
} from 'lucide-react';

export default function ContractInput({
  contractText,
  setContractText,
  contractFilename,
  setContractFilename,
  onLoadDemoContract,
  onAnalyze,
  isAnalyzing,
  canAnalyze,
  threshold,
  setThreshold,
  apiBase = 'http://127.0.0.1:8000'
}) {
  const [activeTab, setActiveTab] = useState('text'); // 'text' | 'file'
  const [showSettings, setShowSettings] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractError, setExtractError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const processFile = async (file) => {
    if (!file) return;
    setExtractError(null);
    const fileName = file.name;
    const isPdf = fileName.toLowerCase().endsWith('.pdf');

    if (isPdf) {
      setIsExtracting(true);
      try {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(`${apiBase}/extract-contract-text`, {
          method: 'POST',
          body: formData,
        });

        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || 'Failed to extract text from PDF.');
        }

        setContractText(data.text);
        setContractFilename(data.filename || fileName);
        setActiveTab('text');
      } catch (err) {
        setExtractError(err.message || 'Error processing PDF document.');
      } finally {
        setIsExtracting(false);
      }
    } else {
      // .txt, .md, or other text file
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target?.result;
        if (typeof content === 'string') {
          setContractText(content);
          setContractFilename(fileName);
          setActiveTab('text');
        }
      };
      reader.onerror = () => {
        setExtractError('Failed to read text file.');
      };
      reader.readAsText(file);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
    // reset input so the same file can be selected again if needed
    if (e.target) e.target.value = '';
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const clearContract = () => {
    setContractText('');
    setContractFilename('');
    setExtractError(null);
  };

  return (
    <div className="card contract-card">
      <div className="card-header">
        <div className="card-title-group">
          <FileCheck className="card-header-icon" size={20} />
          <div>
            <h2 className="card-title">2. Contract Document</h2>
            <p className="card-subtitle">Upload a contract (.pdf / .txt) or edit clauses directly</p>
          </div>
        </div>

        <div className="card-actions">
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={onLoadDemoContract}
            title="Load sample contract with Data Access, Sharing, Retention, and AES-256 clauses"
          >
            Load Sample Contract
          </button>
          <button
            type="button"
            className={`btn btn-ghost btn-sm ${showSettings ? 'btn-active' : ''}`}
            onClick={() => setShowSettings(!showSettings)}
            title="Configure RAG Sensitivity Threshold"
          >
            <Sliders size={15} />
          </button>
        </div>
      </div>

      {showSettings && (
        <div className="settings-panel">
          <div className="settings-header">
            <span className="settings-label">RAG Relevance Threshold (Grounding Guardrail):</span>
            <span className="settings-value">{threshold.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="0.30"
            max="0.75"
            step="0.05"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="slider"
          />
          <span className="settings-hint">
            Clauses retrieving policy evidence with similarity below {threshold.toFixed(2)} are marked 
            <strong> Not Found (Unknown Risk)</strong> to prevent hallucinations.
          </span>
        </div>
      )}

      {/* Tabs */}
      <div className="tab-bar">
        <button
          className={`tab-btn ${activeTab === 'text' ? 'tab-btn-active' : ''}`}
          onClick={() => setActiveTab('text')}
        >
          <FileCode size={14} />
          Contract Editor {contractFilename ? `(${contractFilename})` : ''}
        </button>
        <button
          className={`tab-btn ${activeTab === 'file' ? 'tab-btn-active' : ''}`}
          onClick={() => setActiveTab('file')}
        >
          <UploadCloud size={14} />
          Upload .txt / .pdf File
        </button>
      </div>

      {extractError && (
        <div className="status-message error-message" style={{ margin: '0.75rem 1.25rem 0' }}>
          <AlertCircle size={16} />
          <span>{extractError}</span>
        </div>
      )}

      {activeTab === 'file' ? (
        <div 
          className={`dropzone contract-dropzone ${dragActive ? 'dropzone-active' : ''}`}
          onClick={() => !isExtracting && fileInputRef.current?.click()}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          style={{ cursor: isExtracting ? 'wait' : 'pointer' }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.text,.md"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
          {isExtracting ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
              <RefreshCw size={34} className="spin text-primary" />
              <p className="dropzone-text">Extracting clauses from document with PyMuPDF...</p>
              <span className="dropzone-hint">Parsing structure and numbering</span>
            </div>
          ) : (
            <>
              <UploadCloud size={34} className="dropzone-icon" />
              <p className="dropzone-text">Click to browse or drag & drop contract (.pdf or .txt)</p>
              <span className="dropzone-hint">
                Extracts numbered clauses (e.g. 1. Data Access, Section 2, Article 3) automatically
              </span>
            </>
          )}
        </div>
      ) : (
        <div className="editor-container">
          {contractFilename && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '0.4rem 0.8rem',
              backgroundColor: 'rgba(56, 189, 248, 0.08)',
              borderBottom: '1px solid rgba(56, 189, 248, 0.15)',
              fontSize: '0.8rem',
              color: 'var(--text-secondary)'
            }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <FileText size={13} className="text-primary" />
                Active Document: <strong style={{ color: 'var(--text-primary)' }}>{contractFilename}</strong>
              </span>
              <button 
                type="button" 
                onClick={clearContract} 
                style={{ 
                  background: 'transparent', 
                  border: 'none', 
                  color: 'var(--text-muted)', 
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.2rem',
                  fontSize: '0.75rem'
                }}
                title="Clear current contract text"
              >
                <X size={13} /> Clear
              </button>
            </div>
          )}
          <textarea
            className="contract-textarea"
            value={contractText}
            onChange={(e) => setContractText(e.target.value)}
            placeholder="Paste contract text here or click 'Load Sample Contract' / upload a .pdf or .txt file...

Example:
1. Data Access
Employees may access customer data whenever necessary.

2. Data Sharing
Customer information may be shared with external business partners.

3. Data Retention
Customer records will be retained indefinitely."
            rows={10}
            spellCheck={false}
          />
        </div>
      )}

      {/* Primary Action Button */}
      <div className="card-footer">
        <div className="footer-status-text">
          {!canAnalyze ? (
            <span className="text-warning">
              ⚠️ Upload at least 1 policy and enter contract clauses to enable analysis
            </span>
          ) : (
            <span className="text-success">
              ✓ Ready for grounded compliance analysis ({contractText.trim().length} characters)
            </span>
          )}
        </div>

        <button
          type="button"
          className="btn btn-analyze"
          disabled={!canAnalyze || isAnalyzing || isExtracting}
          onClick={onAnalyze}
        >
          {isAnalyzing ? (
            <>
              <RefreshCw className="spin" size={18} />
              <span>Analyzing Clauses with RAG...</span>
            </>
          ) : (
            <>
              <Play size={18} />
              <span>Analyze Contract</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
