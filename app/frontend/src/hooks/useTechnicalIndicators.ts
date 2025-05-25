import { useState, useEffect, useCallback } from 'react';

interface IndicatorConfig {
  type: 'sma' | 'ema' | 'rsi' | 'macd' | 'bollinger' | 'volume';
  period?: number;
  color?: string;
  enabled: boolean;
}

interface IndicatorData {
  type: IndicatorConfig['type'];
  values: number[];
  dates: string[];
  config: IndicatorConfig;
}

interface UseTechnicalIndicatorsReturn {
  indicators: IndicatorData[];
  loading: boolean;
  error: string | null;
  addIndicator: (config: IndicatorConfig) => Promise<void>;
  removeIndicator: (type: IndicatorConfig['type']) => Promise<void>;
  updateIndicator: (type: IndicatorConfig['type'], config: Partial<IndicatorConfig>) => Promise<void>;
  refresh: () => Promise<void>;
}

export const useTechnicalIndicators = (
  symbol: string,
  timeframe: '1d' | '1w' | '1M' | '3M' | '6M' | '1y' | '5y' | 'max' = '1M'
): UseTechnicalIndicatorsReturn => {
  const [indicators, setIndicators] = useState<IndicatorData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchIndicators = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      const response = await fetch(`/api/indicators/${symbol}?timeframe=${timeframe}`);
      const data = await response.json();
      setIndicators(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch indicators');
      console.error('Error fetching technical indicators:', err);
    } finally {
      setLoading(false);
    }
  }, [symbol, timeframe]);

  useEffect(() => {
    fetchIndicators();
  }, [fetchIndicators]);

  const addIndicator = async (config: IndicatorConfig) => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch(`/api/indicators/${symbol}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...config, timeframe }),
      });
      const newIndicator = await response.json();
      setIndicators((prev) => [...prev, newIndicator]);
    } catch (err) {
      console.error('Error adding indicator:', err);
      throw err;
    }
  };

  const removeIndicator = async (type: IndicatorConfig['type']) => {
    try {
      // TODO: Replace with actual API call
      await fetch(`/api/indicators/${symbol}/${type}`, { method: 'DELETE' });
      setIndicators((prev) => prev.filter((ind) => ind.type !== type));
    } catch (err) {
      console.error('Error removing indicator:', err);
      throw err;
    }
  };

  const updateIndicator = async (
    type: IndicatorConfig['type'],
    config: Partial<IndicatorConfig>
  ) => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch(`/api/indicators/${symbol}/${type}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...config, timeframe }),
      });
      const updatedIndicator = await response.json();
      setIndicators((prev) =>
        prev.map((ind) => (ind.type === type ? updatedIndicator : ind))
      );
    } catch (err) {
      console.error('Error updating indicator:', err);
      throw err;
    }
  };

  return {
    indicators,
    loading,
    error,
    addIndicator,
    removeIndicator,
    updateIndicator,
    refresh: fetchIndicators,
  };
};

 