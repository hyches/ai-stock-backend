
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
import TradeDialog from '@/components/TradeDialog';

const StockDetails = () => {
  const navigate = useNavigate();
  const { symbol } = useParams<{ symbol: string }>();
  const [timeframe, setTimeframe] = useState('1Y');

  // Trade Dialog State
  const [isTradeOpen, setTradeOpen] = useState(false);
  const [tradeSide, setTradeSide] = useState<'buy' | 'sell'>('buy');

  const {
    stockDetails,
    historicalData,
    news,
    recommendations,
    technicals,
    financials,
    isLoading,
    isAnalyzing,
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

  const handleTrade = (side: 'buy' | 'sell') => {
    setTradeSide(side);
    setTradeOpen(true);
  };

  // Display loading skeletons ONLY for initial load (Quote)
  if (isLoading) {
    return (
      <AppLayout title="Loading...">
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

  const price = stockDetails.currentPrice || (stockDetails.dayHigh && stockDetails.dayLow ? (stockDetails.dayHigh + stockDetails.dayLow) / 2 : 0);
  const prevClose = stockDetails.previousClose || (historicalData?.[1]?.Close ?? price);
  const change = price - prevClose;
  const changePercent = prevClose ? (change / prevClose) * 100 : 0;

  return (
    <AppLayout title={`${stockDetails.symbol} - Stock Details`} description={`Detailed analysis for ${stockDetails.longName || symbol}`}>
      {/* Header Actions */}
      <div className="flex items-center justify-between mb-6">
        <Button variant="ghost" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <div className="flex items-center space-x-2">
          {/* Watchlist Toggle - Simplified for now */}
          <Button variant="outline" size="sm" onClick={() => {
            // Add simple watchlist logic or emit event
            const event = new CustomEvent('add-watchlist', { detail: stockDetails });
            window.dispatchEvent(event);
          }}>
            <Bookmark className="h-4 w-4 mr-2" />Watchlist
          </Button>
          <Button variant="outline" size="sm"><Share2 className="h-4 w-4 mr-2" />Share</Button>
        </div>
      </div>

      <div className="space-y-8">
        {/* MAIN PRICE CARD */}
        <Card className="border-l-4 border-l-primary">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-3">
                  <h1 className="text-4xl font-bold">{stockDetails.symbol}</h1>
                  {isAnalyzing && <Badge variant="outline" className="animate-pulse">Analyzing...</Badge>}
                </div>
                <p className="text-lg text-muted-foreground">{stockDetails.longName}</p>
                <div className="flex items-center space-x-2 mt-2">
                  <Badge variant="outline">{stockDetails.sector || '—'}</Badge>
                  <Badge variant="secondary">{stockDetails.industry || '—'}</Badge>
                </div>
              </div>
              <div className="text-right">
                <div className="text-4xl font-bold font-mono">{price.toFixed(2)}</div>
                <div className={`flex items-center justify-end space-x-2 ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {change >= 0 ? <TrendingUp className="h-5 w-5" /> : <TrendingDown className="h-5 w-5" />}
                  <span className="text-xl font-semibold">{change > 0 ? '+' : ''}{change.toFixed(2)} ({changePercent.toFixed(2)}%)</span>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {/* Action Buttons */}
            <div className="flex gap-4 pt-4 border-t mb-6">
              <Button className="w-32 bg-green-600 hover:bg-green-700" onClick={() => handleTrade('buy')}>Buy</Button>
              <Button className="w-32" variant="destructive" onClick={() => handleTrade('sell')}>Sell</Button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-muted/20 rounded-lg">
              <div className="text-center"><div className="text-sm text-muted-foreground">Market Cap</div><div className="text-lg font-semibold">{formatNumber(stockDetails.marketCap)}</div></div>
              <div className="text-center"><div className="text-sm text-muted-foreground">P/E Ratio</div><div className="text-lg font-semibold">{(stockDetails.trailingPE || stockDetails.pe_ratio || 0).toFixed(2)}</div></div>
              <div className="text-center"><div className="text-sm text-muted-foreground">Volume</div><div className="text-lg font-semibold">{formatNumber(stockDetails.volume)}</div></div>
              <div className="text-center"><div className="text-sm text-muted-foreground">52W High</div><div className="text-lg font-semibold">{(stockDetails.fiftyTwoWeekHigh || 0).toFixed(2)}</div></div>
            </div>
          </CardContent>
        </Card>

        {/* TABS FOR DEEP DIVE */}
        <Tabs defaultValue="chart" className="w-full">
          <TabsList className="w-full justify-start overflow-x-auto">
            <TabsTrigger value="chart">Chart</TabsTrigger>
            <TabsTrigger value="research">Research & ML</TabsTrigger>
            <TabsTrigger value="technicals">Technicals</TabsTrigger>
            <TabsTrigger value="financials">Financials</TabsTrigger>
            <TabsTrigger value="news">News</TabsTrigger>
          </TabsList>

          {/* TAB: CHART */}
          <TabsContent value="chart">
            <Card>
              <CardHeader>
                <CardTitle>Price Chart ({timeframe})</CardTitle>
              </CardHeader>
              <CardContent>
                {isAnalyzing && !historicalData ? (
                  <Skeleton className="h-[400px] w-full" />
                ) : (
                  <ResponsiveContainer width="100%" height={400}>
                    <AreaChart data={historicalData}>
                      <defs><linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8} /><stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1} /></linearGradient></defs>
                      <XAxis dataKey="Date" tickFormatter={(str) => new Date(str).toLocaleDateString()} />
                      <YAxis domain={['auto', 'auto']} />
                      <Tooltip />
                      <CartesianGrid strokeDasharray="3 3" />
                      <Area type="monotone" dataKey="Close" stroke="#3B82F6" fill="url(#colorPrice)" />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* TAB: RESEARCH & ML */}
          {/* TAB: RESEARCH & ML */}
          <TabsContent value="research">
            {isAnalyzing ? <Skeleton className="h-96 w-full" /> : (
              <div className="grid grid-cols-1 gap-6">
                <Card>
                  <CardHeader><CardTitle>AI ML Insights</CardTitle></CardHeader>
                  <CardContent>
                    {stockDetails?.ml_predictions ? (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="p-4 border rounded bg-secondary/10 flex flex-col items-center justify-center">
                          <h4 className="text-sm uppercase text-muted-foreground mb-2">Signal</h4>
                          <div className={`text-3xl font-black ${stockDetails.ml_predictions.signal === 'BUY' ? 'text-green-500' : (stockDetails.ml_predictions.signal === 'SELL' ? 'text-red-500' : 'text-yellow-500')}`}>
                            {stockDetails.ml_predictions.signal}
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            Confidence: {Math.round((stockDetails.ml_predictions.confidence || 0) * 100)}%
                          </div>
                        </div>
                        <div className="col-span-2 p-4 border rounded">
                          <h4 className="font-semibold mb-2">Price Prediction (1 Week)</h4>
                          <div className="flex items-end gap-2">
                            <span className="text-2xl font-bold">${stockDetails.ml_predictions.predicted_price_1week?.toFixed(2) || '—'}</span>
                            <span className={`text-sm mb-1 ${stockDetails.ml_predictions.predicted_return_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {stockDetails.ml_predictions.predicted_return_pct >= 0 ? '+' : ''}{stockDetails.ml_predictions.predicted_return_pct?.toFixed(2)}%
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-2">
                            AI-generated forecast based on standard ML models. Not financial advice.
                          </p>
                        </div>
                      </div>
                    ) : (
                      <div className="p-8 text-center text-muted-foreground">
                        <p>ML models are training. Insights will appear here shortly.</p>
                        <Button variant="outline" size="sm" className="mt-4">Train Model Now</Button>
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader><CardTitle>Analyst Recommendations</CardTitle></CardHeader>
                  <CardContent>
                    {(recommendations || []).slice(0, 5).map((rec: any, i: number) => (
                      <div key={i} className="flex justify-between items-center mb-2 p-2 border-b last:border-0 hover:bg-muted/50">
                        <span className="text-sm font-medium">{rec.firm}</span>
                        <Badge variant={rec.toGrade?.toLowerCase().includes('buy') ? 'success' : 'secondary'}>{rec.toGrade}</Badge>
                      </div>
                    ))}
                    {(!recommendations || recommendations.length === 0) && <p className="text-sm text-muted-foreground">No recommendations found.</p>}
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          {/* TAB: TECHNICALS */}
          <TabsContent value="technicals">
            {isAnalyzing && !technicals ? <Skeleton className="h-96 w-full" /> : (
              <Card>
                <CardHeader><CardTitle>Technical Indicators</CardTitle></CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-4 border rounded">
                      <div className="text-sm text-muted-foreground">RSI (14)</div>
                      <div className="text-2xl font-bold">{technicals?.rsi_14?.toFixed(2) || '—'}</div>
                      <div className="text-xs text-muted-foreground">{technicals?.rsi_14 > 70 ? 'Overbought' : technicals?.rsi_14 < 30 ? 'Oversold' : 'Neutral'}</div>
                    </div>
                    <div className="p-4 border rounded">
                      <div className="text-sm text-muted-foreground">SMA 50</div>
                      <div className="text-2xl font-bold">{technicals?.sma_50?.toFixed(2) || '—'}</div>
                    </div>
                    <div className="p-4 border rounded">
                      <div className="text-sm text-muted-foreground">SMA 200</div>
                      <div className="text-2xl font-bold">{technicals?.sma_200?.toFixed(2) || '—'}</div>
                    </div>
                    <div className="p-4 border rounded">
                      <div className="text-sm text-muted-foreground">Trend</div>
                      <div className="text-2xl font-bold text-green-500">Bullish</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* TAB: FINANCIALS */}
          <TabsContent value="financials">
            {isAnalyzing && !financials ? <Skeleton className="h-96 w-full" /> : (
              <Card>
                <CardHeader><CardTitle>Key Financials</CardTitle></CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex justify-between border-b py-2"><span>Revenue</span> <span className="font-mono">{formatNumber(financials?.revenue)}</span></div>
                    <div className="flex justify-between border-b py-2"><span>Net Income</span> <span className="font-mono">{formatNumber(financials?.net_income)}</span></div>
                    <div className="flex justify-between border-b py-2"><span>EPS</span> <span className="font-mono">{financials?.earnings_per_share?.toFixed(2) || '—'}</span></div>
                    <div className="flex justify-between border-b py-2"><span>ROE</span> <span className="font-mono">{(financials?.roe * 100)?.toFixed(2) || '—'}%</span></div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* TAB: NEWS */}
          <TabsContent value="news">
            {isAnalyzing && !news ? <Skeleton className="h-96 w-full" /> : (
              <Card>
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    {(news || []).map((item: any, index: number) => (
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
            )}
          </TabsContent>
        </Tabs>
      </div>

      <TradeDialog
        isOpen={isTradeOpen}
        onClose={() => setTradeOpen(false)}
        symbol={symbol || ''}
        currentPrice={price}
        side={tradeSide}
      />
    </AppLayout >
  );
};

export default StockDetails;
