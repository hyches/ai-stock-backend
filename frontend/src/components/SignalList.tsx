import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';
import { useApi } from '../hooks/useApi';

interface Signal {
  id: number;
  strategy_id: number;
  strategy_name: string;
  symbol: string;
  signal_type: 'buy' | 'sell' | 'neutral';
  confidence: number;
  created_at: string;
  metrics: Record<string, any>;
}

const SignalList: React.FC = () => {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const api = useApi();

  useEffect(() => {
    fetchSignals();
  }, []);

  const fetchSignals = async () => {
    try {
      setLoading(true);
      const response = await api.get('/signals/');
      setSignals(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load signals');
      setLoading(false);
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getSignalColor = (type: string) => {
    switch (type) {
      case 'buy':
        return 'success';
      case 'sell':
        return 'error';
      case 'neutral':
        return 'default';
      default:
        return 'default';
    }
  };

  if (loading) {
    return <Typography>Loading signals...</Typography>;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Trading Signals
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Time</TableCell>
              <TableCell>Strategy</TableCell>
              <TableCell>Symbol</TableCell>
              <TableCell>Signal</TableCell>
              <TableCell align="right">Confidence</TableCell>
              <TableCell>Metrics</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {signals
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((signal) => (
                <TableRow key={signal.id}>
                  <TableCell>
                    {new Date(signal.created_at).toLocaleString()}
                  </TableCell>
                  <TableCell>{signal.strategy_name}</TableCell>
                  <TableCell>{signal.symbol}</TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center">
                      {signal.signal_type === 'buy' ? (
                        <TrendingUpIcon color="success" fontSize="small" />
                      ) : signal.signal_type === 'sell' ? (
                        <TrendingDownIcon color="error" fontSize="small" />
                      ) : null}
                      <Chip
                        label={signal.signal_type.toUpperCase()}
                        color={getSignalColor(signal.signal_type)}
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    </Box>
                  </TableCell>
                  <TableCell align="right">
                    {(signal.confidence * 100).toFixed(1)}%
                  </TableCell>
                  <TableCell>
                    <Tooltip title={JSON.stringify(signal.metrics, null, 2)}>
                      <Typography variant="body2" noWrap>
                        {Object.keys(signal.metrics).join(', ')}
                      </Typography>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={signals.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
    </Box>
  );
};

export default SignalList; 