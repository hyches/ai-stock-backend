import React from 'react';
import { X, TrendingUp, TrendingDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import TradingActions from '@/components/TradingActions';

interface StockDetails {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  pe: number;
  eps: number;
  dividend: number;
  dividendYield: number;
  high52Week: number;
  low52Week: number;
  avgVolume: number;
  beta: number;
  sector: string;
  industry: string;
  description: string;
  website: string;
  employees: number;
  founded: number;
  headquarters: string;
}

interface StockDetailsDisplayProps {
  stock: StockDetails | null;
  isLoading?: boolean;
  onClose?: () => void;
}

const StockDetailsDisplay: React.FC<StockDetailsDisplayProps> = ({ 
  stock, 
  isLoading = false, 
  onClose 
}) => {
  if (isLoading) {
    return (
      <div className="w-full">
        <div className="bg-card border border-border rounded-lg p-6 w-full">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mr-3"></div>
            <span className="text-muted-foreground">Loading stock details...</span>
          </div>
        </div>
      </div>
    );
  }

  if (!stock) {
    return null;
  }

  return (
    <div className="w-full">
      {/* Stock Header */}
      <div className="bg-card border border-border rounded-lg p-6 w-full">
        <div className="flex items-center justify-between mb-6">
          <div className="flex-1">
            <h3 className="text-2xl font-bold text-foreground">{stock.symbol}</h3>
            <p className="text-lg text-muted-foreground">{stock.name}</p>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="outline">{stock.sector}</Badge>
              <Badge variant="secondary">{stock.industry}</Badge>
            </div>
          </div>
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
        
        <div className="space-y-6 w-full">
          {/* Price Information */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-sm text-muted-foreground">Current Price</div>
              <div className="text-2xl font-bold">${stock.price?.toFixed(2) || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Change</div>
              <div className={`text-lg font-semibold ${(stock.change || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {(stock.change || 0) >= 0 ? '+' : ''}${stock.change?.toFixed(2) || 'N/A'}
              </div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Change %</div>
              <div className={`text-lg font-semibold ${(stock.changePercent || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                {(stock.changePercent || 0) >= 0 ? '+' : ''}{stock.changePercent?.toFixed(2) || 'N/A'}%
              </div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Volume</div>
              <div className="text-lg font-semibold">{stock.volume?.toLocaleString() || 'N/A'}</div>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
            <div>
              <div className="text-sm text-muted-foreground">Market Cap</div>
              <div className="text-sm font-semibold">
                {stock.marketCap ? `$${(stock.marketCap / 1e9).toFixed(2)}B` : 'N/A'}
              </div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">P/E Ratio</div>
              <div className="text-sm font-semibold">{stock.pe?.toFixed(2) || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">EPS</div>
              <div className="text-sm font-semibold">${stock.eps?.toFixed(2) || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">Dividend Yield</div>
              <div className="text-sm font-semibold">{stock.dividendYield?.toFixed(2) || 'N/A'}%</div>
            </div>
          </div>

          {/* 52-Week Range */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t">
            <div>
              <div className="text-sm text-muted-foreground">52-Week High</div>
              <div className="text-sm font-semibold">${stock.high52Week?.toFixed(2) || 'N/A'}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">52-Week Low</div>
              <div className="text-sm font-semibold">${stock.low52Week?.toFixed(2) || 'N/A'}</div>
            </div>
          </div>

          {/* Company Description */}
          {stock.description && (
            <div className="pt-4 border-t">
              <div className="text-sm text-muted-foreground mb-2">Company Description</div>
              <div className="max-h-32 overflow-y-auto">
                <p className="text-sm text-foreground pr-2">{stock.description}</p>
              </div>
            </div>
          )}

          {/* Trading Actions - Better positioned */}
          <div className="pt-6 border-t bg-muted/30 -mx-6 px-6 py-6 w-full">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-xl font-semibold text-foreground">Trading Activity</h4>
              <Badge variant="outline" className="text-sm">
                Live Trading
              </Badge>
            </div>
            <div className="w-full">
              <TradingActions
                symbol={stock.symbol}
                name={stock.name}
                currentPrice={stock.price || 0}
                change={stock.change || 0}
                changePercent={stock.changePercent || 0}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockDetailsDisplay;

