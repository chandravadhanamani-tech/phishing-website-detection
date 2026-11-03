/**
 * api.js - Axios HTTP Client
 * Centralized API service with JWT injection and error handling.
 */
import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

// ── Axios Instance ────────────────────────────────────────────────────────────
const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

// ── Request Interceptor: Inject JWT Token ─────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('phishing_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response Interceptor: Handle 401 ─────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('phishing_token');
      localStorage.removeItem('phishing_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ── Auth Endpoints ────────────────────────────────────────────────────────────
export const auth = {
  register: (data) => api.post('/auth/register', data),
  login:    (data) => api.post('/auth/login', data),
  getMe:    ()     => api.get('/auth/me'),
};

// ── Analysis Endpoints ────────────────────────────────────────────────────────
export const analysis = {
  predict:          (data)       => api.post('/analysis/predict', data),
  predictBatchFile: (formData)   => api.post('/analysis/predict-batch-file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getHistory:       (skip=0, limit=20) => api.get(`/analysis/history?skip=${skip}&limit=${limit}`),
  getById:          (id)         => api.get(`/analysis/${id}`),
  deleteById:       (id)         => api.delete(`/analysis/${id}`),
};

// ── Dashboard Endpoints ───────────────────────────────────────────────────────
export const dashboard = {
  getStatistics:       () => api.get('/dashboard/statistics'),
  getRecent:           () => api.get('/dashboard/recent'),
  getRiskDistribution: () => api.get('/dashboard/risk-distribution'),
};

// ── Model Endpoints ───────────────────────────────────────────────────────────
export const model = {
  getPerformance:    () => api.get('/model/performance'),
  getFeatures:       () => api.get('/model/features'),
  getActive:         () => api.get('/model/active'),
};

// ── Admin Endpoints ───────────────────────────────────────────────────────────
export const admin = {
  getUsers:      (skip=0, limit=50) => api.get(`/admin/users?skip=${skip}&limit=${limit}`),
  getStatistics: ()                 => api.get('/admin/statistics'),
  getAnalyses:   (skip=0, limit=50) => api.get(`/admin/analyses?skip=${skip}&limit=${limit}`),
  activateModel: (id)               => api.put(`/admin/model/${id}/activate`),
};

export default api;
