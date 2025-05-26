import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

/**
* Renders a login page component.
* @example
* loginPageComponent()
* <Box>...</Box>
* @returns {JSX.Element} A JSX element containing the login page structure.
* @description
*   - Utilizes Material-UI components to structure the page.
*   - Currently displays placeholder text indicating login form will be available soon.
*   - Centers the card on the page using flexbox styling.
*/
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