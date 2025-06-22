import React from 'react';
import { BarChart, LineChart, PieChart } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import CustomCard from '@/components/ui/custom-card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import ApiTest from '@/components/ApiTest';
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

// Fallback data for when API is not available
const fallbackPortfolioData = [
  { name: 'Apple', value: 35 },
  { name: 'Microsoft', value: 25 },
  { name: 'Amazon', value: 15 },
  { name: 'Google', value: 10 },
  { name: 'Tesla', value: 15 },
];

const fallbackPerformanceData = [
  { date: 'Jan', value: 3200 },
  { date: 'Feb', value: 3500 },
  { date: 'Mar', value: 3300 },
  { date: 'Apr', value: 3700 },
  { date: 'May', value: 4000 },
  { date: 'Jun', value: 4200 },
  { date: 'Jul', value: 4500 },
  { date: 'Aug', value: 4800 },
  { date: 'Sep', value: 5000 },
  { date: 'Oct', value: 5200 },
  { date: 'Nov', value: 5500 },
  { date: 'Dec', value: 5800 },
];

const fallbackStockData = [
  { name: 'AAPL', price: 179.50, change: +2.5 },
  { name: 'MSFT', price: 408.75, change: +1.2 },
  { name: 'AMZN', price: 182.30, change: -0.5 },
  { name: 'GOOGL', price: 176.45, change: +0.3 },
  { name: 'TSLA', price: 178.80, change: -1.7 },
];

const COLORS = ['#4ECDC4', '#0077E6', '#F97316', '#D946EF', '#8B5CF6'];

const Dashboard = () => {
  // Fetch data from API
  const { data: portfolioData, isLoading: portfolioLoading, error: portfolioError } = usePortfolio();
  const { data: watchlistData, isLoading: watchlistLoading, error: watchlistError } = useWatchlist();
  const { data: modelPerformance, isLoading: modelLoading } = useModelPerformance();

  // Use fallback data if API calls fail
  const effectivePortfolioData = portfolioError ? null : portfolioData;
  const effectiveWatchlistData = watchlistError ? null : watchlistData;
  const effectiveModelPerformance = modelLoading ? null : modelPerformance;

  // Transform portfolio data for charts
  const portfolioChartData = effectivePortfolioData?.items?.map(item => ({
    name: item.symbol,
    value: item.totalValue
  })) || fallbackPortfolioData;

  // Calculate total portfolio value
  const totalValue = effectivePortfolioData?.totalValue || 124560.78;
  const totalChange = effectivePortfolioData?.totalChange || 12456;
  const totalChangePercent = effectivePortfolioData?.totalChangePercent || 11.2;

  // Transform watchlist data
  const stockData = effectiveWatchlistData?.map(item => ({
    name: item.symbol,
    price: item.price,
    change: item.changePercent
  })) || fallbackStockData;

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
            ) : (
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
                <RechartsLineChart data={fallbackPerformanceData}>
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
            )}
          </div>
        </CustomCard>
        
        <CustomCard title="Portfolio Allocation" description="Current holdings">
          <div className="h-64">
            {portfolioLoading ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-muted-foreground">Loading allocation...</div>
              </div>
            ) : (
              <ChartContainer 
                config={{
                  Apple: { color: COLORS[0] },
                  Microsoft: { color: COLORS[1] },
                  Amazon: { color: COLORS[2] },
                  Google: { color: COLORS[3] },
                  Tesla: { color: COLORS[4] },
                }}
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
            )}
          </div>
        </CustomCard>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <CustomCard title="Total Assets" description="All accounts">
          <div className="text-3xl font-bold text-teal mt-2">
            ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-sm text-teal/60 mt-1">
            +${totalChange.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ({totalChangePercent.toFixed(1)}%)
          </div>
          <Progress value={85} className="mt-4 h-2" />
        </CustomCard>
        
        <CustomCard title="Investments" description="Stocks, ETFs, Mutual Funds">
          <div className="text-3xl font-bold text-teal mt-2">$98,450.32</div>
          <div className="text-sm text-teal/60 mt-1">+$8,450 (9.4%)</div>
          <Progress value={75} className="mt-4 h-2" />
        </CustomCard>
        
        <CustomCard title="Cash" description="Available for trading">
          <div className="text-3xl font-bold text-teal mt-2">$26,110.46</div>
          <div className="text-sm text-muted-foreground mt-1">21% of portfolio</div>
          <Progress value={21} className="mt-4 h-2" />
        </CustomCard>
        
        <CustomCard title="Day's P&L" description="Today's performance">
          <div className="text-3xl font-bold text-stockup mt-2">+$1,245.32</div>
          <div className="text-sm text-stockup/80 mt-1">+1.01% today</div>
          <Progress value={65} className="mt-4 h-2 bg-secondary [&>div]:bg-stockup" />
        </CustomCard>
      </div>
      
      <CustomCard title="Watchlist" description="Top performing stocks">
        <div className="overflow-x-auto">
          {watchlistLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="text-muted-foreground">Loading watchlist...</div>
            </div>
          ) : (
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
          )}
        </div>
      </CustomCard>
      
      {/* Backend Connection Test */}
      <div className="mt-6">
        <ApiTest />
      </div>
    </AppLayout>
  );
};

export default Dashboard;
