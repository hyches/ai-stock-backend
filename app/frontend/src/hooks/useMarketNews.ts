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