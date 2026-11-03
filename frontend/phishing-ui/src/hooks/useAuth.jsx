/**
 * useAuth.jsx - Authentication Context & Hook
 * Provides global auth state (user, token, login, logout) via React Context.
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { auth as authApi } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(null);
  const [token,   setToken]   = useState(null);
  const [loading, setLoading] = useState(true);

  // Load persisted session on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('phishing_token');
    const savedUser  = localStorage.getItem('phishing_user');
    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('phishing_token');
        localStorage.removeItem('phishing_user');
      }
    }
    setLoading(false);
  }, []);

  const login = useCallback((tokenValue, userData) => {
    setToken(tokenValue);
    setUser(userData);
    localStorage.setItem('phishing_token', tokenValue);
    localStorage.setItem('phishing_user', JSON.stringify(userData));
  }, []);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('phishing_token');
    localStorage.removeItem('phishing_user');
    window.location.href = '/login';
  }, []);

  const isAuthenticated = Boolean(token && user);
  const isAdmin         = user?.role === 'admin';

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, isAuthenticated, isAdmin }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
