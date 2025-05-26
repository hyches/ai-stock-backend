import React from 'react';
import { Box, Typography, Card, CardContent } from '@mui/material';

/**
 * Renders a notifications panel with a title and placeholder text.
 * @example
 * renderNotificationsPanel()
 * <Box>...</Box>
 * @returns {JSX.Element} A React component for displaying the notifications panel.
 * @description
 *   - Utilizes Material UI components such as Box, Card, CardContent, and Typography for styling.
 *   - Displays a title "Notifications" in a Typography element with variant "h5".
 *   - Includes a placeholder "(Coming soon: notifications list)" in a Typography element with variant "body2".
 */
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