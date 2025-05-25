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