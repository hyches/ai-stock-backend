import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Box,
  useTheme,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  ShowChart as ChartIcon,
  Star as StarIcon,
  Settings as SettingsIcon,
  AccountBalance as PortfolioIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const drawerWidth = 240;

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Portfolio', icon: <PortfolioIcon />, path: '/portfolio' },
  { text: 'Watchlist', icon: <StarIcon />, path: '/watchlist' },
  { text: 'Analysis', icon: <ChartIcon />, path: '/analysis' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

/**
* Renders a sidebar drawer component with navigation functionalities.
* @example
* Sidebar({ open: true, onClose: () => {} })
* Returns a Drawer component that allows navigation and closes on small screens.
* @param {boolean} open - Boolean flag to control the drawer's open state.
* @param {function} onClose - Callback function executed to close the drawer.
* @returns {JSX.Element} A styled sidebar drawer component.
* @description
*   - Utilizes Material UI's Drawer component for styling and layout.
*   - Ensures navigation buttons are styled based on their selected state.
*   - Implements responsive design by closing the drawer on small screen sizes.
*   - Integrates React Router hooks to manage navigation within the application.
*/
const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (path: string) => {
    navigate(path);
    if (window.innerWidth < theme.breakpoints.values.md) {
      onClose();
    }
  };

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: theme.palette.background.paper,
          borderRight: `1px solid ${theme.palette.divider}`,
        },
      }}
    >
      <Box sx={{ overflow: 'auto', mt: 8 }}>
        <List>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => handleNavigation(item.path)}
                sx={{
                  '&.Mui-selected': {
                    backgroundColor: theme.palette.action.selected,
                    '&:hover': {
                      backgroundColor: theme.palette.action.selected,
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: location.pathname === item.path
                      ? theme.palette.primary.main
                      : theme.palette.text.primary,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  sx={{
                    color: location.pathname === item.path
                      ? theme.palette.primary.main
                      : theme.palette.text.primary,
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        <Divider />
        <List>
          <ListItem>
            <ListItemText
              primary="Recent Symbols"
              primaryTypographyProps={{
                variant: 'subtitle2',
                color: 'text.secondary',
              }}
            />
          </ListItem>
          {/* Add recent symbols here */}
        </List>
      </Box>
    </Drawer>
  );
};

export default Sidebar; 