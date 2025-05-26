import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  InputBase,
  Badge,
  Menu,
  MenuItem,
  Box,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  AccountCircle,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { styled, alpha } from '@mui/material/styles';

const Search = styled('div')(({ theme }) => ({
  position: 'relative',
  borderRadius: theme.shape.borderRadius,
  backgroundColor: alpha(theme.palette.common.white, 0.15),
  '&:hover': {
    backgroundColor: alpha(theme.palette.common.white, 0.25),
  },
  marginRight: theme.spacing(2),
  marginLeft: 0,
  width: '100%',
  [theme.breakpoints.up('sm')]: {
    marginLeft: theme.spacing(3),
    width: 'auto',
  },
}));

const SearchIconWrapper = styled('div')(({ theme }) => ({
  padding: theme.spacing(0, 2),
  height: '100%',
  position: 'absolute',
  pointerEvents: 'none',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
}));

const StyledInputBase = styled(InputBase)(({ theme }) => ({
  color: 'inherit',
  '& .MuiInputBase-input': {
    padding: theme.spacing(1, 1, 1, 0),
    paddingLeft: `calc(1em + ${theme.spacing(4)})`,
    transition: theme.transitions.create('width'),
    width: '100%',
    [theme.breakpoints.up('md')]: {
      width: '20ch',
    },
  },
}));

interface NavbarProps {
  onMenuClick: () => void;
}

/**
* Functional component for rendering the navigation bar with search and menu functionality.
* @example
* Navbar({ onMenuClick: handleMenuToggle })
* Renders a top app bar with search, menu, and user profile interactions.
* @param {function} onMenuClick - Function to be executed when the menu icon is clicked.
* @returns {JSX.Element} The rendered navigation component.
* @description
*   - Utilizes `useTheme` to access current theme settings for styling purposes.
*   - Employs `useNavigate` from React Router for navigation handling upon search submission.
*   - Manages local state for search input and menu visibility using React's `useState`.
*   - Integrates Material-UI components for consistent styling and layout.
*/
const Navbar: React.FC<NavbarProps> = ({ onMenuClick }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/symbol/${searchQuery.toUpperCase()}`);
      setSearchQuery('');
    }
  };

  return (
    <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={onMenuClick}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <Typography
          variant="h6"
          noWrap
          component="div"
        >
          ML Trading Dashboard
        </Typography>

        <Box sx={{ flexGrow: 1 }} />

        <form onSubmit={handleSearch}>
          <Search>
            <SearchIconWrapper>
              <SearchIcon />
            </SearchIconWrapper>
            <StyledInputBase
              placeholder="Search symbol..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              inputProps={{ 'aria-label': 'search' }}
            />
          </Search>
        </form>

        <Box sx={{ display: 'flex' }}>
          <IconButton color="inherit">
            <Badge badgeContent={4} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>

          <IconButton
            edge="end"
            aria-label="account of current user"
            aria-haspopup="true"
            onClick={handleProfileMenuOpen}
            color="inherit"
          >
            <AccountCircle />
          </IconButton>
        </Box>

        <Menu
          anchorEl={anchorEl}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          keepMounted
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={() => { handleMenuClose(); navigate('/profile'); }}>
            Profile
          </MenuItem>
          <MenuItem onClick={() => { handleMenuClose(); navigate('/settings'); }}>
            Settings
          </MenuItem>
          <MenuItem onClick={handleMenuClose}>Logout</MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar; 