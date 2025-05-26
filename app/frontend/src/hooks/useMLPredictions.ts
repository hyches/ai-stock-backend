import { useState, useEffect, useCallback } from 'react';
import { mlApi } from '../services/api';

interface Prediction {
  symbol: string;
  direction: 'up' | 'down' | 'neutral';
  confidence: number;
  prediction: number;
  timestamp: string;
  features: Record<string, number>;
  historicalAccuracy: {
    lastWeek: number;
    lastMonth: number;
    lastYear: number;
  };
}

interface UseMLPredictionsReturn {
  prediction: Prediction | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  getFeatureImportance: () => Promise<Record<string, number>>;
}

/**
* Fetches and periodically refreshes machine learning predictions for a given stock symbol.
* @example
* useMLPredictions('AAPL', false, 600000)
* {
*   prediction: { /* Prediction object */
export const useMLPredictions = (
  symbol: string,
  autoRefresh: boolean = true,
  refreshInterval: number = 300000 // 5 minutes
): UseMLPredictionsReturn => {
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPrediction = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await mlApi.getPredictions(symbol);
      setPrediction(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch prediction');
      console.error('Error fetching ML prediction:', err);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    fetchPrediction();

    let intervalId: NodeJS.Timeout | null = null;
    if (autoRefresh) {
      intervalId = setInterval(fetchPrediction, refreshInterval);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [symbol, autoRefresh, refreshInterval, fetchPrediction]);

  const getFeatureImportance = async (): Promise<Record<string, number>> => {
    try {
      const response = await mlApi.getFeatureImportance(symbol);
      return response.data;
    } catch (err) {
      console.error('Error fetching feature importance:', err);
      throw err;
    }
  };

  return {
    prediction,
    loading,
    error,
    refresh: fetchPrediction,
    getFeatureImportance,
  };
};

export default useMLPredictions; 