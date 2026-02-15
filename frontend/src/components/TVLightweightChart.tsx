import React from "react";
import { createChart, IChartApi, ISeriesApi, CandlestickData, LineData, ColorType } from "lightweight-charts";

export type Candle = {
  time: number | string; // ISO date like "2024-01-01" or unix timestamp (seconds)
  open: number;
  high: number;
  low: number;
  close: number;
};

export type LinePoint = {
  time: number | string;
  value: number;
};

export type TVLightweightChartProps = {
  candles: Candle[];
  lines?: Record<string, LinePoint[]>; // e.g., { sma20: [...], sma50: [...] }
  height?: number;
};

/**
 * Minimal TradingView Lightweight Charts wrapper.
 * - Renders candlesticks plus optional line series (e.g., SMA/EMA)
 * - Pure client component; no SSR assumptions
 */
export default function TVLightweightChart({
  candles,
  lines,
  height = 420,
}: TVLightweightChartProps) {
  // Normalize: ensure time values are strings (ISO) for consistency with Vite/TS
  const candleData = React.useMemo(() => {
    const arr = (candles ?? []).filter(
      c => typeof c.close === 'number' && !Number.isNaN(c.close) && typeof c.time === 'number' && Number.isFinite(c.time as number)
    ) as Candle[];
    // sort ascending by time to satisfy lightweight-charts
    arr.sort((a,b) => (a.time as number) - (b.time as number));
    console.log('[TVLightweightChart] candles count:', arr.length, 'sample:', arr.slice(0, 3));
    return arr;
  }, [candles]);
  const filteredLines = React.useMemo(() => {
    if (!lines) return {} as Record<string, LinePoint[]>;
    const out: Record<string, LinePoint[]> = {};
    for (const [k, v] of Object.entries(lines)) {
      if (Array.isArray(v) && v.length > 0) {
        const arr = (v as LinePoint[]).filter(p => p && typeof p.value === 'number' && !Number.isNaN(p.value));
        if (arr.length) out[k] = arr;
      }
    }
    console.log('[TVLightweightChart] lines count:', Object.keys(out).length, Object.keys(out));
    return out;
  }, [lines]);

  const chartContainerRef = React.useRef<HTMLDivElement>(null);
  const chartRef = React.useRef<IChartApi | null>(null);

  React.useEffect(() => {
    if (!chartContainerRef.current || candleData.length === 0) return;

    // Create chart instance
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height,
  layout: { textColor: '#CBD5E1', background: { type: ColorType.Solid, color: 'transparent' } },
      rightPriceScale: { borderVisible: false },
      timeScale: { borderVisible: false, timeVisible: true, secondsVisible: false },
      grid: { horzLines: { color: '#1F2937' }, vertLines: { color: '#1F2937' } },
    });
    chartRef.current = chart;

    // Add candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });
    candleSeries.setData(candleData as CandlestickData[]);

    // Add line series
    Object.entries(filteredLines).forEach(([key, data]) => {
      const lineSeries = chart.addLineSeries({
        color: key.includes('sma') ? '#2962FF' : key.includes('ema') ? '#FF6D00' : '#AA00FF',
        lineWidth: 2,
        priceLineVisible: false,
      });
      lineSeries.setData(data as LineData[]);
    });

    chart.timeScale().fitContent();

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [candleData, filteredLines, height]);

  return (
    <div style={{ width: "100%", position: 'relative' }}>
      {candleData.length === 0 ? (
        <div style={{ height }} className="flex items-center justify-center text-sm text-muted-foreground">No chart data</div>
      ) : (
        <div ref={chartContainerRef} style={{ width: '100%', height }} />
      )}
    </div>
  );
}
