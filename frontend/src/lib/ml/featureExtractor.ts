// ML Feature Extraction from Trade Data
import { Trade } from '@/context/TradingContext';
import { OHLCV, calculateRSI, calculateMACD, calculateBollingerBands, calculateATR, calculateSMA, calculateEMA } from '@/lib/backtesting/engine';

export interface TradeFeatures {
  // Price-based features
  priceChange1m: number;
  priceChange5m: number;
  priceChange15m: number;
  priceChange1h: number;

  // Volume features
  volumeRatio: number;
  volumeTrend: number;

  // Technical indicators
  rsi: number;
  rsiSlope: number;
  macd: number;
  macdSignal: number;
  macdHistogram: number;
  bbPosition: number; // 0-1 scale within bands
  bbWidth: number;
  atr: number;
  atrPercent: number;

  // Moving averages
  priceVsSMA20: number;
  priceVsSMA50: number;
  sma20VsSma50: number;
  ema12VsEma26: number;

  // Pattern features
  higherHighs: number;
  lowerLows: number;
  bodyRatio: number;
  upperWickRatio: number;
  lowerWickRatio: number;

  // Time features
  hourOfDay: number;
  dayOfWeek: number;
  minuteOfHour: number;

  // OI features (for options)
  oiChange: number;
  callPutRatio: number;
  ivRank: number;

  // Label (for training)
  outcome?: 'PROFIT' | 'LOSS' | 'NEUTRAL';
  outcomeValue?: number;
}

export interface MLTrainingData {
  features: number[][];
  labels: number[];
  featureNames: string[];
}

// Extract features from OHLCV data at a specific point
export function extractFeaturesFromOHLCV(
  data: OHLCV[],
  index: number,
  lookback: number = 50
): TradeFeatures | null {
  if (index < lookback) return null;

  const slice = data.slice(index - lookback, index + 1);
  const current = slice[slice.length - 1];
  const closes = slice.map(d => d.close);
  const volumes = slice.map(d => d.volume);

  // Price changes
  const priceChange1m = index >= 1 ? ((current.close - data[index - 1].close) / data[index - 1].close) * 100 : 0;
  const priceChange5m = index >= 5 ? ((current.close - data[index - 5].close) / data[index - 5].close) * 100 : 0;
  const priceChange15m = index >= 15 ? ((current.close - data[index - 15].close) / data[index - 15].close) * 100 : 0;
  const priceChange1h = index >= 60 ? ((current.close - data[index - 60].close) / data[index - 60].close) * 100 : 0;

  // Volume
  const avgVolume = volumes.slice(0, -1).reduce((a, b) => a + b, 0) / (volumes.length - 1);
  const volumeRatio = current.volume / avgVolume;
  const recentVolume = volumes.slice(-5).reduce((a, b) => a + b, 0) / 5;
  const olderVolume = volumes.slice(-10, -5).reduce((a, b) => a + b, 0) / 5;
  const volumeTrend = olderVolume > 0 ? recentVolume / olderVolume : 1;

  // RSI
  const rsiValues = calculateRSI(closes, 14);
  const rsi = rsiValues[rsiValues.length - 1] || 50;
  const rsiSlope = rsiValues.length > 5
    ? (rsiValues[rsiValues.length - 1] - rsiValues[rsiValues.length - 5]) / 5
    : 0;

  // MACD
  const macdData = calculateMACD(closes);
  const macd = macdData.macd[macdData.macd.length - 1] || 0;
  const macdSignal = macdData.signal[macdData.signal.length - 1] || 0;
  const macdHistogram = macdData.histogram[macdData.histogram.length - 1] || 0;

  // Bollinger Bands
  const bb = calculateBollingerBands(closes, 20, 2);
  const bbUpper = bb.upper[bb.upper.length - 1];
  const bbLower = bb.lower[bb.lower.length - 1];
  const bbMiddle = bb.middle[bb.middle.length - 1];
  const bbPosition = bbUpper !== bbLower ? (current.close - bbLower) / (bbUpper - bbLower) : 0.5;
  const bbWidth = bbMiddle > 0 ? (bbUpper - bbLower) / bbMiddle : 0;

  // ATR
  const atrValues = calculateATR(slice, 14);
  const atr = atrValues[atrValues.length - 1] || 0;
  const atrPercent = current.close > 0 ? (atr / current.close) * 100 : 0;

  // Moving Averages
  const sma20 = calculateSMA(closes, 20);
  const sma50 = calculateSMA(closes.slice(-50), 50);
  const ema12 = calculateEMA(closes, 12);
  const ema26 = calculateEMA(closes, 26);

  const sma20Val = sma20[sma20.length - 1] || current.close;
  const sma50Val = sma50[sma50.length - 1] || current.close;
  const ema12Val = ema12[ema12.length - 1] || current.close;
  const ema26Val = ema26[ema26.length - 1] || current.close;

  const priceVsSMA20 = sma20Val > 0 ? ((current.close - sma20Val) / sma20Val) * 100 : 0;
  const priceVsSMA50 = sma50Val > 0 ? ((current.close - sma50Val) / sma50Val) * 100 : 0;
  const sma20VsSma50 = sma50Val > 0 ? ((sma20Val - sma50Val) / sma50Val) * 100 : 0;
  const ema12VsEma26 = ema26Val > 0 ? ((ema12Val - ema26Val) / ema26Val) * 100 : 0;

  // Pattern detection
  let higherHighs = 0;
  let lowerLows = 0;
  for (let i = slice.length - 5; i < slice.length - 1; i++) {
    if (slice[i].high < slice[i + 1].high) higherHighs++;
    if (slice[i].low > slice[i + 1].low) lowerLows++;
  }

  // Candlestick features
  const body = Math.abs(current.close - current.open);
  const range = current.high - current.low;
  const bodyRatio = range > 0 ? body / range : 0;
  const upperWick = current.high - Math.max(current.open, current.close);
  const lowerWick = Math.min(current.open, current.close) - current.low;
  const upperWickRatio = range > 0 ? upperWick / range : 0;
  const lowerWickRatio = range > 0 ? lowerWick / range : 0;

  // Time features
  const hourOfDay = current.timestamp.getHours();
  const dayOfWeek = current.timestamp.getDay();
  const minuteOfHour = current.timestamp.getMinutes();

  return {
    priceChange1m,
    priceChange5m,
    priceChange15m,
    priceChange1h,
    volumeRatio,
    volumeTrend,
    rsi,
    rsiSlope,
    macd,
    macdSignal,
    macdHistogram,
    bbPosition,
    bbWidth,
    atr,
    atrPercent,
    priceVsSMA20,
    priceVsSMA50,
    sma20VsSma50,
    ema12VsEma26,
    higherHighs,
    lowerLows,
    bodyRatio,
    upperWickRatio,
    lowerWickRatio,
    hourOfDay,
    dayOfWeek,
    minuteOfHour,
    oiChange: 0, // Would need OI data
    callPutRatio: 1, // Would need option chain data
    ivRank: 50, // Would need IV history
  };
}

// Convert features to array for ML model
export function featuresToArray(features: TradeFeatures): number[] {
  return [
    features.priceChange1m,
    features.priceChange5m,
    features.priceChange15m,
    features.priceChange1h,
    features.volumeRatio,
    features.volumeTrend,
    features.rsi / 100, // Normalize to 0-1
    features.rsiSlope,
    features.macd,
    features.macdSignal,
    features.macdHistogram,
    features.bbPosition,
    features.bbWidth,
    features.atrPercent,
    features.priceVsSMA20,
    features.priceVsSMA50,
    features.sma20VsSma50,
    features.ema12VsEma26,
    features.higherHighs / 4, // Normalize
    features.lowerLows / 4,
    features.bodyRatio,
    features.upperWickRatio,
    features.lowerWickRatio,
    features.hourOfDay / 24, // Normalize
    features.dayOfWeek / 7,
    features.minuteOfHour / 60,
    features.oiChange,
    features.callPutRatio,
    features.ivRank / 100,
  ];
}

export const FEATURE_NAMES = [
  'priceChange1m', 'priceChange5m', 'priceChange15m', 'priceChange1h',
  'volumeRatio', 'volumeTrend',
  'rsi', 'rsiSlope',
  'macd', 'macdSignal', 'macdHistogram',
  'bbPosition', 'bbWidth',
  'atrPercent',
  'priceVsSMA20', 'priceVsSMA50', 'sma20VsSma50', 'ema12VsEma26',
  'higherHighs', 'lowerLows',
  'bodyRatio', 'upperWickRatio', 'lowerWickRatio',
  'hourOfDay', 'dayOfWeek', 'minuteOfHour',
  'oiChange', 'callPutRatio', 'ivRank',
];

// Generate training data from historical OHLCV with forward-looking labels
export function generateTrainingData(
  data: OHLCV[],
  forwardPeriod: number = 15, // Look 15 bars ahead for outcome
  profitThreshold: number = 0.5 // 0.5% threshold for profit/loss classification
): MLTrainingData {
  const features: number[][] = [];
  const labels: number[] = [];

  for (let i = 50; i < data.length - forwardPeriod; i++) {
    const feature = extractFeaturesFromOHLCV(data, i);
    if (!feature) continue;

    // Calculate forward return for label
    const currentPrice = data[i].close;
    const futurePrice = data[i + forwardPeriod].close;
    const forwardReturn = ((futurePrice - currentPrice) / currentPrice) * 100;

    // Label: 0 = bearish, 1 = neutral, 2 = bullish
    let label = 1; // neutral
    if (forwardReturn > profitThreshold) label = 2; // bullish
    else if (forwardReturn < -profitThreshold) label = 0; // bearish

    features.push(featuresToArray(feature));
    labels.push(label);
  }

  return { features, labels, featureNames: FEATURE_NAMES };
}

// Extract features from executed trades for learning
export function extractFeaturesFromTrade(
  trade: Trade,
  priceData: OHLCV[],
  outcome: 'PROFIT' | 'LOSS' | 'NEUTRAL',
  outcomeValue: number
): { features: number[]; label: number } | null {
  // Find the index in price data closest to trade time
  const tradeTime = trade.timestamp.getTime();
  let closestIndex = -1;
  let minDiff = Infinity;

  for (let i = 0; i < priceData.length; i++) {
    const diff = Math.abs(priceData[i].timestamp.getTime() - tradeTime);
    if (diff < minDiff) {
      minDiff = diff;
      closestIndex = i;
    }
  }

  if (closestIndex < 50) return null;

  const feature = extractFeaturesFromOHLCV(priceData, closestIndex);
  if (!feature) return null;

  // For trade-based learning, we use actual outcome
  const label = outcome === 'PROFIT' ? 2 : outcome === 'LOSS' ? 0 : 1;

  return { features: featuresToArray(feature), label };
}
