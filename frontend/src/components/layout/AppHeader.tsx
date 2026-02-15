import React, { useState } from 'react';
import { Bell, Sun, Moon, LogOut, User, Settings, CreditCard } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/context/AuthContext';
import { useNavigate } from 'react-router-dom';
import SearchBar from '@/components/SearchBar';
import { useTheme } from '@/context/ThemeContext';
import ThemeToggle from '@/components/ThemeToggle';

interface StockDetails {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  pe: number;
  eps: number;
  dividend: number;
  dividendYield: number;
  high52Week: number;
  low52Week: number;
  avgVolume: number;
  beta: number;
  sector: string;
  industry: string;
  description: string;
  website: string;
  employees: number;
  founded: number;
  headquarters: string;
}

const AppHeader = () => {
  const [notificationCount, setNotificationCount] = useState(3);
  const { toast } = useToast();
  const { logout } = useAuth();
  const navigate = useNavigate();
  // const { setTheme } = useTheme(); // Removed as it is not exposed/needed anymore

  // Handle stock selection from SearchBar
  const handleStockSelect = (stock: StockDetails | null) => {
    // Dispatch custom event to communicate with page components
    const event = new CustomEvent('stockSelected', { detail: stock });
    window.dispatchEvent(event);
  };

  const handleNotificationClick = () => {
    if (notificationCount > 0) {
      setNotificationCount(0);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
    toast({
      title: "Logged out successfully",
      description: "You have been logged out of your account.",
      duration: 2000,
    });
  };

  return (
    <header className="flex items-center justify-between p-4 border-b border-border bg-card sticky top-0 z-30">
      <div className="flex gap-2 items-center flex-1">
        <div className="hidden md:block w-full max-w-xl">
          <SearchBar
            placeholder="Search for stocks (e.g., RELIANCE, TCS, HDFC)..."
            showInlineDetails={true}
            className="w-full"
            pageContext="header"
            onStockSelect={handleStockSelect}
          />
        </div>
      </div>

      <div className="flex gap-2 items-center ml-4">
        <ThemeToggle />

        {/* Notifications */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="relative text-foreground/70 hover:text-foreground"
              onClick={handleNotificationClick}
            >
              <Bell className="h-5 w-5" />
              {notificationCount > 0 && (
                <Badge variant="destructive" className="absolute -top-1 -right-1 h-4 w-4 flex items-center justify-center p-0 text-[10px]">
                  {notificationCount}
                </Badge>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80">
            <DropdownMenuLabel>Notifications</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <div className="p-8 text-sm text-center text-muted-foreground">
              No new notifications
            </div>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* User Profile */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="flex items-center gap-2 hover:bg-muted ml-1 px-2"
            >
              <Avatar className="h-8 w-8 border border-border">
                <AvatarImage src="https://github.com/shadcn.png" alt="User" />
                <AvatarFallback className="bg-primary/20 text-primary">U</AvatarFallback>
              </Avatar>
              <div className="hidden md:flex flex-col items-start text-xs">
                <span className="font-medium">John Doe</span>
                <span className="text-muted-foreground">Pro Plan</span>
              </div>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <User className="mr-2 h-4 w-4" />
              <span>Profile</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <CreditCard className="mr-2 h-4 w-4" />
              <span>Billing</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Settings className="mr-2 h-4 w-4" />
              <span>Settings</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout} className="text-red-500 focus:text-red-500">
              <LogOut className="mr-2 h-4 w-4" />
              <span>Logout</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};

export default AppHeader;
