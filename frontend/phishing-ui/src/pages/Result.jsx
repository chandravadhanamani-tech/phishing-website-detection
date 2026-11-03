import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FiAlertTriangle, FiCheckCircle, FiArrowLeft, FiSearch, FiCopy } from 'react-icons/fi';
import toast from 'react-hot-toast';
import { analysis as analysisApi } from '../services/api';
import Navbar from '../components/Navbar';
import RiskMeter from '../components/RiskMeter';
import FeatureChart from '../components/FeatureChart';

function SeverityBadge({ severity }) {
  const cls = {
    Critical: 'badge-critical', High: 'badge-high',
    Medium: 'badge-medium', Low: 'badge-low',
  }[severity] || 'badge-low';
  return <span className={`badge ${cls}`}>{severity}</span>;
}

function FeatureRow({ label, value }) {
  const display = value === null || value === undefined ? '—'
    : typeof value === 'boolean' ? (value ? 'Yes' : 'No')
    : typeof value === 'number' ? (Number.isInteger(value) ? value : value.toFixed(4))
    : value;
  return (
    <tr>
      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>{label}</td>
      <td style={{ fontWeight: 500, color: typeof value === 'boolean' && value ? 'var(--accent-warning)' : 'var(--text-primary)', fontFamily: 'var(--font-mono)', fontSize: '0.8125rem' }}>
        {String(display)}
      </td>
    </tr>
  );
}

export default function Result() {
  const { id }    = useParams();
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState('');
  const [showFeatures, setShowFeatures] = useState(false);

  useEffect(() => {
    analysisApi.getById(id)
      .then(res => setData(res.data))
      .catch(() => setError('Could not load analysis result.'))
      .finally(() => setLoading(false));
  }, [id]);

  const copyUrl = () => {
    navigator.clipboard.writeText(data?.url || '');
    toast.success('URL copied to clipboard');
  };

  if (loading) return (
    <div style={{ minHeight: '100vh' }}>
      <Navbar />
      <div className="loading-overlay"><div className="spinner spinner-lg" /><p>Loading result…</p></div>
    </div>
  );

  if (error || !data) return (
    <div style={{ minHeight: '100vh' }}>
      <Navbar />
      <div className="page-wrapper">
        <div className="alert alert-danger">{error || 'Result not found.'}</div>
        <Link to="/analyze" className="btn btn-secondary" style={{ marginTop: '1rem' }}>
          <FiArrowLeft /> Analyze Another
        </Link>
      </div>
    </div>
  );

  const isPhishing = data.prediction === 'PHISHING';
  const pct        = Math.round(data.probability * 100);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <div className="page-wrapper page-enter">
        {/* Back */}
        <Link to="/analyze" className="btn btn-ghost btn-sm" style={{ marginBottom: '1.5rem', display: 'inline-flex' }}>
          <FiArrowLeft /> Back to Analysis
        </Link>

        {/* ── Prediction Banner ── */}
        <div className={isPhishing ? 'prediction-phishing' : 'prediction-legitimate'}
          style={{ padding: '2rem', marginBottom: '1.5rem', textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>
            {isPhishing ? '⛔' : '✅'}
          </div>
          <h2 style={{ fontSize: '2rem', marginBottom: '0.375rem', color: isPhishing ? '#f87171' : '#34d399' }}>
            {data.prediction}
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
            Phishing probability: <strong style={{ color: isPhishing ? '#f87171' : '#34d399' }}>{pct}%</strong>
            {' · '}
            Model: <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.875rem' }}>{data.model_used || 'xgboost'}</span>
            {data.analysis_time_ms && ` · ${data.analysis_time_ms}ms`}
          </p>

          {/* URL */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginTop: '1rem' }}>
            <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0.375rem 0.75rem', borderRadius: 'var(--radius-sm)', fontSize: '0.875rem', maxWidth: 520, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', display: 'block' }}>
              {data.url}
            </code>
            <button onClick={copyUrl} className="btn btn-ghost btn-sm"><FiCopy /></button>
          </div>
        </div>

        {/* ── Risk Score + Distribution ── */}
        <div className="grid-2" style={{ marginBottom: '1.5rem', alignItems: 'start' }}>
          {/* Risk Meter */}
          <div className="card" style={{ textAlign: 'center' }}>
            <h4 style={{ marginBottom: '1rem' }}>Risk Assessment</h4>
            <RiskMeter score={data.risk_score} riskLevel={data.risk_level} />
          </div>

          {/* Risk Factors */}
          <div className="card">
            <h4 style={{ marginBottom: '1rem' }}>
              Detected Risk Factors
              {' '}
              <span style={{ fontSize: '0.875rem', fontWeight: 400, color: 'var(--text-muted)' }}>
                ({data.risk_factors?.length || 0})
              </span>
            </h4>
            {data.risk_factors?.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {data.risk_factors.map((rf, i) => (
                  <div key={i} style={{
                    background: 'var(--bg-secondary)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '0.75rem',
                    borderLeft: `3px solid ${
                      rf.severity === 'Critical' ? 'var(--accent-danger)' :
                      rf.severity === 'High' ? 'var(--accent-orange)' :
                      rf.severity === 'Medium' ? 'var(--accent-warning)' : 'var(--accent-blue)'
                    }`,
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>{rf.factor}</span>
                      <SeverityBadge severity={rf.severity} />
                    </div>
                    <p style={{ fontSize: '0.8125rem', margin: 0 }}>{rf.description}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                No significant risk factors detected for this URL.
              </p>
            )}
          </div>
        </div>

        {/* ── SHAP Explanations ── */}
        {data.shap_features?.length > 0 && (
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <h4 style={{ marginBottom: '0.375rem' }}>AI Explanation (SHAP Feature Contributions)</h4>
            <p style={{ fontSize: '0.875rem', marginBottom: '1.25rem' }}>
              Red bars push the prediction toward <strong style={{ color: '#f87171' }}>PHISHING</strong>.
              Green bars push toward <strong style={{ color: '#34d399' }}>LEGITIMATE</strong>.
            </p>
            <FeatureChart features={data.shap_features.slice(0, 10)} />
            {data.shap_features[0]?.shap_value !== undefined && (
              <div className="alert alert-info" style={{ marginTop: '1rem', fontSize: '0.8125rem' }}>
                ℹ️ These SHAP values show each feature's contribution to the prediction.
                This is not absolute proof of malicious intent — it is a machine learning interpretation.
              </div>
            )}
          </div>
        )}

        {/* ── Recommended Action ── */}
        {data.recommended_action && (
          <div className={`alert ${isPhishing ? 'alert-danger' : 'alert-success'}`} style={{ marginBottom: '1.5rem', fontSize: '0.9rem', lineHeight: 1.6 }}>
            <div>
              <strong>Recommended Action</strong>
              <p style={{ margin: '0.375rem 0 0', color: 'inherit' }}>{data.recommended_action}</p>
            </div>
          </div>
        )}

        {/* ── All Extracted Features (collapsible) ── */}
        {data.features && (
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <button
              onClick={() => setShowFeatures(s => !s)}
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-primary)' }}
            >
              <h4>Extracted URL Features ({showFeatures ? 'Hide' : 'Show all'})</h4>
              <span style={{ color: 'var(--accent-cyan)', fontSize: '0.875rem' }}>{showFeatures ? '▲' : '▼'}</span>
            </button>
            {showFeatures && (
              <div style={{ marginTop: '1rem' }} className="table-container">
                <table className="data-table">
                  <thead><tr><th>Feature</th><th>Value</th></tr></thead>
                  <tbody>
                    {Object.entries(data.features).map(([k, v]) => (
                      v !== null && v !== undefined &&
                      <FeatureRow key={k} label={k.replace(/_/g, ' ')} value={v} />
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* ── Actions ── */}
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <Link to="/analyze" className="btn btn-primary">
            <FiSearch /> Analyze Another URL
          </Link>
          <Link to="/history" className="btn btn-ghost">
            View History
          </Link>
        </div>
      </div>
    </div>
  );
}
