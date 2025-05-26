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
  notes?: string;
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

/**
* Manages user's watchlists by providing operations to fetch, create, update, delete, and modify watchlist items.
* @example
* const { watchlists, currentWatchlist, createWatchlist } = useWatchlist();
* createWatchlist('New Watchlist', 'My stock watchlist');
* @param {void} - No parameters required for initialization, hooks into component lifecycle to manage state.
* @returns {UseWatchlistReturn} An object containing the watchlists, current watchlist, loading state, error state, and various operations on watchlists.
* @description
*   - Handles asynchronous operations for CRUD actions on watchlists using API calls.
*   - Sets the first watchlist as the current one if no current watchlist is selected upon fetching.
*   - Provides error handling for network or API issues with specific error messages.
*   - Automatically refreshes watchlists upon initialization.
*/
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

  /**
  * Creates a new watchlist with the specified name and optional description.
  * @example
  * sync("Movies to Watch", "A list of must-see movies")
  * Updates the application's state with the newly created watchlist object.
  * @param {string} name - The name of the watchlist to be created.
  * @param {string} [description] - Optional description for the watchlist.
  * @returns {Promise<void>} Returns a promise that resolves when the watchlist is created and states are updated.
  * @description
  *   - Sends a POST request to the '/api/watchlists' endpoint to create the watchlist.
  *   - Updates the local state with the response data to reflect the newly created watchlist.
  *   - Logs errors to the console and rethrows them in case of request failure.
  */
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

  /**
   * Updates a specific watchlist with new data.
   * @example
   * sync('1234', { name: 'Tech Stocks', visible: true })
   * // Updates the watchlist with id '1234' and returns the updated watchlist object
   * @param {string} id - The unique identifier of the watchlist to update.
   * @param {Partial<Watchlist>} updates - An object containing the properties to update on the watchlist.
   * @returns {Promise<Watchlist>} Returns a promise that resolves to the updated watchlist object.
   * @description
   *   - Emits a fetch request to the API endpoint to update the watchlist.
   *   - Handles both updating the list of watchlists and updating the current watchlist if it matches the provided id.
   */
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

  /**
  * Deletes a watchlist by its ID and updates the state accordingly.
  * @example
  * sync('12345')
  * // Watchlist with ID '12345' is deleted, and state is updated.
  * @param {string} id - The ID of the watchlist to be deleted.
  * @returns {void} No return value.
  * @description
  *   - Updates the state to remove the watchlist from the list of watchlists.
  *   - Sets the current watchlist to null if the deleted watchlist was the current one.
  *   - Logs an error to the console if the operation fails.
  */
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

  /**
   * Synchronizes a symbol with a specific watchlist on the server.
   * @example
   * sync("abcd1234", "AAPL")
   * // Returns updated watchlist including the symbol "AAPL".
   * @param {string} watchlistId - The ID of the watchlist to update.
   * @param {string} symbol - The stock symbol to be added to the watchlist.
   * @returns {Promise<Object>} Updated watchlist data.
   * @description
   *   - Makes a POST request to the server with the watchlist ID and symbol.
   *   - Updates local state to reflect changes in the targeted watchlist.
   *   - Updates the current watchlist if it matches the ID being synced.
   *   - Handles errors and logs them to the console while rethrowing the error for further handling.
   */
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

  /**
   * Removes a symbol from a specified watchlist.
   * @example
   * sync("123456", "AAPL")
   * undefined
   * @param {string} watchlistId - Unique identifier of the watchlist where the symbol should be removed.
   * @param {string} symbol - The stock symbol to be removed from the watchlist.
   * @returns {void} Does not return a value.
   * @description
   *   - Updates the watchlist data both locally and in response to a successful server call.
   *   - Handles any errors that occur during the API call by logging the error and re-throwing it.
   *   - Checks if the current watchlist is affected and updates it accordingly.
   *   - Uses a placeholder API call for demonstration and requires replacement with the actual API endpoint in production.
   */
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