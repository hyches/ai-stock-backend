import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search as SearchIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { searchStocks } from '@/lib/api-services';

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
  pageContext?: 'home' | 'search' | 'dashboard' | 'header';
  onStockSelect?: (stock: StockDetails | null) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ 
  placeholder = "Search for stocks (e.g., RELIANCE, TCS, HDFC, AAPL)...",
  showInlineDetails = true,
  className = "",
  pageContext = 'header',
  onStockSelect
}) => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<StockSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
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
  const handleStockSelect = (stock: StockSuggestion) => {
    setSearchQuery(stock.symbol);
    setShowSuggestions(false);
    
    // Navigate to stock details page
    if (stock.symbol) {
      navigate(`/stock/${stock.symbol}`);
      // Call callback for backward compatibility (notify parent that selection happened)
      onStockSelect?.(null);
    }
  };

  // Handle search submission
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      const symbol = searchQuery.trim().toUpperCase();
      // Navigate to stock details page
      navigate(`/stock/${symbol}`);
      setShowSuggestions(false);
      // Call callback for backward compatibility (notify parent that selection happened)
      onStockSelect?.(null);
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

    </div>
  );
};

export default SearchBar;
