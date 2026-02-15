import React from 'react';
import { useTrading } from '@/context/TradingContext';
import { cn } from '@/lib/utils';
import { Brain, TrendingUp, TrendingDown, Minus, Zap } from 'lucide-react';

export const MLSignals: React.FC = () => {
  const { trades } = useTrading();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-primary/10">
            <Brain className="text-primary" size={20} />
          </div>
          <div>
            <h2 className="text-xl font-semibold">ML Signals</h2>
            <p className="text-sm text-muted-foreground">AI-powered predictions</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20">
          <Zap size={14} className="text-primary" />
          <span className="text-xs text-primary font-medium">Live Analysis</span>
        </div>
      </div>

      <div className="glass-card p-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-muted">
            <Brain size={18} className="text-muted-foreground" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium">ML Model Training</p>
            <p className="text-xs text-muted-foreground">
              {trades.length} trades recorded for ML training
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            <span className="text-muted-foreground">Recording</span>
          </div>
        </div>
      </div>

      <p className="text-xs text-muted-foreground text-center">
        Visit ML tab for detailed predictions, chart patterns & sentiment analysis
      </p>
    </div>
  );
};