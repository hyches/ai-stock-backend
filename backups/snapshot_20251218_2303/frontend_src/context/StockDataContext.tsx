import React, { createContext, useContext, ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { getComprehensiveStockData } from '@/lib/api-services';

// Define the shape of the context data
interface StockDataContextType {
    symbol: string | undefined;
    stockDetails: any; // Contains all stock info
    historicalData: any;
    news: any;
    recommendations: any;
    isLoading: boolean;
    error: Error | null;
}

// Create the context
const StockDataContext = createContext<StockDataContextType | undefined>(undefined);

// Create the provider component
export const StockDataProvider = ({ children }: { children: ReactNode }) => {
    const { symbol } = useParams<{ symbol: string }>();

    const { data: comprehensiveData, isLoading, error } = useQuery({
        queryKey: ['comprehensive-stock-data', symbol],
        queryFn: () => getComprehensiveStockData(symbol!),
        enabled: !!symbol,
    });

    const value = {
        symbol,
        stockDetails: comprehensiveData?.info,
        historicalData: comprehensiveData?.history,
        news: comprehensiveData?.news,
        recommendations: comprehensiveData?.recommendations,
        isLoading,
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
