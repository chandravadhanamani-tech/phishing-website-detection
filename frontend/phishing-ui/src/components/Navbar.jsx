import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FiShield, FiSearch, FiClock, FiBarChart2, FiGrid, FiLogOut, FiUser } from 'react-icons/fi';
import { useAuth } from '../hooks/useAuth';

const NAV_LINKS = [
  { to: '/dashboard',  label: 'Dashboard',        icon: <FiGrid /> },
  { to: '/analyze',    label: 'Analyze URL',       icon: <FiSearch /> },
  { to: '/history',    label: 'History',           icon: <FiClock /> },
  { to: '/model',      label: 'Model Performance', icon: <FiBarChart2 /> },
];

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();

  return (
    <nav className="navbar">
      {/* Logo */}
      <Link to="/dashboard" className="nav-logo">
        <FiShield size={22} color="var(--accent-cyan)" />
        <span>Phishing<span className="gradient-text">Shield</span></span>
      </Link>

      {/* Links */}
      <div className="nav-links">
        {NAV_LINKS.map(({ to, label, icon }) => (
          <Link
            key={to}
            to={to}
            className={`nav-link ${location.pathname === to ? 'active' : ''}`}
          >
            {icon} {label}
          </Link>
        ))}
        {isAdmin && (
          <Link to="/admin" className={`nav-link ${location.pathname === '/admin' ? 'active' : ''}`}>
            Admin
          </Link>
        )}
      </div>

      {/* User menu */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
          <FiUser size={16} />
          <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{user?.name}</span>
          {isAdmin && <span className="badge badge-critical" style={{ fontSize: '0.65rem' }}>Admin</span>}
        </div>
        <button onClick={logout} className="btn btn-ghost btn-sm" title="Logout">
          <FiLogOut size={15} />
        </button>
      </div>
    </nav>
  );
}
