import React from 'react';
import { useTrading, Trade } from '@/context/TradingContext';
import { cn } from '@/lib/utils';
import { ArrowUpCircle, ArrowDownCircle, Clock, CheckCircle2, XCircle } from 'lucide-react';
import { format } from 'date-fns';

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

interface TradeRowProps {
  trade: Trade;
}

const TradeRow: React.FC<TradeRowProps> = ({ trade }) => {
  const isBuy = trade.action === 'BUY';
  const hasProfit = trade.pnl !== undefined && trade.pnl > 0;
  const hasLoss = trade.pnl !== undefined && trade.pnl < 0;

  const statusIcon = {
    EXECUTED: <CheckCircle2 size={14} className="text-emerald-400" />,
    PENDING: <Clock size={14} className="text-warning" />,
    CANCELLED: <XCircle size={14} className="text-muted-foreground" />,
    REJECTED: <XCircle size={14} className="text-rose-400" />,
  };

  return (
    <div className="glass-card p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={cn(
            'p-2 rounded-lg',
            isBuy ? 'bg-emerald-500/10' : 'bg-rose-500/10'
          )}>
            {isBuy
              ? <ArrowUpCircle size={20} className="text-emerald-400" />
              : <ArrowDownCircle size={20} className="text-rose-400" />
            }
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold">{trade.symbol}</span>
              <span className={cn(
                'text-xs px-2 py-0.5 rounded-full font-medium',
                trade.type === 'CE' && 'bg-emerald-500/20 text-emerald-400',
                trade.type === 'PE' && 'bg-rose-500/20 text-rose-400',
                trade.type === 'FUT' && 'bg-primary/20 text-primary',
                trade.type === 'EQ' && 'bg-muted text-muted-foreground'
              )}>
                {trade.type}
                {trade.strike && ` ${trade.strike}`}
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
              <span>{format(trade.timestamp, 'dd MMM, HH:mm:ss')}</span>
              <span className="flex items-center gap-1">
                {statusIcon[trade.status]}
                {trade.status}
              </span>
            </div>
          </div>
        </div>

        <div className="text-right">
          <div className="flex items-center gap-2 justify-end">
            <span className={cn(
              'text-sm font-medium',
              isBuy ? 'text-emerald-400' : 'text-rose-400'
            )}>
              {trade.action}
            </span>
            <span className="font-mono">{trade.qty} @ ₹{trade.price.toFixed(2)}</span>
          </div>

          {trade.pnl !== undefined && (
            <p className={cn(
              'text-sm font-mono mt-1',
              hasProfit && 'text-emerald-400',
              hasLoss && 'text-rose-400',
              !hasProfit && !hasLoss && 'text-muted-foreground'
            )}>
              P&L: {formatCurrency(trade.pnl)}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export const TradeHistory: React.FC = () => {
  const { trades, portfolio } = useTrading();

  const todayTrades = trades.filter(t => {
    const today = new Date();
    return t.timestamp.toDateString() === today.toDateString();
  });

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-4">
          <p className="text-xs text-muted-foreground">Total Trades</p>
          <p className="text-2xl font-bold font-mono">{portfolio.totalTrades}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs text-muted-foreground">Win Rate</p>
          <p className={cn(
            'text-2xl font-bold font-mono',
            portfolio.winRate >= 0.5 ? 'text-success' : 'text-destructive'
          )}>
            {(portfolio.winRate * 100).toFixed(1)}%
          </p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs text-muted-foreground">Realized P&L</p>
          <p className={cn(
            'text-2xl font-bold font-mono',
            portfolio.realizedPnL >= 0 ? 'text-success' : 'text-destructive'
          )}>
            {formatCurrency(portfolio.realizedPnL)}
          </p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs text-muted-foreground">Avg Return/Trade</p>
          <p className={cn(
            'text-2xl font-bold font-mono',
            portfolio.avgReturn >= 0 ? 'text-success' : 'text-destructive'
          )}>
            {formatCurrency(portfolio.avgReturn)}
          </p>
        </div>
      </div>

      {/* Trade History */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold">Trade History</h2>
            <p className="text-sm text-muted-foreground">
              {todayTrades.length} trades today
            </p>
          </div>
        </div>

        {trades.length === 0 ? (
          <div className="glass-card p-8 text-center">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-muted flex items-center justify-center mb-4">
              <Clock size={32} className="text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No trades yet</h3>
            <p className="text-muted-foreground text-sm">
              Place your first trade to see it here
            </p>
          </div>
        ) : (
          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
            {trades.map(trade => (
              <TradeRow key={trade.id} trade={trade} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
