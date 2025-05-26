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

/**
 * Fetches and manages model performance data based on a provided symbol.
 * @example
 * useModelPerformance('APPL')
 * {
 *   performance: { ... },
 *   loading: false,
 *   error: null,
 *   refresh: [Function],
 *   retrainModel: [Function]
 * }
 * @param {string} symbol - The symbol of the model to retrieve and manage performance data for.
 * @returns {UseModelPerformanceReturn} An object containing the model performance, loading and error states, and functions to refresh data and retrain the model.
 * @description
 *   - Utilizes the useState and useEffect hooks to manage asynchronous data fetching and UI state.
 *   - fetchPerformance is memoized using useCallback to avoid unnecessary re-creations.
 *   - The retrainModel function allows for triggering a model retraining based on the current symbol, followed by updating the performance data.
 */
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

  /**
   * Initiates the retraining of a machine learning model and fetches updated performance metrics.
   * @example
   * sync()
   * Error message or completed retraining process
   * @param {string} symbol - The symbol representing the specific model to retrain.
   * @returns {void} This function does not return a value.
   * @description
   *   - Sets loading state to true at the beginning and false at the end of the process.
   *   - Resets any existing error state before beginning execution.
   *   - If an error occurs during retraining, captures the error message for display.
   *   - Ensures performance metrics are fetched upon successful retraining.
   */
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