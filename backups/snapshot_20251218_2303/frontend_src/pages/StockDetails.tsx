
import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle,
  Bookmark,
  Share2
} from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  AreaChart,
  Area,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { useStockData } from '@/context/StockDataContext';

const StockDetails = () => {
  const navigate = useNavigate();
  const { symbol } = useParams<{ symbol: string }>();
  const [timeframe, setTimeframe] = useState('1Y');
  
  const { 
    stockDetails, 
    historicalData, 
    news, 
    recommendations,
    isLoading, 
    error
  } = useStockData();

  // Helper to format large numbers
  const formatNumber = (value: number | undefined) => {
    const num = value || 0;
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    return `$${num.toLocaleString()}`;
  };
  
  // Display loading skeletons
  if (isLoading) {
    return (
      <AppLayout>
        <div className="space-y-4">
          <Skeleton className="h-10 w-1/4" />
          <Skeleton className="h-24 w-full" />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Skeleton className="h-96 lg:col-span-2" />
            <Skeleton className="h-96" />
          </div>
        </div>
      </AppLayout>
    );
  }

  // Display error message
  if (error) {
    return (
      <AppLayout title="Stock Not Found">
        <div className="flex flex-col items-center justify-center text-center py-10">
          <AlertTriangle className="h-16 w-16 text-red-500 mb-4" />
          <h2 className="text-2xl font-bold mb-2">Error Fetching Stock Data</h2>
          <p className="text-muted-foreground mb-4">Could not retrieve data for symbol "{symbol}". Please try again later.</p>
          <Button onClick={() => navigate('/')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
        </div>
      </AppLayout>
    );
  }

  // Display message if no data is found after loading
  if (!stockDetails) {
    return (
      <AppLayout title="Stock Not Found">
        <div className="flex flex-col items-center justify-center text-center py-10">
          <AlertTriangle className="h-16 w-16 text-yellow-500 mb-4" />
          <h2 className="text-2xl font-bold mb-2">Stock Not Found</h2>
          <p className="text-muted-foreground mb-4">The stock with symbol "{symbol}" could not be found.</p>
           <Button onClick={() => navigate('/')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
        </div>
      </AppLayout>
    );
  }

  const price = stockDetails.dayHigh && stockDetails.dayLow ? (stockDetails.dayHigh + stockDetails.dayLow) / 2 : 0;
  const prevClose = historicalData?.[1]?.Close ?? price;
  const change = price - prevClose;
  const changePercent = prevClose ? (change / prevClose) * 100 : 0;

  return (
    <AppLayout title={`${stockDetails.symbol} - Stock Details`} description={`Detailed analysis for ${stockDetails.longName}`}>
      <div className="flex items-center justify-between mb-6">
        <Button variant="ghost" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm"><Bookmark className="h-4 w-4 mr-2" />Bookmark</Button>
            <Button variant="outline" size="sm"><Share2 className="h-4 w-4 mr-2" />Share</Button>
        </div>
      </div>

      <div className="space-y-8">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">{stockDetails.symbol}</h1>
                <p className="text-lg text-muted-foreground">{stockDetails.longName}</p>
                <div className="flex items-center space-x-2 mt-2">
                  <Badge variant="outline">{stockDetails.sector}</Badge>
                  <Badge variant="secondary">{stockDetails.industry}</Badge>
                </div>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold">{price.toFixed(2)}</div>
                <div className={`flex items-center justify-end space-x-2 ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {change >= 0 ? <TrendingUp /> : <TrendingDown />}
                  <span className="text-lg font-semibold">{change.toFixed(2)} ({changePercent.toFixed(2)}%)</span>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
              <div className="text-center"><div className="text-sm text-muted-foreground">Market Cap</div><div className="text-lg font-semibold">{formatNumber(stockDetails.marketCap)}</div></div>
              <div className="text-center"><div className="text-sm text-muted-foreground">P/E Ratio</div><div className="text-lg font-semibold">{(stockDetails.trailingPE || 0).toFixed(2)}</div></div>
              <div className="text-center"><div className="text-sm text-muted-foreground">Volume</div><div className="text-lg font-semibold">{formatNumber(stockDetails.volume)}</div></div>
              <div className="text-center"><div className="text-sm text-muted-foreground">52W High</div><div className="text-lg font-semibold">{(stockDetails.fiftyTwoWeekHigh || 0).toFixed(2)}</div></div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Price Chart ({timeframe})</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <AreaChart data={historicalData}>
                    <defs><linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/><stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/></linearGradient></defs>
                    <XAxis dataKey="Date" tickFormatter={(str) => new Date(str).toLocaleDateString() }/>
                    <YAxis domain={['dataMin', 'dataMax']} />
                    <Tooltip />
                    <CartesianGrid strokeDasharray="3 3" />
                    <Area type="monotone" dataKey="Close" stroke="#3B82F6" fill="url(#colorPrice)" />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
          <div className="space-y-6">
            <Card>
              <CardHeader><CardTitle>Company Info</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{stockDetails.longBusinessSummary?.slice(0, 280) ?? 'No summary available.'}...</p>
              </CardContent>
            </Card>
             <Card>
              <CardHeader><CardTitle>Analyst Recommendations</CardTitle></CardHeader>
              <CardContent>
                 {(recommendations || []).slice(0, 5).map((rec, i) => (
                    <div key={i} className="flex justify-between items-center mb-2">
                      <span className="text-sm">{rec.firm}</span>
                      <Badge variant={rec.toGrade?.toLowerCase().includes('buy') ? 'success' : 'secondary'}>{rec.toGrade}</Badge>
                    </div>
                 ))}
                 {(!recommendations || recommendations.length === 0) && <p className="text-sm text-muted-foreground">No recommendations found.</p>}
              </CardContent>
            </Card>
          </div>
        </div>
        
        <Tabs defaultValue="news">
          <TabsList><TabsTrigger value="news">Recent News</TabsTrigger></TabsList>
          <TabsContent value="news">
            <Card>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  {(news || []).map((item, index) => (
                    <div key={index} className="border-b pb-4 last:border-b-0">
                      <a href={item.link} target="_blank" rel="noopener noreferrer">
                        <h3 className="font-semibold hover:underline mb-1">{item.title}</h3>
                      </a>
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>{item.publisher}</span>
                        <span>{new Date((item.providerPublishTime || 0) * 1000).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                  {(!news || news.length === 0) && <p className="text-sm text-muted-foreground">No recent news found.</p>}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  );
};

export default StockDetails;
