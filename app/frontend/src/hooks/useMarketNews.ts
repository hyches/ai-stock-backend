import { useState, useEffect, useCallback } from 'react';

interface NewsItem {
  id: string;
  title: string;
  content: string;
  source: string;
  url: string;
  publishedAt: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  symbols: string[];
  categories: string[];
  imageUrl?: string;
}

interface UseMarketNewsReturn {
  news: NewsItem[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  filterBySymbol: (symbol: string) => void;
  filterByCategory: (category: string) => void;
  filterBySentiment: (sentiment: NewsItem['sentiment']) => void;
  clearFilters: () => void;
}

/**
 * Custom hook to fetch and filter market news based on given criteria.
 * @example
 * useMarketNews({ symbols: ['AAPL', 'GOOG'], categories: ['Tech'], sentiment: 'positive' })
 * returns an object containing news items, loading status, errors, methods for filtering news, and a refresh function.
 * @param {?Object} [initialFilters] - Optional initial filters to apply for news fetching.
 * @param {?string[]} [initialFilters.symbols] - List of stock symbols to filter news.
 * @param {?string[]} [initialFilters.categories] - List of categories to filter news.
 * @param {?string} [initialFilters.sentiment] - Type of sentiment to filter news.
 * @returns {Object} - An object containing the fetched news data, loading state, error, and methods for managing filters.
 * @description
 *   - Utilizes useState and useEffect hooks to manage data fetching and component lifecycle.
 *   - Employs fetch API to retrieve news data, handling errors by setting an error state.
 *   - Provides methods to dynamically update filters, retry fetching news, and reset filters.
 */
export const useMarketNews = (
  initialFilters?: {
    symbols?: string[];
    categories?: string[];
    sentiment?: NewsItem['sentiment'];
  }
): UseMarketNewsReturn => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState(initialFilters || {});

  const fetchNews = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      const response = await fetch('/api/news', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters),
      });
      const data = await response.json();
      setNews(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch news');
      console.error('Error fetching market news:', err);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  const filterBySymbol = (symbol: string) => {
    setFilters((prev) => ({
      ...prev,
      symbols: prev.symbols?.includes(symbol)
        ? prev.symbols.filter((s) => s !== symbol)
        : [...(prev.symbols || []), symbol],
    }));
  };

  const filterByCategory = (category: string) => {
    setFilters((prev) => ({
      ...prev,
      categories: prev.categories?.includes(category)
        ? prev.categories.filter((c) => c !== category)
        : [...(prev.categories || []), category],
    }));
  };

  const filterBySentiment = (sentiment: NewsItem['sentiment']) => {
    setFilters((prev) => ({
      ...prev,
      sentiment: prev.sentiment === sentiment ? undefined : sentiment,
    }));
  };

  const clearFilters = () => {
    setFilters({});
  };

  return {
    news,
    loading,
    error,
    refresh: fetchNews,
    filterBySymbol,
    filterByCategory,
    filterBySentiment,
    clearFilters,
  };
};

export default useMarketNews; 