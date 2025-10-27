import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  searchStocks,
  getStockDetails,
  getStockHistoricalData,
  getMarketOverview,
  getPopularStocks,
  getStockNews,
  getStockAnalysis,
  getStockFinancials,
  getStockPeers,
} from '@/lib/api';

// Market data hooks
export const useMarketOverview = () => {
  return useQuery({
    queryKey: ['market-overview'],
    queryFn: getMarketOverview,
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: 1,
  });
};

export const usePopularStocks = () => {
  return useQuery({
    queryKey: ['popular-stocks'],
    queryFn: getPopularStocks,
    refetchInterval: 60000, // Refetch every minute
    retry: 1,
  });
};

export const useStockDetails = (symbol: string) => {
  return useQuery({
    queryKey: ['stock-details', symbol],
    queryFn: () => getStockDetails(symbol),
    enabled: !!symbol,
    retry: 1,
  });
};

export const useStockHistoricalData = (symbol: string, timeframe: string) => {
  return useQuery({
    queryKey: ['stock-historical', symbol, timeframe],
    queryFn: () => getStockHistoricalData(symbol, timeframe),
    enabled: !!symbol && !!timeframe,
    retry: 1,
  });
};

export const useStockNews = (symbol: string) => {
  return useQuery({
    queryKey: ['stock-news', symbol],
    queryFn: () => getStockNews(symbol),
    enabled: !!symbol,
    retry: 1,
  });
};

export const useStockAnalysis = (symbol: string) => {
  return useQuery({
    queryKey: ['stock-analysis', symbol],
    queryFn: () => getStockAnalysis(symbol),
    enabled: !!symbol,
    retry: 1,
  });
};

export const useStockFinancials = (symbol: string) => {
  return useQuery({
    queryKey: ['stock-financials', symbol],
    queryFn: () => getStockFinancials(symbol),
    enabled: !!symbol,
    retry: 1,
  });
};

export const useStockPeers = (symbol: string) => {
  return useQuery({
    queryKey: ['stock-peers', symbol],
    queryFn: () => getStockPeers(symbol),
    enabled: !!symbol,
    retry: 1,
  });
};

// Search hook
export const useStockSearch = (query: string) => {
  return useQuery({
    queryKey: ['stock-search', query],
    queryFn: () => searchStocks(query),
    enabled: query.length >= 2,
    retry: 1,
  });
};

// Placeholder hooks for future implementation
export const usePortfolio = () => {
  return useQuery({
    queryKey: ['portfolio'],
    queryFn: () => Promise.resolve([]),
    retry: 1,
  });
};

export const useWatchlist = () => {
  return useQuery({
    queryKey: ['watchlist'],
    queryFn: () => Promise.resolve([]),
    retry: 1,
  });
};

export const useModelPerformance = () => {
  return useQuery({
    queryKey: ['model-performance'],
    queryFn: () => Promise.resolve({ accuracy: 0, precision: 0, recall: 0 }),
    retry: 1,
  });
};