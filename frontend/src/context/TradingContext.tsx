import React, { createContext, useContext, useState, useEffect, useMemo } from 'react';
import { api } from '@/lib/api-client';
import { useToast } from '@/hooks/use-toast';

export interface Position {
  id: string;
  symbol: string;
  type: 'EQ' | 'CE' | 'PE' | 'FUT';
  qty: number;
  avgPrice: number;
  ltp: number;
  pnl: number;
  pnlPercent: number;
  strike?: number;
  expiry?: string;
  status: 'open' | 'closed';
}

export interface Trade {
  id: string;
  timestamp: Date;
  symbol: string;
  action: 'BUY' | 'SELL';
  type: 'EQ' | 'CE' | 'PE' | 'FUT';
  qty: number;
  price: number;
  status: 'EXECUTED' | 'PENDING' | 'CANCELLED' | 'REJECTED';
  pnl?: number;
  strike?: number;
}

export interface TradingOption {
  type: 'CE' | 'PE';
  strike: number;
  expiry: string;
}

interface WatchlistItem {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

interface PortfolioSummary {
  totalPnL: number;
  totalCapital: number;
  todayPnL: number;
  availableMargin: number;
  usedMargin: number;
  winRate: number;
  totalTrades: number;
  realizedPnL: number;
  avgReturn: number;
}

interface TradingContextType {
  virtualCash: number;
  positions: Position[];
  trades: Trade[];
  watchlist: WatchlistItem[];
  portfolio: PortfolioSummary;
  quotes: Map<string, any>;
  selectedSymbol: string;
  selectedOption: TradingOption | null;
  isLoading: boolean;

  setSelectedSymbol: (symbol: string) => void;
  setSelectedOption: (option: TradingOption | null) => void;
  refreshData: () => Promise<void>;
  executeTrade: (params: any) => Promise<boolean>;
  closePosition: (id: string) => Promise<boolean>;
  closeAllPositions: () => Promise<boolean>;
  addTradeListener: (listener: (trade: Trade) => void) => () => void;

  // Legacy compatibility
  buyStock: (symbol: string, quantity: number, orderType?: string, price?: number) => Promise<boolean>;
  sellStock: (symbol: string, quantity: number, orderType?: string, price?: number) => Promise<boolean>;
  resetBalance: (amount: number) => Promise<boolean>;
  addToWatchlist: (symbol: string, name: string, price: number, change: number, changePercent: number) => void;
  removeFromWatchlist: (symbol: string) => void;
  isInWatchlist: (symbol: string) => boolean;
}

const TradingContext = createContext<TradingContextType | undefined>(undefined);

export const useTrading = () => {
  const context = useContext(TradingContext);
  if (context === undefined) {
    throw new Error('useTrading must be used within a TradingProvider');
  }
  return context;
};

export const TradingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [virtualCash, setVirtualCash] = useState<number>(1000000);
  const [positions, setPositions] = useState<Position[]>([]);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [quotes, setQuotes] = useState<Map<string, any>>(new Map());
  const [selectedSymbol, setSelectedSymbol] = useState('NIFTY');
  const [selectedOption, setSelectedOption] = useState<TradingOption | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();
  const listeners = React.useRef<Set<(trade: Trade) => void>>(new Set());

  // Derived Portfolio Summary
  const portfolio = useMemo(() => {
    const totalPnL = positions.reduce((sum, p) => sum + p.pnl, 0);
    const realizedPnL = trades.filter(t => t.status === 'EXECUTED' && t.pnl !== undefined).reduce((sum, t) => sum + (t.pnl || 0), 0);
    const totalTrades = trades.length;
    const wins = trades.filter(t => (t.pnl || 0) > 0).length;

    return {
      totalPnL,
      totalCapital: virtualCash + positions.reduce((sum, p) => sum + (Math.abs(p.qty) * p.avgPrice), 0),
      todayPnL: totalPnL, // Simplified
      availableMargin: virtualCash,
      usedMargin: positions.reduce((sum, p) => sum + (Math.abs(p.qty) * p.avgPrice), 0),
      winRate: totalTrades > 0 ? wins / totalTrades : 0,
      totalTrades,
      realizedPnL,
      avgReturn: totalTrades > 0 ? realizedPnL / totalTrades : 0
    };
  }, [positions, trades, virtualCash]);

  // Load Watchlist
  useEffect(() => {
    try {
      const saved = localStorage.getItem('watchlist');
      if (saved) setWatchlist(JSON.parse(saved));
    } catch (e) {
      console.error("Failed to load watchlist", e);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('watchlist', JSON.stringify(watchlist));
  }, [watchlist]);

  const refreshData = async () => {
    try {
      const res = await api.trading.getPaperPortfolio();
      const data = res.data;

      setVirtualCash(data.current_balance || 1000000);

      const mappedPositions: Position[] = (data.positions || []).map((p: any) => ({
        id: p.symbol, // Backend might need proper IDs later
        symbol: p.symbol,
        type: 'EQ',
        qty: p.quantity,
        avgPrice: p.avg_price,
        ltp: p.current_price,
        pnl: p.pnl,
        pnlPercent: (p.pnl / (p.quantity * p.avg_price)) * 100,
        status: 'open'
      }));
      setPositions(mappedPositions);

      try {
        const ordersRes = await api.trading.getPaperOrders();
        const mappedTrades: Trade[] = ordersRes.data.map((o: any) => ({
          id: String(o.id),
          timestamp: new Date(o.timestamp || o.created_at),
          symbol: o.symbol,
          action: o.side.toUpperCase() as 'BUY' | 'SELL',
          type: 'EQ',
          qty: o.quantity,
          price: o.price || o.avg_price,
          status: 'EXECUTED', // Defaulting for paper trades
          pnl: o.pnl
        }));
        setTrades(mappedTrades);
      } catch (err) {
        console.warn("Failed to fetch order history", err);
      }

      // Mock quotes for testing UI
      const mockQuotes = new Map();
      mappedPositions.forEach(p => {
        mockQuotes.set(p.symbol, {
          symbol: p.symbol,
          shortName: p.symbol,
          regularMarketPrice: p.ltp,
          regularMarketChange: p.pnl / (p.qty || 1),
          regularMarketChangePercent: p.pnlPercent,
          regularMarketOpen: p.avgPrice,
          regularMarketDayHigh: p.ltp * 1.02,
          regularMarketDayLow: p.ltp * 0.98
        });
      });
      watchlist.forEach(w => {
        if (!mockQuotes.has(w.symbol)) {
          mockQuotes.set(w.symbol, {
            symbol: w.symbol,
            shortName: w.name,
            regularMarketPrice: w.price,
            regularMarketChange: w.change,
            regularMarketChangePercent: w.changePercent,
            regularMarketOpen: w.price,
            regularMarketDayHigh: w.price * 1.01,
            regularMarketDayLow: w.price * 0.99
          });
        }
      });
      setQuotes(mockQuotes);

    } catch (e) {
      console.error("Failed to fetch trading data", e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
    const interval = setInterval(refreshData, 10000);
    return () => clearInterval(interval);
  }, []);

  const addTradeListener = (listener: (trade: Trade) => void) => {
    listeners.current.add(listener);
    return () => {
      listeners.current.delete(listener);
    };
  };

  const executeTrade = async (params: any): Promise<boolean> => {
    try {
      const res = await api.trading.placePaperOrder({
        symbol: params.symbol,
        side: params.action,
        quantity: params.qty,
        order_type: params.orderType || 'MARKET'
      });

      const newTrade: Trade = {
        id: String(res.data?.id || Date.now()),
        timestamp: new Date(),
        symbol: params.symbol,
        action: params.action,
        type: 'EQ',
        qty: params.qty,
        price: 0, // LTP will be fetched in refresh
        status: 'EXECUTED'
      };

      await refreshData();

      // Notify listeners
      listeners.current.forEach(l => l(newTrade));

      toast({ title: "Order Executed", description: `${params.action} ${params.qty} ${params.symbol} success.` });
      return true;
    } catch (e: any) {
      toast({ title: "Order Failed", description: e.response?.data?.detail || "Execution error", variant: "destructive" });
      return false;
    }
  };

  const closePosition = async (id: string): Promise<boolean> => {
    const pos = positions.find(p => p.id === id);
    if (!pos) return false;
    return executeTrade({
      symbol: pos.symbol,
      action: pos.qty > 0 ? 'SELL' : 'BUY',
      qty: Math.abs(pos.qty),
      orderType: 'MARKET'
    });
  };

  const closeAllPositions = async (): Promise<boolean> => {
    for (const pos of positions) {
      await closePosition(pos.id);
    }
    return true;
  };

  // Legacy compat
  const buyStock = (s: string, q: number) => executeTrade({ symbol: s, action: 'BUY', qty: q });
  const sellStock = (s: string, q: number) => executeTrade({ symbol: s, action: 'SELL', qty: q });

  const resetBalance = async (amount: number): Promise<boolean> => {
    try {
      await api.trading.resetBalance(amount);
      await refreshData();
      return true;
    } catch (e) { return false; }
  };

  const addToWatchlist = (symbol: string, name: string, price: number, change: number, changePercent: number) => {
    setWatchlist(prev => {
      if (!prev.some(item => item.symbol === symbol)) {
        return [...prev, { symbol, name, price, change, changePercent }];
      }
      return prev;
    });
  };

  const removeFromWatchlist = (symbol: string) => {
    setWatchlist(prev => prev.filter(item => item.symbol !== symbol));
  };

  const isInWatchlist = (symbol: string) => watchlist.some(item => item.symbol === symbol);

  const value = {
    virtualCash, positions, trades, watchlist, portfolio, quotes,
    selectedSymbol, selectedOption, isLoading,
    setSelectedSymbol, setSelectedOption, refreshData, executeTrade,
    closePosition, closeAllPositions, addTradeListener, buyStock, sellStock,
    resetBalance, addToWatchlist, removeFromWatchlist, isInWatchlist
  };

  return (
    <TradingContext.Provider value={value}>
      {children}
    </TradingContext.Provider>
  );
};




