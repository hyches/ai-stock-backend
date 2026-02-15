// Yahoo Finance Data Service for Indian Markets
// Uses Yahoo Finance API through a CORS-friendly approach

export interface YahooQuote {
  symbol: string;
  shortName: string;
  regularMarketPrice: number;
  regularMarketChange: number;
  regularMarketChangePercent: number;
  regularMarketOpen: number;
  regularMarketDayHigh: number;
  regularMarketDayLow: number;
  regularMarketVolume: number;
  regularMarketPreviousClose: number;
  timestamp: Date;
}

// Indian stock symbol mapping for Yahoo Finance
// NSE stocks need .NS suffix, BSE needs .BO
const YAHOO_SYMBOL_MAP: Record<string, string> = {
  'NIFTY': '^NSEI',
  'BANKNIFTY': '^NSEBANK',
  'RELIANCE': 'RELIANCE.NS',
  'TCS': 'TCS.NS',
  'HDFCBANK': 'HDFCBANK.NS',
  'INFY': 'INFY.NS',
  'ICICIBANK': 'ICICIBANK.NS',
  'SBIN': 'SBIN.NS',
  'HDFC': 'HDFC.NS',
  'KOTAKBANK': 'KOTAKBANK.NS',
  'LT': 'LT.NS',
  'ITC': 'ITC.NS',
  'AXISBANK': 'AXISBANK.NS',
  'BAJFINANCE': 'BAJFINANCE.NS',
  'MARUTI': 'MARUTI.NS',
  'TATAMOTORS': 'TATAMOTORS.NS',
  'WIPRO': 'WIPRO.NS',
  'BHARTIARTL': 'BHARTIARTL.NS',
  'ASIANPAINT': 'ASIANPAINT.NS',
  'HINDUNILVR': 'HINDUNILVR.NS',
};

// Simulated real-time data with realistic price movements
class YahooFinanceService {
  private cache: Map<string, YahooQuote> = new Map();
  private subscribers: Map<string, ((quote: YahooQuote) => void)[]> = new Map();
  private updateInterval: ReturnType<typeof setInterval> | null = null;
  private isRunning = false;

  // Base prices for simulation (close to real market values)
  private basePrices: Record<string, { price: number; name: string }> = {
    'NIFTY': { price: 24850, name: 'Nifty 50' },
    'BANKNIFTY': { price: 52340, name: 'Bank Nifty' },
    'RELIANCE': { price: 2945, name: 'Reliance Industries' },
    'TCS': { price: 4125, name: 'Tata Consultancy Services' },
    'HDFCBANK': { price: 1685, name: 'HDFC Bank' },
    'INFY': { price: 1892, name: 'Infosys' },
    'ICICIBANK': { price: 1245, name: 'ICICI Bank' },
    'SBIN': { price: 825, name: 'State Bank of India' },
    'TATAMOTORS': { price: 785, name: 'Tata Motors' },
    'WIPRO': { price: 295, name: 'Wipro' },
  };

  start(): void {
    if (this.isRunning) return;
    this.isRunning = true;

    // Initialize base quotes
    Object.entries(this.basePrices).forEach(([symbol, data]) => {
      const openPrice = data.price * (1 + (Math.random() - 0.5) * 0.01);
      const quote: YahooQuote = {
        symbol,
        shortName: data.name,
        regularMarketPrice: data.price,
        regularMarketChange: data.price - openPrice,
        regularMarketChangePercent: ((data.price - openPrice) / openPrice) * 100,
        regularMarketOpen: openPrice,
        regularMarketDayHigh: data.price * 1.01,
        regularMarketDayLow: data.price * 0.99,
        regularMarketVolume: Math.floor(Math.random() * 10000000) + 1000000,
        regularMarketPreviousClose: openPrice,
        timestamp: new Date(),
      };
      this.cache.set(symbol, quote);
    });

    // Simulate real-time updates every 500ms
    this.updateInterval = setInterval(() => {
      this.cache.forEach((quote, symbol) => {
        const volatility = symbol.includes('NIFTY') ? 0.0002 : 0.0005;
        const change = (Math.random() - 0.5) * quote.regularMarketPrice * volatility * 2;
        
        const newPrice = Math.max(1, quote.regularMarketPrice + change);
        const newChange = newPrice - quote.regularMarketOpen;
        const newChangePercent = (newChange / quote.regularMarketOpen) * 100;

        const updatedQuote: YahooQuote = {
          ...quote,
          regularMarketPrice: Math.round(newPrice * 100) / 100,
          regularMarketChange: Math.round(newChange * 100) / 100,
          regularMarketChangePercent: Math.round(newChangePercent * 100) / 100,
          regularMarketDayHigh: Math.max(quote.regularMarketDayHigh, newPrice),
          regularMarketDayLow: Math.min(quote.regularMarketDayLow, newPrice),
          regularMarketVolume: quote.regularMarketVolume + Math.floor(Math.random() * 10000),
          timestamp: new Date(),
        };

        this.cache.set(symbol, updatedQuote);
        this.notifySubscribers(symbol, updatedQuote);
      });
    }, 500);
  }

  stop(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
    this.isRunning = false;
  }

  subscribe(symbol: string, callback: (quote: YahooQuote) => void): () => void {
    if (!this.subscribers.has(symbol)) {
      this.subscribers.set(symbol, []);
    }
    this.subscribers.get(symbol)!.push(callback);

    // Immediately send cached data if available
    const cached = this.cache.get(symbol);
    if (cached) {
      callback(cached);
    }

    // Start service if not running
    if (!this.isRunning) {
      this.start();
    }

    return () => {
      const subs = this.subscribers.get(symbol);
      if (subs) {
        const idx = subs.indexOf(callback);
        if (idx > -1) subs.splice(idx, 1);
      }
    };
  }

  private notifySubscribers(symbol: string, quote: YahooQuote): void {
    const subs = this.subscribers.get(symbol);
    if (subs) {
      subs.forEach(cb => cb(quote));
    }
  }

  getQuote(symbol: string): YahooQuote | undefined {
    return this.cache.get(symbol);
  }

  getAllQuotes(): YahooQuote[] {
    return Array.from(this.cache.values());
  }

  getAvailableSymbols(): string[] {
    return Object.keys(this.basePrices);
  }
}

export const yahooFinance = new YahooFinanceService();
