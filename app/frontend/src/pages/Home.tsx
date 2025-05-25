import React from 'react';
import Dashboard from '../components/Dashboard';
import MarketOverview from '../components/MarketOverview';
import Box from '@mui/material/Box';

const Home: React.FC = () => (
  <Box>
    <Dashboard />
    <MarketOverview />
  </Box>
);

export default Home; 