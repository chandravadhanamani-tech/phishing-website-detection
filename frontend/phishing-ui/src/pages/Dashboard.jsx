import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FiSearch, FiAlertTriangle, FiCheckCircle, FiBarChart2, FiShield, FiClock } from 'react-icons/fi';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { dashboard as dashboardApi } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import Navbar from '../components/Navbar';

const RISK_COLORS = {
  'Critical': '#ef4444',
  'High':     '#f97316',
  'Medium':   '#f59e0b',
  'Low':      '#3b82f6',
  'Very Low': '#10b981',
};

function StatCard({ label, value, icon, color, sub }) {
  return (
    <div className="stat-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div className="stat-label">{label}</div>
          <div className="stat-value" style={{ color: color || 'var(--text-white)' }}>{value ?? '—'}</div>
          {sub && <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{sub}</div>}
        </div>
        <div style={{ fontSize: '1.5rem', color: color || 'var(--text-muted)', opacity: 0.7 }}>{icon}</div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const [stats,   setStats]   = useState(null);
  const [recent,  setRecent]  = useState([]);
  const [distrib, setDistrib] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      dashboardApi.getStatistics(),
      dashboardApi.getRecent(),
      dashboardApi.getRiskDistribution(),
    ]).then(([s, r, d]) => {
      setStats(s.data);
      setRecent(r.data);
      setDistrib(d.data.map(item => ({ name: item.risk_level, value: item.count })));
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const riskBadge = (level) => {
    const cls = { Critical: 'badge-critical', High: 'badge-high', Medium: 'badge-medium', Low: 'badge-low', 'Very Low': 'badge-very-low' }[level] || '';
    return <span className={`badge ${cls}`}>{level}</span>;
  };

  if (loading) return (
    <div style={{ minHeight: '100vh' }}>
      <Navbar />
      <div className="loading-overlay"><div className="spinner spinner-lg" /><p>Loading dashboard…</p></div>
    </div>
  );

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <div className="page-wrapper">
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h2 style={{ marginBottom: '0.25rem' }}>Dashboard</h2>
            <p style={{ fontSize: '0.9rem' }}>Welcome back, <strong style={{ color: 'var(--text-primary)' }}>{user?.name}</strong></p>
          </div>
          <Link to="/analyze" className="btn btn-primary">
            <FiSearch /> Analyze New URL
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid-4 stagger-children" style={{ marginBottom: '2rem' }}>
          <StatCard label="Total Analyzed" value={stats?.total_analyses}  icon={<FiBarChart2 />} />
          <StatCard label="Phishing"        value={stats?.phishing_count}  icon={<FiAlertTriangle />} color="#f87171" />
          <StatCard label="Legitimate"      value={stats?.legitimate_count} icon={<FiCheckCircle />}  color="#34d399" />
          <StatCard label="Critical Risk"   value={stats?.critical_count}  icon={<FiShield />}        color="#f87171" />
        </div>

        {/* Charts + Table Row */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '1.5rem', marginBottom: '2rem' }}>
          {/* Risk Distribution Chart */}
          <div className="card">
            <h4 style={{ marginBottom: '1rem' }}>Risk Distribution</h4>
            {distrib.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={distrib} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={3} dataKey="value">
                    {distrib.map((entry) => (
                      <Cell key={entry.name} fill={RISK_COLORS[entry.name] || '#64748b'} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border-default)', borderRadius: 8, color: 'var(--text-primary)' }} />
                  <Legend formatter={(v) => <span style={{ color: 'var(--text-secondary)', fontSize: '0.8125rem' }}>{v}</span>} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state" style={{ padding: '2rem' }}>
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📊</div>
                <p style={{ fontSize: '0.875rem' }}>Analyze URLs to see distribution</p>
              </div>
            )}
          </div>

          {/* Recent Analyses */}
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h4>Recent Analyses</h4>
              <Link to="/history" style={{ fontSize: '0.8125rem', color: 'var(--accent-cyan)' }}>View all →</Link>
            </div>
            {recent.length > 0 ? (
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>URL</th>
                      <th>Prediction</th>
                      <th>Risk</th>
                      <th>Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recent.map((r) => (
                      <tr key={r.id} onClick={() => window.location.href = `/result/${r.id}`}>
                        <td><div className="url-cell">{r.url}</div></td>
                        <td><span className={`badge ${r.prediction === 'PHISHING' ? 'badge-phishing' : 'badge-legitimate'}`}>{r.prediction}</span></td>
                        <td>{riskBadge(r.risk_level)}</td>
                        <td><span style={{ fontWeight: 600, color: r.risk_score > 60 ? 'var(--accent-danger)' : 'var(--text-primary)' }}>{r.risk_score?.toFixed(0)}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state" style={{ padding: '2rem' }}>
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔍</div>
                <p style={{ fontSize: '0.875rem' }}>No analyses yet. <Link to="/analyze">Analyze your first URL</Link></p>
              </div>
            )}
          </div>
        </div>

        {/* Secondary Stats */}
        <div className="grid-4">
          <StatCard label="High Risk"     value={stats?.high_count}     icon={<FiAlertTriangle />} color="var(--accent-orange)" />
          <StatCard label="Medium Risk"   value={stats?.medium_count}   icon={<FiAlertTriangle />} color="var(--accent-warning)" />
          <StatCard label="Low Risk"      value={stats?.low_count}       icon={<FiShield />}        color="var(--accent-blue)" />
          <StatCard label="Very Low Risk" value={stats?.very_low_count} icon={<FiCheckCircle />}   color="var(--accent-success)" />
        </div>
      </div>
    </div>
  );
}
