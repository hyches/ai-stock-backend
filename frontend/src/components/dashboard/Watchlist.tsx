import React from 'react';
import { useTrading } from '@/context/TradingContext';
import { TrendingUp, TrendingDown, Star, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';

const formatNumber = (value: number, decimals: number = 2) => {
  return value.toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

interface WatchlistItemProps {
  symbol: string;
  name: string;
  ltp: number;
  change: number;
  changePercent: number;
  open: number;
  high: number;
  low: number;
  isSelected: boolean;
  onClick?: () => void;
}

const WatchlistItem: React.FC<WatchlistItemProps> = ({
  symbol,
  name,
  ltp,
  change,
  changePercent,
  open,
  high,
  low,
  isSelected,
  onClick
}) => {
  const isPositive = change >= 0;

  return (
    <div
      className={cn(
        'glass-card p-4 cursor-pointer group transition-all relative hover:border-primary/30',
        isSelected && 'ring-2 ring-primary'
      )}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-foreground">{symbol}</span>
            <span className="text-xs px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
              NSE
            </span>
          </div>
          <p className="text-xs text-muted-foreground truncate max-w-[150px]">{name}</p>
        </div>

        <div className="text-right space-y-1">
          <p className="font-mono font-semibold">₹{formatNumber(ltp)}</p>
          <div className={cn(
            'flex items-center justify-end gap-1 text-sm',
            isPositive ? 'text-emerald-400' : 'text-rose-400'
          )}>
            {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            <span className="font-mono">
              {isPositive ? '+' : ''}{formatNumber(change)} ({isPositive ? '+' : ''}{formatNumber(changePercent)}%)
            </span>
          </div>
        </div>
      </div>

      <div className="mt-3 pt-3 border-t border-border/50 grid grid-cols-3 gap-2 text-xs">
        <div>
          <p className="text-muted-foreground">Open</p>
          <p className="font-mono">₹{formatNumber(open)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">High</p>
          <p className="font-mono text-emerald-400">₹{formatNumber(high)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Low</p>
          <p className="font-mono text-rose-400">₹{formatNumber(low)}</p>
        </div>
      </div>

      <button className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-lg hover:bg-primary/10 text-muted-foreground hover:text-primary">
        <Star size={14} />
      </button>
    </div>
  );
};

interface WatchlistProps {
  onSelectStock?: (symbol: string) => void;
}

export const Watchlist: React.FC<WatchlistProps> = ({ onSelectStock }) => {
  const { quotes, selectedSymbol, setSelectedSymbol } = useTrading();

  const quotesArray = Array.from(quotes.values());

  const handleSelect = (symbol: string) => {
    setSelectedSymbol(symbol);
    onSelectStock?.(symbol);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Watchlist</h2>
          <p className="text-sm text-muted-foreground">
            Live market data • {quotesArray.length} symbols
          </p>
        </div>
        <button className="glass-button p-2 hover:text-primary">
          <Plus size={18} />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {quotesArray.map(quote => (
          <WatchlistItem
            key={quote.symbol}
            symbol={quote.symbol}
            name={quote.shortName}
            ltp={quote.regularMarketPrice}
            change={quote.regularMarketChange}
            changePercent={quote.regularMarketChangePercent}
            open={quote.regularMarketOpen}
            high={quote.regularMarketDayHigh}
            low={quote.regularMarketDayLow}
            isSelected={quote.symbol === selectedSymbol}
            onClick={() => handleSelect(quote.symbol)}
          />
        ))}
      </div>
    </div>
  );
};
