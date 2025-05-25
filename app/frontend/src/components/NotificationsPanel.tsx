import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

const NotificationsPanel: React.FC = () => {
  return (
    <Box sx={{ mt: 4 }}>
      <Card>
        <CardContent>
          <Typography variant="h5">Notifications</Typography>
          <Typography variant="body2">(Coming soon: notifications list)</Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default NotificationsPanel; 