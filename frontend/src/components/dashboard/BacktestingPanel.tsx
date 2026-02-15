import React, { useState, useCallback } from 'react';
import { GlassButton } from '@/components/ui/GlassButton';
import { cn } from '@/lib/utils';
import {
  Play,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Target,
  AlertTriangle,
  Clock,
  Percent,
  DollarSign,
  Activity,
  Calendar,
  ChevronDown,
  Settings,
  Download,
} from 'lucide-react';
import {
  runProfessionalBacktest,
  getMonteCarloSimulation,
} from '@/lib/api-services';

// Keep interfaces but move to real API calls
import {
  OHLCV,
} from '@/lib/backtesting/engine';
import { useToast } from '@/hooks/use-toast';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  Cell,
} from 'recharts';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface MetricCardProps {
  label: string;
  value: string | number;
  icon: React.ElementType;
  trend?: 'up' | 'down' | 'neutral';
  sublabel?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, icon: Icon, trend, sublabel }) => (
  <div className="p-4 rounded-xl bg-secondary/30 border border-border/50">
    <div className="flex items-center gap-2 mb-2">
      <Icon size={16} className="text-muted-foreground" />
      <span className="text-sm text-muted-foreground">{label}</span>
    </div>
    <div className={cn(
      'text-xl font-bold font-mono',
      trend === 'up' && 'text-emerald-400',
      trend === 'down' && 'text-rose-400',
      trend === 'neutral' && 'text-foreground',
    )}>
      {value}
    </div>
    {sublabel && <p className="text-xs text-muted-foreground mt-1">{sublabel}</p>}
  </div>
);

// Strat names match backend
const PROF_STRATEGIES = [
  { name: 'RSI Reversal', description: 'Institutional mean reversion strategy' },
  { name: 'MACD Crossover', description: 'Momentum confirmation system' },
  { name: 'Bollinger Bounce', description: 'Volatility range trading' },
  { name: 'MA Crossover', description: 'Trend following system' },
];

export const BacktestingPanel: React.FC = () => {
  const { toast } = useToast();
  const [selectedStrategy, setSelectedStrategy] = useState<string>(PROF_STRATEGIES[0].name);
  const [symbol, setSymbol] = useState('RELIANCE');
  const [days, setDays] = useState(60); // Professional backtests usually need more data
  const [initialCapital, setInitialCapital] = useState(1000000);
  const [positionSize, setPositionSize] = useState(10);
  const [stopLoss, setStopLoss] = useState(2);
  const [takeProfit, setTakeProfit] = useState(4);

  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const runBacktestHandler = useCallback(async () => {
    setIsRunning(true);

    try {
      const backtestResult = await runProfessionalBacktest({
        symbol,
        days,
        strategy: selectedStrategy,
        initial_capital: initialCapital,
        params: {
          position_size_pct: positionSize,
          stop_loss_pct: stopLoss,
          take_profit_pct: takeProfit,
        }
      });

      // Transform backend results to UI format if needed
      // Our backend service returns comprehensive metrics already
      setResult(backtestResult);

      toast({
        title: "Backtest Complete",
        description: `Strategy ${selectedStrategy} achieved ${backtestResult.total_return_pct.toFixed(2)}% return.`,
      });

    } catch (error: any) {
      console.error('Backtest failed:', error);
      toast({
        title: "Backtest Failed",
        description: error.message || "Could not connect to professional backtesting engine.",
        variant: "destructive"
      });
    } finally {
      setIsRunning(false);
    }
  }, [selectedStrategy, symbol, days, initialCapital, positionSize, stopLoss, takeProfit, toast]);

  const equityData = result?.equityCurve.map((point, i) => ({
    date: point.date.toLocaleDateString(),
    equity: point.equity,
    drawdown: result.drawdownCurve[i]?.drawdown || 0,
  })) || [];

  const monthlyData = result?.monthlyReturns.map(m => ({
    month: m.month,
    return: m.return,
  })) || [];

  const tradeDistribution = result ? [
    { name: 'Wins', value: result.winningTrades, color: 'hsl(var(--success))' },
    { name: 'Losses', value: result.losingTrades, color: 'hsl(var(--destructive))' },
  ] : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-primary/10">
            <Activity className="text-primary" size={20} />
          </div>
          <div>
            <h2 className="text-xl font-semibold">Backtesting Engine</h2>
            <p className="text-sm text-muted-foreground">Test strategies against historical data</p>
          </div>
        </div>

        {result && (
          <GlassButton variant="default" size="sm" className="gap-2">
            <Download size={14} />
            Export Report
          </GlassButton>
        )}
      </div>

      {/* Configuration */}
      <div className="glass-card p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-medium">Strategy Configuration</h3>
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-sm text-muted-foreground flex items-center gap-1 hover:text-foreground transition-colors"
            >
              <Settings size={14} />
              {showAdvanced ? 'Hide' : 'Show'} Advanced
              <ChevronDown size={14} className={cn('transition-transform', showAdvanced && 'rotate-180')} />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label className="text-sm text-muted-foreground">Strategy</Label>
              <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
                <SelectTrigger className="bg-secondary/50">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {PROF_STRATEGIES.map(s => (
                    <SelectItem key={s.name} value={s.name}>
                      {s.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                {PROF_STRATEGIES.find(s => s.name === selectedStrategy)?.description}
              </p>
            </div>

            <div className="space-y-2">
              <Label className="text-sm text-muted-foreground">Symbol</Label>
              <Select value={symbol} onValueChange={setSymbol}>
                <SelectTrigger className="bg-secondary/50">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="NIFTY">NIFTY 50</SelectItem>
                  <SelectItem value="BANKNIFTY">BANK NIFTY</SelectItem>
                  <SelectItem value="RELIANCE">RELIANCE</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label className="text-sm text-muted-foreground">Period (Days)</Label>
              <Input
                type="number"
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                min={7}
                max={365}
                className="bg-secondary/50"
              />
            </div>

            <div className="space-y-2">
              <Label className="text-sm text-muted-foreground">Initial Capital (₹)</Label>
              <Input
                type="number"
                value={initialCapital}
                onChange={(e) => setInitialCapital(Number(e.target.value))}
                min={100000}
                className="bg-secondary/50"
              />
            </div>
          </div>

          {showAdvanced && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-border/50">
              <div className="space-y-2">
                <Label className="text-sm text-muted-foreground">Position Size (%)</Label>
                <Input
                  type="number"
                  value={positionSize}
                  onChange={(e) => setPositionSize(Number(e.target.value))}
                  min={1}
                  max={100}
                  className="bg-secondary/50"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-sm text-muted-foreground">Stop Loss (%)</Label>
                <Input
                  type="number"
                  value={stopLoss}
                  onChange={(e) => setStopLoss(Number(e.target.value))}
                  min={0.5}
                  max={10}
                  step={0.5}
                  className="bg-secondary/50"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-sm text-muted-foreground">Take Profit (%)</Label>
                <Input
                  type="number"
                  value={takeProfit}
                  onChange={(e) => setTakeProfit(Number(e.target.value))}
                  min={1}
                  max={20}
                  step={0.5}
                  className="bg-secondary/50"
                />
              </div>
            </div>
          )}

          <div className="pt-4">
            <GlassButton
              onClick={runBacktestHandler}
              disabled={isRunning}
              className="w-full md:w-auto gap-2"
            >
              {isRunning ? (
                <>
                  <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                  Running Backtest...
                </>
              ) : (
                <>
                  <Play size={16} />
                  Run Backtest
                </>
              )}
            </GlassButton>
          </div>
        </div>
      </div>

      {/* Results */}
      {result && (
        <>
          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            <MetricCard
              label="Total Return"
              value={`${result.totalPnLPercent >= 0 ? '+' : ''}${result.totalPnLPercent.toFixed(2)}%`}
              icon={Percent}
              trend={result.totalPnLPercent >= 0 ? 'up' : 'down'}
              sublabel={`₹${result.totalPnL.toLocaleString()}`}
            />
            <MetricCard
              label="Win Rate"
              value={`${result.winRate.toFixed(1)}%`}
              icon={Target}
              trend={result.winRate >= 50 ? 'up' : 'down'}
              sublabel={`${result.winningTrades}W / ${result.losingTrades}L`}
            />
            <MetricCard
              label="Sharpe Ratio"
              value={result.sharpeRatio.toFixed(2)}
              icon={BarChart3}
              trend={result.sharpeRatio >= 1 ? 'up' : result.sharpeRatio >= 0 ? 'neutral' : 'down'}
            />
            <MetricCard
              label="Max Drawdown"
              value={`-${result.maxDrawdownPercent.toFixed(2)}%`}
              icon={AlertTriangle}
              trend="down"
              sublabel={`₹${result.maxDrawdown.toLocaleString()}`}
            />
            <MetricCard
              label="Profit Factor"
              value={result.profitFactor === Infinity ? '∞' : result.profitFactor.toFixed(2)}
              icon={TrendingUp}
              trend={result.profitFactor >= 1.5 ? 'up' : 'neutral'}
            />
            <MetricCard
              label="Avg Holding"
              value={`${result.avgHoldingPeriod.toFixed(1)}d`}
              icon={Clock}
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Equity Curve */}
            <div className="glass-card p-6">
              <h3 className="font-medium mb-4">Equity Curve</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={equityData.filter((_, i) => i % 50 === 0)}>
                    <defs>
                      <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`}
                    />
                    <Tooltip
                      contentStyle={{
                        background: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                      formatter={(value: number) => [`₹${value.toLocaleString()}`, 'Equity']}
                    />
                    <Area
                      type="monotone"
                      dataKey="equity"
                      stroke="hsl(var(--primary))"
                      fill="url(#equityGradient)"
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Drawdown */}
            <div className="glass-card p-6">
              <h3 className="font-medium mb-4">Drawdown</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={equityData.filter((_, i) => i % 50 === 0)}>
                    <defs>
                      <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--destructive))" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="hsl(var(--destructive))" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(value) => `-${value.toFixed(1)}%`}
                    />
                    <Tooltip
                      contentStyle={{
                        background: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                      formatter={(value: number) => [`-${value.toFixed(2)}%`, 'Drawdown']}
                    />
                    <Area
                      type="monotone"
                      dataKey="drawdown"
                      stroke="hsl(var(--destructive))"
                      fill="url(#drawdownGradient)"
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Monthly Returns & Trade List */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Monthly Returns */}
            <div className="glass-card p-6">
              <h3 className="font-medium mb-4">Monthly Returns</h3>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={monthlyData}>
                    <XAxis
                      dataKey="month"
                      tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(value) => `${value.toFixed(0)}%`}
                    />
                    <Tooltip
                      contentStyle={{
                        background: 'hsl(var(--card))',
                        border: '1px solid hsl(var(--border))',
                        borderRadius: '8px',
                      }}
                      formatter={(value: number) => [`${value.toFixed(2)}%`, 'Return']}
                    />
                    <Bar dataKey="return" radius={[4, 4, 0, 0]}>
                      {monthlyData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={entry.return >= 0 ? 'hsl(var(--success))' : 'hsl(var(--destructive))'}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Recent Trades */}
            <div className="glass-card p-6">
              <h3 className="font-medium mb-4">Recent Trades</h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {result.trades.slice(-10).reverse().map((trade, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-2 rounded-lg bg-secondary/30"
                  >
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        'w-2 h-2 rounded-full',
                        trade.type === 'LONG' ? 'bg-emerald-400' : 'bg-rose-400'
                      )} />
                      <div>
                        <span className="text-sm font-medium">{trade.type}</span>
                        <span className="text-xs text-muted-foreground ml-2">
                          @ ₹{trade.entryPrice.toFixed(2)}
                        </span>
                      </div>
                    </div>
                    <div className={cn(
                      'text-sm font-mono',
                      trade.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'
                    )}>
                      {trade.pnl >= 0 ? '+' : ''}{trade.pnlPercent.toFixed(2)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Additional Metrics */}
          <div className="glass-card p-6">
            <h3 className="font-medium mb-4">Detailed Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Sortino Ratio</p>
                <p className="font-mono font-medium">{result.sortinoRatio.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Calmar Ratio</p>
                <p className="font-mono font-medium">{result.calmarRatio.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Avg Win</p>
                <p className="font-mono font-medium text-emerald-400">₹{result.avgWin.toFixed(0)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Avg Loss</p>
                <p className="font-mono font-medium text-rose-400">₹{result.avgLoss.toFixed(0)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Largest Win</p>
                <p className="font-mono font-medium text-emerald-400">₹{result.largestWin.toFixed(0)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Largest Loss</p>
                <p className="font-mono font-medium text-rose-400">₹{result.largestLoss.toFixed(0)}</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
