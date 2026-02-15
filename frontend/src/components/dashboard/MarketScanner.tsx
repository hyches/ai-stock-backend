import React, { useState, useMemo } from 'react';
import { useTrading } from '@/context/TradingContext';
import { cn } from '@/lib/utils';
import {
  Search,
  Filter,
  TrendingUp,
  TrendingDown,
  Zap,
  Volume2,
  BarChart2,
  ArrowUpRight,
  ArrowDownRight,
  Star,
  RefreshCw,
  SlidersHorizontal,
  Sparkles
} from 'lucide-react';

interface ScannerResult {
  symbol: string;
  name: string;
  ltp: number;
  change: number;
  changePercent: number;
  volume: number;
  signal: 'STRONG_BUY' | 'BUY' | 'NEUTRAL' | 'SELL' | 'STRONG_SELL';
  pattern?: string;
  rsi: number;
  macdSignal: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  sector: string;
}

const SCANNER_PRESETS = [
  { id: 'top_gainers', label: 'Top Gainers', icon: TrendingUp },
  { id: 'top_losers', label: 'Top Losers', icon: TrendingDown },
  { id: 'high_volume', label: 'High Volume', icon: Volume2 },
  { id: 'breakout', label: 'Breakouts', icon: Zap },
  { id: 'oversold', label: 'Oversold', icon: BarChart2 },
  { id: 'overbought', label: 'Overbought', icon: BarChart2 },
];

// Mock scanner data
const generateScannerResults = (): ScannerResult[] => {
  const symbols = [
    { symbol: 'RELIANCE', name: 'Reliance Industries', sector: 'Energy' },
    { symbol: 'TCS', name: 'Tata Consultancy', sector: 'IT' },
    { symbol: 'HDFCBANK', name: 'HDFC Bank', sector: 'Banking' },
    { symbol: 'INFY', name: 'Infosys', sector: 'IT' },
    { symbol: 'ICICIBANK', name: 'ICICI Bank', sector: 'Banking' },
    { symbol: 'BHARTIARTL', name: 'Bharti Airtel', sector: 'Telecom' },
    { symbol: 'ITC', name: 'ITC Limited', sector: 'FMCG' },
    { symbol: 'SBIN', name: 'State Bank of India', sector: 'Banking' },
    { symbol: 'BAJFINANCE', name: 'Bajaj Finance', sector: 'Finance' },
    { symbol: 'LT', name: 'Larsen & Toubro', sector: 'Infrastructure' },
    { symbol: 'MARUTI', name: 'Maruti Suzuki', sector: 'Auto' },
    { symbol: 'TITAN', name: 'Titan Company', sector: 'Consumer' },
    { symbol: 'ASIANPAINT', name: 'Asian Paints', sector: 'Paints' },
    { symbol: 'SUNPHARMA', name: 'Sun Pharma', sector: 'Pharma' },
    { symbol: 'WIPRO', name: 'Wipro', sector: 'IT' },
  ];

  const signals: ScannerResult['signal'][] = ['STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL'];
  const patterns = ['Hammer', 'Doji', 'Engulfing', 'Morning Star', 'Three White Soldiers', undefined];
  const macdSignals: ScannerResult['macdSignal'][] = ['BULLISH', 'BEARISH', 'NEUTRAL'];

  return symbols.map(s => {
    const change = (Math.random() - 0.5) * 200;
    const ltp = 1000 + Math.random() * 4000;
    return {
      ...s,
      ltp,
      change,
      changePercent: (change / ltp) * 100,
      volume: Math.floor(Math.random() * 10000000),
      signal: signals[Math.floor(Math.random() * signals.length)],
      pattern: patterns[Math.floor(Math.random() * patterns.length)],
      rsi: 20 + Math.random() * 60,
      macdSignal: macdSignals[Math.floor(Math.random() * macdSignals.length)],
    };
  });
};

const formatNumber = (value: number): string => {
  if (value >= 10000000) return `${(value / 10000000).toFixed(2)}Cr`;
  if (value >= 100000) return `${(value / 100000).toFixed(2)}L`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
  return value.toFixed(0);
};

const SignalBadge: React.FC<{ signal: ScannerResult['signal'] }> = ({ signal }) => {
  const config = {
    STRONG_BUY: { label: 'Strong Buy', className: 'bg-success/20 text-success border-success/30' },
    BUY: { label: 'Buy', className: 'bg-success/10 text-success/80 border-success/20' },
    NEUTRAL: { label: 'Neutral', className: 'bg-muted text-muted-foreground border-border' },
    SELL: { label: 'Sell', className: 'bg-destructive/10 text-destructive/80 border-destructive/20' },
    STRONG_SELL: { label: 'Strong Sell', className: 'bg-destructive/20 text-destructive border-destructive/30' },
  };

  const { label, className } = config[signal];

  return (
    <span className={cn('px-2 py-0.5 rounded-md text-xs font-semibold border', className)}>
      {label}
    </span>
  );
};

export const MarketScanner: React.FC = () => {
  const { setSelectedSymbol } = useTrading();
  const [activePreset, setActivePreset] = useState('top_gainers');
  const [searchQuery, setSearchQuery] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  const [results] = useState<ScannerResult[]>(() => generateScannerResults());

  const filteredResults = useMemo(() => {
    let filtered = [...results];

    // Apply search
    if (searchQuery) {
      filtered = filtered.filter(r =>
        r.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply preset sorting
    switch (activePreset) {
      case 'top_gainers':
        filtered = filtered.filter(r => r.changePercent > 0).sort((a, b) => b.changePercent - a.changePercent);
        break;
      case 'top_losers':
        filtered = filtered.filter(r => r.changePercent < 0).sort((a, b) => a.changePercent - b.changePercent);
        break;
      case 'high_volume':
        filtered = filtered.sort((a, b) => b.volume - a.volume);
        break;
      case 'breakout':
        filtered = filtered.filter(r => r.signal === 'STRONG_BUY' || r.signal === 'BUY');
        break;
      case 'oversold':
        filtered = filtered.filter(r => r.rsi < 30);
        break;
      case 'overbought':
        filtered = filtered.filter(r => r.rsi > 70);
        break;
    }

    return filtered.slice(0, 12);
  }, [results, searchQuery, activePreset]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <div className="glass-card p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20">
            <Sparkles className="text-primary" size={20} />
          </div>
          <div>
            <h2 className="section-title">Market Scanner</h2>
            <p className="text-sm text-muted-foreground">Real-time stock screener</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={cn(
              "quick-action",
              showFilters && "bg-primary/10 text-primary"
            )}
          >
            <SlidersHorizontal size={16} />
            Filters
          </button>
          <button
            onClick={handleRefresh}
            className="quick-action"
            disabled={isRefreshing}
          >
            <RefreshCw size={16} className={cn(isRefreshing && "animate-spin")} />
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search symbols..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="premium-input pl-11"
        />
      </div>

      {/* Preset Tabs */}
      <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-1">
        {SCANNER_PRESETS.map(preset => (
          <button
            key={preset.id}
            onClick={() => setActivePreset(preset.id)}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all",
              activePreset === preset.id
                ? "bg-primary text-primary-foreground shadow-lg shadow-primary/25"
                : "bg-muted/50 text-muted-foreground hover:text-foreground hover:bg-muted"
            )}
          >
            <preset.icon size={16} />
            {preset.label}
          </button>
        ))}
      </div>

      {/* Results Table */}
      <div className="overflow-x-auto -mx-6 px-6">
        <table className="premium-table">
          <thead>
            <tr>
              <th className="rounded-l-lg">Symbol</th>
              <th>LTP</th>
              <th>Change</th>
              <th>Volume</th>
              <th>RSI</th>
              <th>Signal</th>
              <th className="rounded-r-lg">Pattern</th>
            </tr>
          </thead>
          <tbody>
            {filteredResults.map((result, idx) => (
              <tr
                key={result.symbol}
                onClick={() => setSelectedSymbol(result.symbol)}
                className="cursor-pointer"
                style={{ animationDelay: `${idx * 50}ms` }}
              >
                <td>
                  <div className="flex items-center gap-3">
                    <button className="text-muted-foreground hover:text-warning transition-colors">
                      <Star size={14} />
                    </button>
                    <div>
                      <p className="font-semibold text-foreground">{result.symbol}</p>
                      <p className="text-xs text-muted-foreground">{result.sector}</p>
                    </div>
                  </div>
                </td>
                <td className="font-semibold">₹{result.ltp.toFixed(2)}</td>
                <td>
                  <div className={cn(
                    "flex items-center gap-1",
                    result.change >= 0 ? "text-success" : "text-destructive"
                  )}>
                    {result.change >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                    <span className="font-semibold">{result.changePercent.toFixed(2)}%</span>
                  </div>
                </td>
                <td className="text-muted-foreground">{formatNumber(result.volume)}</td>
                <td>
                  <span className={cn(
                    "font-semibold",
                    result.rsi < 30 && "text-success",
                    result.rsi > 70 && "text-destructive"
                  )}>
                    {result.rsi.toFixed(0)}
                  </span>
                </td>
                <td>
                  <SignalBadge signal={result.signal} />
                </td>
                <td>
                  {result.pattern ? (
                    <span className="text-xs px-2 py-1 rounded-md bg-accent text-accent-foreground">
                      {result.pattern}
                    </span>
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredResults.length === 0 && (
        <div className="text-center py-12">
          <Search className="mx-auto text-muted-foreground mb-3" size={32} />
          <p className="text-muted-foreground">No stocks match your criteria</p>
        </div>
      )}
    </div>
  );
};