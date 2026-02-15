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

// Get lightweight quote for fast loading
export const getStockQuoteLite = async (symbol: string): Promise<any> => {
  try {
    const formattedSymbol = symbol.toUpperCase();
    const response = await apiClient.get(`/research/${formattedSymbol}/quote`);
    return response.data;
  } catch (error) {
    console.error('Get quote lite error:', error);
    throw new Error(`Failed to get quote: ${error.response?.data?.detail || error.message}`);
  }
};

// ML and Pattern Detection endpoints
export const getMLFeatures = async (symbol: string, period: string = "2y") => {
  try {
    const response = await apiClient.post(`/research-ml/${symbol}/ml-features?period=${period}`);
    return response.data;
  } catch (error) {
    console.error('Get ML features error:', error);
    throw error;
  }
};

export const triggerMLTraining = async (symbol: string) => {
  try {
    const response = await apiClient.post(`/research-ml/${symbol}/train-on-patterns`);
    return response.data;
  } catch (error) {
    console.error('Trigger ML training error:', error);
    throw error;
  }
};

export const getTrainingStatus = async (symbol: string, jobId: string) => {
  try {
    const response = await apiClient.get(`/research-ml/${symbol}/train-status/${jobId}`);
    return response.data;
  } catch (error) {
    console.error('Get training status error:', error);
    throw error;
  }
};

export const getPatternAnalysis = async (symbol: string) => {
  try {
    const response = await apiClient.get(`/research-ml/${symbol}/pattern-analysis`);
    return response.data;
  } catch (error) {
    console.error('Get pattern analysis error:', error);
    throw error;
  }
};

// --- Professional Trading Platform Endpoints ---

// Backtesting
export interface BacktestRequest {
  symbol: string;
  days: number;
  strategy: string;
  initial_capital: number;
  params?: Record<string, any>;
}

export const runProfessionalBacktest = async (request: BacktestRequest) => {
  try {
    const response = await apiClient.post('/backtest/run', request);
    return response.data;
  } catch (error) {
    console.error('Run backtest error:', error);
    throw error;
  }
};

export const getMonteCarloSimulation = async (backtestId: string) => {
  try {
    const response = await apiClient.get(`/backtest/${backtestId}/monte-carlo`);
    return response.data;
  } catch (error) {
    console.error('Monte Carlo error:', error);
    throw error;
  }
};

// Risk Management
export const getPortfolioRiskMetrics = async () => {
  try {
    const response = await apiClient.get('/risk/metrics');
    return response.data;
  } catch (error) {
    console.error('Get risk metrics error:', error);
    throw error;
  }
};

export const getCorrelationMatrix = async (symbols: string[]) => {
  try {
    const response = await apiClient.post('/risk/correlation', { symbols });
    return response.data;
  } catch (error) {
    console.error('Get correlation error:', error);
    throw error;
  }
};

export const calculatePositionSize = async (params: {
  method: 'kelly' | 'fixed' | 'volatility';
  symbol: string;
  [key: string]: any;
}) => {
  try {
    const response = await apiClient.post('/risk/position-size', params);
    return response.data;
  } catch (error) {
    console.error('Position size error:', error);
    throw error;
  }
};

// Advanced Execution
export interface AdvancedOrderRequest {
  symbol: string;
  side: 'BUY' | 'SELL';
  order_type: 'MARKET' | 'LIMIT' | 'BRACKET' | 'TRAILING_STOP';
  quantity: number;
  price?: number;
  stop_price?: number;
  target_price?: number;
  trail_percent?: number;
}

export const submitAdvancedOrder = async (order: AdvancedOrderRequest) => {
  try {
    const response = await apiClient.post('/trading/advanced-order', order);
    return response.data;
  } catch (error) {
    console.error('Submit advanced order error:', error);
    throw error;
  }
};

// Tax and Reporting
export const calculateTaxLiability = async (year: number) => {
  try {
    const response = await apiClient.get(`/reports/tax-liability?year=${year}`);
    return response.data;
  } catch (error) {
    console.error('Tax liability error:', error);
    throw error;
  }
};

export const downloadProfessionalReport = async (symbol: string, format: 'pdf' | 'csv' = 'pdf') => {
  try {
    const response = await apiClient.get(`/reports/generate/${symbol}?format=${format}`, {
      responseType: 'blob'
    });
    return response.data;
  } catch (error) {
    console.error('Download report error:', error);
    throw error;
  }
};

export default apiClient;