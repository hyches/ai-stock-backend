import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, BarChart3, Globe, Star } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { useQuery } from '@tanstack/react-query';
import { getMarketOverview, getPopularStocks } from '@/lib/api';
import AppLayout from '@/components/layout/AppLayout';
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

const SearchPage = () => {
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
    <AppLayout title="Stock Search" description="Search for stocks, analyze market data, and make informed decisions">
      <div className="space-y-6">
        {/* Search Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Search Stocks
            </CardTitle>
          </CardHeader>
          <CardContent>
            <SearchBar 
              placeholder="Search for stocks (e.g., RELIANCE, TCS, HDFC, AAPL)..."
              showInlineDetails={true}
              className="w-full"
            />
          </CardContent>
        </Card>

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
      </div>
    </AppLayout>
  );
};

export default SearchPage;