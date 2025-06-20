import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';
import { useWatchlist } from '../hooks/useWatchlist';

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