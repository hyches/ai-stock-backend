import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const MarketOverview: React.FC = () => {
  return (
    <Box sx={{ mt: 4 }}>
      <Card>
        <CardContent>
          <Typography variant="h5">Market Overview</Typography>
          <Typography variant="body2">(Coming soon: market indices, sector performance, etc.)</Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default MarketOverview; 