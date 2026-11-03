import React, { useEffect, useState } from 'react';
import { admin as adminApi } from '../services/api';
import Navbar from '../components/Navbar';
import toast from 'react-hot-toast';

export default function Admin() {
  const [stats,   setStats]   = useState(null);
  const [users,   setUsers]   = useState([]);
  const [models,  setModels]  = useState([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    Promise.all([
      adminApi.getStatistics(),
      adminApi.getUsers(),
    ]).then(([s, u]) => {
      setStats(s.data);
      setUsers(u.data);
    }).catch(() => toast.error('Failed to load admin data.')).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const riskBadge = (l) => {
    const cls = { Critical: 'badge-critical', High: 'badge-high', Medium: 'badge-medium', Low: 'badge-low', 'Very Low': 'badge-very-low' }[l] || '';
    return <span className={`badge ${cls}`}>{l}</span>;
  };

  if (loading) return (
    <div style={{ minHeight: '100vh' }}>
      <Navbar />
      <div className="loading-overlay"><div className="spinner spinner-lg" /></div>
    </div>
  );

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <div className="page-wrapper">
        <div style={{ marginBottom: '2rem' }}>
          <h2>Admin Dashboard</h2>
          <p>System-wide statistics and user management.</p>
        </div>

        {/* System Stats */}
        <div className="grid-4 stagger-children" style={{ marginBottom: '2rem' }}>
          {[
            { label: 'Total Analyses', value: stats?.total_analyses, color: 'var(--accent-cyan)' },
            { label: 'Phishing Detected', value: stats?.phishing_count, color: '#f87171' },
            { label: 'Legitimate', value: stats?.legitimate_count, color: '#34d399' },
            { label: 'Critical Risk', value: stats?.critical_count, color: '#f87171' },
          ].map(({ label, value, color }) => (
            <div key={label} className="stat-card">
              <div className="stat-label">{label}</div>
              <div className="stat-value" style={{ color }}>{value ?? '—'}</div>
            </div>
          ))}
        </div>

        {/* Users Table */}
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h4 style={{ marginBottom: '1rem' }}>Registered Users ({users.length})</h4>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Status</th><th>Joined</th></tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontSize: '0.8125rem' }}>{u.id}</td>
                    <td style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{u.name}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem' }}>{u.email}</td>
                    <td>
                      <span className={`badge ${u.role === 'admin' ? 'badge-critical' : 'badge-low'}`}>{u.role}</span>
                    </td>
                    <td>
                      <span className={`badge ${u.is_active ? 'badge-legitimate' : 'badge-phishing'}`}>{u.is_active ? 'Active' : 'Inactive'}</span>
                    </td>
                    <td style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                      {new Date(u.created_at).toLocaleDateString('en-IN')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="alert alert-info">
          ℹ️ Admin panel shows system-wide data. Use <code>GET /admin/analyses</code> API endpoint to view all analyses across users.
        </div>
      </div>
    </div>
  );
}
