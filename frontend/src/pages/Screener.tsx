import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import AppLayout from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Download, Filter, TrendingUp, TrendingDown, RefreshCw, X } from 'lucide-react';
import { screenStocks, ScreenerCriteria, ScreenedStock } from '@/lib/api-services';
import { useToast } from '@/hooks/use-toast';

const sectors = [
  'All',
  'Technology',
  'Finance',
  'FMCG',
  'Energy',
  'Healthcare',
  'Auto'
];

const Screener = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [criteria, setCriteria] = useState<ScreenerCriteria>({});
  const [sortBy, setSortBy] = useState<string>('market_cap');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [showFilters, setShowFilters] = useState(true);

  // Build query key for React Query
  const queryKey = ['screener', criteria];

  // Screen stocks query
  const { data: stocks = [], isLoading, error, refetch } = useQuery<ScreenedStock[]>({
    queryKey,
    queryFn: () => screenStocks(criteria),
    enabled: false, // Don't auto-fetch on mount
    retry: 1,
  });

  const handleFilterChange = (key: keyof ScreenerCriteria, value: string | number | undefined) => {
    setCriteria(prev => ({
      ...prev,
      [key]: value === '' || value === undefined ? undefined : value
    }));
  };

  const handleApplyFilters = () => {
    refetch();
    toast({
      title: 'Screening stocks...',
      description: 'Fetching stocks that match your criteria',
    });
  };

  const handleClearFilters = () => {
    setCriteria({});
    toast({
      title: 'Filters cleared',
      description: 'All filters have been reset',
    });
  };

  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  const sortedStocks = [...stocks].sort((a, b) => {
    let aVal: any = a[sortBy as keyof ScreenedStock];
    let bVal: any = b[sortBy as keyof ScreenedStock];

    // Handle string comparisons for symbol and name
    if (sortBy === 'symbol' || sortBy === 'name') {
      if (sortOrder === 'asc') {
        return (aVal || '').localeCompare(bVal || '');
      } else {
        return (bVal || '').localeCompare(aVal || '');
      }
    }

    // Handle numeric comparisons
    if (aVal === null || aVal === undefined) aVal = 0;
    if (bVal === null || bVal === undefined) bVal = 0;

    if (sortOrder === 'asc') {
      return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
    } else {
      return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
    }
  });

  const formatCurrency = (value: number | undefined | null) => {
    if (value === null || value === undefined || isNaN(value)) return 'N/A';
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toFixed(2)}`;
  };

  const formatNumber = (value: number | undefined | null) => {
    if (value === null || value === undefined || isNaN(value)) return 'N/A';
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
    return value.toFixed(2);
  };

  const exportToCSV = () => {
    const headers = ['Symbol', 'Name', 'Sector', 'Price', 'Volume', 'Market Cap', 'P/E', 'Dividend Yield', 'MA 50', 'MA 200'];
    const rows = sortedStocks.map(stock => [
      stock.symbol || 'N/A',
      stock.name || 'N/A',
      stock.sector || 'N/A',
      stock.price ? stock.price.toFixed(2) : 'N/A',
      stock.volume ? formatNumber(stock.volume) : 'N/A',
      stock.market_cap ? formatCurrency(stock.market_cap) : 'N/A',
      stock.pe_ratio ? stock.pe_ratio.toFixed(2) : 'N/A',
      stock.dividend_yield ? stock.dividend_yield.toFixed(2) + '%' : 'N/A',
      stock.ma_50 ? stock.ma_50.toFixed(2) : 'N/A',
      stock.ma_200 ? stock.ma_200.toFixed(2) : 'N/A',
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `stock_screener_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);

    toast({
      title: 'Export successful',
      description: 'Stock screener results exported to CSV',
    });
  };

  return (
    <AppLayout title="Stock Screener" description="Find stocks based on custom criteria and filters">
      <div className="space-y-6">
        {/* Filters Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Filter className="h-5 w-5" />
                  Screening Criteria
                </CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  Set your criteria to find matching stocks
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
              >
                {showFilters ? 'Hide' : 'Show'} Filters
              </Button>
            </div>
          </CardHeader>
          {showFilters && (
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {/* Sector */}
                <div className="space-y-2">
                  <Label htmlFor="sector">Sector</Label>
                  <Select
                    value={criteria.sector || 'All'}
                    onValueChange={(value) => handleFilterChange('sector', value === 'All' ? undefined : value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select Sector" />
                    </SelectTrigger>
                    <SelectContent>
                      {sectors.map(sector => (
                        <SelectItem key={sector} value={sector}>{sector}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Min Market Cap */}
                <div className="space-y-2">
                  <Label htmlFor="minMarketCap">Min Market Cap (Millions $)</Label>
                  <Input
                    id="minMarketCap"
                    type="number"
                    placeholder="e.g., 1000"
                    value={criteria.min_market_cap || ''}
                    onChange={(e) => handleFilterChange('min_market_cap', e.target.value ? parseFloat(e.target.value) : undefined)}
                  />
                </div>

                {/* Min Price */}
                <div className="space-y-2">
                  <Label htmlFor="minPrice">Min Price ($)</Label>
                  <Input
                    id="minPrice"
                    type="number"
                    placeholder="e.g., 10"
                    value={criteria.min_price || ''}
                    onChange={(e) => handleFilterChange('min_price', e.target.value ? parseFloat(e.target.value) : undefined)}
                  />
                </div>

                {/* Max Price */}
                <div className="space-y-2">
                  <Label htmlFor="maxPrice">Max Price ($)</Label>
                  <Input
                    id="maxPrice"
                    type="number"
                    placeholder="e.g., 500"
                    value={criteria.max_price || ''}
                    onChange={(e) => handleFilterChange('max_price', e.target.value ? parseFloat(e.target.value) : undefined)}
                  />
                </div>

                {/* Max P/E Ratio */}
                <div className="space-y-2">
                  <Label htmlFor="maxPE">Max P/E Ratio</Label>
                  <Input
                    id="maxPE"
                    type="number"
                    placeholder="e.g., 30"
                    value={criteria.max_pe || ''}
                    onChange={(e) => handleFilterChange('max_pe', e.target.value ? parseFloat(e.target.value) : undefined)}
                  />
                </div>

                {/* Min Volume */}
                <div className="space-y-2">
                  <Label htmlFor="minVolume">Min Volume</Label>
                  <Input
                    id="minVolume"
                    type="number"
                    placeholder="e.g., 1000000"
                    value={criteria.min_volume || ''}
                    onChange={(e) => handleFilterChange('min_volume', e.target.value ? parseFloat(e.target.value) : undefined)}
                  />
                </div>

                {/* Min Dividend Yield */}
                <div className="space-y-2">
                  <Label htmlFor="minDividendYield">Min Dividend Yield (%)</Label>
                  <Input
                    id="minDividendYield"
                    type="number"
                    step="0.1"
                    placeholder="e.g., 2.5"
                    value={criteria.min_dividend_yield || ''}
                    onChange={(e) => handleFilterChange('min_dividend_yield', e.target.value ? parseFloat(e.target.value) : undefined)}
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button onClick={handleApplyFilters} className="flex-1">
                  <Filter className="mr-2 h-4 w-4" />
                  Apply Filters
                </Button>
                <Button variant="outline" onClick={handleClearFilters}>
                  <X className="mr-2 h-4 w-4" />
                  Clear All
                </Button>
              </div>
            </CardContent>
          )}
        </Card>

        {/* Results Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Results</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  {isLoading ? 'Loading...' : `${sortedStocks.length} stocks found`}
                </p>
              </div>
              <div className="flex gap-2">
                {sortedStocks.length > 0 && (
                  <Button variant="outline" size="sm" onClick={exportToCSV}>
                    <Download className="mr-2 h-4 w-4" />
                    Export CSV
                  </Button>
                )}
                <Button variant="outline" size="sm" onClick={() => refetch()}>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Refresh
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {error && (
              <div className="text-center py-12 text-destructive">
                <p className="font-semibold">Error loading stocks</p>
                <p className="text-sm text-muted-foreground mt-1">
                  {error instanceof Error ? error.message : 'Failed to fetch stocks'}
                </p>
                <Button variant="outline" className="mt-4" onClick={() => refetch()}>
                  Try Again
                </Button>
              </div>
            )}

            {isLoading && (
              <div className="space-y-3">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="flex gap-4">
                    <Skeleton className="h-12 flex-1" />
                    <Skeleton className="h-12 w-32" />
                    <Skeleton className="h-12 w-32" />
                  </div>
                ))}
              </div>
            )}

            {!isLoading && !error && sortedStocks.length === 0 && (
              <div className="text-center py-12">
                <Filter className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                <p className="text-lg font-semibold">No stocks found</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Try adjusting your filters or apply filters to search for stocks
                </p>
              </div>
            )}

            {!isLoading && !error && sortedStocks.length > 0 && (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead 
                        className="cursor-pointer hover:bg-muted"
                        onClick={() => handleSort('symbol')}
                      >
                        Symbol {sortBy === 'symbol' && (sortOrder === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-muted"
                        onClick={() => handleSort('name')}
                      >
                        Name {sortBy === 'name' && (sortOrder === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead>Sector</TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-muted"
                        onClick={() => handleSort('price')}
                      >
                        Price {sortBy === 'price' && (sortOrder === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-muted"
                        onClick={() => handleSort('volume')}
                      >
                        Volume {sortBy === 'volume' && (sortOrder === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-muted"
                        onClick={() => handleSort('market_cap')}
                      >
                        Market Cap {sortBy === 'market_cap' && (sortOrder === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead 
                        className="cursor-pointer hover:bg-muted"
                        onClick={() => handleSort('pe_ratio')}
                      >
                        P/E {sortBy === 'pe_ratio' && (sortOrder === 'asc' ? '↑' : '↓')}
                      </TableHead>
                      <TableHead>Div. Yield</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sortedStocks.map((stock, index) => (
                      <TableRow key={index} className="hover:bg-muted/50">
                        <TableCell className="font-medium">
                          <button
                            onClick={() => navigate(`/stock/${stock.symbol}`)}
                            className="text-primary hover:underline"
                          >
                            {stock.symbol}
                          </button>
                        </TableCell>
                        <TableCell className="max-w-[200px] truncate">{stock.name}</TableCell>
                        <TableCell>
                          <Badge variant="secondary">{stock.sector}</Badge>
                        </TableCell>
                        <TableCell className="font-semibold">
                          {stock.price ? `$${stock.price.toFixed(2)}` : <span className="text-muted-foreground">N/A</span>}
                        </TableCell>
                        <TableCell>{formatNumber(stock.volume)}</TableCell>
                        <TableCell>{formatCurrency(stock.market_cap)}</TableCell>
                        <TableCell>
                          {stock.pe_ratio ? stock.pe_ratio.toFixed(2) : <span className="text-muted-foreground">N/A</span>}
                        </TableCell>
                        <TableCell>
                          {stock.dividend_yield ? (
                            <span className="flex items-center gap-1">
                              {stock.dividend_yield.toFixed(2)}%
                            </span>
                          ) : (
                            <span className="text-muted-foreground">N/A</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => navigate(`/stock/${stock.symbol}`)}
                          >
                            View Details
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
};

export default Screener;
