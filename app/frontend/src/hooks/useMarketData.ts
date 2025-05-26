import { useState, useEffect, useCallback } from 'react';

interface MarketData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  peRatio: number;
  eps: number;
  dividend: number;
  dividendYield: number;
  high52Week: number;
  low52Week: number;
  lastUpdated: string;
}

interface ChartData {
  symbol: string;
  timeframe: '1d' | '1w' | '1M' | '3M' | '6M' | '1y' | '5y' | 'max';
  data: Array<{
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
}

interface UseMarketDataReturn {
  marketData: MarketData | null;
  chartData: ChartData | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  updateTimeframe: (timeframe: ChartData['timeframe']) => Promise<void>;
  getMultipleSymbols: (symbols: string[]) => Promise<MarketData[]>;
}

/**
 * Fetches and manages market and chart data based on the given symbol and timeframe.
 * @example
 * useMarketData('AAPL', '1M')
 * Returns an object containing market and chart data along with utility functions.
 * @param {string} symbol - The stock symbol for which to fetch market data.
 * @param {ChartData['timeframe']} initialTimeframe - The initial timeframe for chart data; defaults to '1M'.
 * @returns {UseMarketDataReturn} An object containing market data, chart data, loading state, error message, and utility functions for data management.
 * @description
 *   - Fetches market data and chart data asynchronously using mock API endpoints.
 *   - Provides utility functions to refresh market data, update the chart timeframe, and fetch data for multiple symbols.
 *   - Manages loading and error states during data fetching.
 */
export const useMarketData = (
  symbol: string,
  initialTimeframe: ChartData['timeframe'] = '1M'
): UseMarketDataReturn => {
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState<ChartData['timeframe']>(initialTimeframe);

  const fetchMarketData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      const response = await fetch(`/api/market/${symbol}`);
      const data = await response.json();
      setMarketData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch market data');
      console.error('Error fetching market data:', err);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  const fetchChartData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      const response = await fetch(`/api/market/${symbol}/chart?timeframe=${timeframe}`);
      const data = await response.json();
      setChartData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch chart data');
      console.error('Error fetching chart data:', err);
    } finally {
      setLoading(false);
    }
  }, [symbol, timeframe]);

  useEffect(() => {
    fetchMarketData();
    fetchChartData();
  }, [fetchMarketData, fetchChartData]);

  const updateTimeframe = async (newTimeframe: ChartData['timeframe']) => {
    setTimeframe(newTimeframe);
    await fetchChartData();
  };

  /**
  * Fetches market data for an array of symbols.
  * @example
  * sync(['AAPL', 'GOOGL'])
  * Returns a promise that resolves to an array of MarketData objects.
  * @param {string[]} symbols - An array of stock symbols to fetch data for.
  * @returns {Promise<MarketData[]>} A promise that resolves to an array of MarketData objects.
  * @description
  *   - Performs a POST request to fetch data using the provided stock symbols.
  *   - Expects a JSON response from the server with the market data.
  *   - Logs error information to the console if fetching fails.
  *   - The method is intended to be a placeholder until replaced with actual API call logic.
  */
  const getMultipleSymbols = async (symbols: string[]): Promise<MarketData[]> => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch('/api/market/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbols }),
      });
      const data = await response.json();
      return data;
    } catch (err) {
      console.error('Error fetching multiple symbols:', err);
      throw err;
    }
  };

  return {
    marketData,
    chartData,
    loading,
    error,
    refresh: fetchMarketData,
    updateTimeframe,
    getMultipleSymbols,
  };
};

export default useMarketData; 