export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface Strategy {
  id: number;
  user_id: number;
  name: string;
  description: string;
  type: 'trend' | 'mean_reversion' | 'momentum' | 'volatility' | 'stat_arb';
  parameters: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Signal {
  id: number;
  strategy_id: number;
  strategy_name: string;
  symbol: string;
  signal_type: 'buy' | 'sell' | 'neutral';
  confidence: number;
  created_at: string;
  metrics: Record<string, any>;
}

export interface Trade {
  id: number;
  signal_id: number;
  symbol: string;
  action: 'buy' | 'sell';
  quantity: number;
  price: number;
  stop_loss: number;
  take_profit: number;
  status: 'pending' | 'executed' | 'cancelled' | 'closed';
  pnl: number;
  created_at: string;
  closed_at: string | null;
}

export interface Portfolio {
  id: number;
  user_id: number;
  name: string;
  description: string;
  initial_balance: number;
  current_balance: number;
  risk_level: 'low' | 'medium' | 'high';
  created_at: string;
  updated_at: string;
}

export interface Position {
  id: number;
  portfolio_id: number;
  symbol: string;
  quantity: number;
  average_price: number;
  current_price: number;
  unrealized_pnl: number;
  realized_pnl: number;
  status: 'open' | 'closed';
  created_at: string;
  closed_at: string | null;
}

export interface BacktestResult {
  id: number;
  strategy_id: number;
  symbol: string;
  start_date: string;
  end_date: string;
  initial_balance: number;
  final_balance: number;
  total_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  metrics: Record<string, any>;
  created_at: string;
}

export interface EquityCurvePoint {
  date: string;
  equity: number;
  drawdown: number;
}

export interface PortfolioMetrics {
  total_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: number;
  average_trade: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
} 