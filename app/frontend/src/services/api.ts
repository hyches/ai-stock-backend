import axios, { AxiosError, AxiosResponse } from 'axios';

const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle token expiration
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  login: async (credentials: { email: string; password: string }) => {
    const response = await api.post('/auth/login', credentials);
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    return response.data;
  },
  register: (data: { email: string; password: string; name: string }) =>
    api.post('/auth/register', data),
  logout: async () => {
    await api.post('/auth/logout');
    localStorage.removeItem('token');
  },
  getCurrentUser: () => api.get('/auth/me'),
};

// Market API
export const marketApi = {
  getStockData: (symbol: string, interval: string) =>
    api.get(`/market/stock/${symbol}`, { params: { interval } }),
  searchSymbols: (query: string) =>
    api.get('/market/search', { params: { query } }),
};

// ML API
export const mlApi = {
  getPredictions: (symbol: string) =>
    api.get(`/ml/predictions/${symbol}`),
  getModelPerformance: () =>
    api.get('/ml/performance'),
  retrainModel: (symbol: string) =>
    api.post(`/ml/retrain/${symbol}`),
  getFeatureImportance: (symbol: string) =>
    api.get(`/ml/features/${symbol}`),
};

// Settings API
export const settingsApi = {
  getSettings: () => api.get('/settings'),
  updateSettings: (settings: any) => api.patch('/settings', settings),
};

export default api; 