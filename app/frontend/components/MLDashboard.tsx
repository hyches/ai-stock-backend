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

/**
 * Displays machine learning predictions and feature importance for a specific stock symbol.
 * @example
 * MLComponent({ symbol: 'AAPL' })
 * Returns JSX elements showing predictions data and UI components.
 * @param {Object} {symbol} - The stock symbol for which predictions are fetched.
 * @returns {JSX.Element | null} Rendered dashboard of predictions or loading/error UI.
 * @description
 *   - Fetches predictions data every 5 minutes using the specified stock symbol.
 *   - Displays loading indicator or error message based on fetch status.
 *   - Renders prediction cards and feature importance charts using Material-UI components.
 *   - Allows user to switch between different prediction categories using tabs.
 */
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
    /**
     * Fetches machine learning predictions for a given symbol and updates the application state.
     * @example
     * sync('AAPL')
     * // Fetches predictions for Apple Inc.
     * @param {string} symbol - The stock symbol for which predictions are to be fetched.
     * @returns {void} The function does not return a value; it updates the application state directly.
     * @description
     *   - Starts by setting a loading state to true and resets it to false after completion.
     *   - Handles errors by updating the error state with a meaningful message.
     *   - Ensures that the predictions are updated only if the fetch response is successful.
     */
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

  /**
  * Renders a styled card displaying the machine learning prediction details.
  * @example
  * renderPredictionCard("Prediction Title", mlPredictionObject)
  * Returns a styled card component displaying prediction details.
  * @param {string} title - The title to be displayed on the card.
  * @param {MLPrediction} prediction - An object containing prediction details, including predictions and confidence levels.
  * @returns {JSX.Element} A JSX component representing the styled card with prediction information.
  * @description
  *   - Utilizes styled components and Material-UI typography.
  *   - Displays ensemble prediction value to two decimal places.
  *   - Confidence levels are shown as percentages.
  *   - Includes individual model predictions from Random Forest and Gradient Boosting.
  */
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

  /**
   * Creates a chart displaying the importance of various features in a machine learning prediction.
   * @example
   * prediction({ feature_importance: { 'feature1': 0.8, 'feature2': 0.2 } })
   * // Renders a chart with lines showing the importance of 'feature1' and 'feature2'.
   * @param {MLPrediction} prediction - An object containing the feature importance mapping.
   * @returns {React.JSXElement} A Paper component containing a line chart displaying the feature importance.
   * @description
   *   - Utilizes the `LineChart` component to visualize the importance of features from the prediction object.
   *   - Maps feature importance data into a format suitable for the `LineChart` component.
   *   - Adjusts the layout of the chart with padding and margins for better visual appearance.
   */
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