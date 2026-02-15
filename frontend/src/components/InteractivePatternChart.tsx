import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  Line,
  ReferenceArea,
  ReferenceLine,
  Brush,
} from 'recharts';

type SeriesDict = Record<string, number[] | (number | null)[]>;

interface IndicatorSeries {
  dates: string[];
  close: (number | null)[];
  sma20?: (number | null)[];
  sma50?: (number | null)[];
  sma200?: (number | null)[];
  ema12?: (number | null)[];
  ema26?: (number | null)[];
  bb?: { upper?: (number | null)[]; middle?: (number | null)[]; lower?: (number | null)[] };
}

interface Pattern {
  type: string;
  start_date?: string;
  end_date?: string;
  price_level?: number | string;
  confidence?: number;
}

interface Props {
  series: IndicatorSeries;
  patterns?: Pattern[];
  height?: number;
}

const InteractivePatternChart: React.FC<Props> = ({ series, patterns = [], height = 360 }) => {
  if (!series || !series.dates || series.dates.length === 0) {
    return <div className="h-64 flex items-center justify-center text-sm text-muted-foreground">No series to visualize.</div>;
  }

  const n = series.dates.length;
  const safe = (arr?: (number | null)[]) => (arr && arr.length === n ? arr : Array(n).fill(null));
  const data = Array.from({ length: n }, (_, i) => ({
    date: series.dates[i],
    close: series.close?.[i] ?? null,
    sma20: safe(series.sma20)[i],
    sma50: safe(series.sma50)[i],
    sma200: safe(series.sma200)[i],
    ema12: safe(series.ema12)[i],
    ema26: safe(series.ema26)[i],
    bb_upper: safe(series.bb?.upper)[i],
    bb_middle: safe(series.bb?.middle)[i],
    bb_lower: safe(series.bb?.lower)[i],
  }));

  // Map patterns into chart reference shapes
  const refAreas = (patterns || [])
    .filter(p => p.start_date && p.end_date)
    .map((p, idx) => (
      <ReferenceArea key={`area-${idx}`} x1={(p.start_date as string).slice(0, 10)} x2={(p.end_date as string).slice(0, 10)} strokeOpacity={0} fill="#fde68a" fillOpacity={0.25} />
    ));

  const refLines = (patterns || [])
    .filter(p => p.price_level)
    .map((p, idx) => (
      <ReferenceLine key={`line-${idx}`} y={typeof p.price_level === 'number' ? p.price_level : parseFloat(String(p.price_level))} stroke="#b45309" strokeDasharray="4 3" ifOverflow="extendDomain" />
    ));

  return (
    <div className="w-full" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 16, right: 24, left: 8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" minTickGap={24} />
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Legend />
          {refAreas}
          {refLines}

          <Line type="monotone" dataKey="close" name="Close" stroke="#111827" dot={false} strokeWidth={1.5} />
          <Line type="monotone" dataKey="sma20" name="SMA 20" stroke="#1d4ed8" dot={false} strokeWidth={1.2} />
          <Line type="monotone" dataKey="sma50" name="SMA 50" stroke="#0ea5a4" dot={false} strokeWidth={1.2} />
          <Line type="monotone" dataKey="sma200" name="SMA 200" stroke="#7c3aed" dot={false} strokeWidth={1.2} />
          <Line type="monotone" dataKey="bb_upper" name="BB Upper" stroke="#9ca3af" dot={false} strokeWidth={1} />
          <Line type="monotone" dataKey="bb_lower" name="BB Lower" stroke="#9ca3af" dot={false} strokeWidth={1} />

          <Brush dataKey="date" height={24} travellerWidth={8} stroke="#8884d8" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default InteractivePatternChart;
