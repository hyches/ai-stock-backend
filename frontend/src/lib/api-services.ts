import axios from 'axios';
import { API_CONFIG, API_ENDPOINTS } from '@/utils/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
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
      // Handle unauthorized - redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Stock search and autocomplete
export const searchStocks = async (query: string) => {
  try {
    const response = await apiClient.get(`/market/search?q=${encodeURIComponent(query)}`);
    return response.data;
  } catch (error) {
    console.error('Search stocks error:', error);
    throw new Error(`Failed to search stocks: ${error.response?.data?.detail || error.message}`);
  }
};

// Get stock details
export const getStockDetails = async (symbol: string) => {
  try {
    const response = await apiClient.get(`/market/data/${symbol}`);
    return response.data;
  } catch (error) {
    console.error('Get stock details error:', error);
    throw new Error(`Failed to get stock details: ${error.response?.data?.detail || error.message}`);
  }
};

// Get historical data
export const getStockHistoricalData = async (symbol: string, timeframe: string) => {
  try {
    const response = await apiClient.get(`/market/data/${symbol}/historical?period=${timeframe}`);
    return response.data;
  } catch (error) {
    console.error('Get historical data error:', error);
    throw new Error(`Failed to get historical data: ${error.response?.data?.detail || error.message}`);
  }
};

// Get market overview
export const getMarketOverview = async () => {
  try {
    const response = await apiClient.get('/market/overview');
    return response.data;
  } catch (error) {
    console.error('Get market overview error:', error);
    throw new Error(`Failed to get market overview: ${error.response?.data?.detail || error.message}`);
  }
};

// Get popular stocks
export const getPopularStocks = async () => {
  try {
    const response = await apiClient.get('/market/popular');
    return response.data;
  } catch (error) {
    console.error('Get popular stocks error:', error);
    throw new Error(`Failed to get popular stocks: ${error.response?.data?.detail || error.message}`);
  }
};

// Get stock news
export const getStockNews = async (symbol: string) => {
  try {
    const response = await apiClient.get(`/market/news/${symbol}`);
    return response.data;
  } catch (error) {
    console.error('Get stock news error:', error);
    throw new Error(`Failed to get stock news: ${error.response?.data?.detail || error.message}`);
  }
};

// Get stock analysis
export const getStockAnalysis = async (symbol: string) => {
  try {
    const response = await apiClient.get(`/ml/analysis/${symbol}`);
    return response.data;
  } catch (error) {
    console.error('Get stock analysis error:', error);
    throw new Error(`Failed to get stock analysis: ${error.response?.data?.detail || error.message}`);
  }
};

// Get stock financials
export const getStockFinancials = async (symbol: string) => {
  try {
    const response = await apiClient.get(`/market/financials/${symbol}`);
    return response.data;
  } catch (error) {
    console.error('Get stock financials error:', error);
    throw new Error(`Failed to get stock financials: ${error.response?.data?.detail || error.message}`);
  }
};

// Get stock peers
export const getStockPeers = async (symbol: string) => {
  try {
    const response = await apiClient.get(`/market/peers/${symbol}`);
    return response.data;
  } catch (error) {
    console.error('Get stock peers error:', error);
    throw new Error(`Failed to get stock peers: ${error.response?.data?.detail || error.message}`);
  }
};



export default apiClient;