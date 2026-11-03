import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FiSearch, FiShield, FiAlertTriangle, FiInfo, FiUpload,
  FiFileText, FiDownload, FiCheck, FiX, FiRefreshCw
} from 'react-icons/fi';
import toast from 'react-hot-toast';
import { analysis as analysisApi } from '../services/api';
import Navbar from '../components/Navbar';

const EXAMPLE_URLS = [
  { url: 'https://www.google.com',           label: 'Likely Legitimate', color: 'var(--accent-success)' },
  { url: 'https://github.com',               label: 'Likely Legitimate', color: 'var(--accent-success)' },
  { url: 'http://secure-paypal.login.xyz',   label: 'Suspicious',        color: 'var(--accent-warning)' },
  { url: 'http://192.168.1.1/bank/login',    label: 'High Risk',         color: 'var(--accent-danger)'  },
];

export default function Analyze() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('single'); // 'single' | 'bulk'

  // Single URL state
  const [url, setUrl]           = useState('');
  const [deepScan, setDeepScan] = useState(false);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState('');

  // Bulk File state
  const [selectedFile, setSelectedFile] = useState(null);
  const [batchLoading, setBatchLoading] = useState(false);
  const [batchResult, setBatchResult]   = useState(null);
  const [batchError, setBatchError]     = useState('');

  // ── Handle Single URL Submit ─────────────────────────────────────────────
  const handleSubmitSingle = async (e) => {
    e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed) { setError('Please enter a URL to analyze.'); return; }
    if (trimmed.length > 2048) { setError('URL is too long (max 2048 characters).'); return; }
    setError('');
    setLoading(true);
    try {
      const res = await analysisApi.predict({ url: trimmed, deep_scan: deepScan });
      toast.success('Analysis complete!');
      navigate(`/result/${res.data.id}`);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Analysis failed. Please try again.';
      setError(typeof msg === 'string' ? msg : 'Analysis failed.');
    } finally {
      setLoading(false);
    }
  };

  // ── Handle Bulk File Upload ──────────────────────────────────────────────
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const name = file.name.toLowerCase();
      if (!name.endsWith('.csv') && !name.endsWith('.txt')) {
        setBatchError('Please select a valid .csv or .txt file.');
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      setBatchError('');
      setBatchResult(null);
    }
  };

  const handleBatchSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setBatchError('Please select a CSV or TXT file to upload.');
      return;
    }
    setBatchError('');
    setBatchLoading(true);
    setBatchResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await analysisApi.predictBatchFile(formData);
      setBatchResult(res.data);
      toast.success(`Scanned ${res.data.total_scanned} URLs successfully!`);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Batch analysis failed. Please try again.';
      setBatchError(typeof msg === 'string' ? msg : 'Batch analysis failed.');
    } finally {
      setBatchLoading(false);
    }
  };

  const downloadSampleCSV = () => {
    const csvContent = 'data:text/csv;charset=utf-8,url\nhttps://google.com\nhttp://bank-verify-login.xyz\nhttps://github.com\nhttp://192.168.1.1/paypal-account\n';
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'sample_urls.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const exportBatchResultsCSV = () => {
    if (!batchResult || !batchResult.results) return;
    let csv = 'URL,Prediction,Probability,Risk Score,Risk Level\n';
    batchResult.results.forEach(r => {
      csv += `"${r.url}","${r.prediction}",${r.probability},${r.risk_score},"${r.risk_level}"\n`;
    });
    const encodedUri = encodeURI('data:text/csv;charset=utf-8,' + csv);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `batch_results_${batchResult.filename}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />

      <div className="page-wrapper" style={{ flex: 1 }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ marginBottom: '0.5rem' }}>
            <span className="gradient-text">URL Phishing & Risk</span> Analysis
          </h1>
          <p>Scan a single website URL or upload a batch CSV file to analyze multiple links at once.</p>
        </div>

        {/* Tab Navigation */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '2rem' }}>
          <button
            className={`btn ${activeTab === 'single' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('single')}
            style={{ borderRadius: 'var(--radius-full)', padding: '0.625rem 1.5rem' }}
          >
            <FiSearch /> Single URL Scan
          </button>
          <button
            className={`btn ${activeTab === 'bulk' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('bulk')}
            style={{ borderRadius: 'var(--radius-full)', padding: '0.625rem 1.5rem' }}
          >
            <FiUpload /> Bulk File Scanner (.CSV / .TXT)
          </button>
        </div>

        {/* ── TAB 1: SINGLE URL SCAN ────────────────────────────────────────── */}
        {activeTab === 'single' && (
          <>
            <div className="card animate-slide-up" style={{ maxWidth: 760, margin: '0 auto 2rem', padding: '2rem' }}>
              {error && <div className="alert alert-danger" style={{ marginBottom: '1.25rem' }}>{error}</div>}

              <form onSubmit={handleSubmitSingle}>
                <label className="input-label" style={{ marginBottom: '0.5rem', display: 'block', fontSize: '0.9rem' }}>
                  Website URL
                </label>
                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                  <div style={{ position: 'relative', flex: 1, minWidth: 240 }}>
                    <FiSearch style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', fontSize: '1.1rem' }} />
                    <input
                      type="text"
                      value={url}
                      onChange={(e) => { setUrl(e.target.value); setError(''); }}
                      placeholder="https://example.com or paste any URL here"
                      className="input-field"
                      style={{ paddingLeft: '2.75rem', fontSize: '0.9375rem' }}
                      disabled={loading}
                    />
                  </div>
                  <button type="submit" className="btn btn-primary btn-lg" disabled={loading} style={{ minWidth: 140 }}>
                    {loading
                      ? <><span className="spinner" /> Scanning…</>
                      : <><FiShield /> Analyze</>
                    }
                  </button>
                </div>

                {/* Deep Scan Toggle */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '1.25rem' }}>
                  <label className="toggle-switch">
                    <input type="checkbox" checked={deepScan} onChange={(e) => setDeepScan(e.target.checked)} />
                    <span className="toggle-slider" />
                  </label>
                  <div>
                    <span style={{ fontSize: '0.9rem', fontWeight: 500, color: 'var(--text-primary)' }}>
                      Deep Scan
                    </span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
                      (fetches webpage content for additional analysis)
                    </span>
                  </div>
                </div>
              </form>

              {loading && (
                <div style={{
                  marginTop: '1.5rem', padding: '1.25rem',
                  background: 'rgba(0,212,255,0.05)',
                  border: '1px solid rgba(0,212,255,0.15)',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', color: 'var(--accent-cyan)' }}>
                    <span className="spinner" />
                    <span style={{ fontWeight: 500 }}>Extracting features & running ML analysis…</span>
                  </div>
                </div>
              )}
            </div>

            {/* Example URLs */}
            <div style={{ maxWidth: 760, margin: '0 auto 2rem' }}>
              <h4 style={{ marginBottom: '0.875rem', color: 'var(--text-secondary)', fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Try Example URLs
              </h4>
              <div className="grid-2">
                {EXAMPLE_URLS.map(({ url: exUrl, label, color }) => (
                  <button
                    key={exUrl}
                    onClick={() => setUrl(exUrl)}
                    disabled={loading}
                    style={{
                      background: 'var(--bg-card)',
                      border: '1px solid var(--border-card)',
                      borderRadius: 'var(--radius-md)',
                      padding: '0.875rem 1rem',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'all 0.2s',
                    }}
                  >
                    <div style={{ fontSize: '0.75rem', color, fontWeight: 600, marginBottom: '0.25rem' }}>{label}</div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem', color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {exUrl}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}

        {/* ── TAB 2: BULK FILE SCANNER ────────────────────────────────────── */}
        {activeTab === 'bulk' && (
          <div className="card animate-slide-up" style={{ maxWidth: 840, margin: '0 auto 2rem', padding: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <h3 style={{ margin: 0 }}>Batch File Upload & URL Analysis</h3>
                <p style={{ margin: '0.25rem 0 0', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                  Upload a `.csv` or `.txt` file containing website URLs to analyze all of them at once.
                </p>
              </div>
              <button onClick={downloadSampleCSV} className="btn btn-secondary btn-sm">
                <FiDownload /> Download Sample CSV
              </button>
            </div>

            {batchError && <div className="alert alert-danger" style={{ marginBottom: '1.25rem' }}>{batchError}</div>}

            <form onSubmit={handleBatchSubmit}>
              {/* File Upload Box */}
              <div style={{
                border: '2px dashed var(--border-hover)',
                borderRadius: 'var(--radius-md)',
                padding: '2.5rem 1.5rem',
                textAlign: 'center',
                background: 'rgba(0,0,0,0.2)',
                cursor: 'pointer',
                marginBottom: '1.5rem',
              }}>
                <input
                  type="file"
                  accept=".csv,.txt"
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                  id="batch-file-input"
                />
                <label htmlFor="batch-file-input" style={{ cursor: 'pointer' }}>
                  <FiFileText size={40} style={{ color: 'var(--accent-cyan)', marginBottom: '0.75rem' }} />
                  <div style={{ fontWeight: 600, fontSize: '1rem', color: 'var(--text-primary)' }}>
                    {selectedFile ? selectedFile.name : 'Click to select or drag a CSV/TXT file here'}
                  </div>
                  <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.375rem' }}>
                    Supported formats: .CSV, .TXT (Max 50 URLs per file)
                  </div>
                </label>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                {selectedFile && (
                  <button
                    type="button"
                    onClick={() => { setSelectedFile(null); setBatchResult(null); }}
                    className="btn btn-secondary"
                    disabled={batchLoading}
                  >
                    Clear File
                  </button>
                )}
                <button type="submit" className="btn btn-primary btn-lg" disabled={!selectedFile || batchLoading}>
                  {batchLoading ? (
                    <><span className="spinner" /> Analyzing Batch…</>
                  ) : (
                    <><FiUpload /> Start Batch Analysis</>
                  )}
                </button>
              </div>
            </form>

            {/* Batch Results Output */}
            {batchResult && (
              <div style={{ marginTop: '2.5rem', borderTop: '1px solid var(--border-card)', paddingTop: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
                  <h4>Batch Results ({batchResult.total_scanned} URLs)</h4>
                  <button onClick={exportBatchResultsCSV} className="btn btn-primary btn-sm">
                    <FiDownload /> Export Results CSV
                  </button>
                </div>

                {/* Summary Badges */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                  <div style={{ background: 'rgba(255,255,255,0.03)', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>TOTAL SCANNED</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>{batchResult.total_scanned}</div>
                  </div>
                  <div style={{ background: 'rgba(239,68,68,0.1)', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--accent-danger)' }}>PHISHING</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-danger)' }}>{batchResult.phishing_count}</div>
                  </div>
                  <div style={{ background: 'rgba(16,185,129,0.1)', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--accent-success)' }}>LEGITIMATE</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-success)' }}>{batchResult.legitimate_count}</div>
                  </div>
                  <div style={{ background: 'rgba(245,158,11,0.1)', padding: '1rem', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--accent-warning)' }}>HIGH/CRITICAL RISK</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-warning)' }}>{batchResult.high_risk_count}</div>
                  </div>
                </div>

                {/* Table of scanned results */}
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border-card)', textAlign: 'left', color: 'var(--text-muted)' }}>
                        <th style={{ padding: '0.75rem 0.5rem' }}>URL</th>
                        <th style={{ padding: '0.75rem 0.5rem' }}>Prediction</th>
                        <th style={{ padding: '0.75rem 0.5rem' }}>Risk Score</th>
                        <th style={{ padding: '0.75rem 0.5rem' }}>Risk Level</th>
                      </tr>
                    </thead>
                    <tbody>
                      {batchResult.results.map((r, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '0.75rem 0.5rem', maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontFamily: 'var(--font-mono)' }}>
                            {r.url}
                          </td>
                          <td style={{ padding: '0.75rem 0.5rem' }}>
                            <span className={`badge ${r.prediction === 'PHISHING' ? 'badge-danger' : 'badge-success'}`}>
                              {r.prediction}
                            </span>
                          </td>
                          <td style={{ padding: '0.75rem 0.5rem', fontWeight: 600 }}>
                            {r.risk_score} / 100
                          </td>
                          <td style={{ padding: '0.75rem 0.5rem' }}>
                            <span style={{
                              fontSize: '0.75rem', padding: '0.2rem 0.6rem', borderRadius: 'var(--radius-full)', fontWeight: 600,
                              background: r.risk_level === 'Critical' ? 'rgba(239,68,68,0.2)' : r.risk_level === 'High' ? 'rgba(245,158,11,0.2)' : 'rgba(16,185,129,0.2)',
                              color: r.risk_level === 'Critical' ? 'var(--accent-danger)' : r.risk_level === 'High' ? 'var(--accent-warning)' : 'var(--accent-success)',
                            }}>
                              {r.risk_level}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Info Box */}
        <div className="alert alert-info" style={{ maxWidth: 840, margin: '0 auto' }}>
          <FiInfo size={18} style={{ flexShrink: 0 }} />
          <div style={{ fontSize: '0.875rem' }}>
            <strong>What we analyze:</strong> URL structure (length, subdomains, special characters),
            domain signals (TLD, IP address detection, URL shorteners), keyword patterns,
            and optionally webpage content. In Bulk Mode, you can upload up to 50 URLs in a CSV or TXT file for automated batch classification.
          </div>
        </div>
      </div>
    </div>
  );
}
