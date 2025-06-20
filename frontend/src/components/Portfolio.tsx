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

const Portfolio: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [portfolio, setPortfolio] = useState<PortfolioItem[]>([]);
  const [totalValue, setTotalValue] = useState(0);
  const [totalChange, setTotalChange] = useState(0);

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
                    <TableCell>{item.symbol}</TableCell>
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