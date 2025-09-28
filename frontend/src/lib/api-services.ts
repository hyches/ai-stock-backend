import axios from 'axios';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8008/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Portfolio API
export const portfolioApi = {
  getPortfolio: () => apiClient.get('/portfolio/'),
  getPortfolioById: (id: number) => apiClient.get(`/portfolio/${id}`),
  createPortfolio: (data: any) => apiClient.post('/portfolio/', data),
  updatePortfolio: (id: number, data: any) => apiClient.put(`/portfolio/${id}`, data),
  deletePortfolio: (id: number) => apiClient.delete(`/portfolio/${id}`),
  addPosition: (portfolioId: number, data: any) => apiClient.post(`/portfolio/${portfolioId}/positions`, data),
  removePosition: (portfolioId: number, positionId: number) => apiClient.delete(`/portfolio/${portfolioId}/positions/${positionId}`),
};

// Market Data API
export const marketApi = {
  getMarketData: (symbol: string) => apiClient.get(`/market/stock/${symbol}`),
  getWatchlist: () => apiClient.get('/market/watchlist'),
  addToWatchlist: (symbol: string) => apiClient.post('/market/watchlist', { symbol }),
  removeFromWatchlist: (symbol: string) => apiClient.delete(`/market/watchlist/${symbol}`),
  getHistoricalData: (symbol: string, startDate: string, endDate: string) => 
    apiClient.get(`/market/stock/${symbol}?start=${startDate}&end=${endDate}`),
};

// ML API
export const mlApi = {
  getPredictions: (symbol: string) => apiClient.get(`/ml/predictions/${symbol}`),
  getModelPerformance: () => apiClient.get('/ml/performance'),
  getAnomalyDetection: () => apiClient.get('/ml/anomaly-detection'),
  trainModel: (data: any) => apiClient.post('/ml/train', data),
};

// Trading API
export const tradingApi = {
  getOrders: () => apiClient.get('/trading/orders'),
  placeOrder: (data: any) => apiClient.post('/trading/orders', data),
  cancelOrder: (orderId: string) => apiClient.delete(`/trading/orders/${orderId}`),
  getPositions: () => apiClient.get('/trading/positions'),
  getTrades: () => apiClient.get('/trading/trades'),
  getStrategies: () => apiClient.get('/trading/strategies'),
  createStrategy: (data: any) => apiClient.post('/trading/strategies', data),
  updateStrategy: (id: number, data: any) => apiClient.put(`/trading/strategies/${id}`, data),
  deleteStrategy: (id: number) => apiClient.delete(`/trading/strategies/${id}`),
};

// Research API
export const researchApi = {
  getScreener: (filters: any) => apiClient.post('/research/screener', filters),
  getFundamentalAnalysis: (symbol: string) => apiClient.get(`/research/fundamental/${symbol}`),
  getTechnicalAnalysis: (symbol: string) => apiClient.get(`/research/technical/${symbol}`),
  getSentimentAnalysis: (symbol: string) => apiClient.get(`/research/sentiment/${symbol}`),
};

// Reports API
export const reportsApi = {
  getReports: () => apiClient.get('/reports/'),
  generateReport: (type: string, params: any) => apiClient.post('/reports/generate', { type, params }),
  getReportById: (id: number) => apiClient.get(`/reports/${id}`),
  deleteReport: (id: number) => apiClient.delete(`/reports/${id}`),
};

// Settings API
export const settingsApi = {
  getSettings: () => apiClient.get('/settings/'),
  updateSettings: (data: any) => apiClient.put('/settings/', data),
  getApiKeys: () => apiClient.get('/settings/api-keys'),
  generateApiKey: () => apiClient.post('/settings/api-keys'),
  deleteApiKey: (id: number) => apiClient.delete(`/settings/api-keys/${id}`),
};

// Auth API
export const authApi = {
  login: (email: string, password: string) => 
    apiClient.post('/auth/login', { username: email, password }),
  register: (data: any) => apiClient.post('/auth/register', data),
  logout: () => apiClient.post('/auth/logout'),
  refreshToken: () => apiClient.post('/auth/refresh'),
  getCurrentUser: () => apiClient.get('/auth/me'),
};

// Export types for TypeScript
export interface PortfolioData {
  id: number;
  name: string;
  totalValue: number;
  totalChange: number;
  totalChangePercent: number;
  items: PortfolioItem[];
  performanceData: PerformanceDataPoint[];
}

export interface PortfolioItem {
  symbol: string;
  quantity: number;
  price: number;
  value: number;
  change: number;
  changePercent: number;
}

export interface PerformanceDataPoint {
  date: string;
  value: number;
}

export interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  high: number;
  low: number;
  open: number;
  previousClose: number;
}

export interface MLPrediction {
  symbol: string;
  prediction: number;
  confidence: number;
  direction: 'up' | 'down' | 'neutral';
  timeframe: string;
}

export interface TradingOrder {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  price: number;
  status: 'pending' | 'filled' | 'cancelled';
  createdAt: string;
}

export interface TradingStrategy {
  id: number;
  name: string;
  type: string;
  description: string;
  parameters: any;
  isActive: boolean;
  performance: any;
}

export default apiClient;