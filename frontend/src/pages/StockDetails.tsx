import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ArrowLeft, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  BarChart3, 
  Volume, 
  Calendar,
  Globe,
  Building,
  Users,
  Target,
  AlertTriangle,
  Star,
  Share2,
  Bookmark
} from 'lucide-react';
import TradingActions from '@/components/TradingActions';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { Progress } from '@/components/ui/progress';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar
} from 'recharts';
import { 
  getStockDetails, 
  getStockHistoricalData, 
  getStockNews, 
  getStockAnalysis,
  getStockFinancials,
  getStockPeers
} from '@/lib/api';

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

interface HistoricalData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface NewsItem {
  title: string;
  summary: string;
  source: string;
  publishedAt: string;
  url: string;
}

interface Analysis {
  buy: number;
  hold: number;
  sell: number;
  targetPrice: number;
  recommendation: string;
}

interface Financials {
  revenue: number;
  netIncome: number;
  assets: number;
  liabilities: number;
  equity: number;
  cash: number;
  debt: number;
}

interface Peer {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  marketCap: number;
}

const StockDetails = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const navigate = useNavigate();
  const [timeframe, setTimeframe] = useState('1Y');
  const [isBookmarked, setIsBookmarked] = useState(false);

  // Fetch stock details
  const { data: stockDetails, isLoading: detailsLoading, error: detailsError } = useQuery({
    queryKey: ['stock-details', symbol],
    queryFn: () => getStockDetails(symbol!),
    enabled: !!symbol,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Fetch historical data
  const { data: historicalData, isLoading: historicalLoading } = useQuery({
    queryKey: ['stock-historical', symbol, timeframe],
    queryFn: () => getStockHistoricalData(symbol!, timeframe),
    enabled: !!symbol,
  });

  // Fetch news
  const { data: news, isLoading: newsLoading } = useQuery({
    queryKey: ['stock-news', symbol],
    queryFn: () => getStockNews(symbol!),
    enabled: !!symbol,
  });

  // Fetch analysis
  const { data: analysis, isLoading: analysisLoading } = useQuery({
    queryKey: ['stock-analysis', symbol],
    queryFn: () => getStockAnalysis(symbol!),
    enabled: !!symbol,
  });

  // Fetch financials
  const { data: financials, isLoading: financialsLoading } = useQuery({
    queryKey: ['stock-financials', symbol],
    queryFn: () => getStockFinancials(symbol!),
    enabled: !!symbol,
  });

  // Fetch peers
  const { data: peers, isLoading: peersLoading } = useQuery({
    queryKey: ['stock-peers', symbol],
    queryFn: () => getStockPeers(symbol!),
    enabled: !!symbol,
  });

  // Format numbers
  const formatNumber = (value: number) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`;
    return `$${value.toFixed(2)}`;
  };

  const formatVolume = (value: number) => {
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
    return value.toString();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (detailsError) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Stock Not Found</h2>
          <p className="text-gray-600 mb-4">The stock symbol "{symbol}" could not be found.</p>
          <Button onClick={() => navigate('/')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Search
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" onClick={() => navigate('/')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div className="flex items-center space-x-2">
                <BarChart3 className="h-6 w-6 text-primary" />
                <span className="text-xl font-bold text-foreground">AlgoSentia</span>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <Bookmark className="h-4 w-4 mr-2" />
                {isBookmarked ? 'Bookmarked' : 'Bookmark'}
              </Button>
              <Button variant="outline" size="sm">
                <Share2 className="h-4 w-4 mr-2" />
                Share
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {detailsLoading ? (
          <div className="space-y-8">
            <div className="flex items-center space-x-4">
              <Skeleton className="h-8 w-32" />
              <Skeleton className="h-8 w-24" />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <Skeleton className="h-96 w-full" />
              </div>
              <div className="space-y-4">
                <Skeleton className="h-32 w-full" />
                <Skeleton className="h-32 w-full" />
                <Skeleton className="h-32 w-full" />
              </div>
            </div>
          </div>
        ) : stockDetails ? (
          <>
            {/* Stock Header */}
            <div className="bg-card rounded-lg shadow-sm border border-border p-6 mb-8">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h1 className="text-3xl font-bold text-foreground">{stockDetails.symbol}</h1>
                  <p className="text-lg text-muted-foreground">{stockDetails.name}</p>
                  <div className="flex items-center space-x-2 mt-2">
                    <Badge variant="outline">{stockDetails.sector}</Badge>
                    <Badge variant="secondary">{stockDetails.industry}</Badge>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-gray-900">
                    ${stockDetails.price.toFixed(2)}
                  </div>
                  <div className={`flex items-center space-x-2 ${
                    stockDetails.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {stockDetails.change >= 0 ? (
                      <TrendingUp className="h-5 w-5" />
                    ) : (
                      <TrendingDown className="h-5 w-5" />
                    )}
                    <span className="text-lg font-semibold">
                      {stockDetails.change >= 0 ? '+' : ''}{stockDetails.change.toFixed(2)}
                    </span>
                    <span className="text-lg">
                      ({stockDetails.changePercent >= 0 ? '+' : ''}{stockDetails.changePercent.toFixed(2)}%)
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Key Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
                <div className="text-center">
                  <div className="text-sm text-gray-600">Market Cap</div>
                  <div className="text-lg font-semibold">{formatNumber(stockDetails.marketCap)}</div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-600">P/E Ratio</div>
                  <div className="text-lg font-semibold">{stockDetails.pe.toFixed(2)}</div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-600">Volume</div>
                  <div className="text-lg font-semibold">{formatVolume(stockDetails.volume)}</div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-600">52W High</div>
                  <div className="text-lg font-semibold">${stockDetails.high52Week.toFixed(2)}</div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Main Chart */}
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>Price Chart</CardTitle>
                      <div className="flex space-x-2">
                        {['1D', '1W', '1M', '3M', '1Y', '5Y'].map((period) => (
                          <Button
                            key={period}
                            variant={timeframe === period ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setTimeframe(period)}
                          >
                            {period}
                          </Button>
                        ))}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {historicalLoading ? (
                      <Skeleton className="h-96 w-full" />
                    ) : historicalData ? (
                      <ResponsiveContainer width="100%" height={400}>
                        <AreaChart data={historicalData}>
                          <defs>
                            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
                            </linearGradient>
                          </defs>
                          <XAxis 
                            dataKey="date" 
                            tickFormatter={(value) => new Date(value).toLocaleDateString()}
                          />
                          <YAxis domain={['dataMin - 5', 'dataMax + 5']} />
                          <CartesianGrid strokeDasharray="3 3" />
                          <Tooltip 
                            labelFormatter={(value) => new Date(value).toLocaleDateString()}
                            formatter={(value) => [`$${value.toFixed(2)}`, 'Price']}
                          />
                          <Area 
                            type="monotone" 
                            dataKey="close" 
                            stroke="#3B82F6" 
                            fillOpacity={1} 
                            fill="url(#colorPrice)" 
                          />
                        </AreaChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="h-96 flex items-center justify-center text-gray-500">
                        No historical data available
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Sidebar */}
              <div className="space-y-6">
                {/* Analysis */}
                {analysis && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Target className="h-5 w-5" />
                        <span>Analyst Ratings</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div>
                          <div className="flex justify-between text-sm mb-2">
                            <span>Buy</span>
                            <span>{analysis.buy}%</span>
                          </div>
                          <Progress value={analysis.buy} className="h-2" />
                        </div>
                        <div>
                          <div className="flex justify-between text-sm mb-2">
                            <span>Hold</span>
                            <span>{analysis.hold}%</span>
                          </div>
                          <Progress value={analysis.hold} className="h-2" />
                        </div>
                        <div>
                          <div className="flex justify-between text-sm mb-2">
                            <span>Sell</span>
                            <span>{analysis.sell}%</span>
                          </div>
                          <Progress value={analysis.sell} className="h-2" />
                        </div>
                        <div className="pt-4 border-t border-gray-200">
                          <div className="text-sm text-gray-600">Target Price</div>
                          <div className="text-lg font-semibold">${analysis.targetPrice.toFixed(2)}</div>
                          <div className="text-sm text-gray-600">Recommendation: {analysis.recommendation}</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Trading Actions */}
                <TradingActions
                  symbol={stockDetails.symbol}
                  name={stockDetails.name}
                  currentPrice={stockDetails.price}
                  change={stockDetails.change}
                  changePercent={stockDetails.changePercent}
                />

                {/* Key Stats */}
                <Card>
                  <CardHeader>
                    <CardTitle>Key Statistics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">EPS</span>
                        <span className="font-semibold">${stockDetails.eps.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Dividend</span>
                        <span className="font-semibold">${stockDetails.dividend.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Dividend Yield</span>
                        <span className="font-semibold">{stockDetails.dividendYield.toFixed(2)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Beta</span>
                        <span className="font-semibold">{stockDetails.beta.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">52W Low</span>
                        <span className="font-semibold">${stockDetails.low52Week.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Avg Volume</span>
                        <span className="font-semibold">{formatVolume(stockDetails.avgVolume)}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Company Info */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Building className="h-5 w-5" />
                      <span>Company Info</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div>
                        <div className="text-sm text-gray-600">Description</div>
                        <div className="text-sm text-gray-900 mt-1">{stockDetails.description}</div>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Employees</span>
                        <span className="font-semibold">{stockDetails.employees.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Founded</span>
                        <span className="font-semibold">{stockDetails.founded}</span>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Headquarters</div>
                        <div className="text-sm font-semibold">{stockDetails.headquarters}</div>
                      </div>
                      {stockDetails.website && (
                        <div>
                          <div className="text-sm text-gray-600">Website</div>
                          <a 
                            href={stockDetails.website} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-sm text-blue-600 hover:underline"
                          >
                            {stockDetails.website}
                          </a>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* Tabs Section */}
            <div className="mt-8">
              <Tabs defaultValue="news" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="news">News</TabsTrigger>
                  <TabsTrigger value="financials">Financials</TabsTrigger>
                  <TabsTrigger value="peers">Peers</TabsTrigger>
                  <TabsTrigger value="analysis">Analysis</TabsTrigger>
                </TabsList>
                
                <TabsContent value="news" className="mt-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Latest News</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {newsLoading ? (
                        <div className="space-y-4">
                          {[...Array(3)].map((_, i) => (
                            <div key={i} className="border-b border-gray-200 pb-4">
                              <Skeleton className="h-4 w-3/4 mb-2" />
                              <Skeleton className="h-3 w-1/2" />
                            </div>
                          ))}
                        </div>
                      ) : news && news.length > 0 ? (
                        <div className="space-y-4">
                          {news.map((item, index) => (
                            <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0">
                              <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
                              <p className="text-sm text-gray-600 mb-2">{item.summary}</p>
                              <div className="flex items-center justify-between text-xs text-gray-500">
                                <span>{item.source}</span>
                                <span>{formatDate(item.publishedAt)}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center text-gray-500 py-8">
                          No news available
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="financials" className="mt-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Financial Data</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {financialsLoading ? (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          {[...Array(8)].map((_, i) => (
                            <div key={i} className="text-center">
                              <Skeleton className="h-4 w-20 mx-auto mb-2" />
                              <Skeleton className="h-6 w-16 mx-auto" />
                            </div>
                          ))}
                        </div>
                      ) : financials ? (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div className="text-center">
                            <div className="text-sm text-gray-600">Revenue</div>
                            <div className="text-lg font-semibold">{formatNumber(financials.revenue)}</div>
                          </div>
                          <div className="text-center">
                            <div className="text-sm text-gray-600">Net Income</div>
                            <div className="text-lg font-semibold">{formatNumber(financials.netIncome)}</div>
                          </div>
                          <div className="text-center">
                            <div className="text-sm text-gray-600">Assets</div>
                            <div className="text-lg font-semibold">{formatNumber(financials.assets)}</div>
                          </div>
                          <div className="text-center">
                            <div className="text-sm text-gray-600">Liabilities</div>
                            <div className="text-lg font-semibold">{formatNumber(financials.liabilities)}</div>
                          </div>
                          <div className="text-center">
                            <div className="text-sm text-gray-600">Equity</div>
                            <div className="text-lg font-semibold">{formatNumber(financials.equity)}</div>
                          </div>
                          <div className="text-center">
                            <div className="text-sm text-gray-600">Cash</div>
                            <div className="text-lg font-semibold">{formatNumber(financials.cash)}</div>
                          </div>
                          <div className="text-center">
                            <div className="text-sm text-gray-600">Debt</div>
                            <div className="text-lg font-semibold">{formatNumber(financials.debt)}</div>
                          </div>
                        </div>
                      ) : (
                        <div className="text-center text-gray-500 py-8">
                          No financial data available
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="peers" className="mt-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Peer Companies</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {peersLoading ? (
                        <div className="space-y-4">
                          {[...Array(5)].map((_, i) => (
                            <div key={i} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                              <Skeleton className="h-4 w-32" />
                              <Skeleton className="h-4 w-16" />
                            </div>
                          ))}
                        </div>
                      ) : peers && peers.length > 0 ? (
                        <div className="space-y-4">
                          {peers.map((peer, index) => (
                            <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
                              <div>
                                <div className="font-semibold text-gray-900">{peer.symbol}</div>
                                <div className="text-sm text-gray-600">{peer.name}</div>
                              </div>
                              <div className="text-right">
                                <div className="font-semibold text-gray-900">${peer.price.toFixed(2)}</div>
                                <div className={`text-sm ${
                                  peer.change >= 0 ? 'text-green-600' : 'text-red-600'
                                }`}>
                                  {peer.change >= 0 ? '+' : ''}{peer.change.toFixed(2)} ({peer.changePercent >= 0 ? '+' : ''}{peer.changePercent.toFixed(2)}%)
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center text-gray-500 py-8">
                          No peer companies available
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value="analysis" className="mt-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Technical Analysis</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center text-gray-500 py-8">
                        Technical analysis coming soon...
                      </div>
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            </div>
          </>
        ) : null}
      </main>
    </div>
  );
};

export default StockDetails;
