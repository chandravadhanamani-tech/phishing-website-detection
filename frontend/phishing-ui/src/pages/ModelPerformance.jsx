import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { model as modelApi } from '../services/api';
import Navbar from '../components/Navbar';
import FeatureChart from '../components/FeatureChart';

const METRIC_LABELS = {
  accuracy:       'Accuracy',
  precision_score: 'Precision',
  recall_score:   'Recall',
  f1_score:       'F1-Score',
  roc_auc:        'ROC-AUC',
};

const MODEL_COLORS = {
  xgboost:              '#00d4ff',
  random_forest:        '#7c3aed',
  logistic_regression:  '#10b981',
  decision_tree:        '#f59e0b',
  svm:                  '#ef4444',
};

export default function ModelPerformance() {
  const [models,    setModels]    = useState([]);
  const [features,  setFeatures]  = useState([]);
  const [active,    setActive]    = useState(null);
  const [loading,   setLoading]   = useState(true);
  const [activeMetric, setActiveMetric] = useState('f1_score');

  useEffect(() => {
    Promise.all([
      modelApi.getPerformance(),
      modelApi.getFeatures(),
      modelApi.getActive().catch(() => ({ data: null })),
    ]).then(([m, f, a]) => {
      setModels(m.data);
      // Convert features to SHAP-compatible format for FeatureChart
      setFeatures(f.data.slice(0, 15).map(fi => ({
        feature_name:  fi.feature_name,
        shap_value:    fi.importance,
        direction:     'phishing',
        rank_order:    fi.rank,
      })));
      setActive(a.data);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const chartData = models.map(m => ({
    name: m.model_name.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()),
    [activeMetric]: m[activeMetric] !== null ? parseFloat((m[activeMetric] * 100).toFixed(2)) : 0,
    isActive: m.is_active,
  }));

  if (loading) return (
    <div style={{ minHeight: '100vh' }}>
      <Navbar />
      <div className="loading-overlay"><div className="spinner spinner-lg" /><p>Loading model data…</p></div>
    </div>
  );

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <div className="page-wrapper">
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ marginBottom: '0.375rem' }}>Model Performance</h2>
          <p>Evaluation metrics for all trained ML models compared side by side.</p>
        </div>

        {models.length === 0 ? (
          <div className="alert alert-warning">
            No model data found. Please run <code>python ml/train_models.py</code> to train the models first.
          </div>
        ) : (
          <>
            {/* Active Model Card */}
            {active && (
              <div className="card" style={{ marginBottom: '1.5rem', borderColor: 'rgba(0,212,255,0.3)', background: 'rgba(0,212,255,0.04)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: '0.25rem' }}>
                      ✅ Active Model
                    </div>
                    <h3 style={{ margin: 0 }}>{active.model_name?.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</h3>
                  </div>
                  <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                    {Object.entries(METRIC_LABELS).map(([key, label]) => (
                      active[key] !== null && active[key] !== undefined && (
                        <div key={key} style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: '1.375rem', fontWeight: 800, color: 'var(--accent-cyan)' }}>
                            {(active[key] * 100).toFixed(1)}%
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{label}</div>
                        </div>
                      )
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Model Comparison Table */}
            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <h4 style={{ marginBottom: '1rem' }}>Model Comparison</h4>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Model</th>
                      {Object.values(METRIC_LABELS).map(l => <th key={l}>{l}</th>)}
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {models.map(m => (
                      <tr key={m.id} style={{ background: m.is_active ? 'rgba(0,212,255,0.05)' : undefined }}>
                        <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                          {m.model_name.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                        </td>
                        {Object.keys(METRIC_LABELS).map(key => (
                          <td key={key} style={{ fontFamily: 'var(--font-mono)', fontWeight: key === 'f1_score' ? 700 : 400, color: key === 'f1_score' ? 'var(--accent-cyan)' : 'var(--text-secondary)' }}>
                            {m[key] !== null && m[key] !== undefined ? `${(m[key] * 100).toFixed(1)}%` : '—'}
                          </td>
                        ))}
                        <td>{m.is_active ? <span className="badge badge-legitimate">Active</span> : <span className="badge" style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)' }}>Inactive</span>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Bar Chart */}
            <div className="card" style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
                <h4>Performance Comparison</h4>
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  {Object.entries(METRIC_LABELS).map(([key, label]) => (
                    <button key={key} onClick={() => setActiveMetric(key)}
                      className={`btn btn-sm ${activeMetric === key ? 'btn-primary' : 'btn-ghost'}`}>
                      {label}
                    </button>
                  ))}
                </div>
              </div>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} />
                  <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fill: 'var(--text-muted)', fontSize: 12 }} />
                  <Tooltip
                    formatter={(v) => [`${v}%`, METRIC_LABELS[activeMetric]]}
                    contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)', borderRadius: 8, color: 'var(--text-primary)' }}
                  />
                  <Bar dataKey={activeMetric} fill="var(--accent-cyan)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Feature Importance */}
            {features.length > 0 && (
              <div className="card">
                <h4 style={{ marginBottom: '0.375rem' }}>Global Feature Importance</h4>
                <p style={{ fontSize: '0.875rem', marginBottom: '1.25rem' }}>
                  Top 15 most predictive features from the active ML model.
                </p>
                <FeatureChart features={features} />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
