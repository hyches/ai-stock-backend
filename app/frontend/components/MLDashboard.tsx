import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Paper,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { styled } from '@mui/material/styles';

// Styled components
const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.2s',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: theme.shadows[4],
  },
}));

const PredictionValue = styled(Typography)(({ theme }) => ({
  fontSize: '2rem',
  fontWeight: 'bold',
  color: theme.palette.primary.main,
}));

const ConfidenceIndicator = styled(Box)(({ confidence }) => ({
  width: '100%',
  height: '4px',
  backgroundColor: '#e0e0e0',
  borderRadius: '2px',
  marginTop: '8px',
  '&::after': {
    content: '""',
    display: 'block',
    width: `${confidence * 100}%`,
    height: '100%',
    backgroundColor: confidence > 0.7 ? '#4caf50' : confidence > 0.4 ? '#ff9800' : '#f44336',
    borderRadius: '2px',
    transition: 'width 0.3s ease-in-out',
  },
}));

interface MLPrediction {
  predictions: {
    random_forest: number;
    gradient_boosting: number;
    ensemble: number;
  };
  confidence: number;
  time_horizon: string;
  feature_importance: Record<string, number>;
}

interface MLDashboardProps {
  symbol: string;
}

const MLDashboard: React.FC<MLDashboardProps> = ({ symbol }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [predictions, setPredictions] = useState<{
    price: MLPrediction;
    volatility: MLPrediction;
    trend: MLPrediction;
  } | null>(null);

  useEffect(() => {
    const fetchPredictions = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/ml/predictions/${symbol}`);
        if (!response.ok) {
          throw new Error('Failed to fetch predictions');
        }
        const data = await response.json();
        setPredictions(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchPredictions();
    const interval = setInterval(fetchPredictions, 300000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, [symbol]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!predictions) {
    return null;
  }

  const renderPredictionCard = (title: string, prediction: MLPrediction) => (
    <StyledCard>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <PredictionValue>
          {prediction.predictions.ensemble.toFixed(2)}
        </PredictionValue>
        <Typography variant="body2" color="textSecondary">
          Confidence: {(prediction.confidence * 100).toFixed(1)}%
        </Typography>
        <ConfidenceIndicator confidence={prediction.confidence} />
        <Box mt={2}>
          <Typography variant="subtitle2" gutterBottom>
            Model Predictions:
          </Typography>
          <Grid container spacing={1}>
            <Grid item xs={4}>
              <Typography variant="caption" display="block">
                Random Forest
              </Typography>
              <Typography variant="body2">
                {prediction.predictions.random_forest.toFixed(2)}
              </Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="caption" display="block">
                Gradient Boosting
              </Typography>
              <Typography variant="body2">
                {prediction.predictions.gradient_boosting.toFixed(2)}
              </Typography>
            </Grid>
            <Grid item xs={4}>
              <Typography variant="caption" display="block">
                Ensemble
              </Typography>
              <Typography variant="body2">
                {prediction.predictions.ensemble.toFixed(2)}
              </Typography>
            </Grid>
          </Grid>
        </Box>
      </CardContent>
    </StyledCard>
  );

  const renderFeatureImportance = (prediction: MLPrediction) => (
    <Paper sx={{ p: 2, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Feature Importance
      </Typography>
      <Box sx={{ height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={Object.entries(prediction.feature_importance).map(([feature, importance]) => ({
              feature,
              importance,
            }))}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="feature" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="importance"
              stroke="#8884d8"
              activeDot={{ r: 8 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        ML Predictions for {symbol}
      </Typography>
      
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Price" />
        <Tab label="Volatility" />
        <Tab label="Trend" />
      </Tabs>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          {activeTab === 0 && renderPredictionCard('Price Prediction', predictions.price)}
          {activeTab === 1 && renderPredictionCard('Volatility Prediction', predictions.volatility)}
          {activeTab === 2 && renderPredictionCard('Trend Prediction', predictions.trend)}
        </Grid>
        <Grid item xs={12} md={6}>
          {activeTab === 0 && renderFeatureImportance(predictions.price)}
          {activeTab === 1 && renderFeatureImportance(predictions.volatility)}
          {activeTab === 2 && renderFeatureImportance(predictions.trend)}
        </Grid>
      </Grid>
    </Box>
  );
};

export default MLDashboard; 