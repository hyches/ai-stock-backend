import React, { useState, useEffect, useRef } from 'react';
import { Search as SearchIcon, X, TrendingUp, TrendingDown, DollarSign, BarChart3, Globe, Star, Plus, Minus, Heart } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { searchStocks, getStockDetails } from '@/lib/api';
import TradingActions from '@/components/TradingActions';

interface StockSuggestion {
  symbol: string;
  name: string;
  exchange: string;
  type: string;
}

interface StockDetails {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  pe: number;
  eps: number;
  dividend: number;
  dividendYield: number;
  high52Week: number;
  low52Week: number;
  avgVolume: number;
  beta: number;
  sector: string;
  industry: string;
  description: string;
  website: string;
  employees: number;
  founded: number;
  headquarters: string;
}

interface SearchBarProps {
  placeholder?: string;
  showInlineDetails?: boolean;
  className?: string;
}

const SearchBar: React.FC<SearchBarProps> = ({ 
  placeholder = "Search for stocks (e.g., RELIANCE, TCS, HDFC, AAPL)...",
  showInlineDetails = true,
  className = ""
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<StockSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedStock, setSelectedStock] = useState<StockDetails | null>(null);
  const [isLoadingStock, setIsLoadingStock] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

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
  const handleStockSelect = async (stock: StockSuggestion) => {
    setSearchQuery(stock.symbol);
    setShowSuggestions(false);
    
    if (showInlineDetails) {
      setIsLoadingStock(true);
      try {
        const stockData = await getStockDetails(stock.symbol);
        setSelectedStock(stockData);
      } catch (error) {
        console.error('Error fetching stock details:', error);
      } finally {
        setIsLoadingStock(false);
      }
    }
  };

  // Handle search submission
  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      if (showInlineDetails) {
        setIsLoadingStock(true);
        try {
          const stockData = await getStockDetails(searchQuery.trim().toUpperCase());
          setSelectedStock(stockData);
        } catch (error) {
          console.error('Error fetching stock details:', error);
        } finally {
          setIsLoadingStock(false);
        }
      }
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

  // Close stock details
  const handleCloseStockDetails = () => {
    setSelectedStock(null);
    setSearchQuery('');
  };

  return (
    <div className={`relative ${className}`} ref={searchRef}>
      {/* Search Input */}
      <form onSubmit={handleSearchSubmit} className="relative">
        <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
        <Input
          type="text"
          placeholder={placeholder}
          value={searchQuery}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="pl-10 pr-4"
        />
        <Button type="submit" size="sm" className="absolute right-1 top-1/2 transform -translate-y-1/2">
          Search
        </Button>
      </form>

      {/* Search Suggestions */}
      {showSuggestions && (
        <div className="absolute top-full left-0 right-0 z-50 mt-1 bg-background border border-border rounded-md shadow-lg max-h-60 overflow-y-auto">
          {isSearching ? (
            <div className="p-4 text-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto mb-2"></div>
              <span className="text-sm text-muted-foreground">Searching...</span>
            </div>
          ) : suggestions.length > 0 ? (
            <div className="py-1">
              {suggestions.map((stock, index) => (
                <div
                  key={index}
                  className="px-4 py-2 hover:bg-muted cursor-pointer flex items-center justify-between"
                  onClick={() => handleStockSelect(stock)}
                >
                  <div>
                    <div className="font-semibold text-foreground">{stock.symbol}</div>
                    <div className="text-sm text-muted-foreground">{stock.name}</div>
                  </div>
                  <div className="text-right">
                    <Badge variant="secondary" className="text-xs">{stock.exchange}</Badge>
                    <div className="text-xs text-muted-foreground mt-1">{stock.type}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : searchQuery.length >= 2 ? (
            <div className="p-4 text-center text-muted-foreground">
              No stocks found for "{searchQuery}"
            </div>
          ) : null}
        </div>
      )}

      {/* Inline Stock Details */}
      {showInlineDetails && selectedStock && (
        <div className="mt-4 space-y-4">
          {/* Stock Header */}
          <Card>
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-foreground">{selectedStock.symbol}</h3>
                  <p className="text-sm text-muted-foreground">{selectedStock.name}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="outline">{selectedStock.sector}</Badge>
                    <Badge variant="secondary">{selectedStock.industry}</Badge>
                  </div>
                </div>
                <Button variant="ghost" size="sm" onClick={handleCloseStockDetails}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Price Information */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">Current Price</div>
                  <div className="text-2xl font-bold">${selectedStock.price?.toFixed(2) || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Change</div>
                  <div className={`text-lg font-semibold ${(selectedStock.change || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {(selectedStock.change || 0) >= 0 ? '+' : ''}${selectedStock.change?.toFixed(2) || 'N/A'}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Change %</div>
                  <div className={`text-lg font-semibold ${(selectedStock.changePercent || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {(selectedStock.changePercent || 0) >= 0 ? '+' : ''}{selectedStock.changePercent?.toFixed(2) || 'N/A'}%
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Volume</div>
                  <div className="text-lg font-semibold">{selectedStock.volume?.toLocaleString() || 'N/A'}</div>
                </div>
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
                <div>
                  <div className="text-sm text-muted-foreground">Market Cap</div>
                  <div className="text-sm font-semibold">
                    {selectedStock.marketCap ? `$${(selectedStock.marketCap / 1e9).toFixed(2)}B` : 'N/A'}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">P/E Ratio</div>
                  <div className="text-sm font-semibold">{selectedStock.pe?.toFixed(2) || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">EPS</div>
                  <div className="text-sm font-semibold">${selectedStock.eps?.toFixed(2) || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Dividend Yield</div>
                  <div className="text-sm font-semibold">{selectedStock.dividendYield?.toFixed(2) || 'N/A'}%</div>
                </div>
              </div>

              {/* 52-Week Range */}
              <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                <div>
                  <div className="text-sm text-muted-foreground">52-Week High</div>
                  <div className="text-sm font-semibold">${selectedStock.high52Week?.toFixed(2) || 'N/A'}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">52-Week Low</div>
                  <div className="text-sm font-semibold">${selectedStock.low52Week?.toFixed(2) || 'N/A'}</div>
                </div>
              </div>

              {/* Company Description */}
              {selectedStock.description && (
                <div className="pt-4 border-t">
                  <div className="text-sm text-muted-foreground mb-2">Company Description</div>
                  <p className="text-sm text-foreground">{selectedStock.description}</p>
                </div>
              )}

              {/* Trading Actions */}
              <div className="pt-4 border-t">
                <TradingActions
                  symbol={selectedStock.symbol}
                  name={selectedStock.name}
                  currentPrice={selectedStock.price || 0}
                  change={selectedStock.change || 0}
                  changePercent={selectedStock.changePercent || 0}
                />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Loading State for Stock Details */}
      {showInlineDetails && isLoadingStock && (
        <div className="mt-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mr-3"></div>
                <span className="text-muted-foreground">Loading stock details...</span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default SearchBar;
