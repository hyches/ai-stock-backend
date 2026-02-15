
import React, { useState, useEffect } from 'react';
import { ArrowLeft, TrendingUp, TrendingDown, ExternalLink, RefreshCw, Calendar, ArrowUpRight, ArrowDownRight, DollarSign, Plus } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import CustomCard from '@/components/ui/custom-card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useNavigate } from 'react-router-dom';
import { useTrading } from '@/context/TradingContext';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

const Investments = () => {
  const navigate = useNavigate();
  const { portfolio = [], transactions = [], virtualCash = 0, resetBalance } = useTrading();
  const [activeTab, setActiveTab] = useState('holdings');
  const [isAddFundsOpen, setIsAddFundsOpen] = useState(false);

  const formatCurrency = (amount: number) => {
    return `₹${amount.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatDate = (dateString: string | Date) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // --- Holdings Calculations ---
  const totalInvestedPortfolio = portfolio.reduce((sum: number, item: any) => sum + (item.totalValue || 0), 0);
  const totalProfitLossPortfolio = portfolio.reduce((sum: number, item: any) => sum + (item.profitLoss || 0), 0);
  const totalProfitLossPercentPortfolio = totalInvestedPortfolio > 0 ? (totalProfitLossPortfolio / totalInvestedPortfolio) * 100 : 0;

  // --- Capital Gains Calculations (Realized from Transactions) ---
  // Simple logic: Sum of all Sales - Sum of all Buys (for closed positions).
  // This is an approximation if we don't have explicit "Realized P&L" stored.
  // Using the logic from Transactions.tsx: Net P&L = Total Sold - Total Invested. 
  // Note: This includes currently held stock cost, so it's "Account Net Cash Flow" rather than pure "Realized Gain".
  // For a proper Capital Gains report, we'd need closed trade history. We will use the Summary logic from Transactions.tsx for now.
  const totalInvestedTxn = transactions
    .filter((t: any) => t.type === 'buy')
    .reduce((sum: number, t: any) => sum + t.total, 0);

  const totalSoldTxn = transactions
    .filter((t: any) => t.type === 'sell')
    .reduce((sum: number, t: any) => sum + t.total, 0);

  const netCashFlow = totalSoldTxn - totalInvestedTxn; // This is Realized + Unrealized Cash impact

  return (
    <AppLayout title="My Investments" description="Comprehensive view of your portfolio, gains, and history">
      <div className="space-y-6">
        {/* Back Button */}
        <div className="flex justify-between items-center">
          <Button
            variant="outline"
            onClick={() => navigate('/dashboard')}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>

          <Button
            variant="default"
            onClick={() => navigate('/trading')}
          >
            Go to F&O Terminal
          </Button>
        </div>


        <Tabs defaultValue="holdings" value={activeTab} onValueChange={setActiveTab} className="space-y-4">
          <TabsList className="grid w-full grid-cols-3 lg:w-[400px]">
            <TabsTrigger value="holdings">Holdings</TabsTrigger>
            <TabsTrigger value="capital-gains">Capital Gains</TabsTrigger>
            <TabsTrigger value="transactions">Transactions</TabsTrigger>
          </TabsList>

          {/* --- HOLDINGS TAB --- */}
          <TabsContent value="holdings" className="space-y-4">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <CustomCard title="Total Investment" description="Current portfolio value">
                <div className="text-2xl font-bold text-primary mt-2">
                  {formatCurrency(totalInvestedPortfolio)}
                </div>
                <div className="text-sm text-muted-foreground mt-1">
                  {portfolio.length} active positions
                </div>
              </CustomCard>

              <CustomCard title="Unrealized P&L" description="Current open positions">
                <div className={`text-2xl font-bold mt-2 ${totalProfitLossPortfolio >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {totalProfitLossPortfolio >= 0 ? '+' : ''}{formatCurrency(totalProfitLossPortfolio)}
                </div>
                <div className={`text-sm mt-1 ${totalProfitLossPercentPortfolio >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {totalProfitLossPercentPortfolio >= 0 ? '+' : ''}{totalProfitLossPercentPortfolio.toFixed(2)}%
                </div>
              </CustomCard>

              <CustomCard title="Available Cash" description="Virtual Margin">
                <div className="flex justify-between items-center mt-2">
                  <div className="text-2xl font-bold font-mono">
                    {formatCurrency(virtualCash)}
                  </div>
                  <Button size="sm" variant="outline" onClick={() => setIsAddFundsOpen(true)} className="h-8">
                    <Plus className="h-4 w-4 mr-1" /> Add
                  </Button>
                </div>
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
                        <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">Avg Price</th>
                        <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">LtP</th>
                        <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">Value</th>
                        <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">P&L</th>
                        <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolio.map((holding: any, index: number) => (
                        <tr key={index} className="border-b border-border hover:bg-muted/50 cursor-pointer" onClick={() => navigate(`/stock/${holding.symbol}`)}>
                          <td className="py-3 px-4 font-medium">
                            <div>{holding.symbol || 'N/A'}</div>
                            <Badge variant="outline" className="text-[10px] h-4 px-1">{holding.quantity} Qty</Badge>
                          </td>
                          <td className="py-3 px-4 text-muted-foreground text-sm">{holding.name || 'N/A'}</td>
                          <td className="py-3 px-4 text-right text-sm">{formatCurrency(holding.averagePrice || 0)}</td>
                          <td className="py-3 px-4 text-right text-sm">{formatCurrency(holding.currentPrice || 0)}</td>
                          <td className="py-3 px-4 text-right font-medium">{formatCurrency(holding.totalValue || 0)}</td>
                          <td className="py-3 px-4 text-right">
                            <div className={`font-medium ${(holding.profitLoss || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                              {(holding.profitLoss || 0) >= 0 ? '+' : ''}{formatCurrency(holding.profitLoss || 0)}
                            </div>
                            <div className={`text-xs ${(holding.profitLossPercent || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                              {(holding.profitLossPercent || 0) >= 0 ? '+' : ''}{(holding.profitLossPercent || 0).toFixed(2)}%
                            </div>
                          </td>
                          <td className="py-3 px-4 text-center">
                            <Button variant="ghost" size="icon" onClick={(e) => { e.stopPropagation(); navigate(`/trading?symbol=${holding.symbol}`); }}>
                              <TrendingUp className="h-4 w-4" />
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-muted-foreground mb-4">No investments yet</div>
                  <Button onClick={() => navigate('/trading')}>
                    Start Investing
                  </Button>
                </div>
              )}
            </CustomCard>
          </TabsContent>

          {/* --- CAPITAL GAINS TAB --- */}
          <TabsContent value="capital-gains" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <CustomCard title="Realized Gains Summary">
                <div className="space-y-4">
                  <div className="flex justify-between items-center border-b pb-2">
                    <span className="text-muted-foreground">Total Invested (Lifetime)</span>
                    <span className="font-semibold">{formatCurrency(totalInvestedTxn)}</span>
                  </div>
                  <div className="flex justify-between items-center border-b pb-2">
                    <span className="text-muted-foreground">Total Sold (Lifetime)</span>
                    <span className="font-semibold">{formatCurrency(totalSoldTxn)}</span>
                  </div>
                  <div className="flex justify-between items-center pt-2">
                    <span className="text-muted-foreground font-medium">Net Cash Flow</span>
                    <span className={`text-xl font-bold ${netCashFlow >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {netCashFlow >= 0 ? '+' : ''}{formatCurrency(netCashFlow)}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground italic mt-2">
                    *Calculating Tax Harvesting opportunities requires detailed tax lot history.
                  </p>
                </div>
              </CustomCard>

              <CustomCard title="Tax Reports">
                <div className="flex flex-col gap-3 justify-center h-full">
                  <Button variant="outline" className="justify-start">
                    <Calendar className="mr-2 h-4 w-4" /> Current FY 2025-26 Report
                  </Button>
                  <Button variant="outline" className="justify-start">
                    <Calendar className="mr-2 h-4 w-4" /> Previous FY 2024-25 Report
                  </Button>
                  <div className="text-center text-xs text-muted-foreground mt-2">
                    Downloads available in PDF format
                  </div>
                </div>
              </CustomCard>
            </div>
          </TabsContent>

          {/* --- TRANSACTIONS TAB --- */}
          <TabsContent value="transactions" className="space-y-4">
            <CustomCard title="Transaction History" description="All executed trades">
              {transactions.length === 0 ? (
                <div className="text-center py-8">
                  <div className="text-muted-foreground mb-4">
                    No transactions yet.
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  {transactions.slice().reverse().map((transaction: any) => (
                    <div
                      key={transaction.id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`p-2 rounded-full ${transaction.type === 'buy'
                          ? 'bg-green-100 text-green-600 dark:bg-green-900/30'
                          : 'bg-red-100 text-red-600 dark:bg-red-900/30'
                          }`}>
                          {transaction.type === 'buy' ? (
                            <ArrowUpRight className="h-4 w-4" />
                          ) : (
                            <ArrowDownRight className="h-4 w-4" />
                          )}
                        </div>

                        <div>
                          <div className="flex items-center space-x-2">
                            <span className="font-semibold">{transaction.symbol}</span>
                            <Badge variant={transaction.type === 'buy' ? 'default' : 'destructive'} className="text-[10px] h-5">
                              {transaction.type.toUpperCase()}
                            </Badge>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            {formatDate(transaction.timestamp)}
                          </p>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="font-semibold text-sm">
                          {transaction.quantity} @ ₹{transaction.price.toFixed(2)}
                        </div>
                        <div className={`text-sm font-bold ${transaction.type === 'buy' ? 'text-green-600' : 'text-red-600'
                          }`}>
                          {transaction.type === 'buy' ? '-' : '+'}₹{transaction.total.toLocaleString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CustomCard>
          </TabsContent>
        </Tabs>

        {/* Add Funds Dialog */}
        <Dialog open={isAddFundsOpen} onOpenChange={setIsAddFundsOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Virtual Funds</DialogTitle>
              <DialogDescription>Add funds to your paper trading account.</DialogDescription>
            </DialogHeader>
            <div className="flex gap-2 justify-center py-4">
              {[100000, 500000, 1000000].map(amt => (
                <Button key={amt} variant="outline" onClick={() => {
                  resetBalance(amt);
                  setIsAddFundsOpen(false);
                }}>
                  + ₹{(amt / 100000).toFixed(0)}L
                </Button>
              ))}
            </div>
            <div className="text-center text-xs text-muted-foreground">
              Current Balance: {formatCurrency(virtualCash)}
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </AppLayout >
  );
};

export default Investments;

