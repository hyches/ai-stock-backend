import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useApi } from '../hooks/useApi';
import SignalList from './SignalList';
import PortfolioSummary from './PortfolioSummary';
import StrategyList from './StrategyList';
import TradeHistory from './TradeHistory';
import EquityCurveChart from './charts/EquityCurveChart';
import { EquityCurvePoint } from '../types';
import { sharedStyles } from '../styles/shared';

const TradingDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [equityCurve, setEquityCurve] = useState<EquityCurvePoint[]>([]);
  const api = useApi();

  useEffect(() => {
    const initializeDashboard = async () => {
      try {
        setLoading(true);
        // Load initial data
        const [portfolioResponse, strategiesResponse, signalsResponse, tradesResponse, equityResponse] = await Promise.all([
          api.get('/portfolio/summary'),
          api.get('/strategies/'),
          api.get('/signals/'),
          api.get('/trades/'),
          api.get('/portfolio/equity-curve')
        ]);
        
        setEquityCurve(equityResponse.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load dashboard data');
        setLoading(false);
      }
    };

    initializeDashboard();
  }, []);

  if (loading) {
    return (
      <Box sx={sharedStyles.loadingContainer}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={sharedStyles.errorContainer}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Trading Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <PortfolioSummary />
        </Grid>
        <Grid item xs={12} md={6}>
          <StrategyList />
        </Grid>
        <Grid item xs={12}>
          <EquityCurveChart data={equityCurve} />
        </Grid>
        <Grid item xs={12}>
          <SignalList />
        </Grid>
        <Grid item xs={12}>
          <TradeHistory />
        </Grid>
      </Grid>
    </Box>
  );
};

export default TradingDashboard; 