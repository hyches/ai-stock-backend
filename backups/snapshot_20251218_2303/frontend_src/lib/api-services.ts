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

// Screen stocks with criteria
export interface ScreenerCriteria {
  sector?: string;
  min_volume?: number;
  max_pe?: number;
  min_market_cap?: number;
  min_price?: number;
  max_price?: number;
  min_dividend_yield?: number;
}

export interface ScreenedStock {
  symbol: string;
  name: string;
  sector: string;
  price: number;
  volume: number;
  market_cap: number;
  pe_ratio?: number;
  dividend_yield?: number;
  ma_50?: number;
  ma_200?: number;
  last_updated: string;
}

export const screenStocks = async (criteria: ScreenerCriteria): Promise<ScreenedStock[]> => {
  try {
    // Try main screener endpoint first, fallback to research endpoint
    let response;
    try {
      response = await apiClient.post('/screener', criteria);
    } catch (e) {
      // Fallback to research screener endpoint
      response = await apiClient.post('/research/screener', criteria);
    }
    return response.data;
  } catch (error) {
    console.error('Screen stocks error:', error);
    throw new Error(`Failed to screen stocks: ${error.response?.data?.detail || error.message}`);
  }
};

// Research Report interfaces
export interface ResearchReportRequest {
  symbol: string;
  include_technical?: boolean;
  include_sentiment?: boolean;
  include_competitors?: boolean;
  format?: string;
}

export interface ResearchReportResponse {
  symbol: string;
  company_name: string;
  sector: string;
  industry: string;
  current_price: number;
  financials: {
    revenue: number;
    net_income: number;
    eps: number;
    pe_ratio: number;
    market_cap: number;
    dividend_yield?: number;
    debt_to_equity?: number;
    profit_margin: number;
  };
  technicals?: {
    ma_50: number;
    ma_200: number;
    rsi: number;
    macd: number;
    volume_avg: number;
  };
  sentiment?: {
    overall_score: number;
    news_sentiment: number;
    social_sentiment: number;
    analyst_rating: string;
    price_target: number;
  };
  competitors?: string[];
  summary: string;
  recommendations: string[];
  risk_factors: string[];
  generated_at: string;
  report_url?: string;
}

// Generate research report
export const generateResearchReport = async (request: ResearchReportRequest): Promise<ResearchReportResponse> => {
  try {
    const response = await apiClient.post('/research/report', request);
    return response.data;
  } catch (error) {
    console.error('Generate research report error:', error);
    throw new Error(`Failed to generate research report: ${error.response?.data?.detail || error.message}`);
  }
};

// Get comprehensive stock data for details page
export const getComprehensiveStockData = async (symbol: string): Promise<any> => {
  try {
    const formattedSymbol = symbol.toUpperCase();
    const response = await apiClient.get(`/research/${formattedSymbol}`);
    return response.data;
  } catch (error) {
    console.error('Get comprehensive stock data error:', error);
    throw new Error(`Failed to get comprehensive stock data: ${error.response?.data?.detail || error.message}`);
  }
};

export default apiClient;