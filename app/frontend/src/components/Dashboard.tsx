import React from 'react';
import { Box, Typography, Card, CardContent, Grid } from '@mui/material';

const Dashboard: React.FC = () => {
  return (
    <Box>
      <Typography variant="h3" gutterBottom>
        Dashboard
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">ML Predictions</Typography>
              <Typography variant="body2">(Coming soon: summary of ML predictions)</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Quick Stats</Typography>
              <Typography variant="body2">(Coming soon: portfolio/market stats)</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Market Overview</Typography>
              <Typography variant="body2">(See Market Overview page for details)</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard; 