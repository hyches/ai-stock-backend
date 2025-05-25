import { useState, useCallback, useEffect } from 'react';
import { marketApi } from '../services/api';

interface SearchResult {
  symbol: string;
  name: string;
  type: 'stock' | 'crypto' | 'forex' | 'index';
  exchange?: string;
  currency?: string;
}

interface UseSearchReturn {
  results: SearchResult[];
  loading: boolean;
  error: string | null;
  search: (query: string) => Promise<void>;
  clearResults: () => void;
}

export const useSearch = (): UseSearchReturn => {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (query: string) => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await marketApi.searchSymbols(query);
      setResults(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
      console.error('Error searching symbols:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearResults = useCallback(() => {
    setResults([]);
    setError(null);
  }, []);

  // Debounce search
  useEffect(() => {
    let timeoutId: NodeJS.Timeout;
    const debouncedSearch = (query: string) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        search(query);
      }, 300);
    };

    return () => {
      clearTimeout(timeoutId);
    };
  }, [search]);

  return {
    results,
    loading,
    error,
    search,
    clearResults,
  };
};

export default useSearch; 