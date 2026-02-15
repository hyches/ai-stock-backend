// Angel One (SmartAPI) WebSocket Integration
// Note: Full implementation requires API key and secret from Angel One

export interface AngelOneCredentials {
  apiKey: string;
  clientId: string;
  pin: string;
  totpSecret?: string;
}

export interface MarketQuote {
  symbol: string;
  token: string;
  ltp: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  change: number;
  changePercent: number;
  timestamp: Date;
  bid: number;
  ask: number;
  bidQty: number;
  askQty: number;
  oi?: number;
}

export interface WebSocketMessage {
  type: 'QUOTE' | 'DEPTH' | 'INDEX' | 'OI' | 'ERROR';
  data: any;
}

type MessageHandler = (quote: MarketQuote) => void;
type StatusHandler = (status: 'connected' | 'disconnected' | 'error' | 'reconnecting') => void;

// Mock WebSocket for demo (replace with real Angel One WebSocket)
class AngelOneWebSocket {
  private ws: WebSocket | null = null;
  private messageHandlers: Map<string, MessageHandler[]> = new Map();
  private statusHandlers: StatusHandler[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private subscribedSymbols: Set<string> = new Set();
  private mockMode = true; // Set to false when using real API
  private mockInterval: ReturnType<typeof setInterval> | null = null;
  
  // Symbol token mapping for NSE
  private static TOKEN_MAP: Record<string, string> = {
    'NIFTY': '26000',
    'BANKNIFTY': '26009',
    'RELIANCE': '2885',
    'TCS': '11536',
    'HDFCBANK': '1333',
    'INFY': '1594',
    'ICICIBANK': '4963',
    'SBIN': '3045',
    'HDFC': '1330',
    'KOTAKBANK': '1922',
    'LT': '11483',
    'ITC': '1660',
    'AXISBANK': '5900',
    'BAJFINANCE': '317',
    'MARUTI': '10999',
  };
  
  async connect(credentials?: AngelOneCredentials): Promise<void> {
    // In mock mode, simulate connection
    if (this.mockMode) {
      this.notifyStatus('connected');
      this.startMockDataStream();
      return;
    }
    
    // Real Angel One WebSocket connection
    // Would need to authenticate first and get JWT token
    try {
      const wsUrl = 'wss://smartapisocket.angelone.in/smart-stream';
      
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('Angel One WebSocket connected');
        this.reconnectAttempts = 0;
        this.notifyStatus('connected');
        
        // Resubscribe to symbols
        this.subscribedSymbols.forEach(symbol => {
          this.sendSubscription(symbol);
        });
      };
      
      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.notifyStatus('error');
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket closed');
        this.notifyStatus('disconnected');
        this.attemptReconnect(credentials);
      };
    } catch (error) {
      console.error('Failed to connect:', error);
      this.notifyStatus('error');
    }
  }
  
  private startMockDataStream(): void {
    // Generate mock real-time data
    const baseQuotes: Record<string, MarketQuote> = {
      'NIFTY': { symbol: 'NIFTY', token: '26000', ltp: 24850, open: 24725, high: 24892, low: 24680, close: 24725, volume: 245000000, change: 125, changePercent: 0.51, timestamp: new Date(), bid: 24849, ask: 24851, bidQty: 100, askQty: 150 },
      'BANKNIFTY': { symbol: 'BANKNIFTY', token: '26009', ltp: 52340, open: 52521, high: 52600, low: 52200, close: 52521, volume: 89000000, change: -181, changePercent: -0.34, timestamp: new Date(), bid: 52338, ask: 52342, bidQty: 50, askQty: 75 },
      'RELIANCE': { symbol: 'RELIANCE', token: '2885', ltp: 2945, open: 2913, high: 2958, low: 2905, close: 2913, volume: 12500000, change: 32, changePercent: 1.12, timestamp: new Date(), bid: 2944, ask: 2946, bidQty: 200, askQty: 180 },
      'TCS': { symbol: 'TCS', token: '11536', ltp: 4125, open: 4170, high: 4180, low: 4100, close: 4170, volume: 3200000, change: -45, changePercent: -1.08, timestamp: new Date(), bid: 4124, ask: 4126, bidQty: 100, askQty: 120 },
      'HDFCBANK': { symbol: 'HDFCBANK', token: '1333', ltp: 1685, open: 1666, high: 1692, low: 1660, close: 1666, volume: 8900000, change: 19, changePercent: 1.13, timestamp: new Date(), bid: 1684, ask: 1686, bidQty: 300, askQty: 250 },
      'INFY': { symbol: 'INFY', token: '1594', ltp: 1892, open: 1905, high: 1910, low: 1885, close: 1905, volume: 5600000, change: -13, changePercent: -0.66, timestamp: new Date(), bid: 1891, ask: 1893, bidQty: 150, askQty: 175 },
      'ICICIBANK': { symbol: 'ICICIBANK', token: '4963', ltp: 1245, open: 1217, high: 1252, low: 1215, close: 1217, volume: 7800000, change: 28, changePercent: 2.33, timestamp: new Date(), bid: 1244, ask: 1246, bidQty: 200, askQty: 180 },
      'SBIN': { symbol: 'SBIN', token: '3045', ltp: 825, open: 834, high: 838, low: 820, close: 834, volume: 15200000, change: -9, changePercent: -0.99, timestamp: new Date(), bid: 824, ask: 826, bidQty: 500, askQty: 450 },
    };
    
    this.mockInterval = setInterval(() => {
      this.subscribedSymbols.forEach(symbol => {
        const quote = baseQuotes[symbol];
        if (quote) {
          // Add random price movement
          const change = (Math.random() - 0.5) * quote.ltp * 0.001;
          quote.ltp = Math.round((quote.ltp + change) * 100) / 100;
          quote.change = Math.round((quote.ltp - quote.close) * 100) / 100;
          quote.changePercent = Math.round((quote.change / quote.close) * 10000) / 100;
          quote.bid = quote.ltp - 1;
          quote.ask = quote.ltp + 1;
          quote.timestamp = new Date();
          quote.volume += Math.floor(Math.random() * 10000);
          
          if (quote.ltp > quote.high) quote.high = quote.ltp;
          if (quote.ltp < quote.low) quote.low = quote.ltp;
          
          this.notifyQuote(symbol, { ...quote });
        }
      });
    }, 500); // Update every 500ms
  }
  
  private handleMessage(data: any): void {
    try {
      const message: WebSocketMessage = typeof data === 'string' ? JSON.parse(data) : data;
      
      if (message.type === 'QUOTE') {
        const quote = this.parseQuote(message.data);
        if (quote) {
          this.notifyQuote(quote.symbol, quote);
        }
      }
    } catch (error) {
      console.error('Error parsing message:', error);
    }
  }
  
  private parseQuote(data: any): MarketQuote | null {
    // Parse Angel One quote format
    return {
      symbol: data.tk || data.symbol,
      token: data.tk,
      ltp: parseFloat(data.lp),
      open: parseFloat(data.op),
      high: parseFloat(data.hp),
      low: parseFloat(data.lop),
      close: parseFloat(data.c),
      volume: parseInt(data.v),
      change: parseFloat(data.cng),
      changePercent: parseFloat(data.nc),
      timestamp: new Date(data.ft * 1000),
      bid: parseFloat(data.bp1),
      ask: parseFloat(data.sp1),
      bidQty: parseInt(data.bq1),
      askQty: parseInt(data.sq1),
      oi: data.oi ? parseInt(data.oi) : undefined,
    };
  }
  
  private sendSubscription(symbol: string): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    
    const token = AngelOneWebSocket.TOKEN_MAP[symbol];
    if (!token) return;
    
    const subscribeMsg = {
      correlationID: `sub_${symbol}_${Date.now()}`,
      action: 1, // Subscribe
      params: {
        mode: 3, // SnapQuote mode
        tokenList: [{ exchangeType: 1, tokens: [token] }], // 1 = NSE
      },
    };
    
    this.ws.send(JSON.stringify(subscribeMsg));
  }
  
  subscribe(symbol: string, handler: MessageHandler): () => void {
    this.subscribedSymbols.add(symbol);
    
    if (!this.messageHandlers.has(symbol)) {
      this.messageHandlers.set(symbol, []);
    }
    this.messageHandlers.get(symbol)!.push(handler);
    
    // If connected, subscribe immediately
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.sendSubscription(symbol);
    }
    
    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(symbol);
      if (handlers) {
        const index = handlers.indexOf(handler);
        if (index > -1) {
          handlers.splice(index, 1);
        }
        if (handlers.length === 0) {
          this.subscribedSymbols.delete(symbol);
        }
      }
    };
  }
  
  onStatusChange(handler: StatusHandler): () => void {
    this.statusHandlers.push(handler);
    return () => {
      const index = this.statusHandlers.indexOf(handler);
      if (index > -1) {
        this.statusHandlers.splice(index, 1);
      }
    };
  }
  
  private notifyQuote(symbol: string, quote: MarketQuote): void {
    const handlers = this.messageHandlers.get(symbol);
    if (handlers) {
      handlers.forEach(handler => handler(quote));
    }
  }
  
  private notifyStatus(status: 'connected' | 'disconnected' | 'error' | 'reconnecting'): void {
    this.statusHandlers.forEach(handler => handler(status));
  }
  
  private attemptReconnect(credentials?: AngelOneCredentials): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }
    
    this.reconnectAttempts++;
    this.notifyStatus('reconnecting');
    
    setTimeout(() => {
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
      this.connect(credentials);
    }, this.reconnectDelay * this.reconnectAttempts);
  }
  
  disconnect(): void {
    if (this.mockInterval) {
      clearInterval(this.mockInterval);
      this.mockInterval = null;
    }
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.notifyStatus('disconnected');
  }
  
  isConnected(): boolean {
    if (this.mockMode) {
      return this.mockInterval !== null;
    }
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Singleton instance
export const angelOneWS = new AngelOneWebSocket();
