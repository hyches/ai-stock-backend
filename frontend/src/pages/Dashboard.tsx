import React from 'react';
import { BarChart, LineChart, PieChart, ExternalLink } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import CustomCard from '@/components/ui/custom-card';
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
import { usePortfolio, useWatchlist, useModelPerformance } from '@/hooks/use-api';
import { useTrading } from '@/context/TradingContext';

// No fallback data - show loading states instead

const COLORS = ['#4ECDC4', '#0077E6', '#F97316', '#D946EF', '#8B5CF6'];

const Dashboard = () => {
  const navigate = useNavigate();

  // Fetch data from API
  const { data: portfolioData, isLoading: portfolioLoading, error: portfolioError } = usePortfolio();
  const { data: watchlistData, isLoading: watchlistLoading, error: watchlistError } = useWatchlist();
  const { data: modelPerformance, isLoading: modelLoading } = useModelPerformance();
  
  // Get real trading data
  const { watchlist: realWatchlist, portfolio: realPortfolio, virtualCash, transactions } = useTrading();

  // Use real trading data instead of API data
  const effectivePortfolioData = realPortfolio.length > 0 ? {
    performanceData: realPortfolio.map((item, index) => ({
      date: new Date(Date.now() - (realPortfolio.length - index) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      value: item.totalValue
    })),
    items: realPortfolio.map(item => ({
      symbol: item.symbol,
      totalValue: item.totalValue,
      quantity: item.quantity
    }))
  } : portfolioData;
  
  const effectiveWatchlistData = realWatchlist.length > 0 ? {
    items: realWatchlist.map(item => ({
      symbol: item.symbol,
      price: item.price,
      changePercent: item.changePercent
    }))
  } : watchlistData;
  
  const effectiveModelPerformance = modelPerformance;

  // Transform portfolio data for charts
  const portfolioChartData = effectivePortfolioData?.items?.map(item => ({
    name: item.symbol,
    value: item.totalValue
  })) || [];

  // Calculate trading metrics
  const totalInvestments = realPortfolio.reduce((sum, item) => sum + item.totalValue, 0);
  const totalProfitLoss = realPortfolio.reduce((sum, item) => sum + item.profitLoss, 0);
  const totalValue = virtualCash + totalInvestments;
  
  // Calculate today's P&L (unrealized + realized)
  const todayProfitLoss = realPortfolio.reduce((sum, item) => {
    const todayChange = item.change * item.quantity;
    return sum + todayChange;
  }, 0);
  
  // Calculate total change percentage
  const totalChangePercent = totalValue > 0 ? (totalProfitLoss / (totalValue - totalProfitLoss)) * 100 : 0;

  // Transform watchlist data
  const stockData = effectiveWatchlistData?.map(item => ({
    name: item.symbol,
    price: item.price,
    change: item.changePercent
  })) || [];

  return (
    <AppLayout title="Dashboard">

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <CustomCard 
          className="md:col-span-2" 
          title="Portfolio Performance" 
          description="Last 12 months"
          headerAction={
            <Button variant="outline" size="sm">View Details</Button>
          }
        >
          <div className="h-64">
            {portfolioLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-muted-foreground">Loading portfolio data...</div>
              </div>
            ) : effectivePortfolioData ? (
              <ChartContainer 
                config={{
                  performance: {
                    label: "Portfolio Value",
                    theme: {
                      light: "#4ECDC4",
                      dark: "#4ECDC4"
                    }
                  },
                }}
              >
                <RechartsLineChart data={effectivePortfolioData.performanceData || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="date" stroke="rgba(255,255,255,0.5)" />
                  <YAxis stroke="rgba(255,255,255,0.5)" />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#4ECDC4" 
                    name="performance"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 6 }}
                  />
                </RechartsLineChart>
              </ChartContainer>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-muted-foreground">No portfolio data available</div>
              </div>
            )}
          </div>
        </CustomCard>
        
        <CustomCard title="Portfolio Allocation" description="Current holdings">
          <div className="h-64">
            {portfolioLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-muted-foreground">Loading allocation...</div>
              </div>
            ) : portfolioChartData.length > 0 ? (
              <ChartContainer 
                config={portfolioChartData.reduce((acc, item, index) => ({
                  ...acc,
                  [item.name]: { color: COLORS[index % COLORS.length] }
                }), {})}
              >
                <RechartsPieChart>
                  <Pie
                    data={portfolioChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey="value"
                    nameKey="name"
                  >
                    {portfolioChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Legend />
                </RechartsPieChart>
              </ChartContainer>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-muted-foreground">No portfolio allocation data</div>
              </div>
            )}
          </div>
        </CustomCard>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <CustomCard 
          title="Total Assets" 
          description="All accounts"
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => navigate('/transactions')}
        >
          <div className="text-3xl font-bold text-primary mt-2">
            ₹{totalValue.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className={`text-sm mt-1 ${totalProfitLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {totalProfitLoss >= 0 ? '+' : ''}₹{totalProfitLoss.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({totalChangePercent.toFixed(1)}%)
          </div>
          <Progress value={totalValue > 0 ? (totalInvestments / totalValue) * 100 : 0} className="mt-4 h-2" />
          <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
            <span>Investment + Cash + Profit</span>
            <ExternalLink className="h-3 w-3" />
          </div>
        </CustomCard>
        
        <CustomCard 
          title="Investments" 
          description="Stocks, ETFs, Mutual Funds"
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => navigate('/investments')}
        >
          <div className="text-3xl font-bold text-primary mt-2">
            ₹{totalInvestments.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-sm text-muted-foreground mt-1">
            {realPortfolio.length} holdings
          </div>
          <Progress value={totalValue > 0 ? (totalInvestments / totalValue) * 100 : 0} className="mt-4 h-2" />
          <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
            <span>View all investments</span>
            <ExternalLink className="h-3 w-3" />
          </div>
        </CustomCard>
        
        <CustomCard 
          title="Cash" 
          description="Available for trading"
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => navigate('/transactions')}
        >
          <div className="text-3xl font-bold text-primary mt-2">
            ₹{virtualCash.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-sm text-muted-foreground mt-1">
            Ready to deploy
          </div>
          <Progress value={totalValue > 0 ? (virtualCash / totalValue) * 100 : 0} className="mt-4 h-2" />
          <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
            <span>View transactions</span>
            <ExternalLink className="h-3 w-3" />
          </div>
        </CustomCard>
        
        <CustomCard 
          title="Day's P&L" 
          description="Today's performance"
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => navigate('/transactions')}
        >
          <div className={`text-3xl font-bold mt-2 ${todayProfitLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {todayProfitLoss >= 0 ? '+' : ''}₹{todayProfitLoss.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-sm text-muted-foreground mt-1">
            Unrealized + Realized
          </div>
          <Progress value={Math.abs(todayProfitLoss) > 0 ? 50 : 0} className="mt-4 h-2" />
          <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
            <span>View detailed P&L</span>
            <ExternalLink className="h-3 w-3" />
          </div>
        </CustomCard>
      </div>
      
      <CustomCard title="Watchlist" description="Top performing stocks">
        <div className="overflow-x-auto">
          {watchlistLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="text-muted-foreground">Loading watchlist...</div>
            </div>
          ) : stockData.length > 0 ? (
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 px-2 text-sm font-medium text-muted-foreground">Symbol</th>
                  <th className="text-right py-3 px-2 text-sm font-medium text-muted-foreground">Price</th>
                  <th className="text-right py-3 px-2 text-sm font-medium text-muted-foreground">Change</th>
                  <th className="text-right py-3 px-2 text-sm font-medium text-muted-foreground">Chart</th>
                </tr>
              </thead>
              <tbody>
                {stockData.map((stock) => (
                  <tr key={stock.name} className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-3 px-2 font-medium">{stock.name}</td>
                    <td className="py-3 px-2 text-right">${stock.price.toFixed(2)}</td>
                    <td className={`py-3 px-2 text-right ${stock.change >= 0 ? 'text-stockup' : 'text-stockdown'}`}>
                      {stock.change > 0 ? '+' : ''}{stock.change.toFixed(2)}%
                    </td>
                    <td className="py-3 px-2 text-right">
                      {stock.change >= 0 ? 
                        <div className="inline-block w-16 h-8"><LineChart className="text-stockup" /></div> : 
                        <div className="inline-block w-16 h-8"><LineChart className="text-stockdown" /></div>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="flex items-center justify-center py-8">
              <div className="text-muted-foreground">No watchlist data available</div>
            </div>
          )}
        </div>
      </CustomCard>
      
    </AppLayout>
  );
};

export default Dashboard;
