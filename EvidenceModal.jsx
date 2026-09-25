import React from 'react';
import { 
  X, 
  FileText, 
  BookOpen, 
  AlertTriangle, 
  CheckCircle, 
  HelpCircle, 
  ShieldCheck, 
  ShieldAlert,
  Hash,
  Scale
} from 'lucide-react';

export default function EvidenceModal({ finding, onClose }) {
  if (!finding) return null;

  const isConflict = finding.status === 'Conflict';
  const isNotFound = finding.status === 'Not Found';
  const isCompliant = finding.status === 'Compliant';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-title-group">
            <div className={`modal-status-icon ${isConflict ? 'status-icon-conflict' : isNotFound ? 'status-icon-notfound' : 'status-icon-compliant'}`}>
              {isConflict && <AlertTriangle size={24} />}
              {isNotFound && <HelpCircle size={24} />}
              {isCompliant && <CheckCircle size={24} />}
            </div>
            <div>
              <div className="modal-tag-row">
                <span className="clause-id-badge">{finding.clause_id}</span>
                <span className={`badge ${
                  isConflict ? 'badge-status-conflict' : 
                  isNotFound ? 'badge-status-notfound' : 'badge-status-compliant'
                }`}>
                  {finding.status}
                </span>
                <span className={`badge ${
                  finding.risk === 'High' ? 'badge-risk-high' :
                  finding.risk === 'Medium' ? 'badge-risk-medium' :
                  finding.risk === 'Low' ? 'badge-risk-low' : 'badge-risk-unknown'
                }`}>
                  {finding.risk} Risk
                </span>
                <span className="badge badge-evidence-explicit">
                  Evidence: {finding.evidence_status}
                </span>
              </div>
              <h2 className="modal-title">{finding.clause_title}</h2>
            </div>
          </div>

          <button className="modal-close-btn" onClick={onClose} title="Close Evidence Viewer">
            <X size={20} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* Grounding Status Card */}
          <div className={`grounding-card ${isNotFound ? 'grounding-notfound' : 'grounding-verified'}`}>
            <div className="grounding-header">
              {isNotFound ? <ShieldAlert size={18} /> : <ShieldCheck size={18} />}
              <strong>{isNotFound ? 'Grounding Guardrail Active (Not Found)' : 'Verified Evidence-Grounded Finding'}</strong>
            </div>
            <p className="grounding-desc">
              {isNotFound 
                ? 'This clause was not found in the uploaded policy documents. The assistant refuses to guess or hallucinate policy rules without verifiable source text.'
                : `Retrieved from ${finding.source} (Page ${finding.page}) with semantic similarity score of ${(finding.similarity * 100).toFixed(1)}%.`
              }
            </p>
          </div>

          {/* Side-by-Side Comparison */}
          <div className="comparison-grid">
            {/* Contract Clause */}
            <div className="comparison-card contract-clause-card">
              <div className="comparison-header">
                <FileText size={16} className="text-indigo" />
                <h3>Contract Clause (Uploaded Contract)</h3>
              </div>
              <div className="quote-box contract-quote">
                <pre className="quote-text">{finding.contract_clause}</pre>
              </div>
              <div className="quote-footer">
                <span className="quote-source-tag">Source: Contract Input</span>
              </div>
            </div>

            {/* Policy Evidence */}
            <div className={`comparison-card policy-evidence-card ${isConflict ? 'border-conflict' : ''}`}>
              <div className="comparison-header">
                <BookOpen size={16} className={isNotFound ? 'text-amber' : 'text-cyan'} />
                <h3>Policy Evidence (Ground Truth)</h3>
              </div>
              <div className={`quote-box policy-quote ${isNotFound ? 'quote-empty' : ''}`}>
                <pre className="quote-text">{finding.policy_evidence}</pre>
              </div>
              <div className="quote-footer">
                <div className="evidence-metadata-pills">
                  <span className="meta-pill">
                    <strong>Source File:</strong> {finding.source}
                  </span>
                  <span className="meta-pill">
                    <Hash size={12} /> <strong>Page:</strong> {finding.page}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Reason & Legal Governance Analysis */}
          <div className="analysis-card">
            <div className="analysis-header">
              <Scale size={18} className="text-purple" />
              <h3>Compliance Reason & Analysis</h3>
            </div>
            <p className="analysis-body">{finding.explanation}</p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <div className="footer-disclaimer">
            Governed by zero-hallucination policy grounding • Source Page {finding.page}
          </div>
          <button className="btn btn-secondary" onClick={onClose}>
            Close Viewer
          </button>
        </div>
      </div>
    </div>
  );
}
