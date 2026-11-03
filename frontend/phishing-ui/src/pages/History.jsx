import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiTrash2 } from 'react-icons/fi';
import toast from 'react-hot-toast';
import { analysis as analysisApi } from '../services/api';
import Navbar from '../components/Navbar';

export default function History() {
  const navigate    = useNavigate();
  const [records, setRecords]   = useState([]);
  const [loading, setLoading]   = useState(true);
  const [search,  setSearch]    = useState('');
  const [filter,  setFilter]    = useState('All');
  const [page,    setPage]      = useState(0);
  const PAGE_SIZE = 20;

  useEffect(() => {
    setLoading(true);
    analysisApi.getHistory(page * PAGE_SIZE, PAGE_SIZE)
      .then(res => setRecords(res.data))
      .catch(() => toast.error('Failed to load history.'))
      .finally(() => setLoading(false));
  }, [page]);

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Delete this analysis record?')) return;
    try {
      await analysisApi.deleteById(id);
      setRecords(r => r.filter(x => x.id !== id));
      toast.success('Record deleted.');
    } catch { toast.error('Delete failed.'); }
  };

  const filtered = records.filter(r => {
    const matchSearch = !search || r.url.toLowerCase().includes(search.toLowerCase());
    const matchFilter = filter === 'All' || r.prediction === filter;
    return matchSearch && matchFilter;
  });

  const riskBadge = (level) => {
    const cls = { Critical: 'badge-critical', High: 'badge-high', Medium: 'badge-medium', Low: 'badge-low', 'Very Low': 'badge-very-low' }[level] || '';
    return <span className={`badge ${cls}`}>{level}</span>;
  };

  const fmtDate = (dt) => new Date(dt).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' });

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <div className="page-wrapper">
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ marginBottom: '0.375rem' }}>Analysis History</h2>
          <p>All URLs you've analyzed, ordered newest first.</p>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
          <input
            type="text" placeholder="Search by URL…"
            value={search} onChange={e => setSearch(e.target.value)}
            className="input-field" style={{ maxWidth: 320 }}
          />
          {['All', 'PHISHING', 'LEGITIMATE'].map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-ghost'}`}>
              {f}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="loading-overlay"><div className="spinner spinner-lg" /></div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <div style={{ fontSize: '3rem' }}>🔍</div>
            <p>No analysis records found.</p>
          </div>
        ) : (
          <>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>URL</th>
                    <th>Prediction</th>
                    <th>Probability</th>
                    <th>Risk Score</th>
                    <th>Risk Level</th>
                    <th>Date</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((r) => (
                    <tr key={r.id} onClick={() => navigate(`/result/${r.id}`)}>
                      <td style={{ color: 'var(--text-muted)', fontSize: '0.8125rem' }}>{r.id}</td>
                      <td><div className="url-cell" style={{ maxWidth: 280 }}>{r.url}</div></td>
                      <td><span className={`badge ${r.prediction === 'PHISHING' ? 'badge-phishing' : 'badge-legitimate'}`}>{r.prediction}</span></td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: r.probability > 0.5 ? '#f87171' : '#34d399' }}>
                        {(r.probability * 100).toFixed(1)}%
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{r.risk_score?.toFixed(1)}</td>
                      <td>{riskBadge(r.risk_level)}</td>
                      <td style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>{fmtDate(r.created_at)}</td>
                      <td>
                        <button onClick={(e) => handleDelete(r.id, e)}
                          className="btn btn-ghost btn-sm" style={{ color: 'var(--text-muted)', padding: '0.375rem' }}>
                          <FiTrash2 size={15} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
              <button className="btn btn-ghost btn-sm" disabled={page === 0} onClick={() => setPage(p => p - 1)}>← Previous</button>
              <span style={{ alignSelf: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>Page {page + 1}</span>
              <button className="btn btn-ghost btn-sm" disabled={records.length < PAGE_SIZE} onClick={() => setPage(p => p + 1)}>Next →</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
