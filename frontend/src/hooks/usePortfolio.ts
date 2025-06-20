import { useState, useEffect, useCallback } from 'react';

interface Position {
  symbol: string;
  name: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  marketValue: number;
  costBasis: number;
  unrealizedGain: number;
  unrealizedGainPercent: number;
  realizedGain: number;
  realizedGainPercent: number;
  lastUpdated: string;
}

interface Transaction {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
  total: number;
  date: string;
  notes?: string;
}

interface Portfolio {
  positions: Position[];
  transactions: Transaction[];
  totalValue: number;
  totalCost: number;
  totalGain: number;
  totalGainPercent: number;
  cashBalance: number;
  lastUpdated: string;
}

interface UsePortfolioReturn {
  portfolio: Portfolio | null;
  loading: boolean;
  error: string | null;
  addTransaction: (transaction: Omit<Transaction, 'id' | 'date'>) => Promise<void>;
  updatePosition: (symbol: string, updates: Partial<Position>) => Promise<void>;
  refresh: () => Promise<void>;
  getPositionHistory: (symbol: string) => Promise<Transaction[]>;
  getPortfolioPerformance: (timeframe: '1d' | '1w' | '1M' | '3M' | '6M' | '1y' | 'all') => Promise<{
    dates: string[];
    values: number[];
    gains: number[];
    gainPercentages: number[];
  }>;
}

export const usePortfolio = (): UsePortfolioReturn => {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPortfolio = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      const response = await fetch('/api/portfolio');
      const data = await response.json();
      setPortfolio(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch portfolio');
      console.error('Error fetching portfolio:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPortfolio();
  }, [fetchPortfolio]);

  const addTransaction = async (transaction: Omit<Transaction, 'id' | 'date'>) => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch('/api/portfolio/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...transaction,
          date: new Date().toISOString(),
        }),
      });
      const updatedPortfolio = await response.json();
      setPortfolio(updatedPortfolio);
    } catch (err) {
      console.error('Error adding transaction:', err);
      throw err;
    }
  };

  const updatePosition = async (symbol: string, updates: Partial<Position>) => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch(`/api/portfolio/positions/${symbol}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      const updatedPortfolio = await response.json();
      setPortfolio(updatedPortfolio);
    } catch (err) {
      console.error('Error updating position:', err);
      throw err;
    }
  };

  const getPositionHistory = async (symbol: string): Promise<Transaction[]> => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch(`/api/portfolio/positions/${symbol}/history`);
      const data = await response.json();
      return data;
    } catch (err) {
      console.error('Error fetching position history:', err);
      throw err;
    }
  };

  const getPortfolioPerformance = async (
    timeframe: '1d' | '1w' | '1M' | '3M' | '6M' | '1y' | 'all'
  ) => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch(`/api/portfolio/performance?timeframe=${timeframe}`);
      const data = await response.json();
      return data;
    } catch (err) {
      console.error('Error fetching portfolio performance:', err);
      throw err;
    }
  };

  return {
    portfolio,
    loading,
    error,
    addTransaction,
    updatePosition,
    refresh: fetchPortfolio,
    getPositionHistory,
    getPortfolioPerformance,
  };
};

export default usePortfolio; 