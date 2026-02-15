import React from 'react';
import { useTrading, Position } from '@/context/TradingContext';
import { cn } from '@/lib/utils';
import { X, TrendingUp, TrendingDown, Loader2 } from 'lucide-react';
import { GlassButton } from '@/components/ui/GlassButton';

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

interface PositionRowProps {
  position: Position;
  onClose?: () => void;
  isClosing?: boolean;
}

const PositionRow: React.FC<PositionRowProps> = ({ position, onClose, isClosing }) => {
  const isProfit = position.pnl >= 0;
  const isShort = position.qty < 0;

  return (
    <div className="glass-card p-4">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="font-semibold">{position.symbol}</span>
            <span className={cn(
              'text-xs px-2 py-0.5 rounded-full font-medium',
              position.type === 'CE' && 'bg-emerald-500/20 text-emerald-400',
              position.type === 'PE' && 'bg-rose-500/20 text-rose-400',
              position.type === 'FUT' && 'bg-primary/20 text-primary',
              position.type === 'EQ' && 'bg-muted text-muted-foreground'
            )}>
              {position.type}
              {position.strike && ` ${position.strike}`}
            </span>
            <span className={cn(
              'text-xs px-2 py-0.5 rounded-full',
              isShort ? 'bg-rose-500/10 text-rose-400' : 'bg-emerald-500/10 text-emerald-400'
            )}>
              {isShort ? 'SHORT' : 'LONG'}
            </span>
          </div>
          <p className="text-xs text-muted-foreground">
            {position.expiry && `Expiry: ${position.expiry} | `}
            Qty: <span className="text-foreground">{Math.abs(position.qty)}</span>
          </p>
        </div>

        <div className="flex items-start gap-4">
          <div className="text-right space-y-1">
            <p className={cn(
              'text-lg font-semibold font-mono flex items-center gap-1',
              isProfit ? 'text-emerald-400' : 'text-rose-400'
            )}>
              {isProfit ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
              {formatCurrency(position.pnl)}
            </p>
            <p className={cn(
              'text-sm font-mono',
              isProfit ? 'text-emerald-400/80' : 'text-rose-400/80'
            )}>
              {isProfit ? '+' : ''}{position.pnlPercent.toFixed(2)}%
            </p>
          </div>

          <button
            onClick={onClose}
            disabled={isClosing}
            className="p-2 rounded-lg hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors disabled:opacity-50"
          >
            {isClosing ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <X size={16} />
            )}
          </button>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-border/50 grid grid-cols-3 gap-4 text-xs">
        <div>
          <p className="text-muted-foreground">Avg Price</p>
          <p className="font-mono text-foreground">₹{position.avgPrice.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">LTP</p>
          <p className="font-mono text-foreground">₹{position.ltp.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Value</p>
          <p className="font-mono text-foreground">{formatCurrency(Math.abs(position.qty) * position.ltp)}</p>
        </div>
      </div>
    </div>
  );
};

interface PositionsProps {
  onClosePosition?: (id: string) => void;
}

export const Positions: React.FC<PositionsProps> = () => {
  const { positions, closePosition, closeAllPositions } = useTrading();
  const [closingIds, setClosingIds] = React.useState<Set<string>>(new Set());
  const [isClosingAll, setIsClosingAll] = React.useState(false);

  const totalPnL = positions.reduce((acc, pos) => acc + pos.pnl, 0);
  const isOverallProfit = totalPnL >= 0;

  const handleClose = async (id: string) => {
    setClosingIds(prev => new Set(prev).add(id));
    try {
      await closePosition(id);
    } finally {
      setClosingIds(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  const handleCloseAll = async () => {
    setIsClosingAll(true);
    try {
      await closeAllPositions();
    } finally {
      setIsClosingAll(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Open Positions</h2>
          <p className="text-sm text-muted-foreground">{positions.length} active positions</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">Total P&L</p>
          <p className={cn(
            'text-lg font-semibold font-mono',
            isOverallProfit ? 'text-emerald-400' : 'text-rose-400'
          )}>
            {formatCurrency(totalPnL)}
          </p>
        </div>
      </div>

      {positions.length === 0 ? (
        <div className="glass-card p-8 text-center">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-muted flex items-center justify-center mb-4">
            <span className="text-2xl">📈</span>
          </div>
          <h3 className="text-lg font-semibold mb-2">No open positions</h3>
          <p className="text-muted-foreground text-sm">
            Place a trade to open a position
          </p>
        </div>
      ) : (
        <>
          <div className="space-y-3">
            {positions.map(position => (
              <PositionRow
                key={position.id}
                position={position}
                onClose={() => handleClose(position.id)}
                isClosing={closingIds.has(position.id)}
              />
            ))}
          </div>

          <GlassButton
            variant="destructive"
            className="w-full"
            onClick={handleCloseAll}
            disabled={isClosingAll}
          >
            {isClosingAll ? (
              <>
                <Loader2 size={18} className="animate-spin mr-2" />
                Closing All...
              </>
            ) : (
              'Close All Positions'
            )}
          </GlassButton>
        </>
      )}
    </div>
  );
};
