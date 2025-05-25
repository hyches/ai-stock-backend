import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const RegisterPage: React.FC = () => {
  return (
    <Box sx={{ mt: 8, display: 'flex', justifyContent: 'center' }}>
      <Card sx={{ minWidth: 320 }}>
        <CardContent>
          <Typography variant="h5">Register</Typography>
          <Typography variant="body2">(Coming soon: registration form)</Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default RegisterPage; 