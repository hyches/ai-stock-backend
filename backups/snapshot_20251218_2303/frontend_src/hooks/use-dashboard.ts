/**
 * React Query hooks for dashboard data
 * Provides easy access to cached and real-time dashboard data
 */
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api-client';

// Query keys for cache management
export const dashboardKeys = {
  all: ['dashboard'] as const,
  summary: (symbols?: string) => [...dashboardKeys.all, 'summary', symbols] as const,
  portfolio: () => [...dashboardKeys.all, 'portfolio'] as const,
  watchlist: (symbols?: string) => [...dashboardKeys.all, 'watchlist', symbols] as const,
};

/**
 * Hook to fetch dashboard summary with market data, portfolio, and indices
 */
export function useDashboardSummary(symbols?: string) {
  return useQuery({
    queryKey: dashboardKeys.summary(symbols),
    queryFn: async () => {
      const response = await api.dashboard.getSummary(symbols);
      return response.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minute for real-time feel
    refetchInterval: 60000, // Auto-refetch every minute
  });
}

/**
 * Hook to fetch portfolio holdings and analytics
 */
export function useDashboardPortfolio() {
  return useQuery({
    queryKey: dashboardKeys.portfolio(),
    queryFn: async () => {
      const response = await api.dashboard.getPortfolio();
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to fetch watchlist with real-time quotes
 */
export function useDashboardWatchlist(symbols?: string) {
  return useQuery({
    queryKey: dashboardKeys.watchlist(symbols),
    queryFn: async () => {
      const response = await api.dashboard.getWatchlist(symbols);
      return response.data;
    },
    staleTime: 1 * 60 * 1000, // 1 minute
    refetchInterval: 60000, // Auto-refetch every minute
  });
}

/**
 * Hook to manually refresh dashboard data
 */
export function useRefreshDashboard() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      // Invalidate all dashboard queries to trigger refetch
      await queryClient.invalidateQueries({ queryKey: dashboardKeys.all });
      return { success: true };
    },
  });
}

// Type definitions for dashboard data
export interface DashboardSummary {
  portfolio: {
    total_value: number;
    total_change: number;
    change_percent: number;
    positions: Array<{
      symbol: string;
      price: number;
      change: number;
      volume: number;
      quantity: number;
      value: number;
    }>;
    cash_available: number;
  };
  performance: Array<{
    date: string;
    value: number;
  }>;
  market_indices: Array<{
    name: string;
    value: number;
    change: number;
  }>;
  top_gainers: Array<{
    symbol: string;
    price: number;
    change: number;
  }>;
  top_losers: Array<{
    symbol: string;
    price: number;
    change: number;
  }>;
  timestamp: string;
  data_source: string;
}

export interface PortfolioData {
  holdings: any[];
  total_value: number;
  total_cost: number;
  total_pnl: number;
  pnl_percent: number;
  cash_balance: number;
  message?: string;
}

export interface WatchlistData {
  items: Array<{
    symbol: string;
    price: number;
    change: number;
  }>;
}
