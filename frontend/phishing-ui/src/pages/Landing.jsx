import React from 'react';
import { Link } from 'react-router-dom';
import {
  FiShield, FiSearch, FiAlertTriangle, FiCheckCircle,
  FiCpu, FiBarChart2, FiLock, FiZap
} from 'react-icons/fi';

const FEATURES = [
  { icon: <FiSearch />,       title: '30+ URL Features',         desc: 'Extracts structural, domain, and content-based signals from every URL.' },
  { icon: <FiCpu />,          title: '5 ML Models',              desc: 'Logistic Regression, Decision Tree, Random Forest, SVM, and XGBoost compared.' },
  { icon: <FiBarChart2 />,    title: 'Risk Score 0–100',         desc: 'Transparent weighted risk score with 5 severity levels from Very Low to Critical.' },
  { icon: <FiAlertTriangle />, title: 'Risk Factor Analysis',    desc: 'Explains exactly which characteristics contributed to the risk level.' },
  { icon: <FiZap />,          title: 'SHAP Explainability',      desc: 'XAI technology shows which features drove the ML model\'s decision.' },
  { icon: <FiLock />,         title: 'Secure by Design',         desc: 'JWT authentication, bcrypt hashing, ORM-based SQL injection protection.' },
];

const STEPS = [
  { num: '01', title: 'Enter URL',           desc: 'Paste any website URL into the analysis field.' },
  { num: '02', title: 'Feature Extraction',  desc: '30+ structural and content features are extracted automatically.' },
  { num: '03', title: 'ML Inference',        desc: 'XGBoost model classifies the URL as phishing or legitimate.' },
  { num: '04', title: 'Risk Report',         desc: 'Get a detailed risk score, risk factors, and SHAP explanations.' },
];

export default function Landing() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* ── Navbar ── */}
      <nav className="navbar">
        <Link to="/" className="nav-logo">
          <FiShield size={24} color="var(--accent-cyan)" />
          <span>Phishing<span className="gradient-text">Shield</span></span>
        </Link>
        <div className="nav-links">
          <Link to="/login" className="nav-link">Login</Link>
          <Link to="/register" className="btn btn-primary btn-sm" style={{ marginLeft: '0.5rem' }}>
            Get Started
          </Link>
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="cyber-grid" style={{
        padding: '5rem 1.5rem 4rem',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Glow blobs */}
        <div style={{
          position: 'absolute', top: '10%', left: '10%',
          width: 400, height: 400,
          background: 'radial-gradient(circle, rgba(0,212,255,0.06) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />
        <div style={{
          position: 'absolute', bottom: '10%', right: '10%',
          width: 300, height: 300,
          background: 'radial-gradient(circle, rgba(124,58,237,0.08) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div className="animate-slide-up" style={{ position: 'relative', zIndex: 1 }}>
          {/* Badge */}
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
            background: 'rgba(0,212,255,0.08)',
            border: '1px solid rgba(0,212,255,0.2)',
            borderRadius: 'var(--radius-full)',
            padding: '0.375rem 1rem',
            fontSize: '0.8125rem',
            color: 'var(--accent-cyan)',
            marginBottom: '1.5rem',
            fontWeight: 500,
          }}>
            <FiShield size={14} /> Machine Learning-Based Phishing Website 
Detection and Risk Analysis System
          </div>

          <h1 style={{ marginBottom: '1.25rem', maxWidth: 800, margin: '0 auto 1.25rem' }}>
            Detect <span className="gradient-text-danger">Phishing</span> Websites<br />
            with <span className="gradient-text">Explainable AI</span>
          </h1>

          <p style={{ fontSize: '1.125rem', maxWidth: 600, margin: '0 auto 2.5rem', color: 'var(--text-secondary)' }}>
            An ML-based framework that analyzes URLs, extracts 30+ features,
            calculates a transparent risk score, and explains every prediction using SHAP.
          </p>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/register" className="btn btn-primary btn-lg">
              <FiShield /> Start Analyzing URLs
            </Link>
            <Link to="/login" className="btn btn-secondary btn-lg">
              Login
            </Link>
          </div>
        </div>

        {/* Hero illustration */}
        <div className="animate-float" style={{ marginTop: '3.5rem', position: 'relative', zIndex: 1 }}>
          <div style={{
            display: 'inline-flex',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-default)',
            borderRadius: 'var(--radius-xl)',
            padding: '1.5rem 2rem',
            gap: '2rem',
            alignItems: 'center',
            flexWrap: 'wrap',
            justifyContent: 'center',
            boxShadow: 'var(--shadow-card), var(--shadow-glow-cyan)',
          }}>
            {[
              { label: 'Prediction', value: 'PHISHING', color: '#f87171' },
              { label: 'Risk Score', value: '87/100', color: '#f87171' },
              { label: 'Risk Level', value: 'Critical', color: '#f87171' },
              { label: 'Confidence', value: '91%', color: '#fb923c' },
            ].map(({ label, value, color }) => (
              <div key={label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{label}</div>
                <div style={{ fontSize: '1.25rem', fontWeight: 800, color }}>{value}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ── */}
      <section style={{ padding: '5rem 1.5rem', background: 'var(--bg-secondary)' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <h2>How It Works</h2>
            <p style={{ marginTop: '0.5rem' }}>Four steps from URL input to detailed risk report</p>
          </div>

          <div className="grid-4 stagger-children">
            {STEPS.map(({ num, title, desc }) => (
              <div key={num} className="card" style={{ textAlign: 'center', position: 'relative' }}>
                <div style={{
                  fontSize: '2.5rem', fontWeight: 900,
                  background: 'var(--gradient-primary)',
                  WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
                  marginBottom: '0.75rem',
                }}>{num}</div>
                <h4 style={{ marginBottom: '0.5rem' }}>{title}</h4>
                <p style={{ fontSize: '0.875rem' }}>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section style={{ padding: '5rem 1.5rem' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
            <h2>Key Features</h2>
            <p style={{ marginTop: '0.5rem' }}>Built for academic depth and real-world demonstration</p>
          </div>

          <div className="grid-3 stagger-children">
            {FEATURES.map(({ icon, title, desc }) => (
              <div key={title} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{
                  width: 44, height: 44,
                  background: 'rgba(0,212,255,0.1)',
                  border: '1px solid rgba(0,212,255,0.2)',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--accent-cyan)',
                  fontSize: '1.25rem',
                }}>
                  {icon}
                </div>
                <h4>{title}</h4>
                <p style={{ fontSize: '0.875rem' }}>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── What is Phishing ── */}
      <section style={{ padding: '4rem 1.5rem', background: 'var(--bg-secondary)' }}>
        <div style={{ maxWidth: 800, margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ marginBottom: '1rem' }}>What is Phishing?</h2>
          <p style={{ fontSize: '1.0625rem', lineHeight: 1.8 }}>
            Phishing is a type of cyber attack where criminals create <strong style={{ color: 'var(--text-primary)' }}>fake websites</strong> that
            impersonate legitimate services (banks, email providers, online stores) to
            steal user credentials and sensitive information. According to security reports,
            phishing remains one of the most common and damaging cyber threats globally.
            Our system uses machine learning to detect these attacks <em style={{ color: 'var(--accent-cyan)' }}>before</em> users fall victim.
          </p>
        </div>
      </section>

      {/* ── CTA ── */}
      <section style={{ padding: '4rem 1.5rem', textAlign: 'center' }}>
        <div className="card animate-pulse-glow" style={{ maxWidth: 600, margin: '0 auto', padding: '2.5rem' }}>
          <FiShield size={48} color="var(--accent-cyan)" style={{ marginBottom: '1rem' }} />
          <h2 style={{ marginBottom: '0.75rem' }}>Ready to Analyze a URL?</h2>
          <p style={{ marginBottom: '1.75rem' }}>
            Create your free account and start detecting phishing websites instantly.
          </p>
          <Link to="/register" className="btn btn-primary btn-lg">
            Create Free Account
          </Link>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer style={{
        borderTop: '1px solid var(--border-card)',
        padding: '1.5rem',
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: '0.875rem',
        marginTop: 'auto',
      }}>
        <p>PhishingShield · Machine Learning-Based Phishing Website 
Detection and Risk Analysis System</p>
        <p style={{ marginTop: '0.25rem' }}>Built with FastAPI · XGBoost · SHAP · React.js · MySQL</p>
      </footer>
    </div>
  );
}
