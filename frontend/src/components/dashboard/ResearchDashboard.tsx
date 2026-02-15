import React, { useState, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { 
  Newspaper, 
  TrendingUp, 
  TrendingDown,
  Globe,
  Users,
  Building2,
  Sparkles,
  ExternalLink,
  Clock,
  BarChart3,
  PieChart,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Minus
} from 'lucide-react';
import { PieChart as RechartsPie, Pie, Cell, ResponsiveContainer, Treemap } from 'recharts';

interface NewsItem {
  id: string;
  title: string;
  source: string;
  time: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  symbols: string[];
  url: string;
}

interface SectorData {
  name: string;
  value: number;
  change: number;
  color: string;
}

interface FIIDIIData {
  date: string;
  fiiNet: number;
  diiNet: number;
}

interface MarketBreadth {
  advances: number;
  declines: number;
  unchanged: number;
  advanceVolume: number;
  declineVolume: number;
}

// Mock news data
const generateNews = (): NewsItem[] => [
  {
    id: '1',
    title: 'RBI keeps repo rate unchanged at 6.5%, maintains stance',
    source: 'Economic Times',
    time: '15m ago',
    sentiment: 'neutral',
    symbols: ['HDFCBANK', 'ICICIBANK', 'SBIN'],
    url: '#'
  },
  {
    id: '2',
    title: 'Reliance Industries reports 12% rise in Q3 profit',
    source: 'Moneycontrol',
    time: '32m ago',
    sentiment: 'positive',
    symbols: ['RELIANCE'],
    url: '#'
  },
  {
    id: '3',
    title: 'IT stocks surge as rupee weakens against dollar',
    source: 'Livemint',
    time: '1h ago',
    sentiment: 'positive',
    symbols: ['TCS', 'INFY', 'WIPRO'],
    url: '#'
  },
  {
    id: '4',
    title: 'Auto sector faces headwinds amid chip shortage concerns',
    source: 'Business Standard',
    time: '2h ago',
    sentiment: 'negative',
    symbols: ['MARUTI', 'TATAMOTORS'],
    url: '#'
  },
  {
    id: '5',
    title: 'Pharma stocks rally on positive FDA developments',
    source: 'Reuters',
    time: '3h ago',
    sentiment: 'positive',
    symbols: ['SUNPHARMA', 'DRREDDY'],
    url: '#'
  },
];

const SECTOR_DATA: SectorData[] = [
  { name: 'IT', value: 28.5, change: 2.3, color: 'hsl(168, 80%, 50%)' },
  { name: 'Banking', value: 22.1, change: -0.8, color: 'hsl(220, 60%, 55%)' },
  { name: 'Energy', value: 15.3, change: 1.2, color: 'hsl(45, 93%, 58%)' },
  { name: 'FMCG', value: 12.8, change: 0.5, color: 'hsl(280, 60%, 55%)' },
  { name: 'Pharma', value: 10.2, change: 3.1, color: 'hsl(0, 72%, 55%)' },
  { name: 'Auto', value: 11.1, change: -1.5, color: 'hsl(32, 90%, 55%)' },
];

const HEATMAP_DATA = [
  { name: 'RELIANCE', size: 4500, change: 2.3 },
  { name: 'TCS', size: 4200, change: 1.8 },
  { name: 'HDFCBANK', size: 3800, change: -0.5 },
  { name: 'INFY', size: 3500, change: 2.1 },
  { name: 'ICICIBANK', size: 3200, change: 0.3 },
  { name: 'BHARTIARTL', size: 2800, change: -1.2 },
  { name: 'ITC', size: 2600, change: 0.8 },
  { name: 'SBIN', size: 2400, change: -0.2 },
  { name: 'LT', size: 2200, change: 1.5 },
  { name: 'BAJFINANCE', size: 2000, change: -2.1 },
];

const SentimentIcon: React.FC<{ sentiment: NewsItem['sentiment'] }> = ({ sentiment }) => {
  if (sentiment === 'positive') return <TrendingUp size={14} className="text-success" />;
  if (sentiment === 'negative') return <TrendingDown size={14} className="text-destructive" />;
  return <Minus size={14} className="text-muted-foreground" />;
};

const NewsCard: React.FC<{ news: NewsItem }> = ({ news }) => (
  <a 
    href={news.url}
    className="block p-4 rounded-xl bg-muted/30 hover:bg-muted/50 transition-all group"
  >
    <div className="flex items-start justify-between gap-3">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1.5">
          <SentimentIcon sentiment={news.sentiment} />
          <span className="text-xs text-muted-foreground">{news.source}</span>
          <span className="text-xs text-muted-foreground">•</span>
          <span className="text-xs text-muted-foreground flex items-center gap-1">
            <Clock size={10} />
            {news.time}
          </span>
        </div>
        <h4 className="text-sm font-medium text-foreground group-hover:text-primary transition-colors line-clamp-2">
          {news.title}
        </h4>
        <div className="flex flex-wrap gap-1.5 mt-2">
          {news.symbols.map(symbol => (
            <span key={symbol} className="px-2 py-0.5 rounded text-xs bg-accent font-mono">
              {symbol}
            </span>
          ))}
        </div>
      </div>
      <ExternalLink size={14} className="text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
    </div>
  </a>
);

const SectorHeatmapCell: React.FC<{ data: typeof HEATMAP_DATA[0]; x: number; y: number; width: number; height: number }> = ({ 
  data, x, y, width, height 
}) => {
  const bgColor = data.change >= 0 
    ? `hsl(152, 70%, ${40 + Math.min(data.change * 5, 20)}%)`
    : `hsl(0, 72%, ${45 + Math.min(Math.abs(data.change) * 5, 20)}%)`;

  if (width < 40 || height < 30) return null;

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        fill={bgColor}
        rx={8}
        className="transition-all hover:opacity-80 cursor-pointer"
      />
      <text
        x={x + width / 2}
        y={y + height / 2 - 6}
        textAnchor="middle"
        fill="white"
        fontSize={width < 60 ? 9 : 11}
        fontWeight="600"
        fontFamily="JetBrains Mono"
      >
        {data.name}
      </text>
      <text
        x={x + width / 2}
        y={y + height / 2 + 10}
        textAnchor="middle"
        fill="white"
        fontSize={width < 60 ? 8 : 10}
        fontFamily="JetBrains Mono"
        opacity={0.9}
      >
        {data.change >= 0 ? '+' : ''}{data.change.toFixed(1)}%
      </text>
    </g>
  );
};

export const ResearchDashboard: React.FC = () => {
  const [news] = useState<NewsItem[]>(generateNews);
  const [marketBreadth] = useState<MarketBreadth>({
    advances: 1245,
    declines: 876,
    unchanged: 112,
    advanceVolume: 45600000000,
    declineVolume: 32100000000
  });
  const [fiiDii] = useState<FIIDIIData>({
    date: new Date().toISOString().split('T')[0],
    fiiNet: 1250.5,
    diiNet: -890.3
  });

  const breadthRatio = marketBreadth.advances / (marketBreadth.advances + marketBreadth.declines);

  return (
    <div className="space-y-6">
      {/* Top Row - Market Breadth & FII/DII */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Market Breadth */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="p-2 rounded-xl bg-primary/10">
              <Activity className="text-primary" size={20} />
            </div>
            <div>
              <h3 className="font-semibold">Market Breadth</h3>
              <p className="text-xs text-muted-foreground">NSE Advance/Decline</p>
            </div>
          </div>

          <div className="space-y-4">
            {/* Visual bar */}
            <div className="h-4 rounded-full overflow-hidden bg-muted flex">
              <div 
                className="h-full bg-success transition-all"
                style={{ width: `${breadthRatio * 100}%` }}
              />
              <div 
                className="h-full bg-destructive transition-all"
                style={{ width: `${(1 - breadthRatio) * 100}%` }}
              />
            </div>

            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-success">{marketBreadth.advances}</p>
                <p className="text-xs text-muted-foreground">Advances</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-destructive">{marketBreadth.declines}</p>
                <p className="text-xs text-muted-foreground">Declines</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-muted-foreground">{marketBreadth.unchanged}</p>
                <p className="text-xs text-muted-foreground">Unchanged</p>
              </div>
            </div>

            <div className="pt-3 border-t border-border">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">A/D Ratio</span>
                <span className={cn(
                  "font-semibold",
                  breadthRatio > 0.5 ? "text-success" : "text-destructive"
                )}>
                  {(marketBreadth.advances / marketBreadth.declines).toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* FII/DII Data */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="p-2 rounded-xl bg-primary/10">
              <Users className="text-primary" size={20} />
            </div>
            <div>
              <h3 className="font-semibold">FII/DII Activity</h3>
              <p className="text-xs text-muted-foreground">Today's Net Flow (₹ Cr)</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-muted/30">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Globe size={16} className="text-muted-foreground" />
                  <span className="text-sm font-medium">FII/FPI</span>
                </div>
                <div className={cn(
                  "flex items-center gap-1 font-bold",
                  fiiDii.fiiNet >= 0 ? "text-success" : "text-destructive"
                )}>
                  {fiiDii.fiiNet >= 0 ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
                  ₹{Math.abs(fiiDii.fiiNet).toFixed(0)} Cr
                </div>
              </div>
              <div className="h-2 rounded-full bg-muted overflow-hidden">
                <div 
                  className={cn(
                    "h-full transition-all",
                    fiiDii.fiiNet >= 0 ? "bg-success" : "bg-destructive"
                  )}
                  style={{ width: `${Math.min(Math.abs(fiiDii.fiiNet) / 30, 100)}%` }}
                />
              </div>
            </div>

            <div className="p-4 rounded-xl bg-muted/30">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Building2 size={16} className="text-muted-foreground" />
                  <span className="text-sm font-medium">DII</span>
                </div>
                <div className={cn(
                  "flex items-center gap-1 font-bold",
                  fiiDii.diiNet >= 0 ? "text-success" : "text-destructive"
                )}>
                  {fiiDii.diiNet >= 0 ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
                  ₹{Math.abs(fiiDii.diiNet).toFixed(0)} Cr
                </div>
              </div>
              <div className="h-2 rounded-full bg-muted overflow-hidden">
                <div 
                  className={cn(
                    "h-full transition-all",
                    fiiDii.diiNet >= 0 ? "bg-success" : "bg-destructive"
                  )}
                  style={{ width: `${Math.min(Math.abs(fiiDii.diiNet) / 30, 100)}%` }}
                />
              </div>
            </div>

            <div className="pt-2 text-center">
              <p className="text-xs text-muted-foreground">
                Net: <span className={cn(
                  "font-semibold",
                  (fiiDii.fiiNet + fiiDii.diiNet) >= 0 ? "text-success" : "text-destructive"
                )}>
                  ₹{(fiiDii.fiiNet + fiiDii.diiNet).toFixed(0)} Cr
                </span>
              </p>
            </div>
          </div>
        </div>

        {/* Sector Performance */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="p-2 rounded-xl bg-primary/10">
              <PieChart className="text-primary" size={20} />
            </div>
            <div>
              <h3 className="font-semibold">Sector Performance</h3>
              <p className="text-xs text-muted-foreground">Index weightage & change</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="w-24 h-24">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsPie>
                  <Pie
                    data={SECTOR_DATA}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={25}
                    outerRadius={40}
                    paddingAngle={2}
                  >
                    {SECTOR_DATA.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                </RechartsPie>
              </ResponsiveContainer>
            </div>
            <div className="flex-1 space-y-1.5">
              {SECTOR_DATA.slice(0, 5).map(sector => (
                <div key={sector.name} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: sector.color }}
                    />
                    <span className="text-muted-foreground">{sector.name}</span>
                  </div>
                  <span className={cn(
                    "font-mono font-medium",
                    sector.change >= 0 ? "text-success" : "text-destructive"
                  )}>
                    {sector.change >= 0 ? '+' : ''}{sector.change}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Row - Heatmap & News */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Market Heatmap */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="p-2 rounded-xl bg-primary/10">
              <BarChart3 className="text-primary" size={20} />
            </div>
            <div>
              <h3 className="font-semibold">Market Heatmap</h3>
              <p className="text-xs text-muted-foreground">NIFTY 50 constituents by market cap</p>
            </div>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <Treemap
                data={HEATMAP_DATA}
                dataKey="size"
                aspectRatio={4/3}
                stroke="hsl(var(--background))"
                content={<SectorHeatmapCell data={{} as any} x={0} y={0} width={0} height={0} />}
              />
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-center gap-6 mt-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-success" />
              <span className="text-muted-foreground">Gainers</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-destructive" />
              <span className="text-muted-foreground">Losers</span>
            </div>
          </div>
        </div>

        {/* News Feed */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-primary/10">
                <Newspaper className="text-primary" size={20} />
              </div>
              <div>
                <h3 className="font-semibold">Market News</h3>
                <p className="text-xs text-muted-foreground">Latest updates with sentiment</p>
              </div>
            </div>
            <span className="badge-live flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-success pulse-dot" />
              Live
            </span>
          </div>

          <div className="space-y-3 max-h-80 overflow-y-auto scrollbar-hide">
            {news.map(item => (
              <NewsCard key={item.id} news={item} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};