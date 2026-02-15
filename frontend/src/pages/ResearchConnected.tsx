import React, { useState } from 'react';
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
}

interface HistData {
  Date: string;
  Open: number;
  High: number;
  Low: number;
  Close: number;
  Volume: number;
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

interface ComprehensiveStockData {
  info: StockInfo;
  history: HistData[];
  news: NewsData[];
  recommendations: RecommendationData[];
}

const Research = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isFullAnalysis, setIsFullAnalysis] = useState(false);
  const [symbol, setSymbol] = useState('AAPL');
  const [timeframe, setTimeframe] = useState('3months');
  const [data, setData] = useState<ComprehensiveStockData | null>(null);
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
      const resp = await fetch(`/api/research/${encodeURIComponent(symbol.trim())}?period=${period}`, {
        headers: { Accept: 'application/json' },
      });

      if (!resp.ok) {
        toast({ title: 'Error', description: `Failed to fetch data: ${resp.status} ${resp.statusText}` });
        setIsLoading(false);
        return;
      }

      const json: ComprehensiveStockData = await resp.json();
      setData(json);
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
            <TabsList className="mb-4">
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="technical">Technical</TabsTrigger>
              <TabsTrigger value="fundamental">Fundamental</TabsTrigger>
              <TabsTrigger value="news">News & Sentiment</TabsTrigger>
            </TabsList>
            
            <TabsContent value="summary" className="space-y-6">
              <CustomCard 
                title="AI-Generated Stock Summary" 
                description="Key insights and recommendations generated by AI"
              >
                <div className="p-4 bg-teal/5 border border-teal/20 rounded-md">
                  <div className="flex justify-between items-center mb-4">
                    <div>
                      <h3 className="text-xl font-bold">{data?.info?.symbol ?? symbol.toUpperCase()}</h3>
                      <p className="text-sm text-muted-foreground">{data?.info?.longName ?? '—'}</p>
                    </div>
                    <Badge variant={data ? "success" : Math.random() > 0.5 ? "success" : "destructive"}>
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
                  
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-sm text-muted-foreground mb-1">Key Insights</h4>
                      <p className="text-sm">
                        {data?.info?.longBusinessSummary ? data.info.longBusinessSummary.slice(0, 400) + (data.info.longBusinessSummary.length > 400 ? '...' : '') : (
                          'No company summary available. Use Generate Analysis to fetch data.'
                        )}
                      </p>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-sm text-muted-foreground mb-1">Risk Assessment</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Volatility</p>
                          <div className="h-2 w-full bg-gray-200 rounded-full">
                            <div className="h-2 bg-amber-500 rounded-full" style={{ width: '40%' }}></div>
                          </div>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Market Risk</p>
                          <div className="h-2 w-full bg-gray-200 rounded-full">
                            <div className="h-2 bg-red-500 rounded-full" style={{ width: '65%' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-sm text-muted-foreground mb-1">AI Recommendation</h4>
                      <p className="text-sm">
                        {data?.recommendations && data.recommendations.length > 0 ? (
                          <>{data.recommendations[0].toGrade} — {data.recommendations[0].action ?? ''}</>
                        ) : (
                          'No analyst recommendations available.'
                        )}
                      </p>
                    </div>
                  </div>
                </div>
              </CustomCard>
              
              <CustomCard title="Key Performance Indicators">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">Price to Earnings</p>
                    <p className="text-xl font-semibold">{data?.info?.trailingPE ?? '—'}</p>
                    <div className="flex items-center text-xs text-green-500 mt-1">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      <span>vs Industry</span>
                    </div>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">Market Cap</p>
                    <p className="text-xl font-semibold">{data?.info?.marketCap ? Intl.NumberFormat().format(data.info.marketCap) : '—'}</p>
                    <div className="flex items-center text-xs text-red-500 mt-1">
                      <TrendingDown className="h-3 w-3 mr-1" />
                      <span>vs Forecast</span>
                    </div>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">Beta</p>
                    <p className="text-xl font-semibold">{data?.info?.beta ?? '—'}</p>
                    <div className="flex items-center text-xs text-green-500 mt-1">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      <span>vs Previous</span>
                    </div>
                  </div>
                </div>
              </CustomCard>
            </TabsContent>
            
            <TabsContent value="technical">
              <CustomCard title="Technical Analysis">
                <p className="text-muted-foreground mb-4">Technical indicators and chart patterns</p>
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
                          <TableRow key={row.Date}>
                            <TableCell>{row.Date}</TableCell>
                            <TableCell>{row.Open.toFixed(2)}</TableCell>
                            <TableCell>{row.High.toFixed(2)}</TableCell>
                            <TableCell>{row.Low.toFixed(2)}</TableCell>
                            <TableCell>{row.Close.toFixed(2)}</TableCell>
                            <TableCell>{Intl.NumberFormat().format(row.Volume)}</TableCell>
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
              </CustomCard>
            </TabsContent>
            
            <TabsContent value="fundamental">
              <CustomCard title="Fundamental Analysis">
                <p className="text-muted-foreground mb-4">Financial metrics and company fundamentals</p>
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

export default Research;
