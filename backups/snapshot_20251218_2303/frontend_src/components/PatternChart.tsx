import React from 'react';

interface HistRow {
  date: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
}

interface Pattern {
  type: string;
  start_date?: string;
  end_date?: string;
  price_level?: number | string;
  confidence?: number;
}

interface Props {
  history: HistRow[];
  sma20?: number | null;
  sma50?: number | null;
  sma200?: number | null;
  patterns?: Pattern[];
  width?: number;
  height?: number;
}

const PatternChart: React.FC<Props> = ({ history = [], sma20, sma50, sma200, patterns = [], width = 900, height = 320 }) => {
  if (!history || history.length === 0) {
    return <div className="h-64 flex items-center justify-center text-sm text-muted-foreground">No price history available for chart.</div>;
  }

  // We'll render a simple index-based candlestick chart (lightweight, no external deps)
  const padding = 36;
  const innerW = width - padding * 2;
  const innerH = height - padding * 2;

  const closes = history.map(h => (typeof h.close === 'number' ? h.close : 0));
  const highs = history.map(h => (typeof h.high === 'number' ? h.high : 0));
  const lows = history.map(h => (typeof h.low === 'number' ? h.low : 0));

  const maxPrice = Math.max(...highs);
  const minPrice = Math.min(...lows);
  const priceRange = Math.max(1e-6, maxPrice - minPrice);

  const barWidth = Math.max(2, innerW / history.length);

  const xForIndex = (i: number) => padding + i * barWidth + barWidth / 2;
  const yForPrice = (p: number) => padding + innerH - ((p - minPrice) / priceRange) * innerH;

  // helper to find index by date (approximate earliest index with date >= target)
  const findIndexByDate = (d?: string) => {
    if (!d) return 0;
    const t = new Date(d).toISOString().slice(0, 10);
    for (let i = 0; i < history.length; i++) {
      if (history[i].date && history[i].date.slice(0, 10) >= t) return i;
    }
    return history.length - 1;
  };

  return (
    <div className="w-full overflow-auto">
      <svg width="100%" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="xMidYMid meet">
        <rect x={0} y={0} width={width} height={height} fill="transparent" />

        {/* price grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((p, idx) => {
          const price = minPrice + priceRange * (1 - p);
          const y = yForPrice(price);
          return (
            <g key={idx}>
              <line x1={padding} x2={width - padding} y1={y} y2={y} stroke="#eee" strokeWidth={1} />
              <text x={width - padding + 6} y={y + 4} fontSize={10} fill="#666">{price.toFixed(2)}</text>
            </g>
          );
        })}

        {/* pattern shaded spans */}
        {(patterns || []).map((pat, idx) => {
          const s = findIndexByDate(pat.start_date);
          const e = findIndexByDate(pat.end_date);
          const x = Math.min(xForIndex(s), xForIndex(e)) - barWidth;
          const w = Math.max(2, Math.abs(xForIndex(e) - xForIndex(s)) + barWidth);
          const price = typeof pat.price_level === 'number' ? pat.price_level : parseFloat((pat.price_level || '0') as string);
          const y = yForPrice(price || minPrice);
          return (
            <g key={idx}>
              <rect x={x} y={padding} width={w} height={innerH} fill="#ffd" opacity={0.25} />
              <line x1={padding} x2={width - padding} y1={y} y2={y} stroke="#b33" strokeWidth={1} strokeDasharray="4 3" />
              <text x={padding + 4} y={y - 6} fontSize={11} fill="#b33">{pat.type} ({(pat.confidence ?? 0).toFixed(2)})</text>
            </g>
          );
        })}

        {/* candlesticks */}
        {history.map((h, i) => {
          const open = typeof h.open === 'number' ? h.open : (h.close ?? 0);
          const close = typeof h.close === 'number' ? h.close : 0;
          const high = typeof h.high === 'number' ? h.high : Math.max(open, close);
          const low = typeof h.low === 'number' ? h.low : Math.min(open, close);

          const x = xForIndex(i);
          const yHigh = yForPrice(high);
          const yLow = yForPrice(low);
          const yOpen = yForPrice(open);
          const yClose = yForPrice(close);
          const candleColor = close >= open ? '#16a34a' : '#dc2626';

          return (
            <g key={i}>
              {/* wick */}
              <line x1={x} x2={x} y1={yHigh} y2={yLow} stroke={candleColor} strokeWidth={1} />
              {/* body */}
              <rect
                x={x - barWidth * 0.35}
                y={Math.min(yOpen, yClose)}
                width={Math.max(1, barWidth * 0.7)}
                height={Math.max(1, Math.abs(yClose - yOpen))}
                fill={candleColor}
                stroke={candleColor}
              />
            </g>
          );
        })}

        {/* SMA horizontal lines (latest value drawn as horizontal across chart) */}
        {sma20 ? <line x1={padding} x2={width - padding} y1={yForPrice(Number(sma20))} y2={yForPrice(Number(sma20))} stroke="#1e40af" strokeWidth={1.5} /> : null}
        {sma50 ? <line x1={padding} x2={width - padding} y1={yForPrice(Number(sma50))} y2={yForPrice(Number(sma50))} stroke="#0ea5a4" strokeWidth={1.5} /> : null}
        {sma200 ? <line x1={padding} x2={width - padding} y1={yForPrice(Number(sma200))} y2={yForPrice(Number(sma200))} stroke="#9447ff" strokeWidth={1.5} /> : null}

      </svg>
      <div className="text-xs text-muted-foreground mt-2">
        <span className="inline-block mr-3"><span className="inline-block w-3 h-3 mr-1 align-middle bg-blue-700"></span> SMA20</span>
        <span className="inline-block mr-3"><span className="inline-block w-3 h-3 mr-1 align-middle bg-teal-500"></span> SMA50</span>
        <span className="inline-block mr-3"><span className="inline-block w-3 h-3 mr-1 align-middle bg-purple-600"></span> SMA200</span>
      </div>
    </div>
  );
};

export default PatternChart;
