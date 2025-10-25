// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
};

// API Endpoints
export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',
  },
  
  // Portfolio
  PORTFOLIO: {
    LIST: '/portfolios/',
    DETAIL: (id: number) => `/portfolios/${id}`,
    CREATE: '/portfolios/',
    UPDATE: (id: number) => `/portfolios/${id}`,
    DELETE: (id: number) => `/portfolios/${id}`,
    POSITIONS: (id: number) => `/portfolios/${id}/positions`,
    ADD_POSITION: (id: number) => `/portfolios/${id}/positions`,
    REMOVE_POSITION: (id: number, positionId: number) => `/portfolios/${id}/positions/${positionId}`,
  },
  
  // Market Data
  MARKET: {
    DATA: (symbol: string) => `/market-data/${symbol}`,
    WATCHLIST: '/market-data/watchlist',
    ADD_WATCHLIST: '/market-data/watchlist',
    REMOVE_WATCHLIST: (symbol: string) => `/market-data/watchlist/${symbol}`,
    HISTORICAL: (symbol: string) => `/market-data/${symbol}/historical`,
  },
  
  // ML
  ML: {
    PREDICTIONS: (symbol: string) => `/ml/predictions/${symbol}`,
    PERFORMANCE: '/ml/performance',
    ANOMALY: '/ml/anomaly-detection',
    TRAIN: '/ml/train',
  },
  
  // Trading
  TRADING: {
    ORDERS: '/trading/orders',
    PLACE_ORDER: '/trading/orders',
    CANCEL_ORDER: (id: string) => `/trading/orders/${id}`,
    POSITIONS: '/trading/positions',
    TRADES: '/trading/trades',
    STRATEGIES: '/trading/strategies',
    CREATE_STRATEGY: '/trading/strategies',
    UPDATE_STRATEGY: (id: number) => `/trading/strategies/${id}`,
    DELETE_STRATEGY: (id: number) => `/trading/strategies/${id}`,
  },
  
  // Research
  RESEARCH: {
    SCREENER: '/research/screener',
    FUNDAMENTAL: (symbol: string) => `/research/fundamental/${symbol}`,
    TECHNICAL: (symbol: string) => `/research/technical/${symbol}`,
    SENTIMENT: (symbol: string) => `/research/sentiment/${symbol}`,
  },
  
  // Reports
  REPORTS: {
    LIST: '/reports/',
    GENERATE: '/reports/generate',
    DETAIL: (id: number) => `/reports/${id}`,
    DELETE: (id: number) => `/reports/${id}`,
  },
  
  // Settings
  SETTINGS: {
    GET: '/settings/',
    UPDATE: '/settings/',
    API_KEYS: '/settings/api-keys',
    GENERATE_API_KEY: '/settings/api-keys',
    DELETE_API_KEY: (id: number) => `/settings/api-keys/${id}`,
  },
};

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  TIMEOUT_ERROR: 'Request timeout. Please try again.',
  UNAUTHORIZED: 'Unauthorized. Please login again.',
  FORBIDDEN: 'Access forbidden.',
  NOT_FOUND: 'Resource not found.',
  SERVER_ERROR: 'Server error. Please try again later.',
  VALIDATION_ERROR: 'Validation error. Please check your input.',
  UNKNOWN_ERROR: 'An unknown error occurred.',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Login successful!',
  LOGOUT_SUCCESS: 'Logout successful!',
  REGISTER_SUCCESS: 'Registration successful!',
  SAVE_SUCCESS: 'Saved successfully!',
  DELETE_SUCCESS: 'Deleted successfully!',
  UPDATE_SUCCESS: 'Updated successfully!',
  CREATE_SUCCESS: 'Created successfully!',
};

// API Response Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
  success: boolean;
}

export interface ApiError {
  message: string;
  status: number;
  details?: any;
}

// Helper functions
export const getErrorMessage = (error: any): string => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.message) {
    return error.message;
  }
  return ERROR_MESSAGES.UNKNOWN_ERROR;
};

export const isNetworkError = (error: any): boolean => {
  return !error.response && error.request;
};

export const isTimeoutError = (error: any): boolean => {
  return error.code === 'ECONNABORTED';
};

export const isUnauthorizedError = (error: any): boolean => {
  return error.response?.status === 401;
};

export const isForbiddenError = (error: any): boolean => {
  return error.response?.status === 403;
};

export const isNotFoundError = (error: any): boolean => {
  return error.response?.status === 404;
};

export const isServerError = (error: any): boolean => {
  return error.response?.status >= 500;
};

export const isValidationError = (error: any): boolean => {
  return error.response?.status === 422;
};