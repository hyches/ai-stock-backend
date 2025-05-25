import { useState, useEffect, useCallback } from 'react';

interface UserPreferences {
  defaultView: 'portfolio' | 'watchlist' | 'market';
  defaultTimeframe: '1d' | '1w' | '1M' | '3M' | '6M' | '1y';
  defaultChartType: 'line' | 'candle' | 'area';
  defaultIndicators: {
    sma: boolean;
    ema: boolean;
    rsi: boolean;
    macd: boolean;
  };
  notifications: {
    priceAlerts: boolean;
    mlPredictions: boolean;
    portfolioUpdates: boolean;
    marketNews: boolean;
  };
  display: {
    showVolume: boolean;
    showGrid: boolean;
    showLegend: boolean;
    showTooltip: boolean;
  };
  layout: {
    sidebarCollapsed: boolean;
    chartHeight: number;
    tableDensity: 'comfortable' | 'compact' | 'standard';
  };
}

interface UsePreferencesReturn {
  preferences: UserPreferences | null;
  loading: boolean;
  error: string | null;
  updatePreferences: (updates: Partial<UserPreferences>) => Promise<void>;
  resetPreferences: () => Promise<void>;
}

const defaultPreferences: UserPreferences = {
  defaultView: 'portfolio',
  defaultTimeframe: '1M',
  defaultChartType: 'line',
  defaultIndicators: {
    sma: false,
    ema: false,
    rsi: false,
    macd: false,
  },
  notifications: {
    priceAlerts: true,
    mlPredictions: true,
    portfolioUpdates: true,
    marketNews: true,
  },
  display: {
    showVolume: true,
    showGrid: true,
    showLegend: true,
    showTooltip: true,
  },
  layout: {
    sidebarCollapsed: false,
    chartHeight: 400,
    tableDensity: 'comfortable',
  },
};

export const usePreferences = (): UsePreferencesReturn => {
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPreferences = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      const response = await fetch('/api/preferences');
      const data = await response.json();
      setPreferences(data);
    } catch (err) {
      console.error('Error fetching preferences:', err);
      // Fallback to default preferences if API fails
      setPreferences(defaultPreferences);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPreferences();
  }, [fetchPreferences]);

  const updatePreferences = async (updates: Partial<UserPreferences>) => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      const response = await fetch('/api/preferences', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      const updatedPreferences = await response.json();
      setPreferences(updatedPreferences);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update preferences');
      console.error('Error updating preferences:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const resetPreferences = async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      await fetch('/api/preferences/reset', { method: 'POST' });
      setPreferences(defaultPreferences);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to reset preferences');
      console.error('Error resetting preferences:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    preferences,
    loading,
    error,
    updatePreferences,
    resetPreferences,
  };
};

export default usePreferences; 