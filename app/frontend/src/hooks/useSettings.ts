import { useState, useEffect, useCallback } from 'react';
import { settingsApi } from '../services/api';

interface MLSettings {
  modelType: 'lstm' | 'xgboost' | 'random_forest';
  predictionHorizon: number;
  confidenceThreshold: number;
  featureImportance: boolean;
  autoRetrain: boolean;
  retrainInterval: number;
  dataSource: 'alpha_vantage' | 'yahoo_finance' | 'custom';
  apiKey?: string;
}

interface UseSettingsReturn {
  settings: MLSettings | null;
  loading: boolean;
  error: string | null;
  updateSettings: (newSettings: Partial<MLSettings>) => Promise<void>;
}

/**
* Provides a hook to manage and update settings using state and API calls.
* @example
* const { settings, loading, error, updateSettings } = useSettings();
* settings - current settings object, loading - boolean, error - error message
* @param {Partial<MLSettings>} newSettings - An object representing the partial updated settings.
* @returns {UseSettingsReturn} An object containing settings, loading state, error message, and updateSettings function.
* @description
*   - Utilizes effects to automatically fetch settings when the hook is initialized.
*   - Handles loading and error state for both fetching and updating settings operations.
*   - Merges new settings with existing settings before updating.
*   - Throws an error if the updateSettings API operation fails.
*/
export const useSettings = (): UseSettingsReturn => {
  const [settings, setSettings] = useState<MLSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSettings = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await settingsApi.getSettings();
      setSettings(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch settings');
      console.error('Error fetching settings:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  /**
   * Updates the settings by synchronizing new data.
   * @example
   * sync({ theme: 'dark', notifications: true })
   * // Updates the application settings with the new values.
   * @param {Partial<MLSettings>} newSettings - The new settings to be merged and updated.
   * @returns {void} No direct return value, but throws an error if the update fails.
   * @description
   *   - Uses the settings API to send updated settings.
   *   - Provides a loading state and error handling during the update process.
   *   - Logs errors to the console and propagates exceptions for further handling.
   */
  const updateSettings = async (newSettings: Partial<MLSettings>) => {
    try {
      setLoading(true);
      setError(null);
      const response = await settingsApi.updateSettings({
        ...settings,
        ...newSettings,
      });
      setSettings(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update settings');
      console.error('Error updating settings:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    settings,
    loading,
    error,
    updateSettings,
  };
};

export default useSettings; 