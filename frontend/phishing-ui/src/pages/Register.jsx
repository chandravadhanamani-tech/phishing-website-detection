import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiUser, FiMail, FiLock, FiEye, FiEyeOff, FiShield } from 'react-icons/fi';
import toast from 'react-hot-toast';
import { auth as authApi } from '../services/api';
import { useAuth } from '../hooks/useAuth';

function getPasswordStrength(pwd) {
  if (!pwd) return { score: 0, label: '', color: '' };
  let score = 0;
  if (pwd.length >= 8)  score++;
  if (pwd.length >= 12) score++;
  if (/[A-Z]/.test(pwd)) score++;
  if (/[0-9]/.test(pwd)) score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;
  const levels = [
    { label: 'Very Weak', color: '#ef4444' },
    { label: 'Weak',      color: '#f97316' },
    { label: 'Fair',      color: '#f59e0b' },
    { label: 'Good',      color: '#3b82f6' },
    { label: 'Strong',    color: '#10b981' },
  ];
  return { score, ...levels[Math.min(score, 4)] };
}

export default function Register() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm]     = useState({ name: '', email: '', password: '', confirm_password: '' });
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors]   = useState({});

  const strength = getPasswordStrength(form.password);

  const handleChange = (e) => {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));
    setErrors(er => ({ ...er, [e.target.name]: '' }));
  };

  const validate = () => {
    const errs = {};
    if (!form.name.trim() || form.name.trim().length < 2) errs.name = 'Name must be at least 2 characters.';
    if (!form.email.includes('@')) errs.email = 'Enter a valid email address.';
    if (form.password.length < 8) errs.password = 'Password must be at least 8 characters.';
    if (form.password !== form.confirm_password) errs.confirm_password = 'Passwords do not match.';
    return errs;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) { setErrors(errs); return; }

    setLoading(true);
    try {
      const res = await authApi.register(form);
      login(res.data.access_token, res.data.user);
      toast.success('Account created! Welcome to PhishingShield.');
      navigate('/dashboard');
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed. Please try again.';
      if (typeof msg === 'string' && msg.includes('email')) {
        setErrors({ email: msg });
      } else {
        setErrors({ general: typeof msg === 'string' ? msg : 'Registration failed.' });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      padding: '2rem 1rem', background: 'var(--bg-primary)',
    }} className="cyber-grid">
      <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.625rem', marginBottom: '2rem', textDecoration: 'none' }}>
        <FiShield size={28} color="var(--accent-cyan)" />
        <span style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-white)' }}>
          Phishing<span className="gradient-text">Shield</span>
        </span>
      </Link>

      <div className="form-card animate-slide-up" style={{ maxWidth: 480 }}>
        <h2 style={{ marginBottom: '0.375rem', textAlign: 'center' }}>Create Account</h2>
        <p style={{ textAlign: 'center', marginBottom: '2rem', fontSize: '0.9rem' }}>
          Start detecting phishing websites today
        </p>

        {errors.general && <div className="alert alert-danger" style={{ marginBottom: '1.25rem' }}>{errors.general}</div>}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Name */}
          <div className="input-group">
            <label className="input-label">Full Name</label>
            <div style={{ position: 'relative' }}>
              <FiUser style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input type="text" name="name" value={form.name} onChange={handleChange}
                placeholder="Your full name" className={`input-field ${errors.name ? 'error' : ''}`}
                style={{ paddingLeft: '2.5rem' }} required />
            </div>
            {errors.name && <span className="input-error">{errors.name}</span>}
          </div>

          {/* Email */}
          <div className="input-group">
            <label className="input-label">Email Address</label>
            <div style={{ position: 'relative' }}>
              <FiMail style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input type="email" name="email" value={form.email} onChange={handleChange}
                placeholder="you@example.com" className={`input-field ${errors.email ? 'error' : ''}`}
                style={{ paddingLeft: '2.5rem' }} required />
            </div>
            {errors.email && <span className="input-error">{errors.email}</span>}
          </div>

          {/* Password */}
          <div className="input-group">
            <label className="input-label">Password</label>
            <div style={{ position: 'relative' }}>
              <FiLock style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input type={showPwd ? 'text' : 'password'} name="password" value={form.password} onChange={handleChange}
                placeholder="Min. 8 characters" className={`input-field ${errors.password ? 'error' : ''}`}
                style={{ paddingLeft: '2.5rem', paddingRight: '2.75rem' }} required />
              <button type="button" onClick={() => setShowPwd(s => !s)}
                style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: 4 }}>
                {showPwd ? <FiEyeOff size={16} /> : <FiEye size={16} />}
              </button>
            </div>
            {/* Strength bar */}
            {form.password && (
              <div>
                <div className="password-strength">
                  <div className="password-strength-bar" style={{ width: `${(strength.score / 5) * 100}%`, background: strength.color }} />
                </div>
                <span style={{ fontSize: '0.75rem', color: strength.color }}>{strength.label}</span>
              </div>
            )}
            {errors.password && <span className="input-error">{errors.password}</span>}
          </div>

          {/* Confirm */}
          <div className="input-group">
            <label className="input-label">Confirm Password</label>
            <div style={{ position: 'relative' }}>
              <FiLock style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input type="password" name="confirm_password" value={form.confirm_password} onChange={handleChange}
                placeholder="Repeat password" className={`input-field ${errors.confirm_password ? 'error' : ''}`}
                style={{ paddingLeft: '2.5rem' }} required />
            </div>
            {errors.confirm_password && <span className="input-error">{errors.confirm_password}</span>}
          </div>

          <button type="submit" className="btn btn-primary" style={{ marginTop: '0.5rem', width: '100%' }} disabled={loading}>
            {loading ? <><span className="spinner" /> Creating account…</> : 'Create Account'}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          Already have an account? <Link to="/login" style={{ fontWeight: 600 }}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
