import React from 'react';
import { ShieldAlert, Database, CheckCircle2, AlertCircle } from 'lucide-react';

export default function Navbar({ health, onRefreshHealth }) {
  const isHealthy = health?.status === 'healthy';
  const totalChunks = health?.indexed_chunks || 0;

  return (
    <header className="navbar">
      <div className="navbar-container">
        <div className="brand-section">
          <div className="brand-icon-wrapper">
            <ShieldAlert className="brand-icon" size={28} />
          </div>
          <div className="brand-titles">
            <h1 className="brand-title">Grounded Multi-Document Compliance Assistant</h1>
            <p className="brand-subtitle">Evidence-based contract compliance checking</p>
          </div>
        </div>

        <div className="navbar-meta">
          <div className="meta-badge vector-db-badge" title="ChromaDB Vector Store Status">
            <Database size={15} />
            <span>{totalChunks} Policy Section{totalChunks !== 1 ? 's' : ''} Indexed</span>
          </div>

          <div 
            className={`meta-badge status-badge ${isHealthy ? 'badge-online' : 'badge-offline'}`}
            onClick={onRefreshHealth}
            title="Click to check backend API health"
          >
            {isHealthy ? <CheckCircle2 size={15} /> : <AlertCircle size={15} />}
            <span>{isHealthy ? 'API Connected' : 'Connecting API...'}</span>
          </div>
        </div>
      </div>

      <div className="disclaimer-banner">
        <span className="disclaimer-prefix">GOVERNANCE NOTICE:</span> This tool provides document-based compliance assistance and does not replace professional legal advice.
      </div>
    </header>
  );
}
