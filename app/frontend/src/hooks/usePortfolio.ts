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

/**
 * Returns a set of functions and data related to portfolio management, including fetching, adding transactions, and updating positions.
 * @example
 * usePortfolio()
 * {
 *   portfolio: null,
 *   loading: true,
 *   error: null,
 *   addTransaction: async function,
 *   updatePosition: async function,
 *   refresh: async function,
 *   getPositionHistory: async function,
 *   getPortfolioPerformance: async function
 * }
 * @returns {UsePortfolioReturn} Object containing portfolio data and functions for interaction.
 * @description
 *   - Handles asynchronous operations with try-catch blocks to manage errors effectively.
 *   - Utilizes `useState` and `useEffect` hooks to manage portfolio state and lifecycle.
 *   - Provides customizable API call examples that require completion with actual endpoints.
 */
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

  /**
   * Sends a new transaction to the server and updates the portfolio state.
   * @example
   * sync({ type: 'buy', amount: 50, currency: 'USD' })
   * // Updates the portfolio with the new transaction
   * @param {Omit<Transaction, 'id' | 'date'>} transaction - Object containing transaction details, excluding 'id' and 'date'.
   * @returns {Promise<void>} No return value, updates the portfolio state.
   * @description
   *   - Automatically sets the transaction date to the current date and time.
   *   - Logs errors to the console if the API call fails.
   *   - Uses a POST request to '/api/portfolio/transactions' to add the transaction.
   */
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

  /**
   * Updates the portfolio position for a given symbol with specified changes.
   * @example
   * sync('AAPL', { shares: 10, price: 150 })
   * // Updates the position for symbol 'AAPL' in the portfolio
   * @param {string} symbol - The stock symbol that identifies the position to be updated.
   * @param {Partial<Position>} updates - An object containing updates for the position fields such as shares or price.
   * @returns {Promise<void>} Resolves when the update succeeds, or throws an error if the update fails.
   * @description
   *   - Uses the PATCH method to update a position asynchronously.
   *   - Assumes the API endpoint `/api/portfolio/positions/${symbol}` exists and is functional.
   *   - Throws an error if the fetching or updating fails, making it necessary to handle exceptions when calling this function.
   */
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

  /**
   * Fetches portfolio performance data for a given timeframe.
   * @example
   * sync('1d')
   * { performance: [...] }
   * @param {'1d' | '1w' | '1M' | '3M' | '6M' | '1y' | 'all'} timeframe - Specifies the period for which performance data is requested.
   * @returns {Promise<object>} Returns a promise that resolves to the performance data for the specified timeframe.
   * @description
   *   - Utilizes fetch API to retrieve data from the server.
   *   - Handles errors by logging them and rethrowing for further action.
   */
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