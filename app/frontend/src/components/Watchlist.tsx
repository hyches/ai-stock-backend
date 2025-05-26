import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { useWatchlist } from '../hooks/useWatchlist';

/**
 * Renders the user's current watchlist with its name and item count, or appropriate loading/error messages.
 * @example
 * renderWatchlist()
 * <Box>
 *   <Typography variant="h4" gutterBottom>Watchlist</Typography>
 *   <Card>
 *     <CardContent>
 *       <Typography variant="h6">My Watchlist</Typography>
 *       <Typography variant="body2">5 items</Typography>
 *     </CardContent>
 *   </Card>
 * </Box>
 * @param {Object} watchlistData - An object containing watchlists, the current watchlist, loading state, and error message.
 * @returns {JSX.Element} A JSX element displaying loading/error messages or the current watchlist.
 * @description
 *   - Returns a loading message until data is fetched.
 *   - Displays an error message if there's an error during data fetching.
 *   - Shows the name and item count of the selected watchlist when available.
 */
const Watchlist: React.FC = () => {
  const { watchlists, currentWatchlist, loading, error } = useWatchlist();

  if (loading) {
    return (
      <Box>
        <Typography>Loading watchlist...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Watchlist
      </Typography>
      {currentWatchlist ? (
        <Card>
          <CardContent>
            <Typography variant="h6">{currentWatchlist.name}</Typography>
            <Typography variant="body2">
              {currentWatchlist.items.length} items
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <Typography>No watchlist selected</Typography>
      )}
    </Box>
  );
};

export default Watchlist;

 