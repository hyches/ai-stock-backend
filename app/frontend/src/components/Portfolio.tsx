import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Info,
  Refresh,
} from '@mui/icons-material';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from 'recharts';

interface PortfolioItem {
  symbol: string;
  shares: number;
  avgPrice: number;
  currentPrice: number;
  value: number;
  change: number;
  changePercent: number;
  mlPrediction: {
    direction: 'up' | 'down' | 'neutral';
    confidence: number;
    prediction: number;
  };
}

/**
 * Displays a portfolio with its current value, change, and machine learning predictions.
 * @example
 * Portfolio()
 * <Box>...</Box>
 * @param {none} - This component does not take any arguments.
 * @returns {JSX.Element} A React component rendering the portfolio overview including tables, charts, and various details.
 * @description
 *   - Fetches and displays portfolio data from a specified API endpoint.
 *   - Utilizes `useState` and `useEffect` hooks for state management and data fetching.
 *   - Renders dynamic value changes and machine learning predictions using specialized UI components.
 *   - Provides a manual refresh capability to reload portfolio data via button interaction.
 */
const Portfolio: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);
  const [totalValue, setTotalValue] = useState(0);
  const [totalChange, setTotalChange] = useState(0);

  /**
  * Fetches and updates the portfolio information from the API
  * @example
  * sync()
  * // Updates portfolio state with retrieved data
  * @param {None}
  * @returns {void} Does not return a value.
  * @description
  *   - Uses a placeholder API endpoint `/api/portfolio` to fetch portfolio data.
  *   - Handles API call errors by logging them to the console.
  *   - Ensures the loading state is set appropriately before and after the API call.
  */
  const fetchPortfolio = async () => {
    try {
      setLoading(true);
      // TODO: Replace with actual API call
      const response = await fetch('/api/portfolio');
      const data = await response.json();
      setPortfolio(data.items);
      setTotalValue(data.totalValue);
      setTotalChange(data.totalChange);
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  /**
  * Renders a component displaying a financial value and its percentage change with appropriate styling.
  * @example
  * renderFinancialChange(120.50, 5.45)
  * // Returns a JSX element showing "$120.50" in green and "5.45%" with an upward trending icon.
  * @param {number} value - The financial value whose change is represented.
  * @param {number} percent - The percentage change of the financial value.
  * @returns {JSX.Element} A styled Box component with Typography and an icon indicating the trend direction.
  * @description
  *   - Values are styled according to whether they are positive or negative.
  *   - Adjusts font and color based on the value's sign for visual representation.
  *   - Includes an icon representing upward or downward trend correlated with the value sign.
  *   - Uses Material-UI components for styling and structure.
  */
  const renderValueChange = (value: number, percent: number) => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Typography
        variant="body2"
        color={value >= 0 ? 'success.main' : 'error.main'}
        sx={{ fontWeight: 'bold' }}
      >
        ${Math.abs(value).toFixed(2)}
      </Typography>
      <Typography
        variant="body2"
        color={value >= 0 ? 'success.main' : 'error.main'}
      >
        ({percent.toFixed(2)}%)
      </Typography>
      {value >= 0 ? (
        <TrendingUp color="success" fontSize="small" />
      ) : (
        <TrendingDown color="error" fontSize="small" />
      )}
    </Box>
  );

  /**
   * Renders a UI component displaying machine learning predictions for a portfolio item.
   * @example
   * predictionComponent({ direction: 'up', confidence: 0.95, prediction: 1.5 })
   * <Box>...</Box>
   * @param {Object} prediction - The portfolio item prediction object containing direction, confidence, and prediction values.
   * @returns {JSX.Element} A React component that consists of a Chip and a Tooltip, visually representing the prediction details.
   * @description
   *   - The chip color changes based on the prediction direction ('up', 'down', or default).
   *   - The confidence level is displayed as a percentage within the chip label.
   *   - Tooltip provides additional detail on the predicted percentage change.
   */
  const renderMLPrediction = (prediction: PortfolioItem['mlPrediction']) => (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Chip
        label={`${prediction.direction.toUpperCase()} (${(prediction.confidence * 100).toFixed(1)}%)`}
        color={
          prediction.direction === 'up'
            ? 'success'
            : prediction.direction === 'down'
            ? 'error'
            : 'default'
        }
        size="small"
      />
      <Tooltip title={`Predicted change: ${prediction.prediction.toFixed(2)}%`}>
        <Info fontSize="small" color="action" />
      </Tooltip>
    </Box>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Portfolio</Typography>
        <IconButton onClick={fetchPortfolio}>
          <Refresh />
        </IconButton>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Value
              </Typography>
              <Typography variant="h4" sx={{ mb: 1 }}>
                ${totalValue.toFixed(2)}
              </Typography>
              {renderValueChange(totalChange, (totalChange / (totalValue - totalChange)) * 100)}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Portfolio Performance
              </Typography>
              <Box sx={{ height: 200 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={portfolio.map(item => ({
                      date: new Date().toISOString().split('T')[0],
                      value: item.value,
                    }))}
                    margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <RechartsTooltip />
                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="#8884d8"
                      fill="#8884d8"
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12}>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Symbol</TableCell>
                  <TableCell align="right">Shares</TableCell>
                  <TableCell align="right">Avg Price</TableCell>
                  <TableCell align="right">Current Price</TableCell>
                  <TableCell align="right">Value</TableCell>
                  <TableCell align="right">Change</TableCell>
                  <TableCell align="right">ML Prediction</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {portfolio.map((item) => (
                  <TableRow key={item.symbol}>
                    <TableCell component="th" scope="row">
                      {item.symbol}
                    </TableCell>
                    <TableCell align="right">{item.shares}</TableCell>
                    <TableCell align="right">${item.avgPrice.toFixed(2)}</TableCell>
                    <TableCell align="right">${item.currentPrice.toFixed(2)}</TableCell>
                    <TableCell align="right">${item.value.toFixed(2)}</TableCell>
                    <TableCell align="right">
                      {renderValueChange(item.change, item.changePercent)}
                    </TableCell>
                    <TableCell align="right">
                      {renderMLPrediction(item.mlPrediction)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Portfolio; 