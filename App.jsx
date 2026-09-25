import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import PolicyUploader from './components/PolicyUploader';
import ContractInput from './components/ContractInput';
import StatsOverview from './components/StatsOverview';
import FindingsReport from './components/FindingsReport';
import EvidenceModal from './components/EvidenceModal';
import './App.css';

const API_BASE = 'http://127.0.0.1:8000';

export default function App() {
  const [health, setHealth] = useState(null);
  const [contractText, setContractText] = useState('');
  const [contractFilename, setContractFilename] = useState('sample_contract.txt');
  const [isLoading, setIsLoading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [report, setReport] = useState(null);
  const [activeFilter, setActiveFilter] = useState('ALL');
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [threshold, setThreshold] = useState(0.55);

  const fetchHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/health`);
      if (res.ok) {
        const data = await res.json();
        setHealth(data);
      } else {
        setHealth({ status: 'offline', indexed_chunks: 0, indexed_sources: [] });
      }
    } catch {
      setHealth({ status: 'offline', indexed_chunks: 0, indexed_sources: [] });
    }
  };

  useEffect(() => {
    fetchHealth();
    // Periodically sync health / chunks
    const timer = setInterval(fetchHealth, 8000);
    return () => clearInterval(timer);
  }, []);

  const handleUploadPolicies = async (files) => {
    setIsLoading(true);
    setUploadStatus(null);
    try {
      const formData = new FormData();
      for (const file of files) {
        formData.append('files', file);
      }

      const res = await fetch(`${API_BASE}/upload-policy`, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to upload policies.');
      }

      setUploadStatus({
        type: 'success',
        message: `Successfully indexed ${data.processed?.length || 1} policy document(s) into ChromaDB.`
      });
      fetchHealth();
    } catch (err) {
      setUploadStatus({
        type: 'error',
        message: err.message || 'An error occurred while uploading policy documents.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadDemoPolicy = async () => {
    setIsLoading(true);
    setUploadStatus(null);
    try {
      const res = await fetch(`${API_BASE}/demo-files/policy`);
      if (!res.ok) {
        throw new Error('Demo policy file not found on server.');
      }
      const blob = await res.blob();
      const file = new File([blob], 'test_policy.pdf', { type: 'application/pdf' });
      await handleUploadPolicies([file]);
    } catch (err) {
      setUploadStatus({
        type: 'error',
        message: `Could not load demo policy: ${err.message}`
      });
      setIsLoading(false);
    }
  };

  const handleLoadDemoContract = async () => {
    try {
      const res = await fetch(`${API_BASE}/demo-files/contract`);
      if (!res.ok) {
        throw new Error('Demo contract file not found.');
      }
      const data = await res.json();
      setContractText(data.content);
      setContractFilename(data.filename || 'sample_contract.txt');
    } catch {
      // Fallback local contract template
      setContractText(
`Company Customer Data Agreement

1. Data Access
Employees may access customer data whenever necessary.

2. Data Sharing
Customer information may be shared with external business partners when required for business operations.

3. Data Retention
Customer records will be retained indefinitely.

4. Data Encryption
Customer data must be encrypted using AES-256.`
      );
      setContractFilename('sample_contract.txt');
    }
  };

  const handleResetPolicies = async () => {
    if (!window.confirm('Are you sure you want to reset and clear the ChromaDB policy store?')) return;
    try {
      await fetch(`${API_BASE}/reset-policies`, { method: 'POST' });
      fetchHealth();
      setReport(null);
      setUploadStatus({ type: 'success', message: 'Policy store has been cleared.' });
    } catch (err) {
      setUploadStatus({ type: 'error', message: 'Failed to reset store.' });
    }
  };

  const handleAnalyze = async () => {
    if (!contractText.trim()) return;
    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('contract_text', contractText);
      formData.append('threshold', threshold.toString());

      const res = await fetch(`${API_BASE}/analyze-contract`, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Contract analysis failed.');
      }

      setReport(data);
      setActiveFilter('ALL');
    } catch (err) {
      alert(`Analysis Error: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const canAnalyze = (health?.indexed_chunks > 0) && contractText.trim().length > 0;

  return (
    <div className="app-layout">
      <Navbar health={health} onRefreshHealth={fetchHealth} />

      <main className="main-content">
        {/* Top Workflow Configuration Section */}
        <section className="workflow-section">
          <div className="workflow-grid">
            <PolicyUploader
              onUploadPolicies={handleUploadPolicies}
              onLoadDemoPolicy={handleLoadDemoPolicy}
              onResetPolicies={handleResetPolicies}
              indexedSources={health?.indexed_sources || []}
              isLoading={isLoading}
              uploadStatus={uploadStatus}
            />

            <ContractInput
              contractText={contractText}
              setContractText={setContractText}
              contractFilename={contractFilename}
              setContractFilename={setContractFilename}
              onLoadDemoContract={handleLoadDemoContract}
              onAnalyze={handleAnalyze}
              isAnalyzing={isAnalyzing}
              canAnalyze={canAnalyze}
              threshold={threshold}
              setThreshold={setThreshold}
              apiBase={API_BASE}
            />
          </div>
        </section>

        {/* Results Section */}
        {report && (
          <section className="report-section">
            <StatsOverview
              summary={report.summary}
              activeFilter={activeFilter}
              onFilterChange={setActiveFilter}
            />

            <FindingsReport
              findings={report.findings}
              onSelectFinding={setSelectedFinding}
              activeFilter={activeFilter}
              onFilterChange={setActiveFilter}
            />
          </section>
        )}
      </main>

      {/* Evidence Viewer Modal */}
      {selectedFinding && (
        <EvidenceModal
          finding={selectedFinding}
          onClose={() => setSelectedFinding(null)}
        />
      )}
    </div>
  );
}
