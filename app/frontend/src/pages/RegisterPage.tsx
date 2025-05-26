import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

/**
* Renders a registration card with a title and a placeholder text.
* @example
* renderRegistrationCard()
* Returns a React element containing a registration card.
* @returns {JSX.Element} Returns a JSX element displaying the registration title and placeholder text.
* @description
*   - Uses Material-UI components for layout and styling, such as Box, Card, CardContent, and Typography.
*   - The Box component is styled to have a top margin of 8 units and center content alignment.
*   - The Card component has a minimum width set, defining its size.
*   - Currently, it's a static placeholder with a note indicating future development.
*/
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