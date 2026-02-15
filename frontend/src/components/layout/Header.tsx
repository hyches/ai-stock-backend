import React from 'react';
import { Bell, User, Clock, Moon, Sun } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from '@/context/ThemeContext';
import SearchBar from '@/components/SearchBar';

export const Header: React.FC = () => {
  const [currentTime, setCurrentTime] = React.useState(new Date());
  const { theme, toggleTheme } = useTheme();

  React.useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const marketStatus = React.useMemo(() => {
    const hour = currentTime.getHours();
    const minute = currentTime.getMinutes();
    const totalMinutes = hour * 60 + minute;

    // NSE timing: 9:15 AM - 3:30 PM IST
    const marketOpen = 9 * 60 + 15; // 9:15
    const marketClose = 15 * 60 + 30; // 15:30

    if (totalMinutes >= marketOpen && totalMinutes <= marketClose) {
      return { status: 'open', label: 'Market Open', color: 'text-emerald-400' };
    } else if (totalMinutes < marketOpen) {
      return { status: 'pre', label: 'Pre-Market', color: 'text-warning' };
    } else {
      return { status: 'closed', label: 'Market Closed', color: 'text-rose-400' };
    }
  }, [currentTime]);

  return (
    <header className="h-16 glass border-b border-border/50 flex items-center justify-between px-6">
      {/* Search */}
      <div className="flex-1 max-w-md">
        <SearchBar
          placeholder="Search for stocks (e.g., RELIANCE, TCS, HDFC)..."
          className="w-full"
        />
      </div>

      {/* Center - Time & Market Status */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-sm">
          <Clock size={16} className="text-muted-foreground" />
          <span className="font-mono">{currentTime.toLocaleTimeString('en-IN')}</span>
        </div>
        <div className={cn(
          'flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium',
          marketStatus.status === 'open' && 'bg-emerald-500/10',
          marketStatus.status === 'pre' && 'bg-warning/10',
          marketStatus.status === 'closed' && 'bg-rose-500/10'
        )}>
          <span className={cn(
            'w-2 h-2 rounded-full',
            marketStatus.status === 'open' && 'bg-emerald-500 pulse-live',
            marketStatus.status === 'pre' && 'bg-warning animate-pulse',
            marketStatus.status === 'closed' && 'bg-rose-500'
          )} />
          <span className={marketStatus.color}>{marketStatus.label}</span>
        </div>
      </div>

      {/* Right - Actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-xl hover:bg-accent/50 transition-colors text-muted-foreground hover:text-foreground"
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        <button className="relative p-2 rounded-xl hover:bg-accent/50 transition-colors text-muted-foreground hover:text-foreground">
          <Bell size={20} />
          <span className="absolute top-1 right-1 w-2 h-2 bg-primary rounded-full" />
        </button>

        <div className="w-px h-8 bg-border" />

        <button className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-xl hover:bg-accent/50 transition-colors">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-primary/50 flex items-center justify-center">
            <User size={16} className="text-primary-foreground" />
          </div>
          <span className="text-sm font-medium">Paper Account</span>
        </button>
      </div>
    </header>
  );
};
