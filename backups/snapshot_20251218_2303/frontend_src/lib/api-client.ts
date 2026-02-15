/**
 * API Client for backend communication
 * Centralized axios configuration with error handling
 */
import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.status, error.response.data);
      
      // Handle 401 Unauthorized
      if (error.response.status === 401) {
        localStorage.removeItem('authToken');
        window.location.href = '/login';
      }
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Error in request setup
      console.error('Request Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// API methods
export const api = {
  // Dashboard endpoints
  dashboard: {
    getSummary: (symbols?: string) => {
      const params = symbols ? { symbols } : {};
      return apiClient.get('/dashboard/summary', { params });
    },
    getPortfolio: () => apiClient.get('/dashboard/portfolio'),
    getWatchlist: (symbols?: string) => {
      const params = symbols ? { symbols } : {};
      return apiClient.get('/dashboard/watchlist', { params });
    },
  },

  // ML endpoints
  ml: {
    predict: (symbol: string, data: any) => 
      apiClient.post(`/ml/predict/${symbol}`, data),
    explain: (symbol: string) => 
      apiClient.get(`/ml/explain/${symbol}`),
    getModelPerformance: () => 
      apiClient.get('/ml/performance'),
  },

  // Research endpoints
  research: {
    getStockData: (symbol: string, period: string = '1y') => 
      apiClient.get(`/research/${symbol}`, { params: { period } }),
    getIndicators: (symbol: string) => 
      apiClient.get(`/research/${symbol}/indicators`),
    getPatterns: (symbol: string) => 
      apiClient.get(`/research/${symbol}/patterns`),
  },

  // Screener endpoints
  screener: {
    scan: (filters: any) => 
      apiClient.post('/screener/scan', filters),
    getSavedScreens: () => 
      apiClient.get('/screener/saved'),
  },

  // Portfolio endpoints
  portfolio: {
    getHoldings: () => 
      apiClient.get('/portfolio/holdings'),
    optimize: (data: any) => 
      apiClient.post('/portfolio/optimize', data),
  },

  // Trading endpoints (virtual trading)
  trading: {
    getPositions: () => 
      apiClient.get('/trading/positions'),
    placeOrder: (order: any) => 
      apiClient.post('/trading/order', order),
    getOrderHistory: () => 
      apiClient.get('/trading/orders'),
  },

  // Policy endpoints
  policy: {
    getAll: (params?: any) => 
      apiClient.get('/policies', { params }),
    getById: (id: number) => 
      apiClient.get(`/policies/${id}`),
    triggerCheck: () => 
      apiClient.post('/policies/trigger-check'),
    getStats: () => 
      apiClient.get('/policies/stats'),
  },

  // Alerts endpoints
  alerts: {
    getAll: () => 
      apiClient.get('/alerts'),
    create: (alert: any) => 
      apiClient.post('/alerts', alert),
    update: (id: number, alert: any) => 
      apiClient.put(`/alerts/${id}`, alert),
    delete: (id: number) => 
      apiClient.delete(`/alerts/${id}`),
  },

  // Settings endpoints
  settings: {
    get: () => 
      apiClient.get('/settings'),
    update: (settings: any) => 
      apiClient.put('/settings', settings),
  },
};

export default apiClient;
