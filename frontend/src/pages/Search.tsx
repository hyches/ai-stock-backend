import React, { useState, useEffect, useRef } from 'react';
import { Search, TrendingUp, TrendingDown, DollarSign, BarChart3, Globe, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { searchStocks, getMarketOverview, getPopularStocks } from '@/lib/api-services';
import AppLayout from '@/components/layout/AppLayout';

interface StockSuggestion {
  symbol: string;
  name: string;
  exchange: string;
  type: string;
}

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

const Search = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<StockSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
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

  // Handle search input
  const handleSearchChange = async (value: string) => {
    setSearchQuery(value);
    
    if (value.length >= 2) {
      setIsSearching(true);
      try {
        const results = await searchStocks(value);
        setSuggestions(results);
        setShowSuggestions(true);
      } catch (error) {
        console.error('Search error:', error);
        setSuggestions([]);
      } finally {
        setIsSearching(false);
      }
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  // Handle stock selection
  const handleStockSelect = (stock: StockSuggestion) => {
    setSearchQuery(stock.symbol);
    setShowSuggestions(false);
    navigate(`/stock/${stock.symbol}`);
  };

  // Handle search submission
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/stock/${searchQuery.trim().toUpperCase()}`);
    }
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Format market cap
  const formatMarketCap = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toLocaleString()}`;
  };

  // Format volume
  const formatVolume = (value: number) => {
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
    return value.toLocaleString();
  };

  return (
    <AppLayout title="Stock Search" description="Search for stocks, analyze market data, and make informed decisions">
      <div className="space-y-8">
        {/* Search Section */}
        <div className="max-w-2xl mx-auto mb-12">
          <div className="relative" ref={searchRef}>
            <form onSubmit={handleSearchSubmit} className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-5 w-5" />
              <Input
                type="text"
                placeholder="Search for stocks (e.g., AAPL, Microsoft, Tesla)..."
                value={searchQuery}
                onChange={(e) => handleSearchChange(e.target.value)}
                className="pl-10 pr-4 py-3 text-lg h-14 border-2 focus:border-primary"
              />
              <Button
                type="submit"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 h-10 px-6"
              >
                Search
              </Button>
            </form>

            {/* Search Suggestions */}
            {showSuggestions && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-card border border-border rounded-lg shadow-lg z-50 max-h-80 overflow-y-auto">
                {isSearching ? (
                  <div className="p-4 text-center text-muted-foreground">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto mb-2"></div>
                    Searching...
                  </div>
                ) : suggestions.length > 0 ? (
                  suggestions.map((stock, index) => (
                    <div
                      key={index}
                      className="p-3 hover:bg-muted cursor-pointer border-b border-border last:border-b-0"
                      onClick={() => handleStockSelect(stock)}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-foreground">{stock.symbol}</div>
                          <div className="text-sm text-muted-foreground">{stock.name}</div>
                        </div>
                        <div className="text-right">
                          <Badge variant="secondary" className="text-xs">
                            {stock.exchange}
                          </Badge>
                          <div className="text-xs text-muted-foreground mt-1">
                            {stock.type}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : searchQuery.length >= 2 ? (
                  <div className="p-4 text-center text-muted-foreground">
                    No stocks found for "{searchQuery}"
                  </div>
                ) : null}
              </div>
            )}
          </div>
        </div>

        {/* Market Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Market Cap</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {marketLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : marketError ? (
                <div className="text-sm text-muted-foreground">Error loading data</div>
              ) : (
                <div className="text-2xl font-bold">
                  {marketOverview ? formatMarketCap(marketOverview.totalMarketCap) : 'N/A'}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Volume</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {marketLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : marketError ? (
                <div className="text-sm text-muted-foreground">Error loading data</div>
              ) : (
                <div className="text-2xl font-bold">
                  {marketOverview ? formatVolume(marketOverview.totalVolume) : 'N/A'}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Gainers</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              {marketLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : marketError ? (
                <div className="text-sm text-muted-foreground">Error loading data</div>
              ) : (
                <div className="text-2xl font-bold text-green-500">
                  {marketOverview ? marketOverview.gainers.toLocaleString() : 'N/A'}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Losers</CardTitle>
              <TrendingDown className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              {marketLoading ? (
                <Skeleton className="h-8 w-24" />
              ) : marketError ? (
                <div className="text-sm text-muted-foreground">Error loading data</div>
              ) : (
                <div className="text-2xl font-bold text-red-500">
                  {marketOverview ? marketOverview.losers.toLocaleString() : 'N/A'}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Popular Stocks */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-foreground mb-6">Popular Stocks</h2>
          {popularLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[...Array(6)].map((_, i) => (
                <Card key={i}>
                  <CardContent className="p-4">
                    <Skeleton className="h-4 w-20 mb-2" />
                    <Skeleton className="h-6 w-16 mb-2" />
                    <Skeleton className="h-4 w-24" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : popularError ? (
            <div className="text-center text-muted-foreground py-8">
              Error loading popular stocks
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {popularStocks?.map((stock, index) => (
                <Card key={index} className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => navigate(`/stock/${stock.symbol}`)}>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-foreground">{stock.symbol}</h3>
                      <Star className="h-4 w-4 text-yellow-500" />
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{stock.name}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-lg font-bold text-foreground">
                        ${stock.price.toFixed(2)}
                      </span>
                      <div className="text-right">
                        <div className={`text-sm font-medium ${stock.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}
                        </div>
                        <div className={`text-xs ${stock.changePercent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="text-center">
          <h2 className="text-2xl font-bold text-foreground mb-6">Quick Actions</h2>
          <div className="flex flex-wrap justify-center gap-4">
            <Button variant="outline" onClick={() => navigate('/dashboard')}>
              <BarChart3 className="h-4 w-4 mr-2" />
              View Dashboard
            </Button>
            <Button variant="outline" onClick={() => navigate('/screener')}>
              <Globe className="h-4 w-4 mr-2" />
              Stock Screener
            </Button>
            <Button variant="outline" onClick={() => navigate('/research')}>
              <TrendingUp className="h-4 w-4 mr-2" />
              Research Tools
            </Button>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default Search;
