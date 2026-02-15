// Backtesting Engine for Indian Stock Market
export interface OHLCV {
  timestamp: Date;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface BacktestTrade {
  entryTime: Date;
  exitTime: Date;
  type: 'LONG' | 'SHORT';
  entryPrice: number;
  exitPrice: number;
  quantity: number;
  pnl: number;
  pnlPercent: number;
  exitReason: 'SIGNAL' | 'STOP_LOSS' | 'TARGET' | 'TRAILING_STOP' | 'TIME_EXIT';
}

export interface BacktestResult {
  totalTrades: number;
  winningTrades: number;
  losingTrades: number;
  winRate: number;
  totalPnL: number;
  totalPnLPercent: number;
  avgWin: number;
  avgLoss: number;
  largestWin: number;
  largestLoss: number;
  profitFactor: number;
  sharpeRatio: number;
  sortinoRatio: number;
  maxDrawdown: number;
  maxDrawdownPercent: number;
  calmarRatio: number;
  avgHoldingPeriod: number;
  trades: BacktestTrade[];
  equityCurve: { date: Date; equity: number }[];
  drawdownCurve: { date: Date; drawdown: number }[];
  monthlyReturns: { month: string; return: number }[];
}

export interface StrategyConfig {
  name: string;
  initialCapital: number;
  positionSize: number; // Percentage of capital
  stopLoss: number; // Percentage
  takeProfit: number; // Percentage
  trailingStop?: number; // Percentage
  maxHoldingPeriod?: number; // In candles
  entryCondition: (data: OHLCV[], index: number, indicators: IndicatorValues) => 'LONG' | 'SHORT' | null;
  exitCondition?: (data: OHLCV[], index: number, indicators: IndicatorValues, position: 'LONG' | 'SHORT') => boolean;
}

export interface IndicatorValues {
  sma20: number;
  sma50: number;
  ema12: number;
  ema26: number;
  rsi: number;
  macd: number;
  macdSignal: number;
  macdHistogram: number;
  bbUpper: number;
  bbMiddle: number;
  bbLower: number;
  atr: number;
  adx: number;
  obv: number;
  vwap: number;
}

// Technical Indicators
export function calculateSMA(data: number[], period: number): number[] {
  const result: number[] = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(NaN);
    } else {
      const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
      result.push(sum / period);
    }
  }
  return result;
}

export function calculateEMA(data: number[], period: number): number[] {
  const result: number[] = [];
  const multiplier = 2 / (period + 1);
  
  for (let i = 0; i < data.length; i++) {
    if (i === 0) {
      result.push(data[0]);
    } else if (i < period - 1) {
      result.push(NaN);
    } else if (i === period - 1) {
      const sma = data.slice(0, period).reduce((a, b) => a + b, 0) / period;
      result.push(sma);
    } else {
      result.push((data[i] - result[i - 1]) * multiplier + result[i - 1]);
    }
  }
  return result;
}

export function calculateRSI(data: number[], period: number = 14): number[] {
  const result: number[] = [];
  const changes: number[] = [];
  
  for (let i = 1; i < data.length; i++) {
    changes.push(data[i] - data[i - 1]);
  }
  
  for (let i = 0; i < data.length; i++) {
    if (i < period) {
      result.push(NaN);
    } else {
      const relevantChanges = changes.slice(i - period, i);
      const gains = relevantChanges.filter(c => c > 0);
      const losses = relevantChanges.filter(c => c < 0).map(c => Math.abs(c));
      
      const avgGain = gains.length > 0 ? gains.reduce((a, b) => a + b, 0) / period : 0;
      const avgLoss = losses.length > 0 ? losses.reduce((a, b) => a + b, 0) / period : 0;
      
      if (avgLoss === 0) {
        result.push(100);
      } else {
        const rs = avgGain / avgLoss;
        result.push(100 - (100 / (1 + rs)));
      }
    }
  }
  return result;
}

export function calculateMACD(data: number[]): { macd: number[]; signal: number[]; histogram: number[] } {
  const ema12 = calculateEMA(data, 12);
  const ema26 = calculateEMA(data, 26);
  const macd: number[] = [];
  
  for (let i = 0; i < data.length; i++) {
    macd.push(ema12[i] - ema26[i]);
  }
  
  const signal = calculateEMA(macd, 9);
  const histogram = macd.map((m, i) => m - signal[i]);
  
  return { macd, signal, histogram };
}

export function calculateBollingerBands(data: number[], period: number = 20, stdDev: number = 2): { upper: number[]; middle: number[]; lower: number[] } {
  const middle = calculateSMA(data, period);
  const upper: number[] = [];
  const lower: number[] = [];
  
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      upper.push(NaN);
      lower.push(NaN);
    } else {
      const slice = data.slice(i - period + 1, i + 1);
      const mean = middle[i];
      const variance = slice.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / period;
      const std = Math.sqrt(variance);
      upper.push(mean + stdDev * std);
      lower.push(mean - stdDev * std);
    }
  }
  
  return { upper, middle, lower };
}

export function calculateATR(data: OHLCV[], period: number = 14): number[] {
  const tr: number[] = [];
  
  for (let i = 0; i < data.length; i++) {
    if (i === 0) {
      tr.push(data[i].high - data[i].low);
    } else {
      const hl = data[i].high - data[i].low;
      const hc = Math.abs(data[i].high - data[i - 1].close);
      const lc = Math.abs(data[i].low - data[i - 1].close);
      tr.push(Math.max(hl, hc, lc));
    }
  }
  
  return calculateEMA(tr, period);
}

export function calculateAllIndicators(data: OHLCV[]): IndicatorValues[] {
  const closes = data.map(d => d.close);
  const volumes = data.map(d => d.volume);
  
  const sma20 = calculateSMA(closes, 20);
  const sma50 = calculateSMA(closes, 50);
  const ema12 = calculateEMA(closes, 12);
  const ema26 = calculateEMA(closes, 26);
  const rsi = calculateRSI(closes, 14);
  const { macd, signal: macdSignal, histogram: macdHistogram } = calculateMACD(closes);
  const { upper: bbUpper, middle: bbMiddle, lower: bbLower } = calculateBollingerBands(closes, 20, 2);
  const atr = calculateATR(data, 14);
  
  // Simplified OBV
  const obv: number[] = [0];
  for (let i = 1; i < data.length; i++) {
    if (closes[i] > closes[i - 1]) {
      obv.push(obv[i - 1] + volumes[i]);
    } else if (closes[i] < closes[i - 1]) {
      obv.push(obv[i - 1] - volumes[i]);
    } else {
      obv.push(obv[i - 1]);
    }
  }
  
  // Simplified VWAP (intraday approximation)
  const vwap: number[] = [];
  let cumulativeVolume = 0;
  let cumulativeVWAP = 0;
  for (let i = 0; i < data.length; i++) {
    const typicalPrice = (data[i].high + data[i].low + data[i].close) / 3;
    cumulativeVolume += volumes[i];
    cumulativeVWAP += typicalPrice * volumes[i];
    vwap.push(cumulativeVWAP / cumulativeVolume);
  }
  
  return data.map((_, i) => ({
    sma20: sma20[i],
    sma50: sma50[i],
    ema12: ema12[i],
    ema26: ema26[i],
    rsi: rsi[i],
    macd: macd[i],
    macdSignal: macdSignal[i],
    macdHistogram: macdHistogram[i],
    bbUpper: bbUpper[i],
    bbMiddle: bbMiddle[i],
    bbLower: bbLower[i],
    atr: atr[i],
    adx: 25, // Simplified
    obv: obv[i],
    vwap: vwap[i],
  }));
}

// Main Backtesting Engine
export function runBacktest(data: OHLCV[], strategy: StrategyConfig): BacktestResult {
  const indicators = calculateAllIndicators(data);
  const trades: BacktestTrade[] = [];
  let capital = strategy.initialCapital;
  let position: { type: 'LONG' | 'SHORT'; entryPrice: number; entryTime: Date; quantity: number; entryIndex: number } | null = null;
  
  const equityCurve: { date: Date; equity: number }[] = [];
  let peakEquity = capital;
  const drawdownCurve: { date: Date; drawdown: number }[] = [];
  
  for (let i = 50; i < data.length; i++) {
    const currentBar = data[i];
    const ind = indicators[i];
    
    // Update equity curve
    let currentEquity = capital;
    if (position) {
      const unrealizedPnL = position.type === 'LONG' 
        ? (currentBar.close - position.entryPrice) * position.quantity
        : (position.entryPrice - currentBar.close) * position.quantity;
      currentEquity += unrealizedPnL;
    }
    equityCurve.push({ date: currentBar.timestamp, equity: currentEquity });
    
    // Calculate drawdown
    peakEquity = Math.max(peakEquity, currentEquity);
    const drawdown = ((peakEquity - currentEquity) / peakEquity) * 100;
    drawdownCurve.push({ date: currentBar.timestamp, drawdown });
    
    if (!position) {
      // Check entry
      const signal = strategy.entryCondition(data, i, ind);
      if (signal) {
        const positionValue = capital * (strategy.positionSize / 100);
        const quantity = Math.floor(positionValue / currentBar.close);
        if (quantity > 0) {
          position = {
            type: signal,
            entryPrice: currentBar.close,
            entryTime: currentBar.timestamp,
            quantity,
            entryIndex: i,
          };
        }
      }
    } else {
      // Check exit conditions
      let shouldExit = false;
      let exitReason: BacktestTrade['exitReason'] = 'SIGNAL';
      
      const pnlPercent = position.type === 'LONG'
        ? ((currentBar.close - position.entryPrice) / position.entryPrice) * 100
        : ((position.entryPrice - currentBar.close) / position.entryPrice) * 100;
      
      // Stop loss
      if (pnlPercent <= -strategy.stopLoss) {
        shouldExit = true;
        exitReason = 'STOP_LOSS';
      }
      
      // Take profit
      if (pnlPercent >= strategy.takeProfit) {
        shouldExit = true;
        exitReason = 'TARGET';
      }
      
      // Max holding period
      if (strategy.maxHoldingPeriod && (i - position.entryIndex) >= strategy.maxHoldingPeriod) {
        shouldExit = true;
        exitReason = 'TIME_EXIT';
      }
      
      // Custom exit condition
      if (strategy.exitCondition && strategy.exitCondition(data, i, ind, position.type)) {
        shouldExit = true;
        exitReason = 'SIGNAL';
      }
      
      if (shouldExit) {
        const pnl = position.type === 'LONG'
          ? (currentBar.close - position.entryPrice) * position.quantity
          : (position.entryPrice - currentBar.close) * position.quantity;
        
        trades.push({
          entryTime: position.entryTime,
          exitTime: currentBar.timestamp,
          type: position.type,
          entryPrice: position.entryPrice,
          exitPrice: currentBar.close,
          quantity: position.quantity,
          pnl,
          pnlPercent,
          exitReason,
        });
        
        capital += pnl;
        position = null;
      }
    }
  }
  
  // Calculate statistics
  const winningTrades = trades.filter(t => t.pnl > 0);
  const losingTrades = trades.filter(t => t.pnl <= 0);
  
  const totalPnL = trades.reduce((sum, t) => sum + t.pnl, 0);
  const totalPnLPercent = ((capital - strategy.initialCapital) / strategy.initialCapital) * 100;
  
  const avgWin = winningTrades.length > 0 
    ? winningTrades.reduce((sum, t) => sum + t.pnl, 0) / winningTrades.length 
    : 0;
  const avgLoss = losingTrades.length > 0 
    ? losingTrades.reduce((sum, t) => sum + t.pnl, 0) / losingTrades.length 
    : 0;
  
  const grossProfit = winningTrades.reduce((sum, t) => sum + t.pnl, 0);
  const grossLoss = Math.abs(losingTrades.reduce((sum, t) => sum + t.pnl, 0));
  const profitFactor = grossLoss > 0 ? grossProfit / grossLoss : grossProfit > 0 ? Infinity : 0;
  
  // Sharpe Ratio (annualized)
  const returns = trades.map(t => t.pnlPercent);
  const avgReturn = returns.length > 0 ? returns.reduce((a, b) => a + b, 0) / returns.length : 0;
  const stdReturn = Math.sqrt(returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length);
  const sharpeRatio = stdReturn > 0 ? (avgReturn / stdReturn) * Math.sqrt(252) : 0;
  
  // Sortino Ratio (only downside deviation)
  const negativeReturns = returns.filter(r => r < 0);
  const downsideDeviation = Math.sqrt(
    negativeReturns.reduce((sum, r) => sum + Math.pow(r, 2), 0) / negativeReturns.length
  );
  const sortinoRatio = downsideDeviation > 0 ? (avgReturn / downsideDeviation) * Math.sqrt(252) : 0;
  
  // Max Drawdown
  const maxDrawdown = Math.max(...drawdownCurve.map(d => d.drawdown));
  const maxDrawdownValue = (maxDrawdown / 100) * peakEquity;
  
  // Calmar Ratio
  const annualizedReturn = totalPnLPercent * (252 / data.length);
  const calmarRatio = maxDrawdown > 0 ? annualizedReturn / maxDrawdown : 0;
  
  // Average holding period
  const avgHoldingPeriod = trades.length > 0
    ? trades.reduce((sum, t) => sum + (t.exitTime.getTime() - t.entryTime.getTime()), 0) / trades.length / (1000 * 60 * 60 * 24)
    : 0;
  
  // Monthly returns
  const monthlyReturns: { month: string; return: number }[] = [];
  const tradesByMonth = new Map<string, BacktestTrade[]>();
  trades.forEach(t => {
    const month = `${t.exitTime.getFullYear()}-${String(t.exitTime.getMonth() + 1).padStart(2, '0')}`;
    if (!tradesByMonth.has(month)) {
      tradesByMonth.set(month, []);
    }
    tradesByMonth.get(month)!.push(t);
  });
  tradesByMonth.forEach((monthTrades, month) => {
    const monthReturn = monthTrades.reduce((sum, t) => sum + t.pnlPercent, 0);
    monthlyReturns.push({ month, return: monthReturn });
  });
  
  return {
    totalTrades: trades.length,
    winningTrades: winningTrades.length,
    losingTrades: losingTrades.length,
    winRate: trades.length > 0 ? (winningTrades.length / trades.length) * 100 : 0,
    totalPnL,
    totalPnLPercent,
    avgWin,
    avgLoss,
    largestWin: winningTrades.length > 0 ? Math.max(...winningTrades.map(t => t.pnl)) : 0,
    largestLoss: losingTrades.length > 0 ? Math.min(...losingTrades.map(t => t.pnl)) : 0,
    profitFactor,
    sharpeRatio,
    sortinoRatio,
    maxDrawdown: maxDrawdownValue,
    maxDrawdownPercent: maxDrawdown,
    calmarRatio,
    avgHoldingPeriod,
    trades,
    equityCurve,
    drawdownCurve,
    monthlyReturns,
  };
}

// Predefined Strategies
export const predefinedStrategies: { name: string; description: string; config: Partial<StrategyConfig> }[] = [
  {
    name: 'RSI Reversal',
    description: 'Buy when RSI < 30, sell when RSI > 70',
    config: {
      stopLoss: 2,
      takeProfit: 4,
      entryCondition: (data, i, ind) => {
        if (ind.rsi < 30) return 'LONG';
        if (ind.rsi > 70) return 'SHORT';
        return null;
      },
      exitCondition: (data, i, ind, pos) => {
        if (pos === 'LONG' && ind.rsi > 60) return true;
        if (pos === 'SHORT' && ind.rsi < 40) return true;
        return false;
      },
    },
  },
  {
    name: 'MACD Crossover',
    description: 'Trade MACD line crossing signal line',
    config: {
      stopLoss: 1.5,
      takeProfit: 3,
      entryCondition: (data, i, ind) => {
        if (i < 1) return null;
        const prevInd = calculateAllIndicators(data)[i - 1];
        if (prevInd.macd < prevInd.macdSignal && ind.macd > ind.macdSignal) return 'LONG';
        if (prevInd.macd > prevInd.macdSignal && ind.macd < ind.macdSignal) return 'SHORT';
        return null;
      },
    },
  },
  {
    name: 'Bollinger Bounce',
    description: 'Trade price bouncing off Bollinger Bands',
    config: {
      stopLoss: 1,
      takeProfit: 2,
      entryCondition: (data, i, ind) => {
        const close = data[i].close;
        if (close <= ind.bbLower) return 'LONG';
        if (close >= ind.bbUpper) return 'SHORT';
        return null;
      },
      exitCondition: (data, i, ind) => {
        const close = data[i].close;
        return Math.abs(close - ind.bbMiddle) < (ind.bbUpper - ind.bbMiddle) * 0.1;
      },
    },
  },
  {
    name: 'Moving Average Crossover',
    description: 'Trade SMA20 crossing SMA50',
    config: {
      stopLoss: 2,
      takeProfit: 5,
      entryCondition: (data, i, ind) => {
        if (i < 1) return null;
        const prevInd = calculateAllIndicators(data)[i - 1];
        if (prevInd.sma20 < prevInd.sma50 && ind.sma20 > ind.sma50) return 'LONG';
        if (prevInd.sma20 > prevInd.sma50 && ind.sma20 < ind.sma50) return 'SHORT';
        return null;
      },
    },
  },
];

// Generate mock historical data for testing
export function generateMockHistoricalData(symbol: string, days: number): OHLCV[] {
  const data: OHLCV[] = [];
  let basePrice = symbol === 'NIFTY' ? 24500 : symbol === 'BANKNIFTY' ? 52000 : 2900;
  const volatility = 0.015;
  
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  
  for (let i = 0; i < days * 375; i++) { // 375 minutes per trading day
    const date = new Date(startDate.getTime() + i * 60000);
    const hour = date.getHours();
    
    // Skip non-trading hours (9:15 AM to 3:30 PM IST)
    if (hour < 9 || (hour === 9 && date.getMinutes() < 15) || hour > 15 || (hour === 15 && date.getMinutes() > 30)) {
      continue;
    }
    
    const change = (Math.random() - 0.5) * 2 * volatility * basePrice;
    const open = basePrice;
    const close = basePrice + change;
    const high = Math.max(open, close) + Math.random() * volatility * basePrice * 0.5;
    const low = Math.min(open, close) - Math.random() * volatility * basePrice * 0.5;
    const volume = Math.floor(Math.random() * 1000000) + 500000;
    
    data.push({
      timestamp: date,
      open,
      high,
      low,
      close,
      volume,
    });
    
    basePrice = close;
  }
  
  return data;
}
