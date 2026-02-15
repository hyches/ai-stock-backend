// TensorFlow.js ML Model for Trading Predictions
import * as tf from '@tensorflow/tfjs';
import { FEATURE_NAMES, MLTrainingData } from './featureExtractor';

export interface ModelMetrics {
  loss: number;
  accuracy: number;
  epoch: number;
}

export interface TrainingProgress {
  epoch: number;
  totalEpochs: number;
  loss: number;
  accuracy: number;
  valLoss?: number;
  valAccuracy?: number;
}

export interface PredictionResult {
  signal: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  confidence: number;
  probabilities: {
    bearish: number;
    neutral: number;
    bullish: number;
  };
  featureImportance: { name: string; importance: number }[];
}

class TradingMLModel {
  private model: tf.LayersModel | null = null;
  private isTraining: boolean = false;
  private featureMeans: number[] = [];
  private featureStds: number[] = [];
  
  async initialize(): Promise<void> {
    // Try to load saved model from localStorage
    try {
      this.model = await tf.loadLayersModel('localstorage://trading-ml-model');
      const normalization = localStorage.getItem('trading-ml-normalization');
      if (normalization) {
        const { means, stds } = JSON.parse(normalization);
        this.featureMeans = means;
        this.featureStds = stds;
      }
      console.log('Loaded saved model from storage');
    } catch {
      console.log('No saved model found, will create new one when training');
    }
  }
  
  createModel(inputShape: number): tf.LayersModel {
    const model = tf.sequential();
    
    // Input layer with batch normalization
    model.add(tf.layers.dense({
      units: 128,
      activation: 'relu',
      inputShape: [inputShape],
      kernelRegularizer: tf.regularizers.l2({ l2: 0.001 }),
    }));
    model.add(tf.layers.batchNormalization());
    model.add(tf.layers.dropout({ rate: 0.3 }));
    
    // Hidden layers
    model.add(tf.layers.dense({
      units: 64,
      activation: 'relu',
      kernelRegularizer: tf.regularizers.l2({ l2: 0.001 }),
    }));
    model.add(tf.layers.batchNormalization());
    model.add(tf.layers.dropout({ rate: 0.2 }));
    
    model.add(tf.layers.dense({
      units: 32,
      activation: 'relu',
    }));
    model.add(tf.layers.dropout({ rate: 0.1 }));
    
    // Output layer (3 classes: bearish, neutral, bullish)
    model.add(tf.layers.dense({
      units: 3,
      activation: 'softmax',
    }));
    
    model.compile({
      optimizer: tf.train.adam(0.001),
      loss: 'sparseCategoricalCrossentropy',
      metrics: ['accuracy'],
    });
    
    return model;
  }
  
  normalizeFeatures(features: number[][]): { normalized: number[][]; means: number[]; stds: number[] } {
    const numFeatures = features[0].length;
    const means: number[] = [];
    const stds: number[] = [];
    
    // Calculate mean and std for each feature
    for (let j = 0; j < numFeatures; j++) {
      const values = features.map(f => f[j]);
      const mean = values.reduce((a, b) => a + b, 0) / values.length;
      const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
      const std = Math.sqrt(variance) || 1;
      means.push(mean);
      stds.push(std);
    }
    
    // Normalize
    const normalized = features.map(f => 
      f.map((val, j) => (val - means[j]) / stds[j])
    );
    
    return { normalized, means, stds };
  }
  
  async train(
    data: MLTrainingData,
    epochs: number = 50,
    batchSize: number = 32,
    validationSplit: number = 0.2,
    onProgress?: (progress: TrainingProgress) => void
  ): Promise<ModelMetrics[]> {
    if (this.isTraining) {
      throw new Error('Model is already training');
    }
    
    this.isTraining = true;
    const metrics: ModelMetrics[] = [];
    
    try {
      // Normalize features
      const { normalized, means, stds } = this.normalizeFeatures(data.features);
      this.featureMeans = means;
      this.featureStds = stds;
      
      // Create tensors
      const xs = tf.tensor2d(normalized);
      const ys = tf.tensor1d(data.labels, 'int32');
      
      // Create or reinitialize model
      this.model = this.createModel(data.features[0].length);
      
      // Train with callbacks
      await this.model.fit(xs, ys, {
        epochs,
        batchSize,
        validationSplit,
        shuffle: true,
        callbacks: {
          onEpochEnd: async (epoch, logs) => {
            const metric: ModelMetrics = {
              epoch,
              loss: logs?.loss || 0,
              accuracy: logs?.acc || 0,
            };
            metrics.push(metric);
            
            if (onProgress) {
              onProgress({
                epoch,
                totalEpochs: epochs,
                loss: logs?.loss || 0,
                accuracy: logs?.acc || 0,
                valLoss: logs?.val_loss,
                valAccuracy: logs?.val_acc,
              });
            }
          },
        },
      });
      
      // Save model
      await this.model.save('localstorage://trading-ml-model');
      localStorage.setItem('trading-ml-normalization', JSON.stringify({
        means: this.featureMeans,
        stds: this.featureStds,
      }));
      
      // Cleanup tensors
      xs.dispose();
      ys.dispose();
      
      return metrics;
    } finally {
      this.isTraining = false;
    }
  }
  
  async predict(features: number[]): Promise<PredictionResult> {
    if (!this.model) {
      throw new Error('Model not trained yet');
    }
    
    // Normalize using stored means/stds
    const normalized = features.map((val, i) => 
      (val - (this.featureMeans[i] || 0)) / (this.featureStds[i] || 1)
    );
    
    const input = tf.tensor2d([normalized]);
    const prediction = this.model.predict(input) as tf.Tensor;
    const probabilities = await prediction.data();
    
    input.dispose();
    prediction.dispose();
    
    const [bearish, neutral, bullish] = probabilities;
    
    // Determine signal
    let signal: 'BULLISH' | 'BEARISH' | 'NEUTRAL' = 'NEUTRAL';
    let confidence = neutral;
    
    if (bullish > bearish && bullish > neutral) {
      signal = 'BULLISH';
      confidence = bullish;
    } else if (bearish > bullish && bearish > neutral) {
      signal = 'BEARISH';
      confidence = bearish;
    }
    
    // Calculate feature importance using gradient-based method
    const featureImportance = await this.calculateFeatureImportance(features);
    
    return {
      signal,
      confidence,
      probabilities: { bearish, neutral, bullish },
      featureImportance,
    };
  }
  
  async calculateFeatureImportance(features: number[]): Promise<{ name: string; importance: number }[]> {
    if (!this.model) return [];
    
    const importance: { name: string; importance: number }[] = [];
    
    // Simple permutation-based importance estimation
    const baseInput = features.map((val, i) => 
      (val - (this.featureMeans[i] || 0)) / (this.featureStds[i] || 1)
    );
    
    const baseTensor = tf.tensor2d([baseInput]);
    const basePred = (this.model.predict(baseTensor) as tf.Tensor);
    const baseProbs = await basePred.data();
    baseTensor.dispose();
    basePred.dispose();
    
    for (let i = 0; i < features.length; i++) {
      // Perturb feature
      const perturbed = [...baseInput];
      perturbed[i] = 0; // Zero out the feature
      
      const perturbedTensor = tf.tensor2d([perturbed]);
      const perturbedPred = (this.model.predict(perturbedTensor) as tf.Tensor);
      const perturbedProbs = await perturbedPred.data();
      perturbedTensor.dispose();
      perturbedPred.dispose();
      
      // Calculate change in prediction
      const change = Math.abs(baseProbs[2] - perturbedProbs[2]) + 
                     Math.abs(baseProbs[0] - perturbedProbs[0]);
      
      importance.push({
        name: FEATURE_NAMES[i] || `feature_${i}`,
        importance: change,
      });
    }
    
    // Normalize importance scores
    const maxImportance = Math.max(...importance.map(i => i.importance));
    if (maxImportance > 0) {
      importance.forEach(i => i.importance /= maxImportance);
    }
    
    return importance.sort((a, b) => b.importance - a.importance);
  }
  
  async addTrainingExample(features: number[], label: number): Promise<void> {
    // Store in localStorage for incremental learning
    const stored = localStorage.getItem('trading-ml-examples');
    const examples = stored ? JSON.parse(stored) : { features: [], labels: [] };
    
    examples.features.push(features);
    examples.labels.push(label);
    
    localStorage.setItem('trading-ml-examples', JSON.stringify(examples));
    
    // Trigger retraining if we have enough new examples
    if (examples.features.length >= 100) {
      console.log('Auto-retraining with', examples.features.length, 'examples');
      // Could trigger background retraining here
    }
  }
  
  getStoredExamplesCount(): number {
    const stored = localStorage.getItem('trading-ml-examples');
    if (!stored) return 0;
    const examples = JSON.parse(stored);
    return examples.features.length;
  }
  
  isModelTrained(): boolean {
    return this.model !== null;
  }
  
  isCurrentlyTraining(): boolean {
    return this.isTraining;
  }
  
  async dispose(): Promise<void> {
    if (this.model) {
      this.model.dispose();
      this.model = null;
    }
  }
}

// Singleton instance
export const tradingModel = new TradingMLModel();
