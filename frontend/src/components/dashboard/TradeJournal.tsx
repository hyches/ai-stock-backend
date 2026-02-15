import React, { useState, useMemo } from 'react';
import { useTrading } from '@/context/TradingContext';
import { cn } from '@/lib/utils';
import {
  BookOpen,
  Calendar,
  TrendingUp,
  TrendingDown,
  Tag,
  MessageSquare,
  Target,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Filter,
  Download,
  PenLine,
  ChevronDown,
  ChevronRight,
  Clock,
  Lightbulb,
  Brain,
  Flame
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';

interface JournalEntry {
  id: string;
  tradeId: string;
  date: string;
  symbol: string;
  type: 'BUY' | 'SELL';
  instrumentType: 'EQ' | 'CE' | 'PE' | 'FUT';
  quantity: number;
  entryPrice: number;
  exitPrice?: number;
  pnl?: number;
  status: 'OPEN' | 'CLOSED' | 'STOPPED';
  strategy: string;
  setup: string;
  notes: string;
  emotions: ('confident' | 'anxious' | 'fomo' | 'greedy' | 'fearful' | 'neutral')[];
  tags: string[];
  rating: 1 | 2 | 3 | 4 | 5;
  followedPlan: boolean;
  lessons?: string;
}

const STRATEGIES = [
  'Breakout', 'Pullback', 'Trend Following', 'Mean Reversion',
  'Momentum', 'Scalping', 'Swing', 'Options Premium'
];

const SETUPS = [
  'Support Bounce', 'Resistance Break', 'Moving Average Cross',
  'RSI Oversold', 'RSI Overbought', 'MACD Cross', 'Volume Spike'
];

const EMOTIONS = [
  { id: 'confident', label: 'Confident', icon: CheckCircle, color: 'text-success' },
  { id: 'neutral', label: 'Neutral', icon: Target, color: 'text-muted-foreground' },
  { id: 'anxious', label: 'Anxious', icon: AlertTriangle, color: 'text-warning' },
  { id: 'fomo', label: 'FOMO', icon: Flame, color: 'text-warning' },
  { id: 'greedy', label: 'Greedy', icon: TrendingUp, color: 'text-destructive' },
  { id: 'fearful', label: 'Fearful', icon: XCircle, color: 'text-destructive' },
];

// Generate mock journal entries
const generateJournalEntries = (): JournalEntry[] => {
  const entries: JournalEntry[] = [];
  const now = new Date();

  for (let i = 0; i < 15; i++) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);

    const isWin = Math.random() > 0.4;
    const pnl = isWin ? Math.random() * 15000 + 1000 : -(Math.random() * 8000 + 500);

    entries.push({
      id: `j-${i}`,
      tradeId: `t-${i}`,
      date: date.toISOString().split('T')[0],
      symbol: ['NIFTY', 'BANKNIFTY', 'RELIANCE', 'TCS', 'INFY'][Math.floor(Math.random() * 5)],
      type: Math.random() > 0.5 ? 'BUY' : 'SELL',
      instrumentType: ['CE', 'PE', 'FUT', 'EQ'][Math.floor(Math.random() * 4)] as JournalEntry['instrumentType'],
      quantity: [25, 50, 75, 100][Math.floor(Math.random() * 4)],
      entryPrice: 500 + Math.random() * 200,
      exitPrice: 500 + Math.random() * 200,
      pnl,
      status: Math.random() > 0.1 ? 'CLOSED' : 'OPEN',
      strategy: STRATEGIES[Math.floor(Math.random() * STRATEGIES.length)],
      setup: SETUPS[Math.floor(Math.random() * SETUPS.length)],
      notes: 'Entry based on technical breakout above resistance. Volume confirmed the move.',
      emotions: [EMOTIONS[Math.floor(Math.random() * EMOTIONS.length)].id] as JournalEntry['emotions'],
      tags: ['technical', 'momentum'].slice(0, Math.floor(Math.random() * 3) + 1),
      rating: (Math.floor(Math.random() * 5) + 1) as JournalEntry['rating'],
      followedPlan: Math.random() > 0.3,
      lessons: isWin ? 'Patience paid off. Waited for confirmation.' : 'Entered too early. Should have waited for volume.',
    });
  }

  return entries;
};

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

const JournalEntryCard: React.FC<{ entry: JournalEntry; isExpanded: boolean; onToggle: () => void }> = ({
  entry, isExpanded, onToggle
}) => {
  const isProfit = (entry.pnl || 0) >= 0;

  return (
    <div className={cn(
      "glass-card overflow-hidden transition-all",
      isExpanded && "ring-1 ring-primary/30"
    )}>
      {/* Header */}
      <div
        onClick={onToggle}
        className="p-4 cursor-pointer hover:bg-accent/30 transition-colors"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button className="text-muted-foreground">
              {isExpanded ? <ChevronDown size={18} /> : <ChevronRight size={18} />}
            </button>

            <div className="flex items-center gap-3">
              <div className={cn(
                "w-10 h-10 rounded-xl flex items-center justify-center font-bold text-sm",
                isProfit
                  ? "bg-success/10 text-success"
                  : "bg-destructive/10 text-destructive"
              )}>
                {isProfit ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
              </div>

              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold">{entry.symbol}</span>
                  <span className={cn(
                    "px-1.5 py-0.5 rounded text-xs font-medium",
                    entry.type === 'BUY' ? "bg-success/20 text-success" : "bg-destructive/20 text-destructive"
                  )}>
                    {entry.type}
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-xs bg-accent font-mono">
                    {entry.instrumentType}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground mt-0.5">
                  <Calendar size={12} />
                  <span>{entry.date}</span>
                  <span>•</span>
                  <span>{entry.strategy}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="text-right">
              <p className={cn(
                "font-bold font-mono",
                isProfit ? "text-success" : "text-destructive"
              )}>
                {formatCurrency(entry.pnl || 0)}
              </p>
              <p className="text-xs text-muted-foreground">{entry.quantity} qty</p>
            </div>

            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map(star => (
                <div
                  key={star}
                  className={cn(
                    "w-2 h-2 rounded-full",
                    star <= entry.rating ? "bg-warning" : "bg-muted"
                  )}
                />
              ))}
            </div>

            {entry.followedPlan ? (
              <CheckCircle size={18} className="text-success" />
            ) : (
              <XCircle size={18} className="text-destructive" />
            )}
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="px-4 pb-4 pt-2 border-t border-border/50 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Trade Details */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Trade Details</h4>
              <div className="p-3 rounded-lg bg-muted/30 space-y-2 font-mono text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Entry</span>
                  <span>₹{entry.entryPrice.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Exit</span>
                  <span>₹{(entry.exitPrice || 0).toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Setup</span>
                  <span className="text-right">{entry.setup}</span>
                </div>
              </div>
            </div>

            {/* Notes */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
                <MessageSquare size={12} />
                Notes
              </h4>
              <p className="text-sm text-muted-foreground p-3 rounded-lg bg-muted/30">
                {entry.notes}
              </p>
            </div>

            {/* Emotions & Lessons */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
                <Brain size={12} />
                Psychology
              </h4>
              <div className="p-3 rounded-lg bg-muted/30 space-y-3">
                <div className="flex flex-wrap gap-1.5">
                  {entry.emotions.map(emotion => {
                    const em = EMOTIONS.find(e => e.id === emotion);
                    return em ? (
                      <span key={emotion} className={cn(
                        "px-2 py-0.5 rounded text-xs font-medium flex items-center gap-1",
                        "bg-accent"
                      )}>
                        <em.icon size={10} className={em.color} />
                        {em.label}
                      </span>
                    ) : null;
                  })}
                </div>
                {entry.lessons && (
                  <div className="flex items-start gap-2 text-xs">
                    <Lightbulb size={14} className="text-warning flex-shrink-0 mt-0.5" />
                    <span className="text-muted-foreground">{entry.lessons}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Tags */}
          <div className="flex items-center gap-2">
            <Tag size={14} className="text-muted-foreground" />
            {entry.tags.map(tag => (
              <span key={tag} className="px-2 py-0.5 rounded-full text-xs bg-primary/10 text-primary">
                #{tag}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export const TradeJournal: React.FC = () => {
  const { trades } = useTrading();
  const [entries] = useState<JournalEntry[]>(() => generateJournalEntries());
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [filterStrategy, setFilterStrategy] = useState<string>('all');

  const stats = useMemo(() => {
    const closedEntries = entries.filter(e => e.status === 'CLOSED');
    const wins = closedEntries.filter(e => (e.pnl || 0) > 0);
    const totalPnl = closedEntries.reduce((sum, e) => sum + (e.pnl || 0), 0);
    const avgWin = wins.length > 0
      ? wins.reduce((sum, e) => sum + (e.pnl || 0), 0) / wins.length
      : 0;
    const losses = closedEntries.filter(e => (e.pnl || 0) < 0);
    const avgLoss = losses.length > 0
      ? Math.abs(losses.reduce((sum, e) => sum + (e.pnl || 0), 0) / losses.length)
      : 0;
    const followedPlanRate = (closedEntries.filter(e => e.followedPlan).length / closedEntries.length) * 100;

    return {
      totalTrades: closedEntries.length,
      winRate: (wins.length / closedEntries.length) * 100,
      totalPnl,
      avgWin,
      avgLoss,
      profitFactor: avgLoss > 0 ? avgWin / avgLoss : 0,
      followedPlanRate,
    };
  }, [entries]);

  const pnlByDay = useMemo(() => {
    const byDay: Record<string, number> = {};
    entries.forEach(e => {
      if (e.pnl) {
        byDay[e.date] = (byDay[e.date] || 0) + e.pnl;
      }
    });
    return Object.entries(byDay)
      .map(([date, pnl]) => ({ date, pnl }))
      .sort((a, b) => a.date.localeCompare(b.date))
      .slice(-10);
  }, [entries]);

  const strategyPerformance = useMemo(() => {
    const byStrategy: Record<string, { wins: number; losses: number; pnl: number }> = {};
    entries.forEach(e => {
      if (!byStrategy[e.strategy]) {
        byStrategy[e.strategy] = { wins: 0, losses: 0, pnl: 0 };
      }
      if ((e.pnl || 0) > 0) {
        byStrategy[e.strategy].wins++;
      } else {
        byStrategy[e.strategy].losses++;
      }
      byStrategy[e.strategy].pnl += e.pnl || 0;
    });
    return Object.entries(byStrategy)
      .map(([strategy, data]) => ({
        strategy,
        winRate: (data.wins / (data.wins + data.losses)) * 100,
        pnl: data.pnl,
        trades: data.wins + data.losses,
      }))
      .sort((a, b) => b.pnl - a.pnl);
  }, [entries]);

  const filteredEntries = filterStrategy === 'all'
    ? entries
    : entries.filter(e => e.strategy === filterStrategy);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20">
            <BookOpen className="text-primary" size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold font-display">Trade Journal</h1>
            <p className="text-sm text-muted-foreground">Track, analyze, and improve your trading</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button className="quick-action">
            <PenLine size={16} />
            New Entry
          </button>
          <button className="quick-action">
            <Download size={16} />
            Export
          </button>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        <div className="stat-card-primary">
          <p className="metric-label">Total Trades</p>
          <p className="metric-value">{stats.totalTrades}</p>
        </div>
        <div className={stats.winRate >= 50 ? "stat-card-success" : "stat-card-destructive"}>
          <p className="metric-label">Win Rate</p>
          <p className="metric-value">{stats.winRate.toFixed(1)}%</p>
        </div>
        <div className={stats.totalPnl >= 0 ? "stat-card-success" : "stat-card-destructive"}>
          <p className="metric-label">Total P&L</p>
          <p className="metric-value">{formatCurrency(stats.totalPnl)}</p>
        </div>
        <div className="stat-card">
          <p className="metric-label">Avg Win</p>
          <p className="metric-value text-success">{formatCurrency(stats.avgWin)}</p>
        </div>
        <div className="stat-card">
          <p className="metric-label">Avg Loss</p>
          <p className="metric-value text-destructive">{formatCurrency(stats.avgLoss)}</p>
        </div>
        <div className="stat-card">
          <p className="metric-label">Profit Factor</p>
          <p className="metric-value">{stats.profitFactor.toFixed(2)}</p>
        </div>
        <div className={stats.followedPlanRate >= 70 ? "stat-card-success" : "stat-card-destructive"}>
          <p className="metric-label">Plan Adherence</p>
          <p className="metric-value">{stats.followedPlanRate.toFixed(0)}%</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* P&L by Day */}
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4">Daily P&L</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={pnlByDay}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                  tickFormatter={(value) => value.slice(5)}
                />
                <YAxis
                  tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                  tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`}
                />
                <Tooltip
                  formatter={(value: number) => [formatCurrency(value), 'P&L']}
                  contentStyle={{
                    backgroundColor: 'hsl(var(--popover))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="pnl" radius={[4, 4, 0, 0]}>
                  {pnlByDay.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.pnl >= 0 ? 'hsl(var(--success))' : 'hsl(var(--destructive))'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Strategy Performance */}
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4">Strategy Performance</h3>
          <div className="space-y-3 max-h-48 overflow-y-auto">
            {strategyPerformance.map((strat, idx) => (
              <div key={strat.strategy} className="flex items-center gap-4">
                <span className="text-xs text-muted-foreground w-4">{idx + 1}</span>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium">{strat.strategy}</span>
                    <span className={cn(
                      "text-sm font-mono font-semibold",
                      strat.pnl >= 0 ? "text-success" : "text-destructive"
                    )}>
                      {formatCurrency(strat.pnl)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
                      <div
                        className="h-full bg-primary transition-all"
                        style={{ width: `${strat.winRate}%` }}
                      />
                    </div>
                    <span className="text-xs text-muted-foreground">{strat.winRate.toFixed(0)}%</span>
                    <span className="text-xs text-muted-foreground">({strat.trades} trades)</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Filter & Entries */}
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter size={16} className="text-muted-foreground" />
            <select
              value={filterStrategy}
              onChange={(e) => setFilterStrategy(e.target.value)}
              className="premium-input py-2 w-48"
            >
              <option value="all">All Strategies</option>
              {STRATEGIES.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <span className="text-sm text-muted-foreground">
            {filteredEntries.length} entries
          </span>
        </div>

        <div className="space-y-3">
          {filteredEntries.map(entry => (
            <JournalEntryCard
              key={entry.id}
              entry={entry}
              isExpanded={expandedId === entry.id}
              onToggle={() => setExpandedId(expandedId === entry.id ? null : entry.id)}
            />
          ))}
        </div>
      </div>
    </div>
  );
};