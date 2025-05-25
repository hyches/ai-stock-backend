import { useState, useEffect, useCallback } from 'react';
import { mlApi } from '../services/api';

interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1Score: number;
  confusionMatrix: {
    truePositive: number;
    trueNegative: number;
    falsePositive: number;
    falseNegative: number;
  };
}

interface ModelPerformance {
  modelType: string;
  symbol: string;
  metrics: ModelMetrics;
  trainingHistory: Array<{
    epoch: number;
    loss: number;
    accuracy: number;
    validationLoss: number;
    validationAccuracy: number;
  }>;
  featureImportance: Record<string, number>;
  lastTrained: string;
  nextTraining: string;
}

interface UseModelPerformanceReturn {
  performance: ModelPerformance | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  retrainModel: () => Promise<void>;
}

export const useModelPerformance = (
  symbol: string
): UseModelPerformanceReturn => {
  const [performance, setPerformance] = useState<ModelPerformance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPerformance = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await mlApi.getModelPerformance();
      setPerformance(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch model performance');
      console.error('Error fetching model performance:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPerformance();
  }, [fetchPerformance]);

  const retrainModel = async () => {
    try {
      setLoading(true);
      setError(null);
      await mlApi.retrainModel(symbol);
      await fetchPerformance();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to retrain model');
      console.error('Error retraining model:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    performance,
    loading,
    error,
    refresh: fetchPerformance,
    retrainModel,
  };
};

export default useModelPerformance; 