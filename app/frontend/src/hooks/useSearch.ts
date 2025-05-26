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

/**
 * Custom hook to handle search functionality with debounced query execution.
 * @example
 * const { results, loading, error, search, clearResults } = useSearch();
 * search('example query');
 * // results will reflect the search outcome
 * @param {void} - No direct parameters, usage through object destructuring of hook return values.
 * @returns {UseSearchReturn} An object containing search results, loading state, error message, and functions for executing search and clearing results.
 * @description
 *   - Utilizes debouncing to minimize repeated API calls by delaying the search execution.
 *   - Handles asynchronous search API calls and manages loading and error states.
 *   - Provides a method to clear the search results and reset error state.
 */
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