import { useState, useEffect, useCallback } from 'react';

interface WatchlistItem {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  lastUpdated: string;
  notes?: string[];
  tags?: string[];
}

interface Watchlist {
  id: string;
  name: string;
  description?: string;
  items: WatchlistItem[];
  isPublic: boolean;
  createdAt: string;
  updatedAt: string;
}

interface UseWatchlistReturn {
  watchlists: Watchlist[];
  currentWatchlist: Watchlist | null;
  loading: boolean;
  error: string | null;
  createWatchlist: (name: string, description?: string) => Promise<void>;
  updateWatchlist: (id: string, updates: Partial<Watchlist>) => Promise<void>;
  deleteWatchlist: (id: string) => Promise<void>;
  addToWatchlist: (watchlistId: string, symbol: string) => Promise<void>;
  removeFromWatchlist: (watchlistId: string, symbol: string) => Promise<void>;
  setCurrentWatchlist: (id: string) => void;
  refresh: () => Promise<void>;
}

export const useWatchlist = (): UseWatchlistReturn => {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [currentWatchlist, setCurrentWatchlist] = useState<Watchlist | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWatchlists = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      const response = await fetch('/api/watchlists');
      const data = await response.json();
      setWatchlists(data);
      if (data.length > 0 && !currentWatchlist) {
        setCurrentWatchlist(data[0]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch watchlists');
      console.error('Error fetching watchlists:', err);
    } finally {
      setLoading(false);
    }
  }, [currentWatchlist]);

  useEffect(() => {
    fetchWatchlists();
  }, [fetchWatchlists]);

  const createWatchlist = async (name: string, description?: string) => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch('/api/watchlists', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description }),
      });
      const newWatchlist = await response.json();
      setWatchlists((prev) => [...prev, newWatchlist]);
      setCurrentWatchlist(newWatchlist);
    } catch (err) {
      console.error('Error creating watchlist:', err);
      throw err;
    }
  };

  const updateWatchlist = async (id: string, updates: Partial<Watchlist>) => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch(`/api/watchlists/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });
      const updatedWatchlist = await response.json();
      setWatchlists((prev) =>
        prev.map((w) => (w.id === id ? updatedWatchlist : w))
      );
      if (currentWatchlist?.id === id) {
        setCurrentWatchlist(updatedWatchlist);
      }
    } catch (err) {
      console.error('Error updating watchlist:', err);
      throw err;
    }
  };

  const deleteWatchlist = async (id: string) => {
    try {
      // TODO: Replace with actual API call
      await fetch(`/api/watchlists/${id}`, { method: 'DELETE' });
      setWatchlists((prev) => prev.filter((w) => w.id !== id));
      if (currentWatchlist?.id === id) {
        setCurrentWatchlist(null);
      }
    } catch (err) {
      console.error('Error deleting watchlist:', err);
      throw err;
    }
  };

  const addToWatchlist = async (watchlistId: string, symbol: string) => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch(`/api/watchlists/${watchlistId}/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol }),
      });
      const updatedWatchlist = await response.json();
      setWatchlists((prev) =>
        prev.map((w) => (w.id === watchlistId ? updatedWatchlist : w))
      );
      if (currentWatchlist?.id === watchlistId) {
        setCurrentWatchlist(updatedWatchlist);
      }
    } catch (err) {
      console.error('Error adding to watchlist:', err);
      throw err;
    }
  };

  const removeFromWatchlist = async (watchlistId: string, symbol: string) => {
    try {
      // TODO: Replace with actual API call
      const response = await fetch(`/api/watchlists/${watchlistId}/items/${symbol}`, {
        method: 'DELETE',
      });
      const updatedWatchlist = await response.json();
      setWatchlists((prev) =>
        prev.map((w) => (w.id === watchlistId ? updatedWatchlist : w))
      );
      if (currentWatchlist?.id === watchlistId) {
        setCurrentWatchlist(updatedWatchlist);
      }
    } catch (err) {
      console.error('Error removing from watchlist:', err);
      throw err;
    }
  };

  const setCurrentWatchlistById = (id: string) => {
    const watchlist = watchlists.find((w) => w.id === id);
    if (watchlist) {
      setCurrentWatchlist(watchlist);
    }
  };

  return {
    watchlists,
    currentWatchlist,
    loading,
    error,
    createWatchlist,
    updateWatchlist,
    deleteWatchlist,
    addToWatchlist,
    removeFromWatchlist,
    setCurrentWatchlist: setCurrentWatchlistById,
    refresh: fetchWatchlists,
  };
};

export default useWatchlist; 