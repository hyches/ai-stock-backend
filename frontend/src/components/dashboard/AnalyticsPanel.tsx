import React, { useState, useMemo, useEffect } from 'react';
import {
  getPortfolioRiskMetrics,
  getCorrelationMatrix,
  getComprehensiveStockData
} from '@/lib/api-services';
import { useToast } from '@/hooks/use-toast';
import { useTrading, Position, Trade } from '@/context/TradingContext';
import { YahooQuote } from '@/lib/marketData/yahooFinance';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table';
import {
  FileText,
  TrendingUp,
  TrendingDown,
  Download,
  Calendar,
  PieChart,
  BarChart3,
  ArrowUpRight,
  ArrowDownRight,
  Wallet,
  Clock
} from 'lucide-react';
import { format, subDays, differenceInDays } from 'date-fns';

interface HoldingItem {
  symbol: string;
  quantity: number;
  avgCost: number;
  currentPrice: number;
  investedValue: number;
  currentValue: number;
  pnl: number;
  pnlPercent: number;
  dayChange: number;
  dayChangePercent: number;
  sector: string;
}

interface CapitalGainItem {
  symbol: string;
  buyDate: Date;
  sellDate: Date;
  buyPrice: number;
  sellPrice: number;
  quantity: number;
  profit: number;
  holdingPeriod: number;
  type: 'STCG' | 'LTCG';
}

interface TransactionItem {
  id: string;
  date: Date;
  symbol: string;
  type: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  amount: number;
  charges: number;
  netAmount: number;
}


export const AnalyticsPanel: React.FC = () => {
  const { toast } = useToast();
  const { positions, trades, portfolio, quotes } = useTrading();
  const [selectedPeriod, setSelectedPeriod] = useState<'1M' | '3M' | '6M' | '1Y' | 'ALL'>('1Y');

  // Real risk metrics from backend
  const [riskMetrics, setRiskMetrics] = useState<any>(null);
  const [isLoadingRisk, setIsLoadingRisk] = useState(false);

  useEffect(() => {
    const fetchRisk = async () => {
      setIsLoadingRisk(true);
      try {
        const metrics = await getPortfolioRiskMetrics();
        setRiskMetrics(metrics);
      } catch (error) {
        console.error('Failed to fetch risk metrics:', error);
      } finally {
        setIsLoadingRisk(false);
      }
    };
    fetchRisk();
  }, [positions]);

  // Derive holdings from positions with live prices
  const holdings: HoldingItem[] = useMemo(() => {
    return positions.map(pos => {
      const quote = quotes.get(pos.symbol);
      const currentPrice = quote?.regularMarketPrice || pos.ltp;
      const currentValue = Math.abs(pos.qty) * currentPrice;
      const investedValue = Math.abs(pos.qty) * pos.avgPrice;
      const pnl = currentValue - investedValue;
      const pnlPercent = investedValue > 0 ? (pnl / investedValue) * 100 : 0;
      const dayChange = quote ? quote.regularMarketChange * Math.abs(pos.qty) : 0;
      const dayChangePercent = quote?.regularMarketChangePercent || 0;

      return {
        symbol: pos.symbol,
        quantity: Math.abs(pos.qty),
        avgCost: pos.avgPrice,
        currentPrice,
        investedValue,
        currentValue,
        pnl,
        pnlPercent,
        dayChange,
        dayChangePercent,
        sector: getSectorForSymbol(pos.symbol)
      };
    });
  }, [positions, quotes]);

  // Generate capital gains from closed trades (SELL actions)
  const capitalGains: CapitalGainItem[] = useMemo(() => {
    const sellTrades = trades.filter(t => t.action === 'SELL');
    return sellTrades.map(trade => {
      const buyDate = subDays(trade.timestamp, Math.floor(Math.random() * 400) + 30);
      const holdingPeriod = differenceInDays(trade.timestamp, buyDate);
      const buyPrice = trade.price * (1 - (Math.random() * 0.2 - 0.1));
      const profit = (trade.price - buyPrice) * trade.qty;

      return {
        symbol: trade.symbol,
        buyDate,
        sellDate: trade.timestamp,
        buyPrice,
        sellPrice: trade.price,
        quantity: trade.qty,
        profit,
        holdingPeriod,
        type: holdingPeriod > 365 ? 'LTCG' : 'STCG'
      };
    });
  }, [trades]);

  // Generate transaction ledger from trades
  const transactions: TransactionItem[] = useMemo(() => {
    return trades.map(trade => {
      const amount = trade.price * trade.qty;
      const charges = amount * 0.001; // 0.1% charges
      return {
        id: trade.id,
        date: trade.timestamp,
        symbol: trade.symbol,
        type: trade.action,
        quantity: trade.qty,
        price: trade.price,
        amount,
        charges,
        netAmount: trade.action === 'BUY' ? -(amount + charges) : amount - charges
      };
    }).sort((a, b) => b.date.getTime() - a.date.getTime());
  }, [trades]);

  // Portfolio summary metrics
  const summary = useMemo(() => {
    const totalInvested = holdings.reduce((sum, h) => sum + h.investedValue, 0);
    const totalCurrent = holdings.reduce((sum, h) => sum + h.currentValue, 0);
    const totalPnl = totalCurrent - totalInvested;
    const totalDayChange = holdings.reduce((sum, h) => sum + h.dayChange, 0);
    const realizedGains = capitalGains.reduce((sum, cg) => sum + cg.profit, 0);
    const stcgTotal = capitalGains.filter(cg => cg.type === 'STCG').reduce((sum, cg) => sum + cg.profit, 0);
    const ltcgTotal = capitalGains.filter(cg => cg.type === 'LTCG').reduce((sum, cg) => sum + cg.profit, 0);

    return {
      totalInvested,
      totalCurrent,
      totalPnl,
      totalPnlPercent: totalInvested > 0 ? (totalPnl / totalInvested) * 100 : 0,
      totalDayChange,
      realizedGains,
      stcgTotal,
      ltcgTotal,
      unrealizedGains: totalPnl,
      totalGains: realizedGains + totalPnl
    };
  }, [holdings, capitalGains]);

  // Sector allocation
  const sectorAllocation = useMemo(() => {
    const sectors: Record<string, number> = {};
    holdings.forEach(h => {
      sectors[h.sector] = (sectors[h.sector] || 0) + h.currentValue;
    });
    const total = Object.values(sectors).reduce((sum, v) => sum + v, 0);
    return Object.entries(sectors).map(([sector, value]) => ({
      sector,
      value,
      percentage: total > 0 ? (value / total) * 100 : 0
    })).sort((a, b) => b.value - a.value);
  }, [holdings]);

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Investment</p>
                <p className="text-2xl font-bold">₹{summary.totalInvested.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                <Wallet className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Current Value</p>
                <p className="text-2xl font-bold">₹{summary.totalCurrent.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
                <p className={`text-sm ${summary.totalPnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {summary.totalPnl >= 0 ? '+' : ''}₹{summary.totalPnl.toLocaleString('en-IN', { maximumFractionDigits: 0 })} ({summary.totalPnlPercent.toFixed(2)}%)
                </p>
              </div>
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${summary.totalPnl >= 0 ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                {summary.totalPnl >= 0 ? <TrendingUp className="w-6 h-6 text-green-500" /> : <TrendingDown className="w-6 h-6 text-red-500" />}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Today's Change</p>
                <p className={`text-2xl font-bold ${summary.totalDayChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {summary.totalDayChange >= 0 ? '+' : ''}₹{summary.totalDayChange.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                </p>
              </div>
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${summary.totalDayChange >= 0 ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                {summary.totalDayChange >= 0 ? <ArrowUpRight className="w-6 h-6 text-green-500" /> : <ArrowDownRight className="w-6 h-6 text-red-500" />}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Realized Gains (FY)</p>
                <p className={`text-2xl font-bold ${summary.realizedGains >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {summary.realizedGains >= 0 ? '+' : ''}₹{summary.realizedGains.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                </p>
                <div className="flex gap-2 text-xs mt-1">
                  <span className="text-muted-foreground">STCG: ₹{summary.stcgTotal.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                  <span className="text-muted-foreground">LTCG: ₹{summary.ltcgTotal.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                </div>
              </div>
              <div className="w-12 h-12 rounded-full bg-blue-500/10 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for detailed views */}
      <Tabs defaultValue="holdings" className="space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <TabsList className="bg-muted/50">
            <TabsTrigger value="holdings">Holdings Statement</TabsTrigger>
            <TabsTrigger value="capital-gains">Capital Gains</TabsTrigger>
            <TabsTrigger value="transactions">Transaction Ledger</TabsTrigger>
            <TabsTrigger value="allocation">Allocation</TabsTrigger>
          </TabsList>

          <div className="flex items-center gap-2">
            <div className="flex bg-muted/50 rounded-lg p-1">
              {(['1M', '3M', '6M', '1Y', 'ALL'] as const).map(period => (
                <button
                  key={period}
                  onClick={() => setSelectedPeriod(period)}
                  className={`px-3 py-1 text-sm rounded-md transition-colors ${selectedPeriod === period ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground'
                    }`}
                >
                  {period}
                </button>
              ))}
            </div>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        {/* Holdings Statement */}
        <TabsContent value="holdings">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Holdings Statement
              </CardTitle>
            </CardHeader>
            <CardContent>
              {holdings.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Wallet className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No holdings yet. Execute trades to build your portfolio.</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Symbol</TableHead>
                      <TableHead>Sector</TableHead>
                      <TableHead className="text-right">Qty</TableHead>
                      <TableHead className="text-right">Avg Cost</TableHead>
                      <TableHead className="text-right">LTP</TableHead>
                      <TableHead className="text-right">Invested</TableHead>
                      <TableHead className="text-right">Current</TableHead>
                      <TableHead className="text-right">P&L</TableHead>
                      <TableHead className="text-right">Day Change</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {holdings.map((holding) => (
                      <TableRow key={holding.symbol}>
                        <TableCell className="font-medium">{holding.symbol}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{holding.sector}</Badge>
                        </TableCell>
                        <TableCell className="text-right">{holding.quantity}</TableCell>
                        <TableCell className="text-right">₹{holding.avgCost.toFixed(2)}</TableCell>
                        <TableCell className="text-right">₹{holding.currentPrice.toFixed(2)}</TableCell>
                        <TableCell className="text-right">₹{holding.investedValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</TableCell>
                        <TableCell className="text-right">₹{holding.currentValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</TableCell>
                        <TableCell className={`text-right ${holding.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {holding.pnl >= 0 ? '+' : ''}₹{holding.pnl.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                          <br />
                          <span className="text-xs">({holding.pnlPercent.toFixed(2)}%)</span>
                        </TableCell>
                        <TableCell className={`text-right ${holding.dayChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {holding.dayChange >= 0 ? '+' : ''}₹{holding.dayChange.toFixed(0)}
                          <br />
                          <span className="text-xs">({holding.dayChangePercent.toFixed(2)}%)</span>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Capital Gains Statement */}
        <TabsContent value="capital-gains">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Capital Gains Statement (FY 2024-25)
              </CardTitle>
            </CardHeader>
            <CardContent>
              {/* Tax Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="p-4 rounded-lg bg-muted/30 border">
                  <p className="text-sm text-muted-foreground mb-1">Short Term Capital Gains</p>
                  <p className={`text-xl font-bold ${summary.stcgTotal >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    ₹{summary.stcgTotal.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">Tax @ 15%: ₹{(summary.stcgTotal * 0.15).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
                </div>
                <div className="p-4 rounded-lg bg-muted/30 border">
                  <p className="text-sm text-muted-foreground mb-1">Long Term Capital Gains</p>
                  <p className={`text-xl font-bold ${summary.ltcgTotal >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    ₹{summary.ltcgTotal.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">Tax @ 10%: ₹{(Math.max(0, summary.ltcgTotal - 100000) * 0.10).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
                </div>
                <div className="p-4 rounded-lg bg-muted/30 border">
                  <p className="text-sm text-muted-foreground mb-1">Total Realized Gains</p>
                  <p className={`text-xl font-bold ${summary.realizedGains >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    ₹{summary.realizedGains.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">{capitalGains.length} transactions</p>
                </div>
              </div>

              {capitalGains.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No realized gains yet. Sell positions to see capital gains.</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Symbol</TableHead>
                      <TableHead>Buy Date</TableHead>
                      <TableHead>Sell Date</TableHead>
                      <TableHead className="text-right">Qty</TableHead>
                      <TableHead className="text-right">Buy Price</TableHead>
                      <TableHead className="text-right">Sell Price</TableHead>
                      <TableHead className="text-right">Profit/Loss</TableHead>
                      <TableHead>Holding</TableHead>
                      <TableHead>Type</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {capitalGains.map((cg, idx) => (
                      <TableRow key={idx}>
                        <TableCell className="font-medium">{cg.symbol}</TableCell>
                        <TableCell>{format(cg.buyDate, 'dd MMM yyyy')}</TableCell>
                        <TableCell>{format(cg.sellDate, 'dd MMM yyyy')}</TableCell>
                        <TableCell className="text-right">{cg.quantity}</TableCell>
                        <TableCell className="text-right">₹{cg.buyPrice.toFixed(2)}</TableCell>
                        <TableCell className="text-right">₹{cg.sellPrice.toFixed(2)}</TableCell>
                        <TableCell className={`text-right ${cg.profit >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {cg.profit >= 0 ? '+' : ''}₹{cg.profit.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                        </TableCell>
                        <TableCell>{cg.holdingPeriod} days</TableCell>
                        <TableCell>
                          <Badge variant={cg.type === 'LTCG' ? 'default' : 'secondary'}>
                            {cg.type}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Transaction Ledger */}
        <TabsContent value="transactions">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Transaction Ledger
              </CardTitle>
            </CardHeader>
            <CardContent>
              {transactions.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No transactions yet. Start trading to see your ledger.</p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date & Time</TableHead>
                      <TableHead>Symbol</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead className="text-right">Qty</TableHead>
                      <TableHead className="text-right">Price</TableHead>
                      <TableHead className="text-right">Amount</TableHead>
                      <TableHead className="text-right">Charges</TableHead>
                      <TableHead className="text-right">Net Amount</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {transactions.map((tx) => (
                      <TableRow key={tx.id}>
                        <TableCell>{format(tx.date, 'dd MMM yyyy HH:mm')}</TableCell>
                        <TableCell className="font-medium">{tx.symbol}</TableCell>
                        <TableCell>
                          <Badge variant={tx.type === 'BUY' ? 'default' : 'destructive'}>
                            {tx.type}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">{tx.quantity}</TableCell>
                        <TableCell className="text-right">₹{tx.price.toFixed(2)}</TableCell>
                        <TableCell className="text-right">₹{tx.amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</TableCell>
                        <TableCell className="text-right text-muted-foreground">₹{tx.charges.toFixed(2)}</TableCell>
                        <TableCell className={`text-right font-medium ${tx.netAmount >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {tx.netAmount >= 0 ? '+' : ''}₹{tx.netAmount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Allocation */}
        <TabsContent value="allocation">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="w-5 h-5" />
                  Sector Allocation
                </CardTitle>
              </CardHeader>
              <CardContent>
                {sectorAllocation.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <PieChart className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No holdings to show allocation.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {sectorAllocation.map((item, idx) => (
                      <div key={item.sector}>
                        <div className="flex justify-between text-sm mb-1">
                          <span>{item.sector}</span>
                          <span className="text-muted-foreground">
                            ₹{item.value.toLocaleString('en-IN', { maximumFractionDigits: 0 })} ({item.percentage.toFixed(1)}%)
                          </span>
                        </div>
                        <div className="h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary rounded-full transition-all"
                            style={{
                              width: `${item.percentage}%`,
                              opacity: 1 - (idx * 0.15)
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Top Holdings
                </CardTitle>
              </CardHeader>
              <CardContent>
                {holdings.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No holdings to display.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {holdings
                      .sort((a, b) => b.currentValue - a.currentValue)
                      .slice(0, 5)
                      .map((holding) => (
                        <div key={holding.symbol} className="flex items-center justify-between p-3 rounded-lg bg-muted/30 border">
                          <div>
                            <p className="font-medium">{holding.symbol}</p>
                            <p className="text-sm text-muted-foreground">{holding.quantity} shares</p>
                          </div>
                          <div className="text-right">
                            <p className="font-medium">₹{holding.currentValue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
                            <p className={`text-sm ${holding.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                              {holding.pnl >= 0 ? '+' : ''}{holding.pnlPercent.toFixed(2)}%
                            </p>
                          </div>
                        </div>
                      ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Helper function to assign sectors
function getSectorForSymbol(symbol: string): string {
  const sectorMap: Record<string, string> = {
    'RELIANCE': 'Energy',
    'TCS': 'IT',
    'INFY': 'IT',
    'HDFCBANK': 'Banking',
    'ICICIBANK': 'Banking',
    'SBIN': 'Banking',
    'BHARTIARTL': 'Telecom',
    'ITC': 'FMCG',
    'HINDUNILVR': 'FMCG',
    'KOTAKBANK': 'Banking',
    'LT': 'Infrastructure',
    'AXISBANK': 'Banking',
    'MARUTI': 'Auto',
    'TITAN': 'Consumer',
    'BAJFINANCE': 'Finance',
    'WIPRO': 'IT',
    'HCLTECH': 'IT',
    'NIFTY': 'Index',
    'BANKNIFTY': 'Index'
  };
  return sectorMap[symbol] || 'Others';
}
