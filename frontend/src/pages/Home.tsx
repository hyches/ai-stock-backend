import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, BarChart3, Globe, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getMarketOverview, getPopularStocks } from '@/lib/api';
import SearchBar from '@/components/SearchBar';

interface MarketOverview {
  totalMarketCap: number;
  totalVolume: number;
  gainers: number;
  losers: number;
  unchanged: number;
}

interface PopularStock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
}

const Home = () => {
  const navigate = useNavigate();

  // Fetch market overview
  const { data: marketOverview, isLoading: marketLoading, error: marketError } = useQuery({
    queryKey: ['market-overview'],
    queryFn: getMarketOverview,
    refetchInterval: 30000, // Refetch every 30 seconds
    retry: 1, // Only retry once
    retryDelay: 1000,
  });

  // Fetch popular stocks
  const { data: popularStocks, isLoading: popularLoading, error: popularError } = useQuery({
    queryKey: ['popular-stocks'],
    queryFn: getPopularStocks,
    refetchInterval: 60000, // Refetch every minute
    retry: 1, // Only retry once
    retryDelay: 1000,
  });

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Search for <span className="text-blue-200">Stocks</span>
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-blue-100">
              AI-powered stock analysis and trading platform
            </p>
            
            {/* Search Bar */}
            <div className="max-w-2xl mx-auto">
              <SearchBar 
                placeholder="Search for stocks (e.g., AAPL, Microsoft, Tesla)"
                showInlineDetails={true}
                className="w-full"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="space-y-12">
          {/* Market Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Market Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              {marketLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="text-center">
                      <Skeleton className="h-4 w-20 mx-auto mb-2" />
                      <Skeleton className="h-6 w-16 mx-auto" />
                    </div>
                  ))}
                </div>
              ) : marketOverview ? (
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  <div className="text-center">
                    <div className="text-sm text-muted-foreground">Market Cap</div>
                    <div className="text-lg font-semibold">
                      ${(marketOverview.totalMarketCap / 1e12).toFixed(2)}T
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-muted-foreground">Volume</div>
                    <div className="text-lg font-semibold">
                      {(marketOverview.totalVolume / 1e9).toFixed(2)}B
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-muted-foreground text-green-600">Gainers</div>
                    <div className="text-lg font-semibold text-green-600">
                      {marketOverview.gainers}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-muted-foreground text-red-600">Losers</div>
                    <div className="text-lg font-semibold text-red-600">
                      {marketOverview.losers}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm text-muted-foreground">Unchanged</div>
                    <div className="text-lg font-semibold">
                      {marketOverview.unchanged}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  No market data available
                </div>
              )}
            </CardContent>
          </Card>

          {/* Popular Stocks */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5" />
                Popular Stocks
              </CardTitle>
            </CardHeader>
            <CardContent>
              {popularLoading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className="p-4 border rounded-lg">
                      <Skeleton className="h-4 w-20 mb-2" />
                      <Skeleton className="h-6 w-16 mb-2" />
                      <Skeleton className="h-4 w-12" />
                    </div>
                  ))}
                </div>
              ) : popularStocks && popularStocks.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {popularStocks.map((stock, index) => (
                    <div key={index} className="p-4 border rounded-lg hover:bg-muted cursor-pointer transition-colors">
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-semibold text-foreground">{stock.symbol}</div>
                        <Badge variant={stock.change >= 0 ? 'default' : 'destructive'}>
                          {stock.change >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground mb-1">{stock.name}</div>
                      <div className="flex items-center justify-between">
                        <span className="text-lg font-semibold">${stock.price.toFixed(2)}</span>
                        <div className="flex items-center gap-1">
                          {stock.change >= 0 ? (
                            <TrendingUp className="h-4 w-4 text-green-500" />
                          ) : (
                            <TrendingDown className="h-4 w-4 text-red-500" />
                          )}
                          <span className={`text-sm ${stock.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                            {stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  No popular stocks available
                </div>
              )}
            </CardContent>
          </Card>

          {/* Call to Action */}
          <div className="text-center py-12">
            <h2 className="text-3xl font-bold mb-4">Ready to Start Trading?</h2>
            <p className="text-lg text-muted-foreground mb-8">
              Join thousands of investors using our AI-powered platform
            </p>
            <div className="flex gap-4 justify-center">
              <Button size="lg" onClick={() => navigate('/login')}>
                Get Started
              </Button>
              <Button size="lg" variant="outline" onClick={() => navigate('/search')}>
                Explore Stocks
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;