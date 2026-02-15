
import React from 'react';
import { BarChart, LineChart, PieChart, ExternalLink, RefreshCw, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight, Wallet } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import {
  Area,
  AreaChart,
  Bar,
  BarChart as RechartsBarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart as RechartsLineChart,
  Pie,
  PieChart as RechartsPieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useDashboardSummary, useRefreshDashboard } from '@/hooks/use-dashboard';
import { useTrading } from '@/context/TradingContext';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const Dashboard = () => {
  const navigate = useNavigate();

  // Use React Query hooks for dashboard data with Feature Store backend
  const {
    data: dashboardData,
    isLoading,
    isError,
    error
  } = useDashboardSummary();

  const refreshMutation = useRefreshDashboard();

  // Handle manual refresh
  const handleRefresh = () => {
    refreshMutation.mutate();
  };

  // Show loading state
  if (isLoading) {
    return (
      <AppLayout title="Dashboard">
        <div className="flex flex-col items-center justify-center h-[60vh]">
          <RefreshCw className="w-12 h-12 animate-spin mb-4 text-primary" />
          <p className="text-muted-foreground animate-pulse">Loading market data...</p>
        </div>
      </AppLayout>
    );
  }

  // Show error state
  if (isError) {
    return (
      <AppLayout title="Dashboard">
        <div className="flex flex-col items-center justify-center h-[60vh]">
          <div className="bg-destructive/10 p-6 rounded-lg text-center max-w-md">
            <p className="text-destructive font-medium mb-2">Error loading dashboard</p>
            <p className="text-muted-foreground text-sm mb-4">{error?.message}</p>
            <Button onClick={handleRefresh} variant="outline" className="border-destructive/20 hover:bg-destructive/10">
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry Connection
            </Button>
          </div>
        </div>
      </AppLayout>
    );
  }

  // Extract data from dashboard response
  // Use Trading Context for real-time portfolio data from backend
  const { portfolio: contextPortfolio, virtualCash } = useTrading();
  const portfolio = {
    total_value: contextPortfolio.reduce((sum, item) => sum + item.totalValue, 0) + virtualCash,
    cash_available: virtualCash,
    change_percent: 0, // Calculate if historical data available
    total_change: contextPortfolio.reduce((sum, item) => sum + item.profitLoss, 0),
    positions: contextPortfolio.map(p => ({
      symbol: p.symbol,
      value: p.totalValue,
      price: p.currentPrice,
      change: p.profitLossPercent,
      quantity: p.quantity
    }))
  };

  const performance = dashboardData?.performance || [];
  const marketIndices = dashboardData?.market_indices || [];
  // Use positions from context to find top gainers/losers in portfolio or keep market ones
  const positions = portfolio.positions;
  const topGainers = positions.length > 0 ? [...positions].sort((a, b) => b.change - a.change) : (dashboardData?.top_gainers || []);
  const topLosers = positions.length > 0 ? [...positions].sort((a, b) => a.change - b.change) : (dashboardData?.top_losers || []);

  // Transform data for charts
  const portfolioChartData = positions.map((pos: any) => ({
    name: pos.symbol,
    value: pos.value
  }));


  return (
    <AppLayout title="Dashboard" description="Real-time market overview and portfolio tracking.">
      {/* Header Actions */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold tracking-tight hidden md:block">Overview</h2>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={handleRefresh}
            variant="outline"
            size="sm"
            disabled={refreshMutation.isPending}
            className="h-9"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-2 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
            Refresh Data
          </Button>
        </div>
      </div>

      {/* Market Indices Ticker */}
      {marketIndices.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-8">
          {marketIndices.map((index: any, idx: number) => (
            <Card key={idx} className="glass-card border-none bg-card/40 hover:bg-card/60 transition-all">
              <CardContent className="p-4 flex justify-between items-center">
                <div>
                  <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider">{index.name}</p>
                  <p className="text-2xl font-bold mt-1 tracking-tight">
                    {index.value.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                  </p>
                </div>
                <div className={`text-right ${index.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  <span className="flex items-center justify-end font-medium">
                    {index.change >= 0 ? <ArrowUpRight className="w-4 h-4 mr-1" /> : <ArrowDownRight className="w-4 h-4 mr-1" />}
                    {Math.abs(index.change).toFixed(2)}%
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Portfolio Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">

        {/* Total Value */}
        <Card className="glass-card lg:col-span-1 overflow-hidden relative">
          <div className="absolute top-0 right-0 p-3 opacity-10">
            <Wallet className="w-24 h-24" />
          </div>
          <CardHeader className="pb-2">
            <CardDescription>Total Portfolio Value</CardDescription>
            <CardTitle className="text-3xl font-bold text-primary">
              ₹{(portfolio.total_value || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`flex items-center text-sm font-medium mb-3 ${(portfolio.change_percent || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {(portfolio.change_percent || 0) >= 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
              {portfolio.change_percent >= 0 ? '+' : ''}₹{(portfolio.total_change || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })} ({portfolio.change_percent?.toFixed(2)}%)
            </div>
            <Progress value={65} className="h-1.5" />
            <p className="text-xs text-muted-foreground mt-2">Aggregated across all asset classes</p>
          </CardContent>
        </Card>

        {/* Available Cash */}
        <Card className="glass-card">
          <CardHeader className="pb-2">
            <CardDescription>Available Margin</CardDescription>
            <CardTitle className="text-2xl font-bold">
              ₹{(portfolio.cash_available || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-muted-foreground mb-3">
              Free cash for trading
            </div>
            <Button variant="secondary" size="sm" className="w-full text-xs h-7" onClick={() => navigate('/trading')}>
              Add Funds
            </Button>
          </CardContent>
        </Card>

        {/* Top Gainer */}
        <Card className="glass-card cursor-pointer hover:border-green-500/30 transition-all group" onClick={() => topGainers[0] && navigate(`/research?symbol=${topGainers[0].symbol}`)}>
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <CardDescription>Top Gainer</CardDescription>
            <TrendingUp className="w-4 h-4 text-green-500" />
          </CardHeader>
          <CardContent>
            {topGainers[0] ? (
              <>
                <div className="text-xl font-bold group-hover:text-green-500 transition-colors">
                  {topGainers[0].symbol}
                </div>
                <div className="text-sm text-green-500 font-medium mt-1">
                  +{topGainers[0].change.toFixed(2)}%
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  LTP: ₹{topGainers[0].price.toLocaleString('en-IN')}
                </div>
              </>
            ) : (
              <span className="text-muted-foreground">No data</span>
            )}
          </CardContent>
        </Card>

        {/* Top Loser */}
        <Card className="glass-card cursor-pointer hover:border-red-500/30 transition-all group" onClick={() => topLosers[0] && navigate(`/research?symbol=${topLosers[0].symbol}`)}>
          <CardHeader className="pb-2 flex flex-row items-center justify-between">
            <CardDescription>Top Loser</CardDescription>
            <TrendingDown className="w-4 h-4 text-red-500" />
          </CardHeader>
          <CardContent>
            {topLosers[0] ? (
              <>
                <div className="text-xl font-bold group-hover:text-red-500 transition-colors">
                  {topLosers[0].symbol}
                </div>
                <div className="text-sm text-red-500 font-medium mt-1">
                  {topLosers[0].change.toFixed(2)}%
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  LTP: ₹{topLosers[0].price.toLocaleString('en-IN')}
                </div>
              </>
            ) : (
              <span className="text-muted-foreground">No data</span>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Analytics Charts */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card className="md:col-span-2 glass-card">
          <CardHeader>
            <CardTitle className="text-base font-semibold">Portfolio Performance</CardTitle>
            <CardDescription>Value growth over the last 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              {performance.length > 0 ? (
                <ChartContainer
                  config={{
                    value: {
                      label: "Portfolio Value",
                      theme: {
                        light: "hsl(var(--primary))",
                        dark: "hsl(var(--primary))"
                      }
                    },
                  }}
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={performance}>
                      <defs>
                        <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                      <XAxis dataKey="date" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                      <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `₹${value / 1000}k`} />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke="hsl(var(--primary))"
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#colorValue)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </ChartContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-muted-foreground">
                  No performance history available
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="text-base font-semibold">Asset Allocation</CardTitle>
            <CardDescription>Current distribution</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              {portfolioChartData.length > 0 ? (
                <ChartContainer
                  config={portfolioChartData.reduce((acc, item, index) => ({
                    ...acc,
                    [item.name]: { color: COLORS[index % COLORS.length], label: item.name }
                  }), {})}
                >
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsPieChart>
                      <Pie
                        data={portfolioChartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {portfolioChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} strokeWidth={0} />
                        ))}
                      </Pie>
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Legend verticalAlign="bottom" height={36} />
                    </RechartsPieChart>
                  </ResponsiveContainer>
                </ChartContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-muted-foreground">
                  No holdings found
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Holdings Table */}
      <Card className="glass-card overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-lg">Current Holdings</CardTitle>
            <CardDescription>Overview of your open positions</CardDescription>
          </div>
          <Button variant="outline" size="sm" onClick={() => navigate('/trading')}>
            View All
            <ArrowUpRight className="ml-2 h-4 w-4" />
          </Button>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-muted/50 text-muted-foreground font-medium uppercase text-xs">
                <tr>
                  <th className="px-6 py-3">Symbol</th>
                  <th className="px-6 py-3 text-right">Avg Price</th>
                  <th className="px-6 py-3 text-right">Qty</th>
                  <th className="px-6 py-3 text-right">Current Value</th>
                  <th className="px-6 py-3 text-right">P&L</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {positions.length > 0 ? positions.map((pos: any, idx: number) => (
                  <tr key={idx} className="hover:bg-muted/30 transition-colors cursor-pointer" onClick={() => navigate(`/research?symbol=${pos.symbol}`)}>
                    <td className="px-6 py-4 font-semibold">{pos.symbol}</td>
                    <td className="px-6 py-4 text-right font-mono text-muted-foreground">₹{pos.price.toLocaleString('en-IN')}</td>
                    <td className="px-6 py-4 text-right">{pos.quantity.toFixed(0)}</td>
                    <td className="px-6 py-4 text-right font-medium">₹{pos.value.toLocaleString('en-IN')}</td>
                    <td className={`px-6 py-4 text-right font-bold ${pos.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {pos.change >= 0 ? '+' : ''}{pos.change.toFixed(2)}%
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">
                      No open positions found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

    </AppLayout>
  );
};

export default Dashboard;
