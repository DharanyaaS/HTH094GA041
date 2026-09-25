import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, RefreshCw, Trash2, Layers, BookOpen } from 'lucide-react';

export default function PolicyUploader({ 
  onUploadPolicies, 
  onLoadDemoPolicy, 
  onResetPolicies,
  indexedSources, 
  isLoading,
  uploadStatus 
}) {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files) {
      const filesArr = Array.from(e.target.files).filter(f => f.name.toLowerCase().endsWith('.pdf'));
      setSelectedFiles(prev => [...prev, ...filesArr]);
    }
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
    if (e.dataTransfer.files) {
      const filesArr = Array.from(e.dataTransfer.files).filter(f => f.name.toLowerCase().endsWith('.pdf'));
      setSelectedFiles(prev => [...prev, ...filesArr]);
    }
  };

  const removeFile = (idx) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== idx));
  };

  const handleUploadSubmit = () => {
    if (selectedFiles.length > 0) {
      onUploadPolicies(selectedFiles);
      setSelectedFiles([]);
    }
  };

  return (
    <div className="card policy-card">
      <div className="card-header">
        <div className="card-title-group">
          <BookOpen className="card-header-icon" size={20} />
          <div>
            <h2 className="card-title">1. Policy Documents</h2>
            <p className="card-subtitle">Upload company policies or regulatory guidelines in PDF</p>
          </div>
        </div>

        <div className="card-actions">
          <button 
            type="button" 
            className="btn btn-secondary btn-sm"
            onClick={onLoadDemoPolicy}
            disabled={isLoading}
            title="Load default Data Protection Policy PDF"
          >
            Load Demo Policy
          </button>
          {indexedSources && indexedSources.length > 0 && (
            <button 
              type="button" 
              className="btn btn-danger-ghost btn-sm"
              onClick={onResetPolicies}
              disabled={isLoading}
              title="Reset Vector Store"
            >
              <Trash2 size={14} />
            </button>
          )}
        </div>
      </div>

      <div 
        className={`dropzone ${dragActive ? 'dropzone-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input 
          ref={fileInputRef}
          type="file" 
          multiple 
          accept=".pdf,application/pdf"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        <UploadCloud size={36} className="dropzone-icon" />
        <p className="dropzone-text">
          <strong>Click to select PDF files</strong> or drag and drop here
        </p>
        <span className="dropzone-hint">Supports multiple policy & regulation PDFs</span>
      </div>

      {selectedFiles.length > 0 && (
        <div className="selected-files-list">
          <div className="selected-files-header">
            <span>Selected for Upload ({selectedFiles.length})</span>
            <button 
              className="btn btn-primary btn-sm"
              onClick={handleUploadSubmit}
              disabled={isLoading}
            >
              {isLoading ? <RefreshCw className="spin" size={14} /> : null}
              Upload Policies
            </button>
          </div>
          {selectedFiles.map((file, idx) => (
            <div key={idx} className="file-item file-item-pending">
              <FileText size={16} className="file-icon" />
              <div className="file-info">
                <span className="file-name">{file.name}</span>
                <span className="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
              </div>
              <button 
                type="button" 
                className="file-remove-btn"
                onClick={(e) => { e.stopPropagation(); removeFile(idx); }}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Indexed Documents Status */}
      <div className="indexed-section">
        <h3 className="section-label">
          <Layers size={15} />
          Indexed In Vector Store ({indexedSources?.length || 0})
        </h3>
        
        {(!indexedSources || indexedSources.length === 0) ? (
          <div className="empty-state-hint">
            No policy documents currently indexed. Please upload or load demo policy.
          </div>
        ) : (
          <div className="indexed-list">
            {indexedSources.map((doc, idx) => (
              <div key={idx} className="file-item file-item-indexed">
                <FileText size={16} className="file-icon text-indigo" />
                <div className="file-info">
                  <span className="file-name">{doc.source}</span>
                  <div className="file-meta-tags">
                    <span className="badge badge-meta">~{doc.max_page || 1} Pages</span>
                    <span className="badge badge-indigo">{doc.chunks} Sections Indexed</span>
                  </div>
                </div>
                <CheckCircle2 size={16} className="text-emerald" title="Stored in ChromaDB" />
              </div>
            ))}
          </div>
        )}
      </div>

      {uploadStatus && (
        <div className={`status-alert ${uploadStatus.type === 'error' ? 'alert-error' : 'alert-success'}`}>
          {uploadStatus.type === 'error' ? <AlertCircle size={16} /> : <CheckCircle2 size={16} />}
          <span>{uploadStatus.message}</span>
        </div>
      )}
    </div>
  );
}
