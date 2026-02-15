import React, { createContext, useContext, ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { getComprehensiveStockData, getStockQuoteLite } from '@/lib/api-services';
import { useLivePrices } from '@/context/LivePriceContext';
import { useEffect } from 'react';

// Define the shape of the context data
interface StockDataContextType {
    symbol: string | undefined;
    stockDetails: any; // Contains all stock info
    historicalData: any;
    news: any;
    recommendations: any;
    technicals?: any;
    financials?: any;
    isLoading: boolean;
    isAnalyzing: boolean;
    error: Error | null;
    livePrice?: number;
}

// Create the context
const StockDataContext = createContext<StockDataContextType | undefined>(undefined);

// Create the provider component
export const StockDataProvider = ({ children }: { children: ReactNode }) => {
    const { symbol } = useParams<{ symbol: string }>();
    const { prices, subscribe, unsubscribe } = useLivePrices();

    // High-frequency subscription
    useEffect(() => {
        if (symbol) {
            subscribe([symbol]);
            return () => unsubscribe([symbol]);
        }
    }, [symbol, subscribe, unsubscribe]);

    // Fast Query: Quote Only (REST fallback)
    const { data: quoteData, isLoading: isQuoteLoading } = useQuery({
        queryKey: ['stock-quote', symbol],
        queryFn: () => getStockQuoteLite(symbol!),
        enabled: !!symbol,
        staleTime: 10000,
    });

    // Slow Query: Comprehensive Data
    const { data: comprehensiveData, isLoading: isCompLoading, error } = useQuery({
        queryKey: ['comprehensive-stock-data', symbol],
        queryFn: () => getComprehensiveStockData(symbol!),
        enabled: !!symbol,
    });

    const value = {
        symbol,
        // Merge Quote info into Details if Comp data not yet ready
        stockDetails: comprehensiveData?.info || (quoteData ? {
            symbol: quoteData.symbol,
            currentPrice: quoteData.price,
            previousClose: quoteData.previous_close,
            dayHigh: quoteData.day_high,
            dayLow: quoteData.day_low,
            marketCap: quoteData.market_cap,
            volume: quoteData.volume,
            longName: quoteData.name
        } : undefined),
        historicalData: comprehensiveData?.history,
        news: comprehensiveData?.news,
        recommendations: comprehensiveData?.recommendations,
        technicals: comprehensiveData?.technicals,
        financials: comprehensiveData?.financials,
        livePrice: symbol ? prices[symbol]?.ltp : undefined,
        isLoading: isQuoteLoading, // Initial load depends on Quote
        isAnalyzing: isCompLoading, // Secondary load for analysis
        error: error as Error | null,
    };

    return (
        <StockDataContext.Provider value={value}>
            {children}
        </StockDataContext.Provider>
    );
};

// Create a custom hook to use the context
export const useStockData = () => {
    const context = useContext(StockDataContext);
    if (context === undefined) {
        throw new Error('useStockData must be used within a StockDataProvider');
    }
    return context;
};
