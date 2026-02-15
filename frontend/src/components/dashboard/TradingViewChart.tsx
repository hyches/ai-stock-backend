import React, { useEffect, useRef, memo } from 'react';
import { useTheme } from '@/context/ThemeContext';

interface TradingViewChartProps {
  symbol?: string;
  interval?: string;
  theme?: 'light' | 'dark';
  height?: number;
}

// TradingView Widget Component
export const TradingViewChart: React.FC<TradingViewChartProps> = memo(({
  symbol = 'NSE:NIFTY',
  interval = 'D',
  theme: propTheme,
  height = 500,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const scriptRef = useRef<HTMLScriptElement | null>(null);
  const { theme: appTheme } = useTheme();
  const theme = propTheme || appTheme;

  useEffect(() => {
    // Clean up previous widget
    if (containerRef.current) {
      containerRef.current.innerHTML = '';
    }

    // Create new widget
    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    script.type = 'text/javascript';
    script.async = true;
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol: symbol,
      interval: interval,
      timezone: 'Asia/Kolkata',
      theme: theme,
      style: '1',
      locale: 'en',
      enable_publishing: false,
      allow_symbol_change: true,
      calendar: false,
      support_host: 'https://www.tradingview.com',
      hide_side_toolbar: false,
      studies: [
        'STD;RSI',
        'STD;MACD',
        'STD;Bollinger_Bands',
      ],
      show_popup_button: true,
      popup_width: '1000',
      popup_height: '650',
      container_id: 'tradingview_chart_container',
    });

    scriptRef.current = script;

    if (containerRef.current) {
      containerRef.current.appendChild(script);
    }

    return () => {
      if (scriptRef.current && scriptRef.current.parentNode) {
        scriptRef.current.parentNode.removeChild(scriptRef.current);
      }
    };
  }, [symbol, interval, theme]);

  return (
    <div className="glass-card overflow-hidden">
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-medium">TradingView Chart</h3>
            <p className="text-sm text-muted-foreground">Real-time technical analysis</p>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="px-2 py-1 rounded-full bg-secondary">{symbol}</span>
            <span className="px-2 py-1 rounded-full bg-secondary">{interval}</span>
          </div>
        </div>
      </div>
      <div
        className="tradingview-widget-container"
        style={{ height: `${height}px` }}
      >
        <div
          id="tradingview_chart_container"
          ref={containerRef}
          style={{ height: '100%', width: '100%' }}
        />
      </div>
    </div>
  );
});

TradingViewChart.displayName = 'TradingViewChart';

// Symbol Ticker Widget
export const TradingViewTicker: React.FC = memo(() => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.innerHTML = '';
    }

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js';
    script.type = 'text/javascript';
    script.async = true;
    script.innerHTML = JSON.stringify({
      symbols: [
        { proName: 'NSE:NIFTY', title: 'NIFTY 50' },
        { proName: 'NSE:BANKNIFTY', title: 'BANK NIFTY' },
        { proName: 'NSE:RELIANCE', title: 'RELIANCE' },
        { proName: 'NSE:TCS', title: 'TCS' },
        { proName: 'NSE:HDFCBANK', title: 'HDFC BANK' },
        { proName: 'NSE:INFY', title: 'INFOSYS' },
        { proName: 'NSE:ICICIBANK', title: 'ICICI BANK' },
        { proName: 'NSE:SBIN', title: 'SBI' },
      ],
      showSymbolLogo: true,
      isTransparent: true,
      displayMode: 'adaptive',
      colorTheme: 'dark',
      locale: 'en',
    });

    if (containerRef.current) {
      containerRef.current.appendChild(script);
    }
  }, []);

  return (
    <div
      className="tradingview-widget-container h-12"
      ref={containerRef}
    />
  );
});

TradingViewTicker.displayName = 'TradingViewTicker';

// Technical Analysis Widget
export const TradingViewAnalysis: React.FC<{ symbol?: string }> = memo(({ symbol = 'NSE:NIFTY' }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const { theme } = useTheme();
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.innerHTML = '';
    }

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js';
    script.type = 'text/javascript';
    script.async = true;
    script.innerHTML = JSON.stringify({
      interval: '1D',
      width: '100%',
      isTransparent: true,
      height: '400',
      symbol: symbol,
      showIntervalTabs: true,
      displayMode: 'single',
      locale: 'en',
      colorTheme: theme,
    });

    if (containerRef.current) {
      containerRef.current.appendChild(script);
    }
  }, [symbol, theme]);

  return (
    <div className="glass-card overflow-hidden">
      <div className="p-4 border-b border-border">
        <h3 className="font-medium">Technical Analysis</h3>
        <p className="text-sm text-muted-foreground">RSI, MACD, Moving Averages & more</p>
      </div>
      <div
        className="tradingview-widget-container"
        ref={containerRef}
        style={{ height: '400px' }}
      />
    </div>
  );
});

TradingViewAnalysis.displayName = 'TradingViewAnalysis';

// Mini Chart Widget
export const TradingViewMiniChart: React.FC<{ symbol?: string }> = memo(({ symbol = 'NSE:NIFTY' }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.innerHTML = '';
    }

    const script = document.createElement('script');
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js';
    script.type = 'text/javascript';
    script.async = true;
    script.innerHTML = JSON.stringify({
      symbol: symbol,
      width: '100%',
      height: '200',
      locale: 'en',
      dateRange: '1D',
      colorTheme: 'dark',
      isTransparent: true,
      autosize: true,
      largeChartUrl: '',
    });

    if (containerRef.current) {
      containerRef.current.appendChild(script);
    }
  }, [symbol]);

  return (
    <div
      className="tradingview-widget-container"
      ref={containerRef}
      style={{ height: '200px' }}
    />
  );
});

TradingViewMiniChart.displayName = 'TradingViewMiniChart';
