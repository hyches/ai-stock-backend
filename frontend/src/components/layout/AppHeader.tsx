import React, { useState } from 'react';
import { Bell } from 'lucide-react';
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
import ThemeToggle from '@/components/ThemeToggle';
import SearchBar from '@/components/SearchBar';

const AppHeader = () => {
  const [notificationCount, setNotificationCount] = useState(3);
  const { toast } = useToast();
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleNotificationClick = () => {
    if (notificationCount > 0) {
      // In a real app, this would mark notifications as read
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
    <header className="flex items-center justify-between p-4 border-b border-border bg-card">
      <div className="flex gap-2 items-center">
        <div className="hidden md:block w-96">
          <SearchBar 
            placeholder="Search for stocks (e.g., RELIANCE, TCS, HDFC, AAPL)..."
            showInlineDetails={true}
            className="w-full"
          />
        </div>
      </div>
      <div className="flex gap-4 items-center">
        <ThemeToggle />
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="relative text-muted-foreground hover:text-foreground hover:bg-muted"
              onClick={handleNotificationClick}
            >
              <Bell className="h-5 w-5" />
              {notificationCount > 0 && (
                <Badge variant="destructive" className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-[10px]">
                  {notificationCount}
                </Badge>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80">
            <DropdownMenuLabel>Notifications</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="cursor-pointer">
              <div className="flex flex-col">
                <span className="font-semibold">Portfolio Alert</span>
                <span className="text-xs text-muted-foreground">Apple (AAPL) is up by 5%</span>
              </div>
            </DropdownMenuItem>
            <DropdownMenuItem className="cursor-pointer">
              <div className="flex flex-col">
                <span className="font-semibold">Research Report Ready</span>
                <span className="text-xs text-muted-foreground">Tesla (TSLA) report is available</span>
              </div>
            </DropdownMenuItem>
            <DropdownMenuItem className="cursor-pointer">
              <div className="flex flex-col">
                <span className="font-semibold">Price Alert</span>
                <span className="text-xs text-muted-foreground">Microsoft (MSFT) reached target price</span>
              </div>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              className="flex items-center gap-2 hover:bg-muted"
            >
              <Avatar className="h-8 w-8">
                <AvatarImage src="https://github.com/shadcn.png" alt="User" />
                <AvatarFallback className="bg-primary/20 text-primary">U</AvatarFallback>
              </Avatar>
              <span className="hidden md:inline">John Doe</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuItem>Subscription</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleLogout}>Logout</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
};

export default AppHeader;
