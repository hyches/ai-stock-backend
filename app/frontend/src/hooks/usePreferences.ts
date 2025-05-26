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

/**
* Custom hook to manage user preferences with loading and error states.
* @example
* const { preferences, loading, error, updatePreferences, resetPreferences } = usePreferences();
* @returns {UsePreferencesReturn} An object containing the preferences state, loading indicator, error message, and functions to update or reset preferences.
* @description
*   - Fetches user preferences from a mocked API endpoint initially and sets them into local state.
*   - Provides functionality to update user preferences via a PATCH request and reset preferences to default values.
*   - Handles loading and error states to inform the UI about ongoing asynchronous operations.
*/
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

  /**
   * Updates user preferences asynchronously using PATCH request.
   * @example
   * sync({ theme: 'dark', language: 'en' })
   * // Returns updated user preferences object
   * @param {Partial<UserPreferences>} updates - Partial object of user preferences to update.
   * @returns {Promise<void>} Resolves when preferences are successfully updated.
   * @description
   *   - The function sets the loading state while processing the request.
   *   - Handles errors by setting an error state and logging the issue.
   *   - Ensures the loading state is reset in the finally block, regardless of the success or failure of the operation.
   */
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

  /**
   * Resets the user preferences to default settings asynchronously.
   * @example
   * sync()
   * Resets preferences without any return value.
   * @returns {void} Does not return any value.
   * @description
   *   - The function is designed to handle errors that may occur during the API call to reset preferences.
   *   - It sets the loading state to true while the operation is in progress, and false once it is completed or failed.
   *   - The function updates the error state with a descriptive error message in case of failure.
   *   - It logs the error to the console to help with debugging when the preferences reset fails.
   */
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