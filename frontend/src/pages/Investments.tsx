import React from 'react';
import { ArrowLeft, TrendingUp, TrendingDown, ExternalLink } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import CustomCard from '@/components/ui/custom-card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useNavigate } from 'react-router-dom';
import { useTrading } from '@/context/TradingContext';

const Investments = () => {
  const navigate = useNavigate();
  
  // Add error handling for TradingContext
  let portfolio = [];
  try {
    const tradingContext = useTrading();
    portfolio = tradingContext.portfolio || [];
    console.log('Investments page - Portfolio data:', portfolio);
  } catch (error) {
    console.error('Error accessing TradingContext in Investments:', error);
    // Fallback to empty array if context fails
    portfolio = [];
  }

  const formatCurrency = (amount: number) => {
    return `₹${amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const totalInvestments = portfolio.reduce((sum, item) => sum + (item.totalValue || 0), 0);
  const totalProfitLoss = portfolio.reduce((sum, item) => sum + (item.profitLoss || 0), 0);
  const totalProfitLossPercent = totalInvestments > 0 ? (totalProfitLoss / totalInvestments) * 100 : 0;

  return (
    <AppLayout title="My Investments" description="Detailed view of all your stock holdings">
      <div className="space-y-6">
        {/* Back Button */}
        <Button
          variant="outline"
          onClick={() => navigate('/dashboard')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <CustomCard title="Total Investment" description="Current portfolio value">
            <div className="text-2xl font-bold text-primary mt-2">
              {formatCurrency(totalInvestments)}
            </div>
            <div className="text-sm text-muted-foreground mt-1">
              {portfolio.length} holdings
            </div>
          </CustomCard>

          <CustomCard title="Total P&L" description="Unrealized gains/losses">
            <div className={`text-2xl font-bold mt-2 ${totalProfitLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {totalProfitLoss >= 0 ? '+' : ''}{formatCurrency(totalProfitLoss)}
            </div>
            <div className={`text-sm mt-1 ${totalProfitLossPercent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {totalProfitLossPercent >= 0 ? '+' : ''}{totalProfitLossPercent.toFixed(2)}%
            </div>
          </CustomCard>

          <CustomCard title="Best Performer" description="Top gainer in portfolio">
            {portfolio.length > 0 ? (
              <>
                <div className="text-2xl font-bold text-green-500 mt-2">
                  {portfolio.reduce((best, current) => 
                    (current.profitLossPercent || 0) > (best.profitLossPercent || 0) ? current : best
                  ).symbol || 'N/A'}
                </div>
                <div className="text-sm text-green-500 mt-1">
                  +{Math.max(...portfolio.map(p => p.profitLossPercent || 0)).toFixed(2)}%
                </div>
              </>
            ) : (
              <div className="text-muted-foreground mt-2">No holdings</div>
            )}
          </CustomCard>
        </div>

        {/* Detailed Holdings Table */}
        <CustomCard title="Holdings Details" description="All your current stock positions">
          {portfolio.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Symbol</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Company</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">Quantity</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">Avg Price</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">Current Price</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">Market Value</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">P&L</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">P&L %</th>
                    <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolio.map((holding, index) => (
                    <tr key={index} className="border-b border-border hover:bg-muted/50">
                      <td className="py-3 px-4 font-medium">{holding.symbol || 'N/A'}</td>
                      <td className="py-3 px-4 text-muted-foreground">{holding.name || 'N/A'}</td>
                      <td className="py-3 px-4 text-right">{holding.quantity || 0}</td>
                      <td className="py-3 px-4 text-right">{formatCurrency(holding.averagePrice || 0)}</td>
                      <td className="py-3 px-4 text-right">{formatCurrency(holding.currentPrice || 0)}</td>
                      <td className="py-3 px-4 text-right font-medium">{formatCurrency(holding.totalValue || 0)}</td>
                      <td className={`py-3 px-4 text-right font-medium ${(holding.profitLoss || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {(holding.profitLoss || 0) >= 0 ? '+' : ''}{formatCurrency(holding.profitLoss || 0)}
                      </td>
                      <td className={`py-3 px-4 text-right ${(holding.profitLossPercent || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {(holding.profitLossPercent || 0) >= 0 ? '+' : ''}{(holding.profitLossPercent || 0).toFixed(2)}%
                      </td>
                      <td className="py-3 px-4 text-center">
                        <div className="flex items-center justify-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => navigate(`/stock/${holding.symbol || ''}`)}
                          >
                            <ExternalLink className="h-3 w-3" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-muted-foreground mb-4">No investments yet</div>
              <Button onClick={() => navigate('/search')}>
                Start Investing
              </Button>
            </div>
          )}
        </CustomCard>

        {/* Performance Chart Placeholder */}
        <CustomCard title="Portfolio Performance" description="Historical performance of your investments">
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            <div className="text-center">
              <TrendingUp className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Performance chart coming soon</p>
              <p className="text-sm">Track your portfolio's growth over time</p>
            </div>
          </div>
        </CustomCard>
      </div>
    </AppLayout>
  );
};

export default Investments;
