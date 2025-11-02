import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import AppLayout from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Progress } from '@/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Download,
  FileText,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  BarChart3,
  DollarSign,
  PieChart,
  Activity,
  Users,
  Target,
  Shield,
  Brain,
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import {
  generateResearchReport,
  type ResearchReportRequest,
  type ResearchReportResponse,
  getStockDetails,
  getStockAnalysis,
  getStockNews,
  getStockPeers,
} from '@/lib/api-services';
import SearchBar from '@/components/SearchBar';

const Research = (): JSX.Element => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [stockSymbol, setStockSymbol] = useState('');
  const [analysisDepth, setAnalysisDepth] = useState<'quick' | 'deep'>('quick');
  const [includeTechnical, setIncludeTechnical] = useState(true);
  const [includeSentiment, setIncludeSentiment] = useState(true);
  const [includeCompetitors, setIncludeCompetitors] = useState(true);
  const [timeframe, setTimeframe] = useState('3months');
  const [reportGenerated, setReportGenerated] = useState(false);

  // Format symbol for Indian stocks
  const formatIndianSymbol = (symbol: string): string => {
    if (!symbol) return '';
    const cleaned = symbol.toUpperCase().trim();
    if (cleaned.endsWith('.NS') || cleaned.endsWith('.BO')) {
      return cleaned;
    }
    return `${cleaned}.NS`; // Default to NSE
  };

  const formattedSymbol = stockSymbol ? formatIndianSymbol(stockSymbol) : '';

  // Generate report query
  const { data: report, isLoading, error, refetch } = useQuery<ResearchReportResponse, Error>({
    queryKey: ['research-report', formattedSymbol, analysisDepth, includeTechnical, includeSentiment, includeCompetitors],
    queryFn: async () => {
      if (!formattedSymbol) {
        throw new Error('Symbol is required');
      }
      console.log('Fetching report for symbol:', formattedSymbol);
      const request: ResearchReportRequest = {
        symbol: formattedSymbol,
        include_technical: includeTechnical,
        include_sentiment: includeSentiment,
        include_competitors: includeCompetitors,
        format: 'json',
      };
      console.log('Request payload:', request);
      const result = await generateResearchReport(request);
      console.log('Report received:', result);
      return result;
    },
    enabled: reportGenerated && !!formattedSymbol,
    retry: 1,
  });

  useEffect(() => {
    if (report) {
      toast({
        title: 'Report generated',
        description: 'AI research report is ready',
      });
    }
    if (error) {
      toast({
        title: 'Error generating report',
        description: error.message,
        variant: 'destructive',
      });
    }
  }, [report, error, toast]);


  // Get additional stock data
  const { data: stockDetails } = useQuery({
    queryKey: ['stock-details', formattedSymbol],
    queryFn: () => getStockDetails(formattedSymbol),
    enabled: !!formattedSymbol && reportGenerated,
  });

  const { data: stockAnalysis } = useQuery({
    queryKey: ['stock-analysis', formattedSymbol],
    queryFn: () => getStockAnalysis(formattedSymbol),
    enabled: !!formattedSymbol && reportGenerated,
  });

  const { data: stockNews } = useQuery({
    queryKey: ['stock-news', formattedSymbol],
    queryFn: () => getStockNews(formattedSymbol),
    enabled: !!formattedSymbol && reportGenerated && includeSentiment,
  });

  const { data: stockPeers } = useQuery({
    queryKey: ['stock-peers', formattedSymbol],
    queryFn: () => getStockPeers(formattedSymbol),
    enabled: !!formattedSymbol && reportGenerated && includeCompetitors,
  });

  const handleGenerateReport = async () => {
    if (!stockSymbol.trim()) {
      toast({
        title: 'Symbol required',
        description: 'Please enter a stock symbol (e.g., RELIANCE, TCS)',
        variant: 'destructive',
      });
      return;
    }

    console.log('Generating report for:', formatIndianSymbol(stockSymbol));

    // Reset previous report
    setReportGenerated(false);

    // Small delay to ensure state updates
    setTimeout(() => {
      setReportGenerated(true);
      toast({
        title: 'Generating report...',
        description: analysisDepth === 'deep' ? 'Deep analysis may take 30-60 seconds' : 'Quick analysis in progress',
      });
    }, 100);
  };

  // Listen for navigation events from SearchBar (it navigates directly now)
  // Users can also type directly in the input field

  const formatCurrency = (value: number) => {
    if (value >= 1e12) return `₹${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `₹${(value / 1e9).toFixed(2)}Cr`;
    if (value >= 1e7) return `₹${(value / 1e7).toFixed(2)}Cr`;
    if (value >= 1e5) return `₹${(value / 1e5).toFixed(2)}L`;
    return `₹${value.toFixed(2)}`;
  };

  const formatNumber = (value: number) => {
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(2)}K`;
    return value.toFixed(2);
  };

  const getSentimentColor = (score: number) => {
    if (score > 0.3) return 'text-green-500';
    if (score < -0.3) return 'text-red-500';
    return 'text-yellow-500';
  };

  const getSentimentBadge = (score: number) => {
    if (score > 0.3) return { variant: 'default' as const, label: 'Positive' };
    if (score < -0.3) return { variant: 'destructive' as const, label: 'Negative' };
    return { variant: 'secondary' as const, label: 'Neutral' };
  };

  const getRecommendationColor = (recommendation: string) => {
    const lower = recommendation.toLowerCase();
    if (lower.includes('buy') || lower.includes('strong buy')) return 'text-green-500';
    if (lower.includes('sell') || lower.includes('strong sell')) return 'text-red-500';
    if (lower.includes('hold')) return 'text-yellow-500';
    return 'text-blue-500';
  };

  const exportToPDF = () => {
    toast({
      title: 'PDF Export',
      description: 'PDF export feature coming soon. Use browser print for now.',
    });
    window.print();
  };

  const exportToExcel = () => {
    if (!report) return;

    const headers = ['Section', 'Metric', 'Value'];
    const rows: string[][] = [];

    // Executive Summary
    rows.push(['Executive Summary', 'Symbol', report.symbol]);
    rows.push(['Executive Summary', 'Company', report.company_name]);
    rows.push(['Executive Summary', 'Current Price', `₹${report.current_price.toFixed(2)}`]);

    // Financials
    Object.entries(report.financials).forEach(([key, value]) => {
      rows.push(['Financials', key, String(value)]);
    });

    // Technicals
    if (report.technicals) {
      Object.entries(report.technicals).forEach(([key, value]) => {
        rows.push(['Technicals', key, String(value)]);
      });
    }

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research_report_${report.symbol}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);

    toast({
      title: 'Export successful',
      description: 'Research report exported to CSV',
    });
  };
  return (
    <AppLayout title="AI Research Reports" description="Get AI-generated insights and analysis on Indian stocks">
      <div className="space-y-6">

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Research Parameters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Stock Search */}
              <div className="space-y-2">
                <Label htmlFor="stock-symbol">Stock Symbol (Indian Stocks)</Label>
                <div className="space-y-2">
                  <Input
                    id="stock-symbol"
                    placeholder="e.g., RELIANCE, TCS, HDFCBANK (auto-adds .NS)"
                    value={stockSymbol}
                    onChange={(e) => setStockSymbol(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleGenerateReport()}
                  />
                  <div className="mt-2">
                    <SearchBar
                      placeholder="Search Indian stocks..."
                      showInlineDetails={false}
                      className="w-full"
                      pageContext="search"
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Tip: Enter symbol without .NS (e.g., RELIANCE not RELIANCE.NS)
                  </p>
                </div>
              </div>

              {/* Analysis Depth */}
              <div className="space-y-2">
                <Label>Analysis Depth</Label>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <span className="text-sm">Quick Analysis</span>
                  <Switch
                    checked={analysisDepth === 'deep'}
                    onCheckedChange={(checked) => setAnalysisDepth(checked ? 'deep' : 'quick')}
                  />
                  <span className="text-sm">Deep Analysis</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  {analysisDepth === 'deep'
                    ? 'Comprehensive analysis with all sections (30-60s)'
                    : 'Basic overview with key metrics (5-10s)'}
                </p>
              </div>

              {/* Timeframe */}
              <div className="space-y-2">
                <Label htmlFor="timeframe">Analysis Timeframe</Label>
                <Select value={timeframe} onValueChange={setTimeframe}>
                  <SelectTrigger id="timeframe">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1month">1 Month</SelectItem>
                    <SelectItem value="3months">3 Months</SelectItem>
                    <SelectItem value="6months">6 Months</SelectItem>
                    <SelectItem value="1year">1 Year</SelectItem>
                    <SelectItem value="3years">3 Years</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Include Options */}
              <div className="space-y-2">
                <Label>Include Sections</Label>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={includeTechnical}
                      onCheckedChange={setIncludeTechnical}
                    />
                    <Label className="text-sm">Technical Analysis</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={includeSentiment}
                      onCheckedChange={setIncludeSentiment}
                    />
                    <Label className="text-sm">Sentiment Analysis</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={includeCompetitors}
                      onCheckedChange={setIncludeCompetitors}
                    />
                    <Label className="text-sm">Competitor Analysis</Label>
                  </div>
                </div>
              </div>
            </div>

            <Button
              className="w-full mt-6"
              onClick={handleGenerateReport}
              disabled={isLoading || !stockSymbol.trim()}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating {analysisDepth === 'deep' ? 'Deep' : 'Quick'} Analysis...
                </>
              ) : (
                <>
                  <Brain className="mr-2 h-4 w-4" />
                  Generate AI Research Report
                </>
              )}
            </Button>
          </CardContent>
        </Card>


        {/* Error State */}
        {error && (
          <Card className="border-destructive">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-destructive">
                <AlertTriangle className="h-5 w-5" />
                <div>
                  <p className="font-semibold">Error generating report</p>
                  <p className="text-sm text-muted-foreground">
                    {error instanceof Error ? error.message : 'Failed to fetch research report'}
                  </p>
                  <Button variant="outline" className="mt-4" onClick={() => refetch()}>
                    Try Again
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Report Results */}
        {report && (
          <>
            <Card>
              <CardContent className="pt-6">
                <div className="flex gap-2 flex-wrap">
                  <Button variant="outline" onClick={exportToPDF}>
                    <Download className="mr-2 h-4 w-4" />
                    Export PDF
                  </Button>
                  <Button variant="outline" onClick={exportToExcel}>
                    <FileText className="mr-2 h-4 w-4" />
                    Export Excel
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => navigate(`/stock/${report.symbol}`)}
                  >
                    <BarChart3 className="mr-2 h-4 w-4" />
                    View Stock Details
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Report Tabs */}
            <Tabs defaultValue="summary" className="space-y-4">
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="summary">Summary</TabsTrigger>
                <TabsTrigger value="fundamental">Fundamental</TabsTrigger>
                <TabsTrigger value="technical">Technical</TabsTrigger>
                <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
                <TabsTrigger value="valuation">Valuation & Risks</TabsTrigger>
              </TabsList>

              {/* Executive Summary Tab */}
              <TabsContent value="summary" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>Executive Summary</span>
                      <Badge className={getRecommendationColor(report.recommendations[0] || '')}>
                        {report.recommendations[0] || 'Analysis'}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-xs text-muted-foreground">Symbol</p>
                        <p className="text-lg font-semibold">{report.symbol}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Company</p>
                        <p className="text-lg font-semibold truncate">{report.company_name}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Current Price</p>
                        <p className="text-lg font-semibold">₹{report.current_price.toFixed(2)}</p>
                      </div>
                      <div>
                        <p className="text-xs text-muted-foreground">Sector</p>
                        <p className="text-lg font-semibold">{report.sector || 'N/A'}</p>
                      </div>
                    </div>

                    <div className="p-4 bg-muted rounded-lg">
                      <h4 className="font-semibold mb-2">AI-Generated Summary</h4>
                      <p className="text-sm">{report.summary}</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                          Key Strengths
                        </h4>
                        <ul className="list-disc list-inside space-y-1 text-sm">
                          {report.recommendations.slice(0, 3).map((rec, idx) => (
                            <li key={idx}>{rec}</li>
                          ))}
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                          <AlertTriangle className="h-4 w-4 text-red-500" />
                          Risk Factors
                        </h4>
                        <ul className="list-disc list-inside space-y-1 text-sm">
                          {report.risk_factors.slice(0, 3).map((risk, idx) => (
                            <li key={idx}>{risk}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Key Performance Indicators */}
                <Card>
                  <CardHeader>
                    <CardTitle>Key Performance Indicators</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="p-4 border rounded-lg">
                        <p className="text-xs text-muted-foreground mb-1">P/E Ratio</p>
                        <p className="text-2xl font-bold">{report.financials.pe_ratio.toFixed(2)}</p>
                        <p className="text-xs text-muted-foreground mt-1">Price to Earnings</p>
                      </div>
                      <div className="p-4 border rounded-lg">
                        <p className="text-xs text-muted-foreground mb-1">EPS</p>
                        <p className="text-2xl font-bold">₹{report.financials.eps.toFixed(2)}</p>
                        <p className="text-xs text-muted-foreground mt-1">Earnings Per Share</p>
                      </div>
                      <div className="p-4 border rounded-lg">
                        <p className="text-xs text-muted-foreground mb-1">Profit Margin</p>
                        <p className="text-2xl font-bold">{report.financials.profit_margin.toFixed(2)}%</p>
                        <p className="text-xs text-muted-foreground mt-1">Net Profit Margin</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Fundamental Analysis Tab */}
              <TabsContent value="fundamental" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <DollarSign className="h-5 w-5" />
                      Fundamental Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Metric</TableHead>
                          <TableHead>Value</TableHead>
                          <TableHead>Description</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        <TableRow>
                          <TableCell className="font-medium">Market Cap</TableCell>
                          <TableCell>{formatCurrency(report.financials.market_cap)}</TableCell>
                          <TableCell className="text-sm text-muted-foreground">Total market value</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">Revenue</TableCell>
                          <TableCell>{formatCurrency(report.financials.revenue)}</TableCell>
                          <TableCell className="text-sm text-muted-foreground">Annual revenue</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">Net Income</TableCell>
                          <TableCell>{formatCurrency(report.financials.net_income)}</TableCell>
                          <TableCell className="text-sm text-muted-foreground">Annual profit</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">P/E Ratio</TableCell>
                          <TableCell>{report.financials.pe_ratio.toFixed(2)}</TableCell>
                          <TableCell className="text-sm text-muted-foreground">Price to earnings</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">EPS</TableCell>
                          <TableCell>₹{report.financials.eps.toFixed(2)}</TableCell>
                          <TableCell className="text-sm text-muted-foreground">Earnings per share</TableCell>
                        </TableRow>
                        <TableRow>
                          <TableCell className="font-medium">Profit Margin</TableCell>
                          <TableCell>{report.financials.profit_margin.toFixed(2)}%</TableCell>
                          <TableCell className="text-sm text-muted-foreground">Net profit margin</TableCell>
                        </TableRow>
                        {report.financials.dividend_yield && (
                          <TableRow>
                            <TableCell className="font-medium">Dividend Yield</TableCell>
                            <TableCell>{report.financials.dividend_yield.toFixed(2)}%</TableCell>
                            <TableCell className="text-sm text-muted-foreground">Annual dividend yield</TableCell>
                          </TableRow>
                        )}
                        {report.financials.debt_to_equity && (
                          <TableRow>
                            <TableCell className="font-medium">Debt/Equity</TableCell>
                            <TableCell>{report.financials.debt_to_equity.toFixed(2)}</TableCell>
                            <TableCell className="text-sm text-muted-foreground">Financial leverage</TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Technical Analysis Tab */}
              <TabsContent value="technical" className="space-y-6">
                {report.technicals ? (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Activity className="h-5 w-5" />
                        Technical Indicators
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                        <div className="p-3 border rounded-lg">
                          <p className="text-xs text-muted-foreground">MA 50</p>
                          <p className="text-lg font-semibold">₹{report.technicals.ma_50.toFixed(2)}</p>
                        </div>
                        <div className="p-3 border rounded-lg">
                          <p className="text-xs text-muted-foreground">MA 200</p>
                          <p className="text-lg font-semibold">₹{report.technicals.ma_200.toFixed(2)}</p>
                        </div>
                        <div className="p-3 border rounded-lg">
                          <p className="text-xs text-muted-foreground">RSI</p>
                          <p className="text-lg font-semibold">{report.technicals.rsi.toFixed(2)}</p>
                          <p className="text-xs text-muted-foreground">
                            {report.technicals.rsi > 70 ? 'Overbought' : report.technicals.rsi < 30 ? 'Oversold' : 'Neutral'}
                          </p>
                        </div>
                        <div className="p-3 border rounded-lg">
                          <p className="text-xs text-muted-foreground">MACD</p>
                          <p className="text-lg font-semibold">{report.technicals.macd.toFixed(4)}</p>
                        </div>
                        <div className="p-3 border rounded-lg">
                          <p className="text-xs text-muted-foreground">Avg Volume</p>
                          <p className="text-lg font-semibold">{formatNumber(report.technicals.volume_avg)}</p>
                        </div>
                      </div>

                      {/* Price vs Moving Averages Analysis */}
                      <div className="p-4 bg-muted rounded-lg">
                        <h4 className="font-semibold mb-2">Technical Signals</h4>
                        <div className="space-y-2 text-sm">
                          {report.current_price > report.technicals.ma_50 && report.technicals.ma_50 > report.technicals.ma_200 ? (
                            <div className="flex items-center gap-2 text-green-500">
                              <TrendingUp className="h-4 w-4" />
                              <span>Bullish: Price above both 50-day and 200-day MA (Golden Cross)</span>
                            </div>
                          ) : (
                            <div className="flex items-center gap-2 text-red-500">
                              <TrendingDown className="h-4 w-4" />
                              <span>Bearish: Price below key moving averages</span>
                            </div>
                          )}
                          {report.technicals.rsi > 70 && (
                            <div className="flex items-center gap-2 text-red-500">
                              <AlertTriangle className="h-4 w-4" />
                              <span>RSI indicates overbought conditions (>70)</span>
                         </div>
                          )}
                          {report.technicals.rsi < 30 && (
                            <div className="flex items-center gap-2 text-green-500">
                              <Target className="h-4 w-4" />
                              <span>RSI indicates oversold conditions (<30)</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                  <Card>
                    <CardContent className="pt-6">
                      <p className="text-muted-foreground">Technical analysis not included in this report.</p>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* Sentiment Analysis Tab */}
              <TabsContent value="sentiment" className="space-y-6">
                {report.sentiment ? (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <PieChart className="h-5 w-5" />
                        Sentiment Analysis
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="p-4 border rounded-lg">
                          <p className="text-xs text-muted-foreground mb-2">Overall Sentiment</p>
                          <div className="flex items-center justify-between mb-2">
                            <span className={`text-2xl font-bold ${getSentimentColor(report.sentiment.overall_score)}`}>
                              {(report.sentiment.overall_score * 100).toFixed(0)}%
                            </span>
                            <Badge {...getSentimentBadge(report.sentiment.overall_score)} />
                          </div>
                          <Progress
                            value={(report.sentiment.overall_score + 1) * 50}
                            className="mt-2"
                          />
                        </div>
                        <div className="p-4 border rounded-lg">
                          <p className="text-xs text-muted-foreground mb-2">News Sentiment</p>
                          <div className="flex items-center justify-between mb-2">
                            <span className={`text-2xl font-bold ${getSentimentColor(report.sentiment.news_sentiment)}`}>
                              {(report.sentiment.news_sentiment * 100).toFixed(0)}%
                            </span>
                            <Badge {...getSentimentBadge(report.sentiment.news_sentiment)} />
                          </div>
                          <Progress
                            value={(report.sentiment.news_sentiment + 1) * 50}
                            className="mt-2"
                          />
                        </div>
                        <div className="p-4 border rounded-lg">
                          <p className="text-xs text-muted-foreground mb-2">Social Sentiment</p>
                          <div className="flex items-center justify-between mb-2">
                            <span className={`text-2xl font-bold ${getSentimentColor(report.sentiment.social_sentiment)}`}>
                              {(report.sentiment.social_sentiment * 100).toFixed(0)}%
                            </span>
                            <Badge {...getSentimentBadge(report.sentiment.social_sentiment)} />
                          </div>
                          <Progress
                            value={(report.sentiment.social_sentiment + 1) * 50}
                            className="mt-2"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-4 border rounded-lg">
                          <p className="text-xs text-muted-foreground mb-1">Analyst Rating</p>
                          <p className="text-xl font-semibold">{report.sentiment.analyst_rating}</p>
                        </div>
                        <div className="p-4 border rounded-lg">
                          <p className="text-xs text-muted-foreground mb-1">Price Target</p>
                          <p className="text-xl font-semibold">₹{report.sentiment.price_target.toFixed(2)}</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {report.sentiment.price_target > report.current_price ? (
                              <span className="text-green-500">
                                +{((report.sentiment.price_target / report.current_price - 1) * 100).toFixed(1)}% upside
                              </span>
                            ) : (
                              <span className="text-red-500">
                                {((report.sentiment.price_target / report.current_price - 1) * 100).toFixed(1)}% downside
                              </span>
                            )}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                  <Card>
                    <CardContent className="pt-6">
                      <p className="text-muted-foreground">Sentiment analysis not included in this report.</p>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* Valuation & Risks Tab */}
              <TabsContent value="valuation" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="h-5 w-5" />
                      Valuation Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h4 className="font-semibold mb-4">Current Valuation</h4>
                        <div className="space-y-3">
                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Market Cap</span>
                            <span className="font-semibold">{formatCurrency(report.financials.market_cap)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">P/E Ratio</span>
                            <span className="font-semibold">{report.financials.pe_ratio.toFixed(2)}</span>
                          </div>
                          {report.sentiment && (
                            <div className="flex justify-between">
                              <span className="text-sm text-muted-foreground">Analyst Target</span>
                              <span className="font-semibold">₹{report.sentiment.price_target.toFixed(2)}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      <div>
                        <h4 className="font-semibold mb-4">Price Target Scenarios</h4>
                        <div className="space-y-3">
                          {report.sentiment && (
                            <>
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">Conservative</span>
                                <span className="font-semibold text-yellow-500">
                                  ₹{(report.sentiment.price_target * 0.9).toFixed(2)}
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">Base Case</span>
                                <span className="font-semibold text-blue-500">
                                  ₹{report.sentiment.price_target.toFixed(2)}
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm text-muted-foreground">Bullish</span>
                                <span className="font-semibold text-green-500">
                                  ₹{(report.sentiment.price_target * 1.15).toFixed(2)}
                                </span>
                              </div>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Risk Assessment */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="h-5 w-5" />
                      Risk Assessment
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <h4 className="font-semibold">Identified Risk Factors</h4>
                      <ul className="space-y-2">
                        {report.risk_factors.map((risk, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-sm">
                            <AlertTriangle className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
                            <span>{risk}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>

                {/* Competitors */}
                {report.competitors && report.competitors.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Users className="h-5 w-5" />
                        Competitor Analysis
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {report.competitors.map((competitor, idx) => (
                          <Badge key={idx} variant="outline" className="cursor-pointer hover:bg-muted">
                            {competitor}
                          </Badge>
                        ))}
                      </div>
                      <p className="text-xs text-muted-foreground mt-4">
                        Click on competitor symbols to view their analysis
                      </p>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>
            </Tabs>
          </>
        )}

        {/* Empty State */}
        {!report && !isLoading && !error && (
          <Card>
            <CardContent className="pt-12 pb-12">
              <div className="text-center">
                <Brain className="h-12 w-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                <h3 className="text-lg font-semibold mb-2">No Report Generated</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Enter a stock symbol above and click "Generate AI Research Report" to get started.
                </p>
                <p className="text-xs text-muted-foreground">
                  Focus: Indian stocks (NSE/BSE) - Enter symbols like RELIANCE, TCS, HDFCBANK
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </AppLayout>
  );
};

export default Research;
