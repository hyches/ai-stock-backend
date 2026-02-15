/**
 * API Client for backend communication
 * Centralized axios configuration with error handling
 */
import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper to get cookie value
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
  return null;
}

// Request interceptor for adding auth token and CSRF token
apiClient.interceptors.request.use(
  (config) => {
    // Add Bearer token
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add CSRF token from cookie (Double Submit Cookie pattern)
    const csrfToken = getCookie('csrf_token');
    if (csrfToken) {
      config.headers['X-CSRF-Token'] = csrfToken;
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

export const api = {
  // Auth endpoints
  auth: {
    login: (credentials: any) =>
      apiClient.post('/auth/login', credentials),
    register: (userData: any) =>
      apiClient.post('/auth/register', userData),
    me: () =>
      apiClient.get('/auth/me'),
    getCsrfToken: () =>
      apiClient.get('/auth/csrf'),
  },

  // Market endpoints
  market: {
    getOverview: () =>
      apiClient.get('/market/overview'),
    search: (query: string) =>
      apiClient.get(`/market/search?q=${query}`),
    getQuote: (symbol: string) =>
      apiClient.get(`/market/quote/${symbol}`),
    getHistory: (symbol: string, period: string = '1mo', interval: string = '1d') =>
      apiClient.get(`/market/history/${symbol}?period=${period}&interval=${interval}`),
    getPopular: () =>
      apiClient.get('/market/popular'),
  },

  // Research endpoints  
  research: {
    get: (symbol: string, period = '1y') =>
      apiClient.get(`/research/${symbol}?period=${period}`),
    getMlFeatures: (symbol: string, data: any) =>
      apiClient.post(`/research/${symbol}/ml-features`, data),
    getAnomalies: (symbol: string, period = '1y') =>
      apiClient.get(`/research/${symbol}/anomalies?period=${period}`),
    getMarketWeather: () =>
      apiClient.get('/research/market/weather'),
    getMLPredictions: (symbol: string) =>
      apiClient.get(`/research/${symbol}/ml-predictions`),
  },

  // Dashboard endpoints
  dashboard: {
    getSummary: () => apiClient.get('/dashboard/summary'),
  },

  // Trading endpoints
  trading: {
    getPortfolio: () =>
      apiClient.get('/trading/portfolio'),
    getPositions: () =>
      apiClient.get('/trading/positions'),
    placeOrder: (order: any) =>
      apiClient.post('/trading/order', order),
    getOrderHistory: () =>
      apiClient.get('/trading/orders'),
    getStrategies: () => apiClient.get('/trading/strategies/'),
    getTrades: () => apiClient.get('/trading/trades/'),
    rebalance: (portfolioId: number) => apiClient.post(`/portfolio/${portfolioId}/rebalance`),

    // Paper Trading
    getPaperPortfolio: () => apiClient.get('/trading/paper/portfolio'),
    getPaperOrders: () => apiClient.get('/trading/paper/orders'),
    placePaperOrder: (order: { symbol: string, side: string, quantity: number, order_type: string }) =>
      apiClient.post('/trading/paper/orders', order),
    resetBalance: (amount: number) => apiClient.post(`/trading/paper/reset?amount=${amount}`),

    // Strategies
    startGridBot: (config: { symbol: string, lower_range: number, upper_range: number, grid_count: number, investment: number }) =>
      apiClient.post('/trading/strategies/grid', config),

    // Market Data
    getOptionChain: (symbol: string) => apiClient.get(`/trading/market/option-chain/${encodeURIComponent(symbol)}`),
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