import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import { Box, Paper, Typography, useTheme } from '@mui/material';
import { EquityCurvePoint } from '../../types';
import { sharedStyles } from '../../styles/shared';

interface EquityCurveChartProps {
  data: EquityCurvePoint[];
  title?: string;
  height?: number;
}

const EquityCurveChart: React.FC<EquityCurveChartProps> = ({
  data,
  title = 'Equity Curve',
  height = 400,
}) => {
  const theme = useTheme();

  const formatYAxis = (value: number) => {
    return `$${value.toLocaleString()}`;
  };

  const formatTooltip = (value: number, name: string) => {
    if (name === 'equity') {
      return [`$${value.toLocaleString()}`, 'Equity'];
    }
    return [`${value.toFixed(2)}%`, 'Drawdown'];
  };

  return (
    <Paper sx={sharedStyles.paper}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ ...sharedStyles.chartContainer, height }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor={theme.palette.primary.main}
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor={theme.palette.primary.main}
                  stopOpacity={0}
                />
              </linearGradient>
              <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor={theme.palette.error.main}
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor={theme.palette.error.main}
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tickFormatter={(value) => new Date(value).toLocaleDateString()}
            />
            <YAxis
              yAxisId="left"
              orientation="left"
              tickFormatter={formatYAxis}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip
              formatter={formatTooltip}
              labelFormatter={(label) => new Date(label).toLocaleDateString()}
            />
            <Legend />
            <Area
              yAxisId="left"
              type="monotone"
              dataKey="equity"
              stroke={theme.palette.primary.main}
              fillOpacity={1}
              fill="url(#equityGradient)"
            />
            <Area
              yAxisId="right"
              type="monotone"
              dataKey="drawdown"
              stroke={theme.palette.error.main}
              fillOpacity={1}
              fill="url(#drawdownGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
};

export default EquityCurveChart; 