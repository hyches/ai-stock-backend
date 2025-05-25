import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
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
import { useApi } from '../hooks/useApi';

interface BacktestResult {
  id: number;
  strategy_id: number;
  strategy_name: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  total_return: number;
  annualized_return: number;
  sharpe_ratio: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: number;
  equity_curve: Array<{
    date: string;
    equity: number;
  }>;
  trades: Array<{
    date: string;
    symbol: string;
    side: string;
    quantity: number;
    price: number;
    pnl: number;
  }>;
}

const BacktestResults: React.FC = () => {
  const [results, setResults] = useState<BacktestResult[]>([]);
  const [selectedResult, setSelectedResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const api = useApi();

  const [formData, setFormData] = useState({
    strategy_id: '',
    start_date: '',
    end_date: '',
    initial_capital: 100000,
  });

  useEffect(() => {
    fetchResults();
  }, []);

  const fetchResults = async () => {
    try {
      setLoading(true);
      const response = await api.get('/strategies/1/backtest-results');
      setResults(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load backtest results');
      setLoading(false);
    }
  };

  const handleOpenDialog = () => {
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async () => {
    try {
      const response = await api.post('/strategies/1/backtest', formData);
      setResults((prev) => [response.data, ...prev]);
      handleCloseDialog();
    } catch (err) {
      setError('Failed to run backtest');
    }
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

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h6">Backtest Results</Typography>
        <Button variant="contained" color="primary" onClick={handleOpenDialog}>
          Run New Backtest
        </Button>
      </Box>

      <Grid container spacing={3}>
        {results.map((result) => (
          <Grid item xs={12} key={result.id}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                {result.strategy_name} - {new Date(result.start_date).toLocaleDateString()} to{' '}
                {new Date(result.end_date).toLocaleDateString()}
              </Typography>

              <Grid container spacing={3} mb={3}>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Total Return
                  </Typography>
                  <Typography
                    variant="h6"
                    color={result.total_return >= 0 ? 'success.main' : 'error.main'}
                  >
                    {result.total_return >= 0 ? '+' : ''}
                    {result.total_return.toFixed(2)}%
                  </Typography>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Annualized Return
                  </Typography>
                  <Typography
                    variant="h6"
                    color={result.annualized_return >= 0 ? 'success.main' : 'error.main'}
                  >
                    {result.annualized_return >= 0 ? '+' : ''}
                    {result.annualized_return.toFixed(2)}%
                  </Typography>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Sharpe Ratio
                  </Typography>
                  <Typography variant="h6">{result.sharpe_ratio.toFixed(2)}</Typography>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="subtitle2" color="textSecondary">
                    Max Drawdown
                  </Typography>
                  <Typography variant="h6" color="error.main">
                    {result.max_drawdown.toFixed(2)}%
                  </Typography>
                </Grid>
              </Grid>

              <Box height={400}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={result.equity_curve}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="equity"
                      stroke="#8884d8"
                      name="Portfolio Value"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Run New Backtest</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={2}>
            <FormControl fullWidth>
              <InputLabel>Strategy</InputLabel>
              <Select
                name="strategy_id"
                value={formData.strategy_id}
                onChange={handleInputChange}
                label="Strategy"
              >
                <MenuItem value="1">Trend Following Strategy</MenuItem>
                <MenuItem value="2">Mean Reversion Strategy</MenuItem>
                <MenuItem value="3">Breakout Strategy</MenuItem>
              </Select>
            </FormControl>

            <TextField
              name="start_date"
              label="Start Date"
              type="date"
              value={formData.start_date}
              onChange={handleInputChange}
              InputLabelProps={{ shrink: true }}
              fullWidth
            />

            <TextField
              name="end_date"
              label="End Date"
              type="date"
              value={formData.end_date}
              onChange={handleInputChange}
              InputLabelProps={{ shrink: true }}
              fullWidth
            />

            <TextField
              name="initial_capital"
              label="Initial Capital"
              type="number"
              value={formData.initial_capital}
              onChange={handleInputChange}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            Run Backtest
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BacktestResults; 