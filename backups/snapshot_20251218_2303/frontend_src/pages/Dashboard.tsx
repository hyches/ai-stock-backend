import React from 'react';
import { BarChart, LineChart, PieChart, ExternalLink, RefreshCw, TrendingUp, TrendingDown } from 'lucide-react';
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
import { useDashboardSummary, useRefreshDashboard } from '@/hooks/use-dashboard';

const COLORS = ['#4ECDC4', '#0077E6', '#F97316', '#D946EF', '#8B5CF6'];

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
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <RefreshCw className="w-12 h-12 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading dashboard data...</p>
          </div>
        </div>
      </AppLayout>
    );
  }
  
  // Show error state
  if (isError) {
    return (
      <AppLayout title="Dashboard">
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <p className="text-destructive mb-4">Error loading dashboard: {error?.message}</p>
            <Button onClick={handleRefresh} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
          </div>
        </div>
      </AppLayout>
    );
  }
  
  // Extract data from dashboard response
  const portfolio = dashboardData?.portfolio || {};
  const performance = dashboardData?.performance || [];
  const marketIndices = dashboardData?.market_indices || [];
  const topGainers = dashboardData?.top_gainers || [];
  const topLosers = dashboardData?.top_losers || [];
  const positions = portfolio.positions || [];
  
  // Transform data for charts
  const portfolioChartData = positions.map((pos: any) => ({
    name: pos.symbol,
    value: pos.value
  }));
  
  const stockData = positions.map((pos: any) => ({
    name: pos.symbol,
    price: pos.price,
    change: pos.change
  }));


  return (
    <AppLayout title="Dashboard">
      {/* Header with Refresh Button */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold">Dashboard Overview</h2>
          <p className="text-sm text-muted-foreground">
            Real-time market data powered by Feature Store
          </p>
        </div>
        <Button 
          onClick={handleRefresh} 
          variant="outline" 
          size="sm"
          disabled={refreshMutation.isPending}
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Market Indices */}
      {marketIndices.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {marketIndices.map((index: any, idx: number) => (
            <CustomCard key={idx} title={index.name} className="p-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-2xl font-bold">
                    {index.value.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                  </p>
                  <p className={`text-sm flex items-center ${index.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {index.change >= 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                    {index.change >= 0 ? '+' : ''}{index.change.toFixed(2)}%
                  </p>
                </div>
              </div>
            </CustomCard>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <CustomCard 
          className="md:col-span-2" 
          title="Portfolio Performance" 
          description="Last 30 days"
        >
          <div className="h-64">
            {performance.length > 0 ? (
              <ChartContainer 
                config={{
                  value: {
                    label: "Portfolio Value",
                    theme: {
                      light: "#4ECDC4",
                      dark: "#4ECDC4"
                    }
                  },
                }}
              >
                <RechartsLineChart data={performance}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="date" stroke="rgba(255,255,255,0.5)" />
                  <YAxis stroke="rgba(255,255,255,0.5)" />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke="#4ECDC4" 
                    name="value"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 6 }}
                  />
                </RechartsLineChart>
              </ChartContainer>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-muted-foreground">No performance data available</div>
              </div>
            )}
          </div>
        </CustomCard>
        
        <CustomCard title="Portfolio Allocation" description="Current holdings">
          <div className="h-64">
            {portfolioChartData.length > 0 ? (
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
                <div className="text-muted-foreground">No allocation data</div>
              </div>
            )}
          </div>
        </CustomCard>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <CustomCard 
          title="Total Portfolio Value" 
          description="Current holdings"
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => navigate('/trading')}
        >
          <div className="text-3xl font-bold text-primary mt-2">
            ₹{(portfolio.total_value || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className={`text-sm mt-1 flex items-center ${(portfolio.change_percent || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {(portfolio.change_percent || 0) >= 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
            {(portfolio.change_percent || 0) >= 0 ? '+' : ''}₹{(portfolio.total_change || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })} ({(portfolio.change_percent || 0).toFixed(2)}%)
          </div>
          <Progress value={50} className="mt-4 h-2" />
          <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
            <span>Investments + Cash</span>
            <ExternalLink className="h-3 w-3" />
          </div>
        </CustomCard>
        
        <CustomCard 
          title="Available Cash" 
          description="Trading balance"
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => navigate('/trading')}
        >
          <div className="text-3xl font-bold text-primary mt-2">
            ₹{(portfolio.cash_available || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-sm text-muted-foreground mt-1">
            Ready to deploy
          </div>
          <Progress value={50} className="mt-4 h-2" />
          <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
            <span>Virtual trading balance</span>
            <ExternalLink className="h-3 w-3" />
          </div>
        </CustomCard>
        
        <CustomCard 
          title="Top Gainer" 
          description="Best performing"
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => topGainers[0] && navigate(`/research?symbol=${topGainers[0].symbol}`)}
        >
          {topGainers[0] ? (
            <>
              <div className="text-2xl font-bold text-primary mt-2">
                {topGainers[0].symbol}
              </div>
              <div className="text-sm text-green-500 mt-1 flex items-center">
                <TrendingUp className="w-4 h-4 mr-1" />
                +{topGainers[0].change.toFixed(2)}%
              </div>
              <div className="text-xs text-muted-foreground mt-2">
                ₹{topGainers[0].price.toLocaleString('en-IN')}
              </div>
            </>
          ) : (
            <div className="text-muted-foreground mt-2">No data</div>
          )}
        </CustomCard>
        
        <CustomCard 
          title="Top Loser" 
          description="Needs attention"
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => topLosers[0] && navigate(`/research?symbol=${topLosers[0].symbol}`)}
        >
          {topLosers[0] ? (
            <>
              <div className="text-2xl font-bold text-primary mt-2">
                {topLosers[0].symbol}
              </div>
              <div className="text-sm text-red-500 mt-1 flex items-center">
                <TrendingDown className="w-4 h-4 mr-1" />
                {topLosers[0].change.toFixed(2)}%
              </div>
              <div className="text-xs text-muted-foreground mt-2">
                ₹{topLosers[0].price.toLocaleString('en-IN')}
              </div>
            </>
          ) : (
            <div className="text-muted-foreground mt-2">No data</div>
          )}
        </CustomCard>
      </div>
      
      {/* Positions Table */}
      <CustomCard title="Current Positions" description={`${positions.length} holdings`} className="mb-6">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">Symbol</th>
                <th className="text-right p-2">Price</th>
                <th className="text-right p-2">Quantity</th>
                <th className="text-right p-2">Value</th>
                <th className="text-right p-2">Change</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((pos: any, idx: number) => (
                <tr 
                  key={idx} 
                  className="border-b hover:bg-muted/50 cursor-pointer"
                  onClick={() => navigate(`/research?symbol=${pos.symbol}`)}
                >
                  <td className="p-2 font-medium">{pos.symbol}</td>
                  <td className="text-right p-2">₹{pos.price.toLocaleString('en-IN')}</td>
                  <td className="text-right p-2">{pos.quantity.toFixed(0)}</td>
                  <td className="text-right p-2">₹{pos.value.toLocaleString('en-IN')}</td>
                  <td className={`text-right p-2 ${pos.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {pos.change >= 0 ? '+' : ''}{pos.change.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CustomCard>
      
      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <CustomCard 
          title="Research & Analysis" 
          description="Technical & fundamental analysis"
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => navigate('/research')}
        >
          <div className="flex items-center justify-between mt-4">
            <BarChart className="w-8 h-8 text-primary" />
            <ExternalLink className="w-4 h-4 text-muted-foreground" />
          </div>
        </CustomCard>
        
        <CustomCard 
          title="Stock Screener" 
          description="Find investment opportunities"
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => navigate('/screener')}
        >
          <div className="flex items-center justify-between mt-4">
            <PieChart className="w-8 h-8 text-primary" />
            <ExternalLink className="w-4 h-4 text-muted-foreground" />
          </div>
        </CustomCard>
        
        <CustomCard 
          title="Virtual Trading" 
          description="Practice with paper money"
          className="cursor-pointer hover:shadow-md transition-shadow"
          onClick={() => navigate('/trading')}
        >
          <div className="flex items-center justify-between mt-4">
            <LineChart className="w-8 h-8 text-primary" />
            <ExternalLink className="w-4 h-4 text-muted-foreground" />
          </div>
        </CustomCard>
      </div>
      
    </AppLayout>
  );
};

export default Dashboard;
