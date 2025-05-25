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

interface Trade {
  id: number;
  symbol: string;
  side: 'buy' | 'sell';
  quantity: number;
  price: number;
  timestamp: string;
  strategy_id: number;
  strategy_name: string;
  status: 'executed' | 'pending' | 'cancelled' | 'failed';
  pnl?: number;
  pnl_percentage?: number;
}

const TradeHistory: React.FC = () => {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const api = useApi();

  useEffect(() => {
    fetchTrades();
  }, []);

  const fetchTrades = async () => {
    try {
      setLoading(true);
      const response = await api.get('/trades/');
      setTrades(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load trade history');
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'executed':
        return 'success';
      case 'pending':
        return 'warning';
      case 'cancelled':
        return 'error';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return <Typography>Loading trade history...</Typography>;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Trade History
      </Typography>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Time</TableCell>
              <TableCell>Symbol</TableCell>
              <TableCell>Side</TableCell>
              <TableCell align="right">Quantity</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell>Strategy</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">P&L</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {trades
              .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
              .map((trade) => (
                <TableRow key={trade.id}>
                  <TableCell>
                    {new Date(trade.timestamp).toLocaleString()}
                  </TableCell>
                  <TableCell>{trade.symbol}</TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center">
                      {trade.side === 'buy' ? (
                        <TrendingUpIcon color="success" fontSize="small" />
                      ) : (
                        <TrendingDownIcon color="error" fontSize="small" />
                      )}
                      <Typography
                        variant="body2"
                        color={trade.side === 'buy' ? 'success.main' : 'error.main'}
                        ml={1}
                      >
                        {trade.side.toUpperCase()}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell align="right">{trade.quantity}</TableCell>
                  <TableCell align="right">
                    ${trade.price.toFixed(2)}
                  </TableCell>
                  <TableCell>{trade.strategy_name}</TableCell>
                  <TableCell>
                    <Chip
                      label={trade.status}
                      color={getStatusColor(trade.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      color: trade.pnl && trade.pnl >= 0 ? 'success.main' : 'error.main',
                    }}
                  >
                    {trade.pnl ? (
                      <>
                        ${trade.pnl.toLocaleString()}
                        <Typography variant="caption" display="block">
                          {trade.pnl >= 0 ? '+' : ''}
                          {trade.pnl_percentage?.toFixed(2)}%
                        </Typography>
                      </>
                    ) : (
                      '-'
                    )}
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={trades.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
    </Box>
  );
};

export default TradeHistory; 