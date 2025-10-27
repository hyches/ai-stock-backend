import React, { createContext, useContext } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { placeOrder } from '@/lib/api';
import { usePortfolio, useWatchlist } from '@/lib/queries';

interface TradingContextType {
  buyStock: (symbol: string, name: string, quantity: number, price: number) => Promise<any>;
  sellStock: (symbol: string, name: string, quantity: number, price: number) => Promise<any>;
  addToWatchlist: (symbol: string, name: string, price: number, change: number, changePercent: number) => Promise<any>;
  removeFromWatchlist: (symbol: string) => Promise<any>;
  isInWatchlist: (symbol: string) => boolean;
  getPortfolioItem: (symbol: string) => any;
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
  const queryClient = useQueryClient();
  const { data: portfolio = [] } = usePortfolio();
  const { data: watchlist = [] } = useWatchlist();

  const mutationOptions = {
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolio'] });
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['watchlist'] });
    },
  };

  const buyStockMutation = useMutation({
    mutationFn: (variables: { symbol: string; name: string; quantity: number; price: number }) =>
      placeOrder({ ...variables, side: 'buy' }),
    ...mutationOptions,
  });

  const sellStockMutation = useMutation({
    mutationFn: (variables: { symbol: string; name: string; quantity: number; price: number }) =>
      placeOrder({ ...variables, side: 'sell' }),
    ...mutationOptions,
  });

  const addToWatchlistMutation = useMutation({
    mutationFn: (variables: { symbol: string; name: string; price: number; change: number; changePercent: number }) =>
      addToWatchlistApi(variables), // Replace with your actual API call
    ...mutationOptions,
  });

  const removeFromWatchlistMutation = useMutation({
    mutationFn: (symbol: string) => removeFromWatchlistApi(symbol), // Replace with your actual API call
    ...mutationOptions,
  });

  const isInWatchlist = (symbol: string): boolean => {
    return watchlist.some((item: any) => item.symbol === symbol);
  };

  const getPortfolioItem = (symbol: string) => {
    return portfolio.find((item: any) => item.symbol === symbol);
  };

  const value: TradingContextType = {
    buyStock: buyStockMutation.mutateAsync,
    sellStock: sellStockMutation.mutateAsync,
    addToWatchlist: addToWatchlistMutation.mutateAsync,
    removeFromWatchlist: removeFromWatchlistMutation.mutateAsync,
    isInWatchlist,
    getPortfolioItem,
  };

  return (
    <TradingContext.Provider value={value}>
      {children}
    </TradingContext.Provider>
  );
};

// Placeholder API functions for watchlist - replace with your actual API calls
const addToWatchlistApi = async (variables: any) => {
  console.log('Adding to watchlist:', variables);
  return Promise.resolve();
};

const removeFromWatchlistApi = async (symbol: string) => {
  console.log('Removing from watchlist:', symbol);
  return Promise.resolve();
};
