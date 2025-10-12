import React, { createContext, useContext, useState, useEffect } from 'react';

interface Transaction {
  id: string;
  type: 'buy' | 'sell';
  symbol: string;
  name: string;
  quantity: number;
  price: number;
  total: number;
  timestamp: Date;
}

interface WatchlistItem {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

interface PortfolioItem {
  symbol: string;
  name: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  totalValue: number;
  profitLoss: number;
  profitLossPercent: number;
}

interface TradingContextType {
  virtualCash: number;
  transactions: Transaction[];
  watchlist: WatchlistItem[];
  portfolio: PortfolioItem[];
  buyStock: (symbol: string, name: string, quantity: number, price: number) => boolean;
  sellStock: (symbol: string, quantity: number, price: number) => boolean;
  addToWatchlist: (symbol: string, name: string, price: number, change: number, changePercent: number) => void;
  removeFromWatchlist: (symbol: string) => void;
  isInWatchlist: (symbol: string) => boolean;
  getPortfolioItem: (symbol: string) => PortfolioItem | undefined;
}

const TradingContext = createContext<TradingContextType | undefined>(undefined);

export const useTrading = () => {
  const context = useContext(TradingContext);
  if (context === undefined) {
    throw new Error('useTrading must be used within a TradingProvider');
  }
  return context;
};

interface TradingProviderProps {
  children: React.ReactNode;
}

export const TradingProvider: React.FC<TradingProviderProps> = ({ children }) => {
  const [virtualCash, setVirtualCash] = useState<number>(10000000); // 1 crore virtual cash
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);

  // Load data from localStorage on mount
  useEffect(() => {
    const savedCash = localStorage.getItem('virtualCash');
    const savedTransactions = localStorage.getItem('transactions');
    const savedWatchlist = localStorage.getItem('watchlist');
    const savedPortfolio = localStorage.getItem('portfolio');

    if (savedCash) setVirtualCash(parseFloat(savedCash));
    if (savedTransactions) setTransactions(JSON.parse(savedTransactions));
    if (savedWatchlist) setWatchlist(JSON.parse(savedWatchlist));
    if (savedPortfolio) setPortfolio(JSON.parse(savedPortfolio));
  }, []);

  // Save to localStorage whenever state changes
  useEffect(() => {
    localStorage.setItem('virtualCash', virtualCash.toString());
  }, [virtualCash]);

  useEffect(() => {
    localStorage.setItem('transactions', JSON.stringify(transactions));
  }, [transactions]);

  useEffect(() => {
    localStorage.setItem('watchlist', JSON.stringify(watchlist));
  }, [watchlist]);

  useEffect(() => {
    localStorage.setItem('portfolio', JSON.stringify(portfolio));
  }, [portfolio]);

  const buyStock = (symbol: string, name: string, quantity: number, price: number): boolean => {
    const totalCost = quantity * price;
    
    if (totalCost > virtualCash) {
      return false; // Insufficient funds
    }

    // Update virtual cash
    setVirtualCash(prev => prev - totalCost);

    // Add transaction
    const transaction: Transaction = {
      id: Date.now().toString(),
      type: 'buy',
      symbol,
      name,
      quantity,
      price,
      total: totalCost,
      timestamp: new Date()
    };
    setTransactions(prev => [transaction, ...prev]);

    // Update portfolio
    setPortfolio(prev => {
      const existingItem = prev.find(item => item.symbol === symbol);
      if (existingItem) {
        // Update existing position
        const newQuantity = existingItem.quantity + quantity;
        const newTotalCost = (existingItem.averagePrice * existingItem.quantity) + totalCost;
        const newAveragePrice = newTotalCost / newQuantity;
        
        return prev.map(item =>
          item.symbol === symbol
            ? {
                ...item,
                quantity: newQuantity,
                averagePrice: newAveragePrice,
                currentPrice: price,
                totalValue: newQuantity * price,
                profitLoss: (price - newAveragePrice) * newQuantity,
                profitLossPercent: ((price - newAveragePrice) / newAveragePrice) * 100
              }
            : item
        );
      } else {
        // Add new position
        const newItem: PortfolioItem = {
          symbol,
          name,
          quantity,
          averagePrice: price,
          currentPrice: price,
          totalValue: quantity * price,
          profitLoss: 0,
          profitLossPercent: 0
        };
        return [...prev, newItem];
      }
    });

    return true;
  };

  const sellStock = (symbol: string, quantity: number, price: number): boolean => {
    const portfolioItem = portfolio.find(item => item.symbol === symbol);
    
    if (!portfolioItem || portfolioItem.quantity < quantity) {
      return false; // Insufficient shares
    }

    const totalValue = quantity * price;

    // Update virtual cash
    setVirtualCash(prev => prev + totalValue);

    // Add transaction
    const transaction: Transaction = {
      id: Date.now().toString(),
      type: 'sell',
      symbol,
      name: portfolioItem.name,
      quantity,
      price,
      total: totalValue,
      timestamp: new Date()
    };
    setTransactions(prev => [transaction, ...prev]);

    // Update portfolio
    setPortfolio(prev => {
      const newQuantity = portfolioItem.quantity - quantity;
      if (newQuantity === 0) {
        // Remove position completely
        return prev.filter(item => item.symbol !== symbol);
      } else {
        // Update position
        return prev.map(item =>
          item.symbol === symbol
            ? {
                ...item,
                quantity: newQuantity,
                currentPrice: price,
                totalValue: newQuantity * price,
                profitLoss: (price - item.averagePrice) * newQuantity,
                profitLossPercent: ((price - item.averagePrice) / item.averagePrice) * 100
              }
            : item
        );
      }
    });

    return true;
  };

  const addToWatchlist = (symbol: string, name: string, price: number, change: number, changePercent: number) => {
    const watchlistItem: WatchlistItem = {
      symbol,
      name,
      price,
      change,
      changePercent
    };
    
    setWatchlist(prev => {
      const exists = prev.some(item => item.symbol === symbol);
      if (!exists) {
        return [...prev, watchlistItem];
      }
      return prev;
    });
  };

  const removeFromWatchlist = (symbol: string) => {
    setWatchlist(prev => prev.filter(item => item.symbol !== symbol));
  };

  const isInWatchlist = (symbol: string): boolean => {
    return watchlist.some(item => item.symbol === symbol);
  };

  const getPortfolioItem = (symbol: string): PortfolioItem | undefined => {
    return portfolio.find(item => item.symbol === symbol);
  };

  const value: TradingContextType = {
    virtualCash,
    transactions,
    watchlist,
    portfolio,
    buyStock,
    sellStock,
    addToWatchlist,
    removeFromWatchlist,
    isInWatchlist,
    getPortfolioItem
  };

  return (
    <TradingContext.Provider value={value}>
      {children}
    </TradingContext.Provider>
  );
};
