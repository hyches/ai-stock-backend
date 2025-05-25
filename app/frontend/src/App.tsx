import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, Container } from '@mui/material';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import MLDashboard from './components/MLDashboard';
import Portfolio from './components/Portfolio';
import Watchlist from './components/Watchlist';
import Settings from './components/Settings';

// Create a dark theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#1e1e1e',
          borderRadius: 12,
        },
      },
    },
  },
});

const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

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
            <Container maxWidth="xl">
              <Routes>
                <Route path="/" element={<MLDashboard symbol="AAPL" />} />
                <Route path="/portfolio" element={<Portfolio />} />
                <Route path="/watchlist" element={<Watchlist />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/symbol/:symbol" element={<MLDashboard />} />
              </Routes>
            </Container>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App; 