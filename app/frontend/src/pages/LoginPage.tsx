import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const LoginPage: React.FC = () => {
  return (
    <Box sx={{ mt: 8, display: 'flex', justifyContent: 'center' }}>
      <Card sx={{ minWidth: 320 }}>
        <CardContent>
          <Typography variant="h5">Login</Typography>
          <Typography variant="body2">(Coming soon: login form)</Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default LoginPage; 