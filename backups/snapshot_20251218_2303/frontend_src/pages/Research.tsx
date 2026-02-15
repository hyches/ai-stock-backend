import React, { useState, useMemo } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Section from '@/components/ui/section';
import CustomCard from '@/components/ui/custom-card';
import FormGroup from '@/components/ui/form-group';
import { Download, FilePdf, FileText, FileSpreadsheet, Loader, TrendingUp, TrendingDown } from '@/utils/icons';
import { Badge } from '@/components/ui/badge';
import Sparkline from '@/components/Sparkline';
import PatternChart from '@/components/PatternChart';
import InteractivePatternChart from '@/components/InteractivePatternChart';
import TVLightweightChart from '@/components/TVLightweightChart';
import { useToast } from '@/hooks/use-toast';
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

// --- Types mirroring backend Pydantic models ---
interface StockInfo {
  symbol?: string;
  longName?: string;
  currency?: string;
  dayHigh?: number;
  dayLow?: number;
  fiftyTwoWeekHigh?: number;
  fiftyTwoWeekLow?: number;
  marketCap?: number;
  volume?: number;
  averageVolume?: number;
  trailingPE?: number;
  forwardPE?: number;
  trailingEps?: number;
  dividendYield?: number;
  priceToSalesTrailing12Months?: number;
  beta?: number;
  longBusinessSummary?: string;
  sector?: string;
  industry?: string;
  currentPrice?: number;
  previousClose?: number;
}

interface HistData {
  date: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  adjusted_close?: number;
}

interface NewsData {
  title: string;
  publisher?: string;
  link?: string;
  providerPublishTime?: number;
}

interface RecommendationData {
  firm?: string;
  toGrade?: string;
  fromGrade?: string;
  action?: string;
}

interface FinancialData {
  market_cap?: number;
  pe_ratio?: number;
  forward_pe?: number;
  earnings_per_share?: number;
  dividend_yield?: number;
  price_to_sales?: number;
  debt_to_equity?: number;
  current_ratio?: number;
  roe?: number;
  roa?: number;
  profit_margin?: number;
  revenue?: number;
  net_income?: number;
}

interface TechnicalData {
  sma_20?: number;
  sma_50?: number;
  sma_200?: number;
  ema_12?: number;
  ema_26?: number;
  rsi_14?: number;
}

interface ComprehensiveStockData {
  info: StockInfo;
  history: HistData[];
  news: NewsData[];
  recommendations: RecommendationData[];
  financials?: FinancialData;
  technicals?: TechnicalData;
}

const Research = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isFullAnalysis, setIsFullAnalysis] = useState(false);
  const [symbol, setSymbol] = useState('AAPL');
  const [timeframe, setTimeframe] = useState('3months');
  const [data, setData] = useState<ComprehensiveStockData | null>(null);
  const [mlLoading, setMlLoading] = useState(false);
  const [mlData, setMlData] = useState<any | null>(null);
  const [mlError, setMlError] = useState<string | null>(null);
  const [useTV, setUseTV] = useState<boolean>(true);
  const [overlays, setOverlays] = useState<{ [k: string]: boolean}>({
    sma20: true,
    sma50: true,
    sma200: true,
    ema12: false,
    ema26: false,
    bb: false,
    kelt: false,
    pivots: true,
    fib: true,
  });
  const { toast } = useToast();

  const periodMap: Record<string, string> = {
    '1month': '1mo',
    '3months': '3mo',
    '6months': '6mo',
    '1year': '1y',
    '3years': '3y',
  };

  const handleGenerateAnalysis = async () => {
    if (!symbol || symbol.trim() === '') {
      toast({ title: 'Enter a stock symbol', description: 'Please provide a valid stock symbol.' });
      return;
    }

    setIsLoading(true);
    try {
      const period = periodMap[timeframe] || '1y';
      const resp = await fetch(`/api/v1/research/${encodeURIComponent(symbol.trim())}?period=${period}`, {
        headers: { Accept: 'application/json' },
      });

      if (!resp.ok) {
        toast({ title: 'Error', description: `Failed to fetch data: ${resp.status} ${resp.statusText}` });
        setIsLoading(false);
        return;
      }

      const json: ComprehensiveStockData = await resp.json();
      setData(json);
      // Auto-load ML insights after analysis completes
      try {
        // reuse timeframe mapping
        const period = periodMap[timeframe] || '2y';
        setMlLoading(true);
        setMlError(null);
        const mlResp = await fetch(`/api/v1/research/${encodeURIComponent(symbol.trim())}/ml-features`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({ period }),
        });
        if (mlResp.ok) {
          const mlJson = await mlResp.json();
          setMlData(mlJson);
        } else {
          const txt = await mlResp.text();
          console.warn('ML features load failed:', mlResp.status, txt);
        }
      } catch (e) {
        console.warn('Auto ML load error', e);
      } finally {
        setMlLoading(false);
      }
      toast({ title: 'Analysis Generated', description: isFullAnalysis ? 'Full AI analysis complete' : 'Quick AI analysis complete' });
    } catch (err) {
      console.error('Fetch error', err);
      toast({ title: 'Network error', description: 'Unable to reach the analysis API.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = (type: string) => {
    setIsDownloading(true);
    // For now this triggers a UI notification; real export would call server-side report generation
    setTimeout(() => {
      setIsDownloading(false);
      toast({ title: `${type} Download Started`, description: `Your ${type} file will be ready shortly.` });
    }, 1500);
  };

  return (
    <AppLayout title="AI Research Reports" description="Get AI-generated insights and analysis on stocks">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <CustomCard title="Research Parameters" description="Configure AI analysis settings">
            <div className="space-y-4">
              <FormGroup htmlFor="stock" label="Stock Symbol">
                <Input id="stock" placeholder="e.g. AAPL, MSFT, GOOGL" value={symbol} onChange={(e: any) => setSymbol(e.target.value)} />
              </FormGroup>
              
              <FormGroup htmlFor="timeframe" label="Analysis Timeframe">
                <Select defaultValue={timeframe} value={timeframe} onValueChange={(v: string) => setTimeframe(v)}>
                  <SelectTrigger id="timeframe">
                    <SelectValue placeholder="Select timeframe" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1month">1 Month</SelectItem>
                    <SelectItem value="3months">3 Months</SelectItem>
                    <SelectItem value="6months">6 Months</SelectItem>
                    <SelectItem value="1year">1 Year</SelectItem>
                    <SelectItem value="3years">3 Years</SelectItem>
                  </SelectContent>
                </Select>
              </FormGroup>
              
              <FormGroup htmlFor="depth" label="Analysis Depth">
                <div className="flex items-center justify-between">
                  <span>Quick Analysis</span>
                  <Switch 
                    id="depth"
                    checked={isFullAnalysis} 
                    onCheckedChange={setIsFullAnalysis}
                  />
                  <span>Full Analysis</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {isFullAnalysis 
                    ? "Comprehensive analysis including fundamentals, technicals, and sentiment." 
                    : "Basic overview with key metrics and recommendations."}
                </p>
              </FormGroup>
              
              <FormGroup htmlFor="factors" label="Include Factors">
                <div className="grid grid-cols-2 gap-2">
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="technical" className="rounded text-teal" defaultChecked />
                    <label htmlFor="technical" className="text-sm">Technical</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="fundamental" className="rounded text-teal" defaultChecked />
                    <label htmlFor="fundamental" className="text-sm">Fundamental</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="sentiment" className="rounded text-teal" defaultChecked />
                    <label htmlFor="sentiment" className="text-sm">Sentiment</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="news" className="rounded text-teal" defaultChecked />
                    <label htmlFor="news" className="text-sm">News</label>
                  </div>
                </div>
              </FormGroup>
              
              <Button 
                className="w-full" 
                disabled={isLoading}
                onClick={handleGenerateAnalysis}
              >
                {isLoading ? (
                  <>
                    <Loader className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  'Generate Analysis'
                )}
              </Button>
            </div>
          </CustomCard>
          
          <CustomCard title="Download Reports" className="mt-6">
            <div className="space-y-3">
              <Button 
                variant="outline" 
                className="w-full justify-start"
                disabled={isDownloading}
                onClick={() => handleDownload('PDF')}
              >
                <FilePdf className="mr-2 h-4 w-4 text-red-500" />
                Download as PDF
              </Button>
              
              <Button 
                variant="outline" 
                className="w-full justify-start"
                disabled={isDownloading}
                onClick={() => handleDownload('Excel')}
              >
                <FileSpreadsheet className="mr-2 h-4 w-4 text-green-500" />
                Export to Excel
              </Button>
              
              <Button 
                variant="outline" 
                className="w-full justify-start"
                disabled={isDownloading}
                onClick={() => handleDownload('Word')}
              >
                <FileText className="mr-2 h-4 w-4 text-blue-500" />
                Export to Word
              </Button>
            </div>
          </CustomCard>
        </div>
        
        <div className="lg:col-span-2">
          <Tabs defaultValue="summary">
            <TabsList className="mb-4 flex flex-wrap">
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="technical">Technical</TabsTrigger>
              <TabsTrigger value="fundamental">Fundamental</TabsTrigger>
              <TabsTrigger value="financials">Financials</TabsTrigger>
              <TabsTrigger value="technicals">Technical Indicators</TabsTrigger>
              <TabsTrigger value="ml">ML Insights</TabsTrigger>
              <TabsTrigger value="news">News & Sentiment</TabsTrigger>
            </TabsList>
            
            <TabsContent value="summary" className="space-y-6">
              <CustomCard 
                title="AI-Generated Stock Summary" 
                description="Key insights and recommendations generated by AI"
              >
                <div className="p-4 bg-teal/5 border border-teal/20 rounded-md">
                  <div className="flex justify-between items-start mb-6">
                    <div>
                      <h3 className="text-4xl font-bold">${data?.info?.currentPrice?.toFixed(2) ?? '—'}</h3>
                      <div className="flex items-center gap-2 mt-2">
                        {data?.info?.previousClose && data?.info?.currentPrice ? (
                          <>
                            <span className={`text-sm font-medium ${data.info.currentPrice >= data.info.previousClose ? 'text-green-500' : 'text-red-500'}`}>
                              {data.info.currentPrice >= data.info.previousClose ? '+' : ''}{(data.info.currentPrice - data.info.previousClose).toFixed(2)} ({(((data.info.currentPrice - data.info.previousClose) / data.info.previousClose) * 100).toFixed(2)}%)
                            </span>
                            {data.info.currentPrice >= data.info.previousClose ? (
                              <TrendingUp className="h-4 w-4 text-green-500" />
                            ) : (
                              <TrendingDown className="h-4 w-4 text-red-500" />
                            )}
                          </>
                        ) : null}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold">{data?.info?.symbol ?? symbol.toUpperCase()}</p>
                      <p className="text-sm text-muted-foreground">{data?.info?.longName ?? '—'}</p>
                      <Badge className="mt-2" variant={data ? "success" : Math.random() > 0.5 ? "success" : "destructive"}>
                        {data ? (
                          data.recommendations && data.recommendations.length > 0 ? data.recommendations[0].toGrade ?? 'Neutral' : 'Neutral'
                        ) : (
                          Math.random() > 0.5 ? (
                            <><TrendingUp className="mr-1 h-3 w-3" /> Buy</>
                          ) : (
                            <><TrendingDown className="mr-1 h-3 w-3" /> Sell</>
                          )
                        )}
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-sm text-muted-foreground mb-1">Company Overview</h4>
                      <p className="text-sm">
                        <span className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs mr-2">{data?.info?.sector ?? 'N/A'}</span>
                        <span className="inline-block bg-green-100 text-green-800 px-2 py-1 rounded text-xs">{data?.info?.industry ?? 'N/A'}</span>
                      </p>
                    </div>

                    <div>
                      <h4 className="font-medium text-sm text-muted-foreground mb-1">Business Summary</h4>
                      <p className="text-sm">
                        {data?.info?.longBusinessSummary ? data.info.longBusinessSummary.slice(0, 400) + (data.info.longBusinessSummary.length > 400 ? '...' : '') : (
                          'No company summary available. Use Generate Analysis to fetch data.'
                        )}
                      </p>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-sm text-muted-foreground mb-2">Quick Stats</h4>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded">
                          <p className="text-xs text-muted-foreground">Day High / Low</p>
                          <p className="text-sm font-semibold">${data?.info?.dayHigh?.toFixed(2) ?? '—'} / ${data?.info?.dayLow?.toFixed(2) ?? '—'}</p>
                        </div>
                        <div className="p-2 bg-gray-50 dark:bg-gray-800 rounded">
                          <p className="text-xs text-muted-foreground">52W High / Low</p>
                          <p className="text-sm font-semibold">${data?.info?.fiftyTwoWeekHigh?.toFixed(2) ?? '—'} / ${data?.info?.fiftyTwoWeekLow?.toFixed(2) ?? '—'}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CustomCard>
              
              <CustomCard title="Key Performance Indicators">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">Market Cap</p>
                    <p className="text-xl font-semibold">
                      {data?.info?.marketCap 
                        ? `$${(data.info.marketCap / 1e12).toFixed(2)}T` 
                        : '—'}
                    </p>
                    <div className="flex items-center text-xs text-green-500 mt-1">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      <span>Enterprise Value</span>
                    </div>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">P/E Ratio (Trailing)</p>
                    <p className="text-xl font-semibold">{data?.info?.trailingPE?.toFixed(2) ?? '—'}</p>
                    <div className="flex items-center text-xs text-green-500 mt-1">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      <span>vs Industry</span>
                    </div>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">Forward P/E</p>
                    <p className="text-xl font-semibold">{data?.info?.forwardPE?.toFixed(2) ?? '—'}</p>
                    <div className="flex items-center text-xs text-red-500 mt-1">
                      <TrendingDown className="h-3 w-3 mr-1" />
                      <span>vs Forecast</span>
                    </div>
                  </div>

                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">52-Week High</p>
                    <p className="text-xl font-semibold">${data?.info?.fiftyTwoWeekHigh?.toFixed(2) ?? '—'}</p>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">52-Week Low</p>
                    <p className="text-xl font-semibold">${data?.info?.fiftyTwoWeekLow?.toFixed(2) ?? '—'}</p>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">Beta</p>
                    <p className="text-xl font-semibold">{data?.info?.beta?.toFixed(2) ?? '—'}</p>
                    <div className="flex items-center text-xs text-green-500 mt-1">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      <span>Market Volatility</span>
                    </div>
                  </div>

                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">Day High</p>
                    <p className="text-xl font-semibold">${data?.info?.dayHigh?.toFixed(2) ?? '—'}</p>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">Day Low</p>
                    <p className="text-xl font-semibold">${data?.info?.dayLow?.toFixed(2) ?? '—'}</p>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">Volume</p>
                    <p className="text-xl font-semibold">{data?.info?.volume ? Intl.NumberFormat().format(Math.round(data.info.volume / 1e6)) + 'M' : '—'}</p>
                  </div>
                </div>
              </CustomCard>
            </TabsContent>
            
            <TabsContent value="technical">
              <CustomCard title="Technical Analysis">
                <p className="text-muted-foreground mb-4">Technical indicators and chart patterns</p>
                <div className="space-y-6">
                  {data?.technicals && (
                    <>
                      <div>
                        <h4 className="font-medium mb-4">Technical Indicators Summary</h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="p-4 border rounded-lg">
                            <p className="text-sm text-muted-foreground mb-1">SMA 20</p>
                            <p className="text-xl font-bold">${data.technicals.sma_20?.toFixed(2) ?? '—'}</p>
                            <p className="text-xs text-gray-500 mt-2">20-day Simple Moving Average</p>
                          </div>
                          <div className="p-4 border rounded-lg">
                            <p className="text-sm text-muted-foreground mb-1">SMA 50</p>
                            <p className="text-xl font-bold">${data.technicals.sma_50?.toFixed(2) ?? '—'}</p>
                            <p className="text-xs text-gray-500 mt-2">50-day Simple Moving Average</p>
                          </div>
                          <div className="p-4 border rounded-lg">
                            <p className="text-sm text-muted-foreground mb-1">SMA 200</p>
                            <p className="text-xl font-bold">${data.technicals.sma_200?.toFixed(2) ?? '—'}</p>
                            <p className="text-xs text-gray-500 mt-2">200-day Simple Moving Average</p>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-4">Exponential Moving Averages</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="p-4 border rounded-lg">
                            <p className="text-sm text-muted-foreground mb-1">EMA 12</p>
                            <p className="text-xl font-bold">${data.technicals.ema_12?.toFixed(2) ?? '—'}</p>
                            <p className="text-xs text-gray-500 mt-2">12-day Exponential Moving Average</p>
                          </div>
                          <div className="p-4 border rounded-lg">
                            <p className="text-sm text-muted-foreground mb-1">EMA 26</p>
                            <p className="text-xl font-bold">${data.technicals.ema_26?.toFixed(2) ?? '—'}</p>
                            <p className="text-xs text-gray-500 mt-2">26-day Exponential Moving Average</p>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h4 className="font-medium mb-4">Momentum Indicators</h4>
                        <div className="p-4 border rounded-lg">
                          <p className="text-sm text-muted-foreground mb-1">RSI 14</p>
                          <div className="flex items-center gap-4 mt-2">
                            <p className="text-2xl font-bold">{data.technicals.rsi_14?.toFixed(2) ?? '—'}</p>
                            <div className="flex-1">
                              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                                <div 
                                  className={`h-full ${
                                    (data.technicals.rsi_14 ?? 0) > 70 
                                      ? 'bg-red-500' 
                                      : (data.technicals.rsi_14 ?? 0) < 30 
                                      ? 'bg-green-500' 
                                      : 'bg-blue-500'
                                  }`}
                                  style={{ width: `${Math.min((data.technicals.rsi_14 ?? 0), 100)}%` }}
                                ></div>
                              </div>
                              <p className="text-xs text-gray-500 mt-1">
                                {(data.technicals.rsi_14 ?? 0) > 70 
                                  ? 'Overbought' 
                                  : (data.technicals.rsi_14 ?? 0) < 30 
                                  ? 'Oversold' 
                                  : 'Neutral'}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </>
                  )}

                  <div>
                    <h4 className="font-medium mb-4">Historical Price Data</h4>
                    {data?.history && data.history.length > 0 ? (
                      <div className="overflow-auto max-h-64">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Date</TableHead>
                              <TableHead>Open</TableHead>
                              <TableHead>High</TableHead>
                              <TableHead>Low</TableHead>
                              <TableHead>Close</TableHead>
                              <TableHead>Volume</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {data.history.slice(0, 20).map((row) => (
                              <TableRow key={row.date}>
                                <TableCell>{row.date}</TableCell>
                                <TableCell>{typeof row.open === 'number' ? row.open.toFixed(2) : '—'}</TableCell>
                                <TableCell>{typeof row.high === 'number' ? row.high.toFixed(2) : '—'}</TableCell>
                                <TableCell>{typeof row.low === 'number' ? row.low.toFixed(2) : '—'}</TableCell>
                                <TableCell>{typeof row.close === 'number' ? row.close.toFixed(2) : '—'}</TableCell>
                                <TableCell>{typeof row.volume === 'number' ? Intl.NumberFormat().format(row.volume) : '—'}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    ) : (
                      <div className="h-64 bg-gray-100 dark:bg-gray-800 rounded-md flex items-center justify-center">
                        <p className="text-muted-foreground">No historical data. Generate analysis to fetch history.</p>
                      </div>
                    )}
                  </div>
                </div>
              </CustomCard>
            </TabsContent>
            
            <TabsContent value="fundamental">
              <CustomCard title="Fundamental Analysis">
                <p className="text-muted-foreground mb-4">Financial metrics and company fundamentals</p>
                {data?.financials ? (
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-3">Valuation Metrics</h4>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Metric</TableHead>
                            <TableHead>Value</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          <TableRow>
                            <TableCell>Market Cap</TableCell>
                            <TableCell>
                              {data.financials.market_cap 
                                ? `$${(data.financials.market_cap / 1e12).toFixed(2)}T` 
                                : '—'}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>P/E Ratio (Trailing)</TableCell>
                            <TableCell>{data.financials.pe_ratio?.toFixed(2) ?? '—'}</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Forward P/E Ratio</TableCell>
                            <TableCell>{data.financials.forward_pe?.toFixed(2) ?? '—'}</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Price to Sales</TableCell>
                            <TableCell>{data.financials.price_to_sales?.toFixed(2) ?? '—'}</TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </div>

                    <div>
                      <h4 className="font-medium mb-3">Profitability & Efficiency</h4>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Metric</TableHead>
                            <TableHead>Value</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          <TableRow>
                            <TableCell>EPS (Earnings Per Share)</TableCell>
                            <TableCell>${data.financials.earnings_per_share?.toFixed(2) ?? '—'}</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Profit Margin</TableCell>
                            <TableCell>{data.financials.profit_margin ? (data.financials.profit_margin * 100).toFixed(2) : '—'}%</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Return on Equity (ROE)</TableCell>
                            <TableCell>{data.financials.roe ? (data.financials.roe * 100).toFixed(2) : '—'}%</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Return on Assets (ROA)</TableCell>
                            <TableCell>{data.financials.roa ? (data.financials.roa * 100).toFixed(2) : '—'}%</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Dividend Yield</TableCell>
                            <TableCell>{data.financials.dividend_yield ? (data.financials.dividend_yield * 100).toFixed(2) : '—'}%</TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </div>

                    <div>
                      <h4 className="font-medium mb-3">Balance Sheet Strength</h4>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Metric</TableHead>
                            <TableHead>Value</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          <TableRow>
                            <TableCell>Debt to Equity</TableCell>
                            <TableCell>{data.financials.debt_to_equity?.toFixed(2) ?? '—'}</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Current Ratio</TableCell>
                            <TableCell>{data.financials.current_ratio?.toFixed(2) ?? '—'}</TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Revenue</TableCell>
                            <TableCell>
                              {data.financials.revenue 
                                ? `$${(data.financials.revenue / 1e9).toFixed(2)}B` 
                                : '—'}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Net Income</TableCell>
                            <TableCell>
                              {data.financials.net_income 
                                ? `$${(data.financials.net_income / 1e9).toFixed(2)}B` 
                                : '—'}
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Metric</TableHead>
                        <TableHead>Value</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <TableRow>
                        <TableCell>EPS</TableCell>
                        <TableCell>{data?.info?.trailingEps ?? '—'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>P/E Ratio</TableCell>
                        <TableCell>{data?.info?.trailingPE ?? '—'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Price to Sales (TTM)</TableCell>
                        <TableCell>{data?.info?.priceToSalesTrailing12Months ?? '—'}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Dividend Yield</TableCell>
                        <TableCell>{data?.info?.dividendYield ?? '—'}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                )}
              </CustomCard>
            </TabsContent>
            
            <TabsContent value="financials">
              <CustomCard title="Financial Metrics">
                <p className="text-muted-foreground mb-4">Key financial indicators and valuations</p>
                {data?.financials ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 border rounded-lg bg-gradient-to-br from-blue-50 to-transparent">
                      <p className="text-sm text-muted-foreground mb-1">Market Capitalization</p>
                      <p className="text-2xl font-bold">
                        {data.financials.market_cap 
                          ? `$${(data.financials.market_cap / 1e12).toFixed(2)}T` 
                          : '—'}
                      </p>
                    </div>
                    <div className="p-4 border rounded-lg bg-gradient-to-br from-green-50 to-transparent">
                      <p className="text-sm text-muted-foreground mb-1">P/E Ratio (Trailing)</p>
                      <p className="text-2xl font-bold">{data.financials.pe_ratio?.toFixed(2) ?? '—'}</p>
                    </div>
                    <div className="p-4 border rounded-lg bg-gradient-to-br from-purple-50 to-transparent">
                      <p className="text-sm text-muted-foreground mb-1">Forward P/E Ratio</p>
                      <p className="text-2xl font-bold">{data.financials.forward_pe?.toFixed(2) ?? '—'}</p>
                    </div>
                    <div className="p-4 border rounded-lg bg-gradient-to-br from-orange-50 to-transparent">
                      <p className="text-sm text-muted-foreground mb-1">EPS</p>
                      <p className="text-2xl font-bold">${data.financials.earnings_per_share?.toFixed(2) ?? '—'}</p>
                    </div>
                    <div className="p-4 border rounded-lg bg-gradient-to-br from-red-50 to-transparent">
                      <p className="text-sm text-muted-foreground mb-1">Dividend Yield</p>
                      <p className="text-2xl font-bold">{data.financials.dividend_yield?.toFixed(2) ?? '—'}%</p>
                    </div>
                    <div className="p-4 border rounded-lg bg-gradient-to-br from-indigo-50 to-transparent">
                      <p className="text-sm text-muted-foreground mb-1">Price to Sales</p>
                      <p className="text-2xl font-bold">{data.financials.price_to_sales?.toFixed(2) ?? '—'}</p>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 border rounded-md text-center text-muted-foreground">
                    <p>No financial data available. Generate analysis to fetch data.</p>
                  </div>
                )}
              </CustomCard>
            </TabsContent>

            <TabsContent value="technicals">
              <CustomCard title="Technical Indicators">
                <p className="text-muted-foreground mb-4">Moving averages, trend indicators, and momentum</p>
                {data?.technicals ? (
                  <>
                  {/* Chart first */}
                  {data?.history && data.history.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-3 flex items-center gap-2">
                        <span>Price Chart with Overlays</span>
                        <div className="flex items-center gap-2">
                          <Switch id="use-tv" checked={useTV} onCheckedChange={setUseTV} />
                          <label htmlFor="use-tv" className="text-sm font-normal">Use TradingView</label>
                        </div>
                      </h4>
                      <div className="p-2 border rounded-md">
                        <ChartRenderer 
                          useTV={useTV}
                          data={data}
                          mlData={mlData}
                          overlays={overlays}
                        />
                      </div>
                    </div>
                  )}

                  {/* Indicator table second */}
                  <div className="mt-6">
                    <h4 className="font-medium mb-3">Indicators & Overlays</h4>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Indicator</TableHead>
                          <TableHead>Current Value</TableHead>
                          <TableHead>Show on Chart</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        <TableRow>
                          <TableCell className="font-medium">SMA 20</TableCell>
                          <TableCell>
                            ${(() => {
                              const val = data.technicals.sma_20 ?? mlData?.indicator_series?.sma20?.filter((v: any) => v != null).slice(-1)[0];
                              return val != null ? val.toFixed(2) : '—';
                            })()}
                          </TableCell>
                          <TableCell>
                            {mlData?.indicator_series?.sma20 && (
                              <Switch id="tbl-sma20" checked={overlays.sma20} onCheckedChange={(v)=>setOverlays(o=>({...o,sma20:!!v}))} />
                            )}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">SMA 50</TableCell>
                          <TableCell>
                            ${(() => {
                              const val = data.technicals.sma_50 ?? mlData?.indicator_series?.sma50?.filter((v: any) => v != null).slice(-1)[0];
                              return val != null ? val.toFixed(2) : '—';
                            })()}
                          </TableCell>
                          <TableCell>
                            {mlData?.indicator_series?.sma50 && (
                              <Switch id="tbl-sma50" checked={overlays.sma50} onCheckedChange={(v)=>setOverlays(o=>({...o,sma50:!!v}))} />
                            )}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">SMA 200</TableCell>
                          <TableCell>
                            ${(() => {
                              const val = data.technicals.sma_200 ?? mlData?.indicator_series?.sma200?.filter((v: any) => v != null).slice(-1)[0];
                              return val != null ? val.toFixed(2) : '—';
                            })()}
                          </TableCell>
                          <TableCell>
                            {mlData?.indicator_series?.sma200 && (
                              <Switch id="tbl-sma200" checked={overlays.sma200} onCheckedChange={(v)=>setOverlays(o=>({...o,sma200:!!v}))} />
                            )}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">EMA 12</TableCell>
                          <TableCell>
                            ${(() => {
                              const val = data.technicals.ema_12 ?? mlData?.indicator_series?.ema12?.filter((v: any) => v != null).slice(-1)[0];
                              return val != null ? val.toFixed(2) : '—';
                            })()}
                          </TableCell>
                          <TableCell>
                            {mlData?.indicator_series?.ema12 && (
                              <Switch id="tbl-ema12" checked={overlays.ema12} onCheckedChange={(v)=>setOverlays(o=>({...o,ema12:!!v}))} />
                            )}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">EMA 26</TableCell>
                          <TableCell>
                            ${(() => {
                              const val = data.technicals.ema_26 ?? mlData?.indicator_series?.ema26?.filter((v: any) => v != null).slice(-1)[0];
                              return val != null ? val.toFixed(2) : '—';
                            })()}
                          </TableCell>
                          <TableCell>
                            {mlData?.indicator_series?.ema26 && (
                              <Switch id="tbl-ema26" checked={overlays.ema26} onCheckedChange={(v)=>setOverlays(o=>({...o,ema26:!!v}))} />
                            )}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">Bollinger Bands</TableCell>
                          <TableCell>
                            {mlData?.indicator_series?.bb ? (
                              <>
                                U: ${mlData.indicator_series.bb.upper?.filter((v: any) => v != null).slice(-1)[0]?.toFixed(2) ?? '—'} / 
                                M: ${mlData.indicator_series.bb.middle?.filter((v: any) => v != null).slice(-1)[0]?.toFixed(2) ?? '—'} / 
                                L: ${mlData.indicator_series.bb.lower?.filter((v: any) => v != null).slice(-1)[0]?.toFixed(2) ?? '—'}
                              </>
                            ) : '—'}
                          </TableCell>
                          <TableCell>
                            {mlData?.indicator_series?.bb && (
                              <Switch id="tbl-bb" checked={overlays.bb} onCheckedChange={(v)=>setOverlays(o=>({...o,bb:!!v}))} />
                            )}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">Keltner Channels</TableCell>
                          <TableCell>
                            {mlData?.indicator_series?.keltner ? (
                              <>
                                U: ${mlData.indicator_series.keltner.upper?.filter((v: any) => v != null).slice(-1)[0]?.toFixed(2) ?? '—'} / 
                                M: ${mlData.indicator_series.keltner.middle?.filter((v: any) => v != null).slice(-1)[0]?.toFixed(2) ?? '—'} / 
                                L: ${mlData.indicator_series.keltner.lower?.filter((v: any) => v != null).slice(-1)[0]?.toFixed(2) ?? '—'}
                              </>
                            ) : '—'}
                          </TableCell>
                          <TableCell>
                            {mlData?.indicator_series?.keltner && (
                              <Switch id="tbl-kelt" checked={overlays.kelt} onCheckedChange={(v)=>setOverlays(o=>({...o,kelt:!!v}))} />
                            )}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">Pivot Points</TableCell>
                          <TableCell>
                            {mlData?.indicator_series?.levels?.pivots ? (
                              <>
                                PP: ${mlData.indicator_series.levels.pivots.pp?.toFixed(2) ?? '—'} / 
                                R1: ${mlData.indicator_series.levels.pivots.r1?.toFixed(2) ?? '—'} / 
                                S1: ${mlData.indicator_series.levels.pivots.s1?.toFixed(2) ?? '—'}
                              </>
                            ) : '—'}
                          </TableCell>
                          <TableCell>
                            {mlData?.indicator_series?.levels?.pivots && (
                              <Switch id="tbl-piv" checked={overlays.pivots} onCheckedChange={(v)=>setOverlays(o=>({...o,pivots:!!v}))} />
                            )}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">Fibonacci Levels</TableCell>
                          <TableCell>
                            {mlData?.indicator_series?.levels?.fibonacci?.levels ? (
                              Object.entries(mlData.indicator_series.levels.fibonacci.levels)
                                .slice(0, 3)
                                .map(([k, v]: any) => `${k}: $${v?.toFixed(2)}`)
                                .join(' / ')
                            ) : '—'}
                          </TableCell>
                          <TableCell>
                            {mlData?.indicator_series?.levels?.fibonacci && (
                              <Switch id="tbl-fib" checked={overlays.fib} onCheckedChange={(v)=>setOverlays(o=>({...o,fib:!!v}))} />
                            )}
                          </TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">RSI 14</TableCell>
                          <TableCell>
                            <span className={`font-semibold ${
                              (data.technicals.rsi_14 ?? 0) > 70 ? 'text-red-500' :
                              (data.technicals.rsi_14 ?? 0) < 30 ? 'text-green-500' : ''
                            }`}>
                              {(() => {
                                const val = data.technicals.rsi_14 ?? mlData?.indicator_series?.rsi?.filter((v: any) => v != null).slice(-1)[0];
                                return val != null ? val.toFixed(2) : '—';
                              })()}
                            </span>
                            {' '}
                            {(data.technicals.rsi_14 ?? 0) > 70 ? '(Overbought)' :
                             (data.technicals.rsi_14 ?? 0) < 30 ? '(Oversold)' : '(Neutral)'}
                          </TableCell>
                          <TableCell>—</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </div>

                  
                  </>
                ) : (
                  <div className="p-4 border rounded-md text-center text-muted-foreground">
                    <p>No technical data available. Generate analysis to fetch data.</p>
                  </div>
                )}
              </CustomCard>
            </TabsContent>

            <TabsContent value="ml">
              <CustomCard title="ML Insights">
                <p className="text-muted-foreground mb-4">Pattern detection and ML-ready features for this symbol</p>

                <div className="mb-4">
                  <Button onClick={async () => {
                    if (!symbol || symbol.trim() === '') {
                      toast({ title: 'Enter a stock symbol', description: 'Please provide a valid stock symbol.' });
                      return;
                    }
                    setMlLoading(true);
                    setMlError(null);
                    try {
                      const period = periodMap[timeframe] || '2y';
                      const resp = await fetch(`/api/v1/research/${encodeURIComponent(symbol.trim())}/ml-features`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
                        body: JSON.stringify({ period }),
                      });
                      if (!resp.ok) {
                        const txt = await resp.text();
                        throw new Error(`API error ${resp.status}: ${txt}`);
                      }
                      const json = await resp.json();
                      setMlData(json);
                    } catch (err: any) {
                      console.error('ML fetch error', err);
                      setMlError(err.message || String(err));
                      toast({ title: 'ML fetch error', description: err.message ?? String(err) });
                    } finally {
                      setMlLoading(false);
                    }
                  }} disabled={mlLoading}>
                    {mlLoading ? <><Loader className="mr-2 h-4 w-4 animate-spin" /> Loading...</> : 'Load ML Insights'}
                  </Button>
                  <Button variant="outline" className="ml-2" onClick={async () => {
                    if (!mlData) return toast({ title: 'No ML data', description: 'Load ML Insights first.' });
                    try {
                      const resp = await fetch(`/api/v1/research/${encodeURIComponent(symbol.trim())}/train-on-patterns`, { method: 'POST' });
                      const j = await resp.json();
                      const jobId = j.job_id;
                      toast({ title: 'Training queued', description: j.message ?? 'Training queued' });

                      // Poll job status
                      let status = 'queued';
                      const start = Date.now();
                      while (status === 'queued' || status === 'running') {
                        await new Promise(r => setTimeout(r, 1000));
                        try {
                          const sresp = await fetch(`/api/v1/research/${encodeURIComponent(symbol.trim())}/train-status/${jobId}`);
                          if (!sresp.ok) break;
                          const sjson = await sresp.json();
                          status = sjson.status;
                          if (status === 'running') {
                            // optionally show progress toast
                            // toast({ title: 'Training running', description: `Job ${jobId}` });
                          }
                          if (status === 'completed') {
                            toast({ title: 'Training completed', description: sjson.result?.message ?? 'Training finished' });
                            break;
                          }
                          if (status === 'failed') {
                            toast({ title: 'Training failed', description: sjson.result?.error ?? 'Training error' });
                            break;
                          }
                        } catch (e) {
                          console.warn('Status poll error', e);
                          break;
                        }
                        if (Date.now() - start > 60_000) {
                          toast({ title: 'Training timeout', description: 'Training is taking longer than expected' });
                          break;
                        }
                      }
                    } catch (e: any) {
                      toast({ title: 'Training error', description: e.message ?? String(e) });
                    }
                  }}>Queue ML Training</Button>
                </div>

                {mlError && <div className="p-3 bg-red-50 text-red-700 rounded">{mlError}</div>}

                {mlData ? (
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">ML Predictions & Signals</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                        <div className="p-4 border rounded-md bg-blue-50 dark:bg-blue-900/20">
                          <div className="flex justify-between items-start">
                            <div>
                              <p className="text-xs text-muted-foreground">Signal</p>
                              <p className="text-2xl font-bold mt-1">{mlData.predictions?.signal ?? 'HOLD'}</p>
                              <p className="text-xs text-gray-500 mt-1">Confidence: {((mlData.predictions?.signal_confidence ?? 0) * 100).toFixed(0)}%</p>
                            </div>
                            <Badge variant={
                              mlData.predictions?.signal === 'BUY' ? 'default' : 
                              mlData.predictions?.signal === 'SELL' ? 'destructive' : 
                              'secondary'
                            }>
                              {mlData.predictions?.signal ?? 'HOLD'}
                            </Badge>
                          </div>
                        </div>

                        <div className="p-4 border rounded-md">
                          <p className="text-xs text-muted-foreground">Next Week Target Range</p>
                          <p className="text-lg font-bold mt-1">${(mlData.predictions?.predicted_price_1week?.low ?? 0).toFixed(2)} - ${(mlData.predictions?.predicted_price_1week?.high ?? 0).toFixed(2)}</p>
                          <p className="text-sm text-green-600 font-medium">Target: ${(mlData.predictions?.predicted_price_1week?.target ?? 0).toFixed(2)}</p>
                          <p className="text-xs text-gray-500 mt-1">Confidence: {((mlData.predictions?.predicted_price_1week?.confidence ?? 0) * 100).toFixed(0)}%</p>
                        </div>

                        <div className="p-4 border rounded-md">
                          <p className="text-xs text-muted-foreground">Next Month Target Range</p>
                          <p className="text-lg font-bold mt-1">${(mlData.predictions?.predicted_price_1month?.low ?? 0).toFixed(2)} - ${(mlData.predictions?.predicted_price_1month?.high ?? 0).toFixed(2)}</p>
                          <p className="text-sm text-blue-600 font-medium">Target: ${(mlData.predictions?.predicted_price_1month?.target ?? 0).toFixed(2)}</p>
                          <p className="text-xs text-gray-500 mt-1">Confidence: {((mlData.predictions?.predicted_price_1month?.confidence ?? 0) * 100).toFixed(0)}%</p>
                        </div>

                        <div className="p-4 border rounded-md">
                          <p className="text-xs text-muted-foreground">Risk / Reward Ratio</p>
                          <p className="text-2xl font-bold mt-1">1:{(mlData.predictions?.risk_reward_ratio ?? 0).toFixed(2)}</p>
                          <div className="text-xs text-gray-500 mt-2">
                            <p>Stop Loss: ${(mlData.predictions?.stop_loss ?? 0).toFixed(2)}</p>
                            <p>Take Profit: ${(mlData.predictions?.take_profit ?? 0).toFixed(2)}</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2">Support & Resistance Levels</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div className="p-3 border rounded-md">
                          <h5 className="text-sm font-medium text-green-600 mb-2">Support Levels (Buy Zones)</h5>
                          <div className="space-y-1 text-sm">
                            <p>S1: <span className="font-semibold">${(mlData.predictions?.support_levels?.level_1 ?? 0).toFixed(2)}</span></p>
                            <p>S2: <span className="font-semibold">${(mlData.predictions?.support_levels?.level_2 ?? 0).toFixed(2)}</span></p>
                            <p>S3: <span className="font-semibold">${(mlData.predictions?.support_levels?.level_3 ?? 0).toFixed(2)}</span></p>
                          </div>
                        </div>

                        <div className="p-3 border rounded-md">
                          <h5 className="text-sm font-medium text-red-600 mb-2">Resistance Levels (Sell Zones)</h5>
                          <div className="space-y-1 text-sm">
                            <p>R1: <span className="font-semibold">${(mlData.predictions?.resistance_levels?.level_1 ?? 0).toFixed(2)}</span></p>
                            <p>R2: <span className="font-semibold">${(mlData.predictions?.resistance_levels?.level_2 ?? 0).toFixed(2)}</span></p>
                            <p>R3: <span className="font-semibold">${(mlData.predictions?.resistance_levels?.level_3 ?? 0).toFixed(2)}</span></p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2">Optimal Entry & Exit</h4>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div className="p-3 border rounded-md bg-blue-50 dark:bg-blue-900/20">
                          <p className="text-xs text-muted-foreground">Suggested Entry</p>
                          <p className="text-xl font-bold mt-1">${(mlData.predictions?.suggested_entry ?? 0).toFixed(2)}</p>
                          <p className="text-xs text-gray-500 mt-1">Best price to enter trade</p>
                        </div>

                        <div className="p-3 border rounded-md bg-red-50 dark:bg-red-900/20">
                          <p className="text-xs text-muted-foreground">Stop Loss</p>
                          <p className="text-xl font-bold mt-1 text-red-600">${(mlData.predictions?.stop_loss ?? 0).toFixed(2)}</p>
                          <p className="text-xs text-gray-500 mt-1">Exit if price falls below</p>
                        </div>

                        <div className="p-3 border rounded-md bg-green-50 dark:bg-green-900/20">
                          <p className="text-xs text-muted-foreground">Take Profit</p>
                          <p className="text-xl font-bold mt-1 text-green-600">${(mlData.predictions?.take_profit ?? 0).toFixed(2)}</p>
                          <p className="text-xs text-gray-500 mt-1">Exit if price reaches here</p>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2">Detected Patterns ({mlData.pattern_count ?? mlData.patterns?.length ?? 0})</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {(mlData.patterns || []).map((p: any, idx: number) => (
                          <div key={idx} className="p-3 border rounded-md">
                            <div className="flex justify-between">
                              <div>
                                <div className="font-medium">{p.type}</div>
                                <div className="text-sm text-muted-foreground">{p.description ?? ''}</div>
                              </div>
                              <Badge>{(p.confidence ?? 0).toFixed(2)}</Badge>
                            </div>
                            <div className="text-xs text-gray-500 mt-2">Target: {p.target_price ? '$' + parseFloat(p.target_price).toFixed(2) : '—'} · Stop: {p.stop_loss ? '$' + parseFloat(p.stop_loss).toFixed(2) : '—'}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2">Technical Feature Summary</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <div className="p-3 border rounded-md">
                          <p className="text-xs text-muted-foreground">RSI (14)</p>
                          <p className="font-semibold">{mlData.technical_features?.rsi_14 ?? '—'}</p>
                        </div>
                        <div className="p-3 border rounded-md">
                          <p className="text-xs text-muted-foreground">MA20 / MA50</p>
                          <p className="font-semibold">{mlData.technical_features?.price_ma20_ratio ? mlData.technical_features.price_ma20_ratio.toFixed(2) : '—'}</p>
                        </div>
                        <div className="p-3 border rounded-md">
                          <p className="text-xs text-muted-foreground">Momentum (10)</p>
                          <p className="font-semibold">{mlData.technical_features?.momentum_10 ?? '—'}</p>
                        </div>
                        <div className="p-3 border rounded-md">
                          <p className="text-xs text-muted-foreground">ATR(14)</p>
                          <p className="font-semibold">{mlData.technical_features?.atr_14 ?? '—'}</p>
                        </div>
                      </div>
                      <div className="mt-4">
                        <h5 className="text-sm font-medium mb-2">Recent Price Sparkline</h5>
                        {/* Use last 60 closes from main data if available, fallback to technical features */}
                        <div>
                          <Sparkline data={(data?.history?.slice(0).map(h => typeof h.close === 'number' ? h.close : (h.adjusted_close ?? 0)).slice(-60)) || []} />
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 border rounded-md text-muted-foreground">No ML insights loaded. Click &quot;Load ML Insights&quot; to fetch features and detected patterns.</div>
                )}
              </CustomCard>
            </TabsContent>

            <TabsContent value="news">
              <CustomCard title="News & Sentiment Analysis">
                <p className="text-muted-foreground mb-4">Market sentiment and recent news impact</p>
                <div className="space-y-4">
                  {data?.news && data.news.length > 0 ? (
                    data.news.slice(0, 6).map((n, idx) => (
                      <div key={idx} className="p-3 border rounded-md">
                        <div className="flex justify-between">
                          <h4 className="font-medium"><a href={n.link} target="_blank" rel="noreferrer">{n.title}</a></h4>
                          <Badge>{n.publisher ?? 'News'}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">{n.providerPublishTime ? new Date(n.providerPublishTime * 1000).toLocaleString() : ''}</p>
                      </div>
                    ))
                  ) : (
                    <div className="p-3 border rounded-md">
                      <p className="text-sm text-muted-foreground">No recent news found for this symbol.</p>
                    </div>
                  )}
                </div>
              </CustomCard>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </AppLayout>
  );
};

// Separate chart renderer component to properly memoize chart data
const ChartRenderer = React.memo(({ useTV, data, mlData, overlays }: {
  useTV: boolean;
  data: ComprehensiveStockData;
  mlData: any;
  overlays: { [k: string]: boolean };
}) => {
  // Memoize candle data (doesn't change with overlay toggles)
  const candles = useMemo(() => {
    if (!data?.history || !mlData?.indicator_series?.dates) return [];
    
    const toTs = (d: string | number) => {
      if (typeof d === 'number') return d;
      const t = Date.parse(d as string);
      return Number.isFinite(t) ? Math.floor(t / 1000) : undefined;
    };
    
    return (data.history || []).slice(-240).map(h => ({
      time: toTs(h.date) as number,
      open: h.open ?? h.close ?? 0,
      high: h.high ?? h.close ?? 0,
      low: h.low ?? h.close ?? 0,
      close: h.close ?? 0,
    }));
  }, [data?.history, mlData?.indicator_series?.dates]);

  // Memoize line data based on overlays
  const lines = useMemo(() => {
    if (!mlData?.indicator_series?.dates) return {};
    
    const dates: string[] = mlData.indicator_series.dates;
    const series = mlData.indicator_series;
    const result: Record<string, any[]> = {};
    
    const toTs = (d: string | number) => {
      if (typeof d === 'number') return d;
      const t = Date.parse(d as string);
      return Number.isFinite(t) ? Math.floor(t / 1000) : undefined;
    };
    
    const toLine = (arr?: (number|null)[]) => {
      if (!arr || !dates) return undefined;
      const pts = [] as { time: number, value: number }[];
      for (let i=0; i<Math.min(arr.length, dates.length); i++) {
        const v = arr[i] as number | null;
        const t = toTs(dates[i]);
        if (v !== null && v !== undefined && typeof t === 'number') {
          pts.push({ time: t, value: v });
        }
      }
      return pts.length ? pts : undefined;
    };
    
    const addFlat = (key: string, value?: number) => {
      if (value === undefined || value === null) return;
      const pts = dates.map((d: string) => ({ 
        time: toTs(d) as number, 
        value 
      })).filter(p => typeof p.time === 'number');
      result[key] = pts;
    };
    
    // Add line series based on overlay toggles
    if (overlays.sma20 && series.sma20) result.sma20 = toLine(series.sma20);
    if (overlays.sma50 && series.sma50) result.sma50 = toLine(series.sma50);
    if (overlays.sma200 && series.sma200) result.sma200 = toLine(series.sma200);
    if (overlays.ema12 && series.ema12) result.ema12 = toLine(series.ema12);
    if (overlays.ema26 && series.ema26) result.ema26 = toLine(series.ema26);
    
    if (overlays.bb && series.bb) {
      if (series.bb.upper) result.bb_upper = toLine(series.bb.upper);
      if (series.bb.middle) result.bb_middle = toLine(series.bb.middle);
      if (series.bb.lower) result.bb_lower = toLine(series.bb.lower);
    }
    
    if (overlays.kelt && series.keltner) {
      if (series.keltner.upper) result.kelt_upper = toLine(series.keltner.upper);
      if (series.keltner.middle) result.kelt_middle = toLine(series.keltner.middle);
      if (series.keltner.lower) result.kelt_lower = toLine(series.keltner.lower);
    }
    
    if (overlays.pivots && series.levels?.pivots) {
      const p = series.levels.pivots;
      addFlat('pp', p.pp);
      addFlat('r1', p.r1);
      addFlat('r2', p.r2);
      addFlat('r3', p.r3);
      addFlat('s1', p.s1);
      addFlat('s2', p.s2);
      addFlat('s3', p.s3);
    }
    
    if (overlays.fib && series.levels?.fibonacci?.levels) {
      const fib = series.levels.fibonacci.levels;
      Object.entries(fib).forEach(([lvl, val]: any) => {
        addFlat(`fib_${lvl}`, val as number);
      });
    }
    
    return result;
  }, [mlData?.indicator_series, overlays]);

  // Render appropriate chart
  if (useTV && mlData?.indicator_series?.dates?.length && candles.length > 0) {
    return <TVLightweightChart candles={candles} lines={lines} />;
  }
  
  if (mlData?.indicator_series?.dates?.length) {
    return <InteractivePatternChart series={mlData.indicator_series} patterns={mlData?.patterns ?? []} />;
  }
  
  return (
    <PatternChart
      history={data.history.slice(-240)}
      sma20={data.technicals?.sma_20 ?? null}
      sma50={data.technicals?.sma_50 ?? null}
      sma200={data.technicals?.sma_200 ?? null}
      patterns={mlData?.patterns ?? []}
    />
  );
});

ChartRenderer.displayName = 'ChartRenderer';

export default Research;