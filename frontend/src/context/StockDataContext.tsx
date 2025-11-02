import React, { createContext, useContext, ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import {
    getStockDetails,
    getStockHistoricalData,
    getStockNews,
    getStockAnalysis,
    getStockFinancials,
    getStockPeers,
} from '@/lib/api-services';

// Define the shape of the context data
interface StockDataContextType {
    symbol: string | undefined;
    stockDetails: any;
    historicalData: any;
    news: any;
    analysis: any;
    financials: any;
    peers: any;
    isLoading: boolean;
    error: Error | null;
}

// Create the context
const StockDataContext = createContext<StockDataContextType | undefined>(undefined);

// Create the provider component
export const StockDataProvider = ({ children }: { children: ReactNode }) => {
    const { symbol } = useParams<{ symbol: string }>();

    const { data: stockDetails, isLoading: detailsLoading, error: detailsError } = useQuery({
        queryKey: ['stock-details', symbol],
        queryFn: () => getStockDetails(symbol!),
        enabled: !!symbol,
    });

    const { data: historicalData, isLoading: historicalLoading } = useQuery({
        queryKey: ['stock-historical', symbol, '1Y'],
        queryFn: () => getStockHistoricalData(symbol!, '1Y'),
        enabled: !!symbol,
    });

    const { data: news, isLoading: newsLoading } = useQuery({
        queryKey: ['stock-news', symbol],
        queryFn: () => getStockNews(symbol!),
        enabled: !!symbol,
    });

    const { data: analysis, isLoading: analysisLoading } = useQuery({
        queryKey: ['stock-analysis', symbol],
        queryFn: () => getStockAnalysis(symbol!),
        enabled: !!symbol,
    });

    const { data: financials, isLoading: financialsLoading } = useQuery({
        queryKey: ['stock-financials', symbol],
        queryFn: () => getStockFinancials(symbol!),
        enabled: !!symbol,
    });

    const { data: peers, isLoading: peersLoading } = useQuery({
        queryKey: ['stock-peers', symbol],
        queryFn: () => getStockPeers(symbol!),
        enabled: !!symbol,
    });

    const isLoading = detailsLoading || historicalLoading || newsLoading || analysisLoading || financialsLoading || peersLoading;

    const value = {
        symbol,
        stockDetails,
        historicalData,
        news,
        analysis,
        financials,
        peers,
        isLoading,
        error: detailsError as Error | null,
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
