import React from 'react';
import { usePortfolio, useWatchlist } from '@/hooks/use-api';

const ApiTest = () => {
  const { data: portfolio, isLoading: portfolioLoading, error: portfolioError } = usePortfolio();
  const { data: watchlist, isLoading: watchlistLoading, error: watchlistError } = useWatchlist();

  return (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold">API Connection Test</h2>
      
      <div className="space-y-2">
        <h3 className="font-semibold">Portfolio Data:</h3>
        {portfolioLoading && <p className="text-blue-500">Loading portfolio...</p>}
        {portfolioError && <p className="text-red-500">Error loading portfolio: {portfolioError.message}</p>}
        {portfolio && (
          <pre className="bg-gray-800 p-2 rounded text-sm overflow-auto">
            {JSON.stringify(portfolio, null, 2)}
          </pre>
        )}
      </div>

      <div className="space-y-2">
        <h3 className="font-semibold">Watchlist Data:</h3>
        {watchlistLoading && <p className="text-blue-500">Loading watchlist...</p>}
        {watchlistError && <p className="text-red-500">Error loading watchlist: {watchlistError.message}</p>}
        {watchlist && (
          <pre className="bg-gray-800 p-2 rounded text-sm overflow-auto">
            {JSON.stringify(watchlist, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
};

export default ApiTest; 