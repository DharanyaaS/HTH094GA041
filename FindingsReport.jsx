import React, { useState } from 'react';
import { 
  AlertTriangle, 
  CheckCircle, 
  HelpCircle, 
  Eye, 
  FileText, 
  Search, 
  SlidersHorizontal,
  FileCheck2,
  ExternalLink
} from 'lucide-react';

export default function FindingsReport({ findings, onSelectFinding, activeFilter, onFilterChange }) {
  const [searchQuery, setSearchQuery] = useState('');

  if (!findings || findings.length === 0) {
    return (
      <div className="card findings-empty-card">
        <FileCheck2 size={48} className="empty-icon text-muted" />
        <h3>No Compliance Analysis Yet</h3>
        <p>Upload your policy documents and contract above, then click <strong>Analyze Contract</strong> to generate the grounded compliance report.</p>
      </div>
    );
  }

  // Filter findings based on activeFilter and searchQuery
  const filteredFindings = findings.filter(f => {
    // 1. Category / Stat filter
    if (activeFilter === 'Conflict' && f.status !== 'Conflict') return false;
    if (activeFilter === 'Compliant' && f.status !== 'Compliant') return false;
    if (activeFilter === 'Not Found' && f.status !== 'Not Found') return false;
    if (activeFilter === 'High' && f.risk !== 'High') return false;
    if (activeFilter === 'Medium' && f.risk !== 'Medium') return false;
    if (activeFilter === 'Low' && f.risk !== 'Low') return false;

    // 2. Search query filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchClause = (f.contract_clause || '').toLowerCase().includes(q);
      const matchTitle = (f.clause_title || '').toLowerCase().includes(q);
      const matchPolicy = (f.policy_evidence || '').toLowerCase().includes(q);
      const matchExplanation = (f.explanation || '').toLowerCase().includes(q);
      return matchClause || matchTitle || matchPolicy || matchExplanation;
    }

    return true;
  });

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'Conflict': return 'badge-status-conflict';
      case 'Compliant': return 'badge-status-compliant';
      case 'Not Found': return 'badge-status-notfound';
      default: return 'badge-status-default';
    }
  };

  const getRiskBadgeClass = (risk) => {
    switch (risk) {
      case 'High': return 'badge-risk-high';
      case 'Medium': return 'badge-risk-medium';
      case 'Low': return 'badge-risk-low';
      default: return 'badge-risk-unknown';
    }
  };

  const getEvidenceStatusBadgeClass = (evidenceStatus) => {
    switch (evidenceStatus) {
      case 'Explicitly Stated': return 'badge-evidence-explicit';
      case 'Inferred': return 'badge-evidence-inferred';
      default: return 'badge-evidence-notfound';
    }
  };

  return (
    <div className="card findings-card">
      <div className="findings-header">
        <div>
          <h2 className="card-title">Contract Compliance Findings ({findings.length})</h2>
          <p className="card-subtitle">Every clause checked against indexed policy requirements with source traceability</p>
        </div>

        <div className="findings-controls">
          <div className="search-input-wrapper">
            <Search size={15} className="search-icon" />
            <input
              type="text"
              placeholder="Search findings, clauses, or policy text..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            {searchQuery && (
              <button className="search-clear-btn" onClick={() => setSearchQuery('')}>✕</button>
            )}
          </div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="filter-pill-bar">
        {['ALL', 'Conflict', 'High', 'Not Found', 'Compliant'].map((filterKey) => (
          <button
            key={filterKey}
            type="button"
            className={`filter-pill ${activeFilter === filterKey ? 'filter-pill-active' : ''}`}
            onClick={() => onFilterChange(filterKey)}
          >
            {filterKey === 'ALL' ? 'All Findings' : filterKey}
          </button>
        ))}
        <span className="results-count-tag">
          Showing {filteredFindings.length} of {findings.length}
        </span>
      </div>

      {/* Findings Table */}
      <div className="table-responsive">
        <table className="findings-table">
          <thead>
            <tr>
              <th style={{ width: '18%' }}>Clause</th>
              <th style={{ width: '11%' }}>Status</th>
              <th style={{ width: '10%' }}>Risk</th>
              <th style={{ width: '13%' }}>Evidence Status</th>
              <th style={{ width: '22%' }}>Policy Evidence</th>
              <th style={{ width: '10%' }}>Source & Page</th>
              <th style={{ width: '16%' }}>Explanation & Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredFindings.map((finding, idx) => (
              <tr 
                key={idx} 
                className={`finding-row ${finding.status === 'Conflict' ? 'row-conflict' : ''}`}
                onClick={() => onSelectFinding(finding)}
              >
                {/* Clause Column */}
                <td>
                  <div className="clause-cell">
                    <span className="clause-id-badge">{finding.clause_id}</span>
                    <strong className="clause-title">{finding.clause_title}</strong>
                    <div className="clause-preview" title={finding.contract_clause}>
                      "{finding.contract_clause?.length > 70 
                        ? finding.contract_clause.slice(0, 70) + '...' 
                        : finding.contract_clause}"
                    </div>
                  </div>
                </td>

                {/* Status Column */}
                <td>
                  <span className={`badge ${getStatusBadgeClass(finding.status)}`}>
                    {finding.status === 'Conflict' && <AlertTriangle size={12} />}
                    {finding.status === 'Compliant' && <CheckCircle size={12} />}
                    {finding.status === 'Not Found' && <HelpCircle size={12} />}
                    {finding.status}
                  </span>
                </td>

                {/* Risk Column */}
                <td>
                  <span className={`badge ${getRiskBadgeClass(finding.risk)}`}>
                    {finding.risk}
                  </span>
                </td>

                {/* Evidence Status */}
                <td>
                  <span className={`badge ${getEvidenceStatusBadgeClass(finding.evidence_status)}`}>
                    {finding.evidence_status}
                  </span>
                </td>

                {/* Policy Evidence */}
                <td>
                  <div className="evidence-snippet-cell" title={finding.policy_evidence}>
                    {finding.status === 'Not Found' ? (
                      <em className="text-muted">No relevant policy requirement found.</em>
                    ) : (
                      <span>{finding.policy_evidence?.length > 90 
                        ? finding.policy_evidence.slice(0, 90) + '...' 
                        : finding.policy_evidence}</span>
                    )}
                  </div>
                </td>

                {/* Source & Page */}
                <td>
                  {finding.source !== 'N/A' ? (
                    <div className="source-cell">
                      <span className="source-filename" title={finding.source}>
                        {finding.source}
                      </span>
                      <span className="badge badge-page">
                        Page {finding.page}
                      </span>
                    </div>
                  ) : (
                    <span className="text-muted">N/A</span>
                  )}
                </td>

                {/* Explanation & Action */}
                <td>
                  <div className="explanation-action-cell">
                    <p className="explanation-text" title={finding.explanation}>
                      {finding.explanation?.length > 75 
                        ? finding.explanation.slice(0, 75) + '...' 
                        : finding.explanation}
                    </p>
                    <button 
                      type="button" 
                      className="btn btn-view-evidence btn-xs"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectFinding(finding);
                      }}
                    >
                      <Eye size={12} />
                      View Evidence
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
