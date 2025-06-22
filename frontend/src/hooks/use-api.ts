import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  portfolioApi,
  marketApi,
  mlApi,
  tradingApi,
  researchApi,
  reportsApi,
  settingsApi,
  type PortfolioData,
  type MarketData,
  type MLPrediction,
} from '@/lib/api-services';

// Portfolio hooks
export const usePortfolio = () => {
  return useQuery({
    queryKey: ['portfolio'],
    queryFn: () => portfolioApi.getPortfolio().then(res => res.data),
    staleTime: 30000, // 30 seconds
  });
};

export const useAddPosition = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: portfolioApi.addPosition,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio'] });
    },
  });
};

export const useRemovePosition = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: portfolioApi.removePosition,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio'] });
    },
  });
};

// Market data hooks
export const useMarketData = (symbol: string) => {
  return useQuery({
    queryKey: ['market-data', symbol],
    queryFn: () => marketApi.getMarketData(symbol).then(res => res.data),
    enabled: !!symbol,
    staleTime: 10000, // 10 seconds
  });
};

export const useWatchlist = () => {
  return useQuery({
    queryKey: ['watchlist'],
    queryFn: () => marketApi.getWatchlist().then(res => res.data),
    staleTime: 30000,
  });
};

export const useAddToWatchlist = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: marketApi.addToWatchlist,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] });
    },
  });
};

export const useRemoveFromWatchlist = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: marketApi.removeFromWatchlist,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlist'] });
    },
  });
};

// ML predictions hooks
export const useMLPredictions = (symbol: string) => {
  return useQuery({
    queryKey: ['ml-predictions', symbol],
    queryFn: () => mlApi.getPredictions(symbol).then(res => res.data),
    enabled: !!symbol,
    staleTime: 60000, // 1 minute
  });
};

export const useModelPerformance = () => {
  return useQuery({
    queryKey: ['model-performance'],
    queryFn: () => mlApi.getModelPerformance().then(res => res.data),
    staleTime: 300000, // 5 minutes
  });
};

export const useAnomalyDetection = () => {
  return useQuery({
    queryKey: ['anomaly-detection'],
    queryFn: () => mlApi.getAnomalyDetection().then(res => res.data),
    staleTime: 60000,
  });
};

// Trading hooks
export const useOrders = () => {
  return useQuery({
    queryKey: ['orders'],
    queryFn: () => tradingApi.getOrders().then(res => res.data),
    staleTime: 15000,
  });
};

export const usePlaceOrder = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: tradingApi.placeOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
      queryClient.invalidateQueries({ queryKey: ['portfolio'] });
    },
  });
};

export const useCancelOrder = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: tradingApi.cancelOrder,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['orders'] });
    },
  });
};

// Research hooks
export const useScreener = (filters: any) => {
  return useQuery({
    queryKey: ['screener', filters],
    queryFn: () => researchApi.getScreener(filters).then(res => res.data),
    enabled: !!filters,
    staleTime: 60000,
  });
};

export const useFundamentalAnalysis = (symbol: string) => {
  return useQuery({
    queryKey: ['fundamental-analysis', symbol],
    queryFn: () => researchApi.getFundamentalAnalysis(symbol).then(res => res.data),
    enabled: !!symbol,
    staleTime: 300000,
  });
};

export const useTechnicalAnalysis = (symbol: string) => {
  return useQuery({
    queryKey: ['technical-analysis', symbol],
    queryFn: () => researchApi.getTechnicalAnalysis(symbol).then(res => res.data),
    enabled: !!symbol,
    staleTime: 60000,
  });
};

// Reports hooks
export const useReports = () => {
  return useQuery({
    queryKey: ['reports'],
    queryFn: () => reportsApi.getReports().then(res => res.data),
    staleTime: 300000,
  });
};

export const useGenerateReport = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ type, params }: { type: string; params: any }) => 
      reportsApi.generateReport(type, params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
    },
  });
};

// Settings hooks
export const useSettings = () => {
  return useQuery({
    queryKey: ['settings'],
    queryFn: () => settingsApi.getSettings().then(res => res.data),
    staleTime: 300000,
  });
};

export const useUpdateSettings = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: settingsApi.updateSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
  });
};

export const useApiKeys = () => {
  return useQuery({
    queryKey: ['api-keys'],
    queryFn: () => settingsApi.getApiKeys().then(res => res.data),
    staleTime: 300000,
  });
};

export const useGenerateApiKey = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: settingsApi.generateApiKey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['api-keys'] });
    },
  });
}; 