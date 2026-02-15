import React from 'react';
import { useTrading } from '@/context/TradingContext';
import { TrendingUp, TrendingDown, Wallet, Target, Activity, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(value);
};

const formatPercent = (value: number) => `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;

interface StatCardProps {
  title: string;
  value: string | number;
  subValue?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
}

const StatCard: React.FC<StatCardProps> = ({ title, value, subValue, icon, trend }) => (
  <div className="glass-card p-5 hover:border-primary/30 transition-colors">
    <div className="flex items-start justify-between">
      <div className="space-y-2">
        <p className="text-sm text-muted-foreground">{title}</p>
        <p className={cn('text-2xl font-semibold font-mono', trend === 'up' && 'text-success', trend === 'down' && 'text-destructive', trend === 'neutral' && 'text-foreground')}>{value}</p>
        {subValue && <p className="text-xs text-muted-foreground">{subValue}</p>}
      </div>
      <div className={cn('p-2.5 rounded-xl', trend === 'up' && 'bg-success/10 text-success', trend === 'down' && 'bg-destructive/10 text-destructive', trend === 'neutral' && 'bg-primary/10 text-primary')}>{icon}</div>
    </div>
  </div>
);

export const PortfolioOverview: React.FC = () => {
  const { portfolio } = useTrading();
  const pnlPercent = (portfolio.totalPnL / portfolio.totalCapital) * 100;
  const todayPercent = (portfolio.todayPnL / portfolio.totalCapital) * 100;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Portfolio Overview</h2>
          <p className="text-sm text-muted-foreground">Paper Trading Account</p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
          <span className="w-2 h-2 rounded-full bg-emerald-500 pulse-live" />
          <span className="text-xs text-emerald-400 font-medium">Market Open</span>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <StatCard title="Total P&L" value={formatCurrency(portfolio.totalPnL)} subValue={formatPercent(pnlPercent)} icon={portfolio.totalPnL >= 0 ? <TrendingUp size={20} /> : <TrendingDown size={20} />} trend={portfolio.totalPnL >= 0 ? 'up' : 'down'} />
        <StatCard title="Today's P&L" value={formatCurrency(portfolio.todayPnL)} subValue={formatPercent(todayPercent)} icon={portfolio.todayPnL >= 0 ? <TrendingUp size={20} /> : <TrendingDown size={20} />} trend={portfolio.todayPnL >= 0 ? 'up' : 'down'} />
        <StatCard title="Available Margin" value={formatCurrency(portfolio.availableMargin)} subValue={`Used: ${formatCurrency(portfolio.usedMargin)}`} icon={<Wallet size={20} />} trend="neutral" />
        <StatCard title="Win Rate" value={`${(portfolio.winRate * 100).toFixed(1)}%`} subValue={`${portfolio.totalTrades} total trades`} icon={<Target size={20} />} trend="neutral" />
        <StatCard title="Realized P&L" value={formatCurrency(portfolio.realizedPnL)} icon={<Activity size={20} />} trend={portfolio.realizedPnL >= 0 ? 'up' : 'down'} />
        <StatCard title="Avg. Return" value={`${portfolio.avgReturn.toFixed(2)}%`} subValue="Per trade" icon={<Zap size={20} />} trend={portfolio.avgReturn >= 0 ? 'up' : 'down'} />
      </div>
    </div>
  );
};