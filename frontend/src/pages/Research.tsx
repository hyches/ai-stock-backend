import React, { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AppLayout from '@/components/layout/AppLayout';
import { api } from '@/lib/api-client';
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
  ml_predictions?: any;
}

import TradeDialog from '@/components/TradeDialog';
import AgentAnalysisPanel from '@/components/dashboard/AgentAnalysisPanel';

interface PriceTarget {
  target: number;
  low: number;
  high: number;
  confidence: number;
}

interface PriceLevels {
  level_1: number;
  level_2: number;
  level_3: number;
}

interface MLPredictions {
  signal: string;
  signal_confidence: number;
  predicted_price_1week: PriceTarget;
  predicted_price_1month: PriceTarget;
  support_levels: PriceLevels;
  resistance_levels: PriceLevels;
  overall_confidence: number;
  ml_model_used: boolean;
}

const PriceZonesPanel = ({ predictions }: { predictions: MLPredictions }) => {
  if (!predictions || !predictions.predicted_price_1week) return null;

  return (
    <div className="space-y-6 animate-in slide-in-from-bottom-2 duration-500">
      <div>
        <h4 className="font-bold text-sm mb-3 flex items-center gap-2">
          <span>Price Zones</span>
          <Badge variant="outline" className="text-[9px] uppercase tracking-tighter py-0 h-4">Contract v1.0</Badge>
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Price Targets */}
          <div className="p-4 border rounded-xl bg-card space-y-4">
            <h5 className="text-xs font-bold uppercase text-muted-foreground flex items-center justify-between">
              Price Targets
              <span className="text-[9px] lowercase font-normal italic">Derived from Ensemble expected return</span>
            </h5>

            <div className="space-y-3">
              {/* 1-Week */}
              <div className="flex justify-between items-center bg-muted/30 p-2 rounded-lg border border-border/50">
                <div>
                  <p className="text-[10px] text-muted-foreground uppercase font-semibold">1-Week Target</p>
                  <p className="text-lg font-mono font-bold">${predictions.predicted_price_1week.target.toFixed(2)}</p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] text-muted-foreground uppercase font-semibold">Confidence Band</p>
                  <p className="text-xs font-mono font-medium text-primary">
                    ${predictions.predicted_price_1week.low.toFixed(2)} – ${predictions.predicted_price_1week.high.toFixed(2)}
                  </p>
                </div>
              </div>

              {/* 1-Month */}
              <div className="flex justify-between items-center bg-muted/30 p-2 rounded-lg border border-border/50">
                <div>
                  <p className="text-[10px] text-muted-foreground uppercase font-semibold">1-Month Target</p>
                  <p className="text-lg font-mono font-bold">${predictions.predicted_price_1month.target.toFixed(2)}</p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] text-muted-foreground uppercase font-semibold">Confidence Band</p>
                  <p className="text-xs font-mono font-medium text-primary">
                    ${predictions.predicted_price_1month.low.toFixed(2)} – ${predictions.predicted_price_1month.high.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Support & Resistance */}
          <div className="p-4 border rounded-xl bg-card space-y-3">
            <h5 className="text-xs font-bold uppercase text-muted-foreground flex items-center justify-between">
              Support & Resistance
            </h5>

            <div className="space-y-1">
              {/* Resistance Stack */}
              <div className="space-y-1 mb-2">
                {[3, 2, 1].map(lvl => (
                  <div key={`r${lvl}`} className="flex justify-between items-center px-2 py-1 rounded bg-rose-500/5 border border-rose-500/10">
                    <span className="text-[10px] font-bold text-rose-600 uppercase">Resistance {lvl}</span>
                    <span className="text-xs font-mono font-bold">${(predictions.resistance_levels as any)[`level_${lvl}`]?.toFixed(2)}</span>
                  </div>
                ))}
              </div>

              {/* Support Stack */}
              <div className="space-y-1">
                {[1, 2, 3].map(lvl => (
                  <div key={`s${lvl}`} className="flex justify-between items-center px-2 py-1 rounded bg-emerald-500/5 border border-emerald-500/10">
                    <span className="text-[10px] font-bold text-emerald-600 uppercase">Support {lvl}</span>
                    <span className="text-xs font-mono font-bold">${(predictions.support_levels as any)[`level_${lvl}`]?.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>

            <p className="text-[9px] text-muted-foreground italic leading-tight pt-1">
              Support and Resistance levels are statistically derived (ATR + recent volatility), not ML predictions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

const Research = ({ standalone = true }: { standalone?: boolean }) => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [isTradeOpen, setTradeOpen] = useState(false);
  const [tradeSide, setTradeSide] = useState<'buy' | 'sell'>('buy');

  const [isDownloading, setIsDownloading] = useState(false);
  const [isFullAnalysis, setIsFullAnalysis] = useState(false);
  const [symbol, setSymbol] = useState('AAPL');
  const [timeframe, setTimeframe] = useState('3months');
  const [data, setData] = useState<ComprehensiveStockData | null>(null);
  const [mlLoading, setMlLoading] = useState(false);
  const [mlData, setMlData] = useState<any | null>(null);
  const [mlError, setMlError] = useState<string | null>(null);
  const [useTV, setUseTV] = useState<boolean>(true);
  const [overlays, setOverlays] = useState<{ [k: string]: boolean }>({
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
  const [searchError, setSearchError] = useState<string | null>(null);
  const { toast } = useToast();

  const [agentData, setAgentData] = useState<any | null>(null);
  const [agentLoading, setAgentLoading] = useState(false);

  const handleTradeOpen = (side: 'buy' | 'sell') => {
    setTradeSide(side);
    setTradeOpen(true);
  };

  const handleTradeIntent = (side: 'buy' | 'sell') => {
    if (!data?.info?.currentPrice) {
      toast({
        title: "Incomplete Data",
        description: "Please wait for market data to load before initiating a trade.",
        variant: "destructive"
      });
      return;
    }

    const params = new URLSearchParams({
      symbol: symbol.trim().toUpperCase(),
      side: side.toUpperCase(),
      price: data.info.currentPrice.toString()
    });

    navigate(`/trading?${params.toString()}&tab=dashboard`);

    toast({
      title: "Trade Intent Captured",
      description: `Navigating to Trading Terminal for ${side.toUpperCase()} ${symbol}.`,
    });
  };

  const handleDownload = (format: string) => {
    toast({
      title: "Download Started",
      description: `Preparing your ${format} report...`,
    });
    // For this showcase, we simulate the download
    setTimeout(() => {
      toast({
        title: "Download Ready",
        description: `Your ${format} report for ${symbol} is ready for download.`,
      });
    }, 1500);
  };

  const periodMap: Record<string, string> = {
    '1month': '1mo',
    '3months': '3mo',
    '6months': '6mo',
    '1year': '1y',
    '3years': '3y',
  };

  const [weather, setWeather] = useState<any>(null);
  const [anomalies, setAnomalies] = useState<any[]>([]);

  // Fetch Market Weather on mount
  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const res = await api.research.getMarketWeather();
        setWeather(res.data);
      } catch (e) {
        console.error("Failed to fetch market weather");
      }
    };
    fetchWeather();
  }, []);

  const handleGenerateAnalysis = async () => {
    if (!symbol || symbol.trim() === '') return;

    setIsLoading(true);
    setSearchError(null);
    setData(null);
    setMlData(null);
    setAnomalies([]);

    try {
      const period = periodMap[timeframe] || '1y';
      const resp = await fetch(`/api/v1/research/${encodeURIComponent(symbol.trim())}?period=${period}`, {
        headers: { Accept: 'application/json' },
      });

      if (!resp.ok) {
        if (resp.status === 404) {
          setSearchError('Symbol not found.');
        } else {
          setSearchError('Data unavailable. Please try again later.');
        }
        setIsLoading(false);
        return;
      }

      const json: ComprehensiveStockData = await resp.json();
      setData(json);

      // Fetch Anomalies
      try {
        const anomResp = await api.research.getAnomalies(symbol.trim(), period);
        setAnomalies(anomResp.data.anomalies || []);
      } catch (e) {
        console.error("Failed to fetch anomalies");
      }

      // Auto-populate ML insights
      if (json.ml_predictions) {
        // Wrap in a mock root for consistency if it came from the main research call
        setMlData({ predictions: json.ml_predictions, technical_features: json.technicals });
      } else {
        try {
          const mlResp = await fetch(`/api/v1/research-ml/${encodeURIComponent(symbol.trim())}/ml-features?period=${period}`, {
            method: 'POST', // Still a retrieval POST in this backend architecture, but we treat it as read-only view
            headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          });
          if (mlResp.ok) {
            const mlJson = await mlResp.json();
            // This endpoint already returns a root object with 'predictions' key
            setMlData(mlJson);
          }
        } catch (e) {
          console.warn('Auto ML load error', e);
        }
      }
    } catch (err) {
      setSearchError('Data unavailable. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAgentAnalysis = async () => {
    if (!symbol || symbol.trim() === '') return;

    setAgentLoading(true);
    setAgentData(null);

    try {
      const resp = await fetch('/api/v1/agents/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: symbol.trim() }),
      });

      if (!resp.ok) {
        throw new Error('Agent analysis failed');
      }

      const json = await resp.json();
      setAgentData(json);
      toast({
        title: "Agent Analysis Complete",
        description: `Multi-agent team has reached a consensus for ${symbol}.`,
      });
    } catch (err) {
      toast({
        title: "Ollama Error",
        description: "Could not reach the local agent team. Ensure Ollama is running and Llama3.1 is pulled.",
        variant: "destructive"
      });
    } finally {
      setAgentLoading(false);
    }
  };

  // ... (render return) ...
  const content = (
    <>
      {!standalone && (
        <div className="mb-6">
          <h1 className="text-2xl md:text-3xl font-bold text-foreground">AI Research Reports</h1>
          <p className="text-muted-foreground mt-1">Get AI-generated insights and analysis on stocks</p>
          <div className="mt-1 h-1 w-16 bg-primary rounded-full"></div>
        </div>
      )}
      {/* Market Weather Banner */}
      {weather && (
        <div className={`mb-6 p-4 rounded-lg border flex items-center justify-between ${weather.status === 'Sunny' ? 'bg-green-50 border-green-200 text-green-800' :
          weather.status === 'Stormy' ? 'bg-red-50 border-red-200 text-red-800' :
            'bg-yellow-50 border-yellow-200 text-yellow-800'
          }`}>
          <div className="flex items-center gap-4">
            <div className="text-4xl">
              {weather.status === 'Sunny' ? '☀️' : weather.status === 'Stormy' ? '⛈️' : '☁️'}
            </div>
            <div>
              <h3 className="font-bold text-lg">Market Weather: {weather.status}</h3>
              <p className="text-sm opacity-80">Volatility Index: {weather.volatility_index?.toFixed(4)}</p>
            </div>
          </div>
          <div className="text-sm font-mono">
            Updated: {new Date().toLocaleTimeString()}
          </div>
        </div>
      )}

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
                disabled={isLoading || !symbol.trim()}
                onClick={handleGenerateAnalysis}
              >
                {isLoading ? (
                  <>
                    <Loader className="mr-2 h-4 w-4 animate-spin" />
                    Fetching market data...
                  </>
                ) : (
                  'Generate Analysis'
                )}
              </Button>

              {searchError && (
                <p className="text-sm text-destructive mt-2 font-medium">{searchError}</p>
              )}
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
              <TabsTrigger value="agents" className="bg-primary/10 text-primary data-[state=active]:bg-primary data-[state=active]:text-primary-foreground font-bold">Agents</TabsTrigger>
              <TabsTrigger value="anomalies">Anomalies</TabsTrigger>
              <TabsTrigger value="news">News & Sentiment</TabsTrigger>
            </TabsList>

            <TabsContent value="anomalies">
              <CustomCard title="Price Anomalies (Z-Score Analysis)">
                <p className="text-muted-foreground mb-4">
                  Statistical anomalies detected in the price action ({timeframe}).
                </p>
                {isLoading ? (
                  <div className="py-12 text-center text-muted-foreground animate-pulse">Fetching market data...</div>
                ) : anomalies.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Date</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Price</TableHead>
                        <TableHead>Z-Score</TableHead>
                        <TableHead>Severity</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {anomalies.map((a, i) => (
                        <TableRow key={i}>
                          <TableCell>{a.date}</TableCell>
                          <TableCell className={a.type === 'spike' ? 'text-green-600' : 'text-red-600'}>
                            {a.type.toUpperCase()}
                          </TableCell>
                          <TableCell>{a.price.toFixed(2)}</TableCell>
                          <TableCell>{a.z_score.toFixed(2)}</TableCell>
                          <TableCell>
                            <Badge variant={a.severity === 'critical' ? 'destructive' : 'secondary'}>
                              {a.severity}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : data ? (
                  <div className="p-8 text-center border border-dashed rounded-md text-muted-foreground">
                    No anomalies detected in this period.
                  </div>
                ) : (
                  <div className="p-8 text-center border border-dashed rounded-md text-muted-foreground">
                    No data available for this symbol.
                  </div>
                )}
              </CustomCard>
            </TabsContent>

            <TabsContent value="agents">
              <CustomCard
                title="Deep COLLAB AI (Multi-Agent Debate)"
                description="Specialized agents debating Technical, Fundamental, and Sentiment data to reach a trade consensus."
              >
                <AgentAnalysisPanel
                  data={agentData}
                  isLoading={agentLoading}
                  onRunAnalysis={handleAgentAnalysis}
                />
              </CustomCard>
            </TabsContent>

            <TabsContent value="summary" className="space-y-6">
              <CustomCard
                title="AI-Generated Stock Summary"
                description="Key insights and recommendations generated by AI"
              >
                <div className="flex items-center gap-2 mb-4">
                  <Badge variant="secondary" className="bg-amber-500/10 text-amber-600 border-amber-200">🧪 Experimental</Badge>
                  <span className="text-[10px] text-muted-foreground italic">Experimental — for research purposes only.</span>
                </div>

                {isLoading ? (
                  <div className="py-12 text-center text-muted-foreground animate-pulse">Fetching market data...</div>
                ) : data ? (
                  <div className="p-4 bg-teal/5 border border-teal/20 rounded-md">
                    <div className="flex justify-between items-start mb-6">
                      <div>
                        <h3 className="text-4xl font-bold">${data?.info?.currentPrice?.toFixed(2) ?? '—'}</h3>
                        <div className="flex items-center gap-2 mt-2">
                          {data?.info?.previousClose && data?.info?.currentPrice ? (
                            <>
                              <span className={`text - sm font - medium ${data.info.currentPrice >= data.info.previousClose ? 'text-green-500' : 'text-red-500'} `}>
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
                        <Badge className="mt-2" variant="outline">
                          {data.recommendations && data.recommendations.length > 0 ? data.recommendations[0].toGrade ?? 'Hold' : 'Hold'}
                        </Badge>
                      </div>
                    </div>

                    {/* ML BIAS OVERVIEW */}
                    {mlData?.predictions && (
                      <div className="mb-6 p-4 border rounded-lg bg-primary/5 flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <Badge variant="secondary" className="bg-amber-500/10 text-amber-600 border-amber-200">🧪 Experimental</Badge>
                          <div>
                            <p className="text-xs text-muted-foreground uppercase font-semibold text-[10px]">ML Directional Bias</p>
                            <p className={`text - lg font - black ${mlData.predictions.signal === 'BUY' ? 'text-green-600' : mlData.predictions.signal === 'SELL' ? 'text-red-600' : 'text-amber-600'} `}>
                              {mlData.predictions.signal || 'NEUTRAL'}
                            </p>
                          </div>
                        </div>
                        <Button variant="ghost" size="sm" className="text-primary hover:bg-primary/10" onClick={() => {
                          // This is a bit of a hack to switch tabs if we don't have controlled state, 
                          // but Research.tsx uses uncontrolled Tabs with defaultValue
                          const mlTab = document.querySelector('[data-value="ml"]') as HTMLElement;
                          mlTab?.click();
                        }}>
                          View ML Insights →
                        </Button>
                      </div>
                    )}

                    {/* ACTION BUTTONS - INTENT HANDOFF */}
                    <div className="flex flex-wrap gap-2 mb-6">
                      <Button size="sm" variant="outline" onClick={() => handleTradeIntent('buy')}>Buy (Intent Only — Execution in Trading Terminal)</Button>
                      <Button size="sm" variant="outline" onClick={() => handleTradeIntent('sell')}>Sell (Intent Only — Execution in Trading Terminal)</Button>
                      <Button size="sm" variant="outline" onClick={() => toast({ title: "Read-Only Page", description: "This research view is read-only." })}>+ Watchlist</Button>
                      <Button size="sm" variant="secondary" onClick={() => window.location.href = `/ trading ? symbol = ${symbol}& tab=optionChain`}>Option Chain</Button>
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
                            'No company summary available.'
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
                ) : (
                  <div className="py-12 flex flex-col items-center justify-center text-muted-foreground">
                    <p className="mb-2 italic">Search for a symbol to generate insights.</p>
                  </div>
                )}
              </CustomCard>

              <CustomCard title="Key Performance Indicators">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">Market Cap</p>
                    <p className="text-xl font-semibold">
                      {data?.info?.marketCap
                        ? `$${(data.info.marketCap / 1e12).toFixed(2)} T`
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

            <TabsContent value="technical" className="space-y-6">
              <CustomCard title="Technical Analysis">
                <p className="text-muted-foreground mb-4">Technical indicators and chart patterns</p>
                {isLoading ? (
                  <div className="py-12 text-center text-muted-foreground animate-pulse">Fetching market data...</div>
                ) : data?.technicals ? (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-4 border rounded-lg">
                        <p className="text-sm text-muted-foreground mb-1">SMA 20</p>
                        <p className="text-xl font-bold">${data.technicals.sma_20?.toFixed(2) ?? '—'}</p>
                      </div>
                      <div className="p-4 border rounded-lg">
                        <p className="text-sm text-muted-foreground mb-1">RSI 14</p>
                        <p className="text-xl font-bold">{data.technicals.rsi_14?.toFixed(2) ?? '—'}</p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="py-12 text-center text-muted-foreground">No technical data available for this symbol.</div>
                )}
              </CustomCard>
            </TabsContent>

            <TabsContent value="fundamental" className="space-y-6">
              <CustomCard title="Fundamental Analysis">
                <p className="text-muted-foreground mb-4">Financial metrics and company fundamentals</p>
                {isLoading ? (
                  <div className="py-12 text-center text-muted-foreground animate-pulse">Fetching market data...</div>
                ) : data?.financials ? (
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
                                ? `$${(data.financials.market_cap / 1e12).toFixed(2)} T`
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
                                ? `$${(data.financials.revenue / 1e9).toFixed(2)} B`
                                : '—'}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell>Net Income</TableCell>
                            <TableCell>
                              {data.financials.net_income
                                ? `$${(data.financials.net_income / 1e9).toFixed(2)} B`
                                : '—'}
                            </TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                ) : (
                  <div className="py-12 text-center text-muted-foreground">No fundamental data available for this symbol.</div>
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
                          ? `$${(data.financials.market_cap / 1e12).toFixed(2)} T`
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
                                return val != null && !isNaN(val) ? val.toFixed(2) : '—';
                              })()}
                            </TableCell>
                            <TableCell>
                              {mlData?.indicator_series?.sma20 && (
                                <Switch id="tbl-sma20" checked={overlays.sma20} onCheckedChange={(v) => setOverlays(o => ({ ...o, sma20: !!v }))} />
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
                                <Switch id="tbl-sma50" checked={overlays.sma50} onCheckedChange={(v) => setOverlays(o => ({ ...o, sma50: !!v }))} />
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
                                <Switch id="tbl-sma200" checked={overlays.sma200} onCheckedChange={(v) => setOverlays(o => ({ ...o, sma200: !!v }))} />
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
                                <Switch id="tbl-ema12" checked={overlays.ema12} onCheckedChange={(v) => setOverlays(o => ({ ...o, ema12: !!v }))} />
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
                                <Switch id="tbl-ema26" checked={overlays.ema26} onCheckedChange={(v) => setOverlays(o => ({ ...o, ema26: !!v }))} />
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
                                <Switch id="tbl-bb" checked={overlays.bb} onCheckedChange={(v) => setOverlays(o => ({ ...o, bb: !!v }))} />
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
                                <Switch id="tbl-kelt" checked={overlays.kelt} onCheckedChange={(v) => setOverlays(o => ({ ...o, kelt: !!v }))} />
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
                                <Switch id="tbl-piv" checked={overlays.pivots} onCheckedChange={(v) => setOverlays(o => ({ ...o, pivots: !!v }))} />
                              )}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell className="font-medium">Fibonacci Levels</TableCell>
                            <TableCell>
                              {mlData?.indicator_series?.levels?.fibonacci?.levels ? (
                                Object.entries(mlData.indicator_series.levels.fibonacci.levels)
                                  .slice(0, 3)
                                  .map(([k, v]: any) => `${k}: $${v?.toFixed(2)} `)
                                  .join(' / ')
                              ) : '—'}
                            </TableCell>
                            <TableCell>
                              {mlData?.indicator_series?.levels?.fibonacci && (
                                <Switch id="tbl-fib" checked={overlays.fib} onCheckedChange={(v) => setOverlays(o => ({ ...o, fib: !!v }))} />
                              )}
                            </TableCell>
                          </TableRow>
                          <TableRow>
                            <TableCell className="font-medium">RSI 14</TableCell>
                            <TableCell>
                              <span className={`font - semibold ${(data.technicals.rsi_14 ?? 0) > 70 ? 'text-red-500' :
                                (data.technicals.rsi_14 ?? 0) < 30 ? 'text-green-500' : ''
                                } `}>
                                {(() => {
                                  // Prefer mlData.technical_features (standardized) then series fallback
                                  const val = mlData?.technical_features?.rsi_14 ?? data.technicals.rsi_14 ?? mlData?.indicator_series?.rsi_14?.filter((v: any) => v != null).slice(-1)[0];
                                  return val != null && !isNaN(val) ? val.toFixed(2) : '—';
                                })()}
                              </span>
                              {' '}
                              {(mlData?.technical_features?.rsi_14 ?? data.technicals.rsi_14 ?? 0) > 70 ? '(Overbought)' :
                                (mlData?.technical_features?.rsi_14 ?? data.technicals.rsi_14 ?? 0) < 30 ? '(Oversold)' : '(Neutral)'}
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

            <TabsContent value="ml" className="space-y-6">
              <CustomCard title="ML Insights">
                <div className="flex items-center gap-2 mb-4">
                  <Badge variant="secondary" className="bg-amber-500/10 text-amber-600 border-amber-200">🧪 Experimental</Badge>
                  <span className="text-[10px] text-muted-foreground italic">Experimental — for research purposes only.</span>
                </div>

                <div className="mb-6 flex gap-2">
                  <Button onClick={async () => {
                    if (!symbol || symbol.trim() === '') return;
                    setMlLoading(true);
                    setMlError(null);
                    try {
                      const period = periodMap[timeframe] || '2y';
                      const resp = await fetch(`/ api / v1 / research - ml / ${encodeURIComponent(symbol.trim())}/ml-features?period=${period}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
                      });
                      if (!resp.ok) throw new Error(`API error ${resp.status}`);
                      const json = await resp.json();
                      setMlData(json);
                    } catch (err: any) {
                      setMlError('Failed to load ML insights.');
                    } finally {
                      setMlLoading(false);
                    }
                  }} disabled={mlLoading || !symbol.trim()}>
                    {mlLoading ? "Loading..." : "Load ML Insights"}
                  </Button >
                  <Button disabled variant="outline" className="opacity-50 cursor-not-allowed">Train Model (Disabled)</Button>
                </div >

                {mlError && <p className="text-sm text-destructive mb-4">{mlError}</p>}

                {
                  mlData ? (
                    <div className="space-y-6">
                      {/* GUARDRAIL: Verify predictions block */}
                      {!mlData.predictions ? (
                        <div className="p-8 text-center border border-dashed rounded-lg text-muted-foreground">
                          <p className="font-bold text-amber-600 mb-1">ML Core Response Missing</p>
                          <p className="text-sm italic">Predictions were not found in the backend response for this symbol.</p>
                        </div>
                      ) : (
                        <>
                          {/* ML INTERPRETATION PANEL */}
                          <div className="p-5 border rounded-xl bg-primary/5 space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                              {/* Directional Bias */}
                              <div>
                                <p className="text-xs text-muted-foreground uppercase font-black mb-1 text-[10px]">Directional Bias</p>
                                <p className={`text-2xl font-black ${mlData.predictions.signal === 'BUY' ? 'text-green-600' : mlData.predictions.signal === 'SELL' ? 'text-red-600' : 'text-amber-600'}`}>
                                  {mlData.predictions.signal || 'NEUTRAL'}
                                </p>
                              </div>

                              {/* Prediction Horizon */}
                              <div>
                                <p className="text-xs text-muted-foreground uppercase font-black mb-1 text-[10px]">Prediction Horizon</p>
                                <p className="text-lg font-bold">Short-term Horizon (heuristic)</p>
                              </div>

                              {/* Signal Strength */}
                              <div>
                                <p className="text-xs text-muted-foreground uppercase font-black mb-1 text-[10px]">Signal Strength</p>
                                <p className={`text-lg font-bold ${mlData.predictions.signal_confidence > 0.7 ? 'text-green-600' : mlData.predictions.signal_confidence > 0.4 ? 'text-amber-600' : 'text-muted-foreground'}`}>
                                  {mlData.predictions.signal_confidence > 0.7 ? 'Strong' : mlData.predictions.signal_confidence > 0.4 ? 'Moderate' : 'Weak'}
                                </p>
                                <p className="text-[8px] text-muted-foreground italic mt-0.5">Derived from ensemble confidence score</p>
                              </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t">
                              {/* Intelligence Source */}
                              <div>
                                <p className="text-xs text-muted-foreground uppercase font-black mb-1 text-[10px]">Intelligence Source</p>
                                <p className="text-sm font-medium">
                                  {mlData.predictions.ml_model_used ? 'Ensemble Verified Signal' : 'Heuristic Approximation'}
                                </p>
                              </div>

                              {/* Uncertainty Note */}
                              <div>
                                <p className="text-xs text-muted-foreground uppercase font-black mb-1 text-[10px]">Uncertainty Note</p>
                                <p className="text-sm italic text-muted-foreground">
                                  {mlData.predictions.signal_confidence < 0.4 ? 'Confidence < 0.4 increases uncertainty in volatile sessions.' : 'Standard operational variance; higher uncertainty in high volatility sessions.'}
                                </p>
                              </div>
                            </div>
                          </div>

                          {/* PRICE ZONES (Targets & S/R) */}
                          <PriceZonesPanel predictions={mlData.predictions} />
                        </>
                      )}

                      {/* KEY CONTRIBUTING FACTORS */}
                      <div>
                        <h4 className="font-bold text-sm mb-3">Key Contributing Factors (Heuristic Mapping)</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {mlData.technical_features ? (
                            <>
                              {mlData.technical_features.rsi_14 !== undefined && (
                                <div className="p-3 border rounded-lg bg-background flex justify-between items-center">
                                  <div>
                                    <p className="text-xs text-muted-foreground font-medium">RSI (14)</p>
                                    <p className="text-sm font-bold">{mlData.technical_features.rsi_14.toFixed(2)}</p>
                                  </div>
                                  <Badge variant="outline" className={mlData.technical_features.rsi_14 > 70 ? 'text-red-500 border-red-200 bg-red-50' : mlData.technical_features.rsi_14 < 30 ? 'text-green-500 border-green-200 bg-green-50' : ''}>
                                    {mlData.technical_features.rsi_14 > 70 ? 'Bearish (Overbought)' : mlData.technical_features.rsi_14 < 30 ? 'Bullish (Oversold)' : 'Neutral'}
                                  </Badge>
                                </div>
                              )}
                              {mlData.technical_features.momentum_10 !== undefined && (
                                <div className="p-3 border rounded-lg bg-background flex justify-between items-center">
                                  <div>
                                    <p className="text-xs text-muted-foreground font-medium">Momentum (10)</p>
                                    <p className="text-sm font-bold">{mlData.technical_features.momentum_10.toFixed(2)}</p>
                                  </div>
                                  <Badge variant="outline" className={mlData.technical_features.momentum_10 > 0 ? 'text-green-500 border-green-200 bg-green-50' : 'text-red-500 border-red-200 bg-red-50'}>
                                    {mlData.technical_features.momentum_10 > 0 ? 'Bullish Bias' : 'Bearish Bias'}
                                  </Badge>
                                </div>
                              )}
                            </>
                          ) : (
                            <div className="col-span-full py-4 text-center text-muted-foreground italic border border-dashed rounded-lg">
                              Detailed factor mapping unavailable for this symbol.
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="py-12 text-center text-muted-foreground border border-dashed rounded-md">
                      No ML insights loaded. Click &quot;Load ML Insights&quot; to fetch features.
                    </div>
                  )
                }
              </CustomCard >
            </TabsContent >

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
          </Tabs >
        </div >
      </div >
      <TradeDialog
        isOpen={isTradeOpen}
        onClose={() => setTradeOpen(false)}
        symbol={symbol}
        currentPrice={data?.info?.currentPrice || 0}
        initialSide={tradeSide}
      />
    </>
  );

  if (!standalone) return content;

  return (
    <AppLayout title="AI Research Reports" description="Get AI-generated insights and analysis on stocks">
      {content}
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

    const toLine = (arr?: (number | null)[]) => {
      if (!arr || !dates) return undefined;
      const pts = [] as { time: number, value: number }[];
      for (let i = 0; i < Math.min(arr.length, dates.length); i++) {
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