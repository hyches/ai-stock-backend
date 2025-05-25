import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  LinearProgress,
} from '@mui/material';

interface PortfolioData {
  total_value: number;
  cash_balance: number;
  invested_amount: number;
  daily_pnl: number;
  daily_pnl_percentage: number;
  total_pnl: number;
  total_pnl_percentage: number;
  positions: Array<{
    symbol: string;
    quantity: number;
    average_price: number;
    current_price: number;
    market_value: number;
    pnl: number;
    pnl_percentage: number;
  }>;
}

interface PortfolioOverviewProps {
  data: PortfolioData;
}

const PortfolioOverview: React.FC<PortfolioOverviewProps> = ({ data }) => {
  if (!data) {
    return <Typography>No portfolio data available</Typography>;
  }

  const {
    total_value,
    cash_balance,
    invested_amount,
    daily_pnl,
    daily_pnl_percentage,
    total_pnl,
    total_pnl_percentage,
    positions,
  } = data;

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Summary Cards */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle2" color="textSecondary">
              Total Portfolio Value
            </Typography>
            <Typography variant="h5" gutterBottom>
              ${total_value.toLocaleString()}
            </Typography>
            <Box display="flex" alignItems="center">
              <Typography
                variant="body2"
                color={daily_pnl >= 0 ? 'success.main' : 'error.main'}
              >
                {daily_pnl >= 0 ? '+' : ''}
                {daily_pnl_percentage.toFixed(2)}% Today
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle2" color="textSecondary">
              Cash Balance
            </Typography>
            <Typography variant="h5" gutterBottom>
              ${cash_balance.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {((cash_balance / total_value) * 100).toFixed(1)}% of portfolio
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle2" color="textSecondary">
              Invested Amount
            </Typography>
            <Typography variant="h5" gutterBottom>
              ${invested_amount.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {((invested_amount / total_value) * 100).toFixed(1)}% of portfolio
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle2" color="textSecondary">
              Total P&L
            </Typography>
            <Typography
              variant="h5"
              color={total_pnl >= 0 ? 'success.main' : 'error.main'}
              gutterBottom
            >
              ${total_pnl.toLocaleString()}
            </Typography>
            <Typography
              variant="body2"
              color={total_pnl >= 0 ? 'success.main' : 'error.main'}
            >
              {total_pnl >= 0 ? '+' : ''}
              {total_pnl_percentage.toFixed(2)}%
            </Typography>
          </Paper>
        </Grid>

        {/* Positions Table */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Current Positions
            </Typography>
            <Box sx={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ textAlign: 'left', padding: '8px' }}>Symbol</th>
                    <th style={{ textAlign: 'right', padding: '8px' }}>Quantity</th>
                    <th style={{ textAlign: 'right', padding: '8px' }}>Avg Price</th>
                    <th style={{ textAlign: 'right', padding: '8px' }}>Current Price</th>
                    <th style={{ textAlign: 'right', padding: '8px' }}>Market Value</th>
                    <th style={{ textAlign: 'right', padding: '8px' }}>P&L</th>
                    <th style={{ textAlign: 'right', padding: '8px' }}>P&L %</th>
                  </tr>
                </thead>
                <tbody>
                  {positions.map((position) => (
                    <tr key={position.symbol}>
                      <td style={{ padding: '8px' }}>{position.symbol}</td>
                      <td style={{ textAlign: 'right', padding: '8px' }}>
                        {position.quantity}
                      </td>
                      <td style={{ textAlign: 'right', padding: '8px' }}>
                        ${position.average_price.toFixed(2)}
                      </td>
                      <td style={{ textAlign: 'right', padding: '8px' }}>
                        ${position.current_price.toFixed(2)}
                      </td>
                      <td style={{ textAlign: 'right', padding: '8px' }}>
                        ${position.market_value.toLocaleString()}
                      </td>
                      <td
                        style={{
                          textAlign: 'right',
                          padding: '8px',
                          color: position.pnl >= 0 ? '#4caf50' : '#f44336',
                        }}
                      >
                        ${position.pnl.toLocaleString()}
                      </td>
                      <td
                        style={{
                          textAlign: 'right',
                          padding: '8px',
                          color: position.pnl >= 0 ? '#4caf50' : '#f44336',
                        }}
                      >
                        {position.pnl >= 0 ? '+' : ''}
                        {position.pnl_percentage.toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PortfolioOverview; 