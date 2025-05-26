import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import Portfolio from './Portfolio';
import Watchlist from './Watchlist';
import Settings from './Settings';
import Dashboard from './Dashboard';
import MarketOverview from './MarketOverview';
import NotificationsPanel from './NotificationsPanel';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import { useAuth } from '../hooks/useAuth';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#90caf9' },
    secondary: { main: '#f48fb1' },
    background: { default: '#121212', paper: '#1e1e1e' },
  },
  typography: { fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif' },
});

/**
 * Main application component that wraps routing and theme configuration.
 * @example
 * App()
 * JSX.Element containing the application's layout and routing logic
 * @param {void} - This component does not take any props.
 * @returns {JSX.Element} The function returns the main application layout including navigation and routing.
 * @description
 *   - Utilizes Material-UI's ThemeProvider and CssBaseline for styling consistency.
 *   - Sidebar visibility is controlled via component state and can be toggled.
 *   - Protected routes redirect to the login page if the user is not authenticated.
 *   - Supports routing to multiple pages including Dashboard, Portfolio, Watchlist, Settings, and more.
 */
const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);
  const { isAuthenticated } = useAuth();

  const toggleSidebar = () => setSidebarOpen((open) => !open);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          <Navbar onMenuClick={toggleSidebar} />
          <Sidebar open={sidebarOpen} onClose={toggleSidebar} />
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              mt: 8,
              ml: sidebarOpen ? '240px' : 0,
              transition: 'margin 0.2s',
            }}
          >
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/portfolio" element={isAuthenticated ? <Portfolio /> : <Navigate to="/login" />} />
              <Route path="/watchlist" element={isAuthenticated ? <Watchlist /> : <Navigate to="/login" />} />
              <Route path="/settings" element={isAuthenticated ? <Settings /> : <Navigate to="/login" />} />
              <Route path="/market" element={<MarketOverview />} />
              <Route path="/notifications" element={<NotificationsPanel />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App; 