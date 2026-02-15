import React, { useState, useMemo } from 'react';
import { useTrading } from '@/context/TradingContext';
import { cn } from '@/lib/utils';
import {
  Activity,
  TrendingUp,
  TrendingDown,
  Gauge,
  Target,
  BarChart3,
  PieChart,
  Calculator,
  Info,
  RefreshCw,
  Zap
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, Cell } from 'recharts';

interface OptionGreeks {
  delta: number;
  gamma: number;
  theta: number;
  vega: number;
  rho: number;
}

interface IVData {
  strike: number;
  callIV: number;
  putIV: number;
  skew: number;
}

interface OIData {
  strike: number;
  callOI: number;
  putOI: number;
  callOIChange: number;
  putOIChange: number;
}

const formatNumber = (value: number, decimals: number = 2): string => {
  if (Math.abs(value) >= 10000000) return `${(value / 10000000).toFixed(2)}Cr`;
  if (Math.abs(value) >= 100000) return `${(value / 100000).toFixed(2)}L`;
  return value.toFixed(decimals);
};

// Generate mock data
const generateIVData = (spotPrice: number): IVData[] => {
  const data: IVData[] = [];
  const baseStrike = Math.round(spotPrice / 100) * 100;

  for (let i = -10; i <= 10; i++) {
    const strike = baseStrike + i * 100;
    const distance = Math.abs(spotPrice - strike) / spotPrice;
    const atmIV = 14 + Math.random() * 2;
    const skewFactor = strike < spotPrice ? 0.8 : 1.2;

    const callIV = atmIV + distance * 50 * (strike > spotPrice ? 0.5 : 1.5) + Math.random() * 2;
    const putIV = atmIV + distance * 50 * skewFactor + Math.random() * 2;

    data.push({
      strike,
      callIV,
      putIV,
      skew: putIV - callIV,
    });
  }

  return data;
};

const generateOIData = (spotPrice: number): OIData[] => {
  const data: OIData[] = [];
  const baseStrike = Math.round(spotPrice / 100) * 100;

  for (let i = -8; i <= 8; i++) {
    const strike = baseStrike + i * 100;

    data.push({
      strike,
      callOI: Math.round(Math.random() * 5000000 + 500000),
      putOI: Math.round(Math.random() * 5000000 + 500000),
      callOIChange: Math.round((Math.random() - 0.5) * 100000),
      putOIChange: Math.round((Math.random() - 0.5) * 100000),
    });
  }

  return data;
};

const GreekCard: React.FC<{
  label: string;
  value: number;
  description: string;
  color: string;
}> = ({ label, value, description, color }) => (
  <div className="glass-card p-4 relative overflow-hidden group">
    <div className="flex items-start justify-between">
      <div>
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">{label}</p>
        <p className={cn("text-2xl font-bold font-mono mt-1", color)}>
          {value >= 0 ? '+' : ''}{value.toFixed(4)}
        </p>
      </div>
      <button className="p-1.5 rounded-lg hover:bg-accent opacity-0 group-hover:opacity-100 transition-opacity">
        <Info size={14} className="text-muted-foreground" />
      </button>
    </div>
    <p className="text-xs text-muted-foreground mt-2">{description}</p>
  </div>
);

const PCRGauge: React.FC<{ pcr: number }> = ({ pcr }) => {
  const angle = Math.min(Math.max((pcr - 0.5) * 180, -90), 90);
  const sentiment = pcr > 1.2 ? 'Bullish' : pcr < 0.8 ? 'Bearish' : 'Neutral';
  const sentimentColor = pcr > 1.2 ? 'text-success' : pcr < 0.8 ? 'text-destructive' : 'text-warning';

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Gauge className="text-primary" size={20} />
          <h3 className="font-semibold">Put-Call Ratio</h3>
        </div>
        <span className={cn("text-sm font-semibold", sentimentColor)}>{sentiment}</span>
      </div>

      <div className="relative h-32 flex items-center justify-center">
        {/* Gauge background */}
        <svg className="absolute w-48 h-24" viewBox="0 0 200 100">
          {/* Background arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="hsl(var(--muted))"
            strokeWidth="12"
            strokeLinecap="round"
          />
          {/* Colored sections */}
          <path
            d="M 20 100 A 80 80 0 0 1 60 40"
            fill="none"
            stroke="hsl(var(--destructive))"
            strokeWidth="12"
            strokeLinecap="round"
            opacity="0.3"
          />
          <path
            d="M 60 40 A 80 80 0 0 1 140 40"
            fill="none"
            stroke="hsl(var(--warning))"
            strokeWidth="12"
            strokeLinecap="round"
            opacity="0.3"
          />
          <path
            d="M 140 40 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="hsl(var(--success))"
            strokeWidth="12"
            strokeLinecap="round"
            opacity="0.3"
          />
          {/* Needle */}
          <g transform={`rotate(${angle}, 100, 100)`}>
            <line
              x1="100"
              y1="100"
              x2="100"
              y2="35"
              stroke="hsl(var(--foreground))"
              strokeWidth="3"
              strokeLinecap="round"
            />
            <circle cx="100" cy="100" r="6" fill="hsl(var(--foreground))" />
          </g>
        </svg>

        <div className="absolute bottom-0 text-center">
          <p className="text-3xl font-bold font-mono">{pcr.toFixed(2)}</p>
          <p className="text-xs text-muted-foreground">OI Based PCR</p>
        </div>
      </div>

      <div className="flex justify-between text-xs text-muted-foreground mt-4">
        <span>Bearish (0.5)</span>
        <span>Neutral (1.0)</span>
        <span>Bullish (1.5)</span>
      </div>
    </div>
  );
};

export const OptionsAnalytics: React.FC = () => {
  const { quotes, selectedSymbol } = useTrading();
  const spotPrice = quotes[selectedSymbol]?.ltp || 24500;

  const [ivData] = useState<IVData[]>(() => generateIVData(spotPrice));
  const [oiData] = useState<OIData[]>(() => generateOIData(spotPrice));

  // Calculate analytics
  const analytics = useMemo(() => {
    const totalCallOI = oiData.reduce((sum, d) => sum + d.callOI, 0);
    const totalPutOI = oiData.reduce((sum, d) => sum + d.putOI, 0);
    const pcr = totalPutOI / totalCallOI;

    // Find max pain
    let maxPainStrike = oiData[0].strike;
    let minPain = Infinity;
    oiData.forEach(d => {
      let pain = 0;
      oiData.forEach(other => {
        if (other.strike < d.strike) {
          pain += other.callOI * (d.strike - other.strike);
        } else if (other.strike > d.strike) {
          pain += other.putOI * (other.strike - d.strike);
        }
      });
      if (pain < minPain) {
        minPain = pain;
        maxPainStrike = d.strike;
      }
    });

    // Max OI strikes
    const maxCallOI = oiData.reduce((max, d) => d.callOI > max.callOI ? d : max, oiData[0]);
    const maxPutOI = oiData.reduce((max, d) => d.putOI > max.putOI ? d : max, oiData[0]);

    // IV percentile (mock)
    const currentIV = ivData.find(d => Math.abs(d.strike - spotPrice) < 100)?.callIV || 15;
    const ivPercentile = 35 + Math.random() * 30;

    return {
      pcr,
      maxPain: maxPainStrike,
      maxCallOIStrike: maxCallOI.strike,
      maxPutOIStrike: maxPutOI.strike,
      totalCallOI,
      totalPutOI,
      currentIV,
      ivPercentile,
    };
  }, [oiData, ivData, spotPrice]);

  // Mock Greeks for ATM option
  const greeks: OptionGreeks = {
    delta: 0.5123,
    gamma: 0.0234,
    theta: -12.45,
    vega: 8.76,
    rho: 0.0156,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20">
            <Activity className="text-primary" size={24} />
          </div>
          <div>
            <h1 className="text-2xl font-bold font-display">Options Analytics</h1>
            <p className="text-sm text-muted-foreground">{selectedSymbol} • Spot: ₹{spotPrice.toFixed(2)}</p>
          </div>
        </div>
        <button className="quick-action">
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="stat-card-primary">
          <p className="metric-label">Max Pain</p>
          <p className="metric-value">₹{analytics.maxPain}</p>
        </div>
        <div className="stat-card">
          <p className="metric-label">PCR (OI)</p>
          <p className="metric-value">{analytics.pcr.toFixed(2)}</p>
        </div>
        <div className="stat-card">
          <p className="metric-label">ATM IV</p>
          <p className="metric-value">{analytics.currentIV.toFixed(1)}%</p>
        </div>
        <div className="stat-card">
          <p className="metric-label">IV Percentile</p>
          <p className="metric-value">{analytics.ivPercentile.toFixed(0)}%</p>
        </div>
        <div className="stat-card-success">
          <p className="metric-label">Max Call OI</p>
          <p className="metric-value">₹{analytics.maxCallOIStrike}</p>
        </div>
        <div className="stat-card-destructive">
          <p className="metric-label">Max Put OI</p>
          <p className="metric-value">₹{analytics.maxPutOIStrike}</p>
        </div>
      </div>

      {/* Greeks & PCR */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <Calculator className="text-primary" size={20} />
            <h3 className="font-semibold">Option Greeks (ATM)</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <GreekCard
              label="Delta (Δ)"
              value={greeks.delta}
              description="Price sensitivity"
              color="text-primary"
            />
            <GreekCard
              label="Gamma (Γ)"
              value={greeks.gamma}
              description="Delta sensitivity"
              color="text-primary"
            />
            <GreekCard
              label="Theta (Θ)"
              value={greeks.theta}
              description="Time decay/day"
              color="text-destructive"
            />
            <GreekCard
              label="Vega (ν)"
              value={greeks.vega}
              description="IV sensitivity"
              color="text-warning"
            />
            <GreekCard
              label="Rho (ρ)"
              value={greeks.rho}
              description="Rate sensitivity"
              color="text-muted-foreground"
            />
          </div>
        </div>

        <PCRGauge pcr={analytics.pcr} />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* IV Smile */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="text-primary" size={20} />
            <h3 className="font-semibold">Implied Volatility Smile</h3>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={ivData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis
                  dataKey="strike"
                  tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                  tickFormatter={(value) => value.toString()}
                />
                <YAxis
                  tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                  tickFormatter={(value) => `${value}%`}
                  domain={['dataMin - 2', 'dataMax + 2']}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--popover))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                  formatter={(value: number) => [`${value.toFixed(2)}%`, '']}
                />
                <Line
                  type="monotone"
                  dataKey="callIV"
                  stroke="hsl(var(--success))"
                  strokeWidth={2}
                  dot={false}
                  name="Call IV"
                />
                <Line
                  type="monotone"
                  dataKey="putIV"
                  stroke="hsl(var(--destructive))"
                  strokeWidth={2}
                  dot={false}
                  name="Put IV"
                />
                {/* Spot price marker */}
                <Line
                  type="monotone"
                  dataKey={() => null}
                  stroke="transparent"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-6 mt-4 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-3 h-0.5 bg-success rounded" />
              <span className="text-muted-foreground">Call IV</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-0.5 bg-destructive rounded" />
              <span className="text-muted-foreground">Put IV</span>
            </div>
          </div>
        </div>

        {/* OI Distribution */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-2 mb-4">
            <PieChart className="text-primary" size={20} />
            <h3 className="font-semibold">Open Interest Distribution</h3>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={oiData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis
                  type="number"
                  tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                  tickFormatter={(value) => formatNumber(value, 0)}
                />
                <YAxis
                  type="category"
                  dataKey="strike"
                  tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                  width={60}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--popover))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px',
                  }}
                  formatter={(value: number) => [formatNumber(value, 0), '']}
                />
                <Bar dataKey="callOI" fill="hsl(var(--success))" opacity={0.7} name="Call OI" />
                <Bar dataKey="putOI" fill="hsl(var(--destructive))" opacity={0.7} name="Put OI" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-between text-xs text-muted-foreground mt-4 px-4">
            <span>Total Call OI: {formatNumber(analytics.totalCallOI, 0)}</span>
            <span>Total Put OI: {formatNumber(analytics.totalPutOI, 0)}</span>
          </div>
        </div>
      </div>

      {/* OI Change Table */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-2 mb-4">
          <Zap className="text-primary" size={20} />
          <h3 className="font-semibold">OI Change Analysis</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="premium-table">
            <thead>
              <tr>
                <th className="rounded-l-lg">Strike</th>
                <th>Call OI</th>
                <th>Call OI Chg</th>
                <th>Put OI</th>
                <th>Put OI Chg</th>
                <th className="rounded-r-lg">Signal</th>
              </tr>
            </thead>
            <tbody>
              {oiData.slice(3, 14).map(d => {
                const isATM = Math.abs(d.strike - spotPrice) < 100;
                const signal = d.callOIChange > 0 && d.putOIChange < 0
                  ? 'Bearish'
                  : d.callOIChange < 0 && d.putOIChange > 0
                    ? 'Bullish'
                    : 'Neutral';

                return (
                  <tr key={d.strike} className={isATM ? 'bg-primary/5' : ''}>
                    <td className={cn("font-semibold", isATM && "text-primary")}>
                      {d.strike}
                      {isATM && <span className="ml-2 text-xs text-primary">(ATM)</span>}
                    </td>
                    <td>{formatNumber(d.callOI, 0)}</td>
                    <td className={cn(
                      "font-medium",
                      d.callOIChange >= 0 ? "text-success" : "text-destructive"
                    )}>
                      {d.callOIChange >= 0 ? '+' : ''}{formatNumber(d.callOIChange, 0)}
                    </td>
                    <td>{formatNumber(d.putOI, 0)}</td>
                    <td className={cn(
                      "font-medium",
                      d.putOIChange >= 0 ? "text-success" : "text-destructive"
                    )}>
                      {d.putOIChange >= 0 ? '+' : ''}{formatNumber(d.putOIChange, 0)}
                    </td>
                    <td>
                      <span className={cn(
                        "px-2 py-0.5 rounded text-xs font-medium",
                        signal === 'Bullish' && "bg-success/20 text-success",
                        signal === 'Bearish' && "bg-destructive/20 text-destructive",
                        signal === 'Neutral' && "bg-muted text-muted-foreground"
                      )}>
                        {signal}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};