import { useState, useCallback, useEffect } from 'react';
import { marketApi } from '../services/api';

interface ChartData {
  date: string;
  price: number;
  volume: number;
  indicators?: {
    sma?: number;
    ema?: number;
    rsi?: number;
    macd?: {
      value: number;
      signal: number;
      histogram: number;
    };
  };
}

interface ChartSettings {
  type: 'line' | 'candle' | 'area';
  interval: '1m' | '5m' | '15m' | '30m' | '1h' | '1d' | '1w' | '1M';
  indicators: {
    sma: boolean;
    ema: boolean;
    rsi: boolean;
    macd: boolean;
  };
  timeRange: '1d' | '1w' | '1M' | '3M' | '6M' | '1y' | '5y' | 'max';
}

interface UseChartReturn {
  data: ChartData[];
  settings: ChartSettings;
  loading: boolean;
  error: string | null;
  updateSettings: (newSettings: Partial<ChartSettings>) => void;
  refresh: () => Promise<void>;
}

const defaultSettings: ChartSettings = {
  type: 'line',
  interval: '1d',
  indicators: {
    sma: false,
    ema: false,
    rsi: false,
    macd: false,
  },
  timeRange: '1M',
};

export const useChart = (
  symbol: string,
  initialSettings?: Partial<ChartSettings>
): UseChartReturn => {
  const [data, setData] = useState<ChartData[]>([]);
  const [settings, setSettings] = useState<ChartSettings>({
    ...defaultSettings,
    ...initialSettings,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await marketApi.getStockData(symbol, settings.interval);
      setData(response.data.chartData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch chart data');
      console.error('Error fetching chart data:', err);
    } finally {
      setLoading(false);
    }
  }, [symbol, settings.interval]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const updateSettings = useCallback((newSettings: Partial<ChartSettings>) => {
    setSettings((prev) => ({ ...prev, ...newSettings }));
  }, []);

  return {
    data,
    settings,
    loading,
    error,
    updateSettings,
    refresh: fetchData,
  };
};

export default useChart; 