import React from 'react';
import { cn } from '@/lib/utils';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  LineChart,
  Layers,
  History,
  Brain,
  Settings,
  TrendingUp,
  FlaskConical,
  BarChart3,
  Search,
  BookOpen,
  Activity,
  Globe
} from 'lucide-react';

interface NavItem {
  icon: React.ElementType;
  label: string;
  id: string;
  category?: string;
}

const navItems: NavItem[] = [
  { icon: LayoutDashboard, label: 'Dashboard', id: 'dashboard', category: 'main' },
  { icon: LineChart, label: 'Charts', id: 'charts', category: 'main' },
  { icon: Search, label: 'Scanner', id: 'scanner', category: 'main' },
  { icon: Globe, label: 'Research', id: 'research', category: 'main' },
  { icon: Layers, label: 'Options', id: 'options', category: 'trading' },
  { icon: Activity, label: 'Greeks', id: 'greeks', category: 'trading' },
  { icon: TrendingUp, label: 'Positions', id: 'positions', category: 'trading' },
  { icon: History, label: 'History', id: 'history', category: 'trading' },
  { icon: BookOpen, label: 'Journal', id: 'journal', category: 'trading' },
  { icon: BarChart3, label: 'Analytics', id: 'analytics', category: 'tools' },
  { icon: FlaskConical, label: 'Backtest', id: 'backtest', category: 'tools' },
  { icon: Brain, label: 'ML Signals', id: 'ml', category: 'tools' },
];

interface SidebarProps {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange
}) => {
  const navigate = useNavigate();
  const location = useLocation();

  // Get active tab from props OR from URL search params
  const searchParams = new URLSearchParams(location.search);
  const urlTab = searchParams.get('tab');
  const currentActiveTab = activeTab || urlTab || 'dashboard';

  const mainItems = navItems.filter(i => i.category === 'main');
  const tradingItems = navItems.filter(i => i.category === 'trading');
  const toolsItems = navItems.filter(i => i.category === 'tools');

  const handleClick = (id: string) => {
    if (onTabChange) {
      onTabChange(id);
    } else {
      // Automatic navigation for AppLayout usage
      navigate(`/trading?tab=${id}`);
    }
  };

  const renderNavItem = (item: NavItem) => (
    <button
      key={item.id}
      onClick={() => handleClick(item.id)}
      className={cn(
        'w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-200 group relative',
        currentActiveTab === item.id
          ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/30'
          : 'text-muted-foreground hover:text-foreground hover:bg-accent'
      )}
    >
      <item.icon size={20} />

      <span className="absolute left-full ml-3 px-3 py-1.5 rounded-lg bg-popover text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 border border-border shadow-lg">
        {item.label}
      </span>
    </button>
  );

  return (
    <aside className="fixed left-0 top-0 h-screen w-20 bg-card border-r border-border flex flex-col items-center py-4 z-50">
      <div className="mb-6 cursor-pointer" onClick={() => navigate('/trading')}>
        <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center shadow-lg shadow-primary/20">
          <TrendingUp className="text-primary-foreground" size={22} />
        </div>
      </div>

      <nav className="flex-1 flex flex-col items-center gap-1 w-full px-3 overflow-y-auto scrollbar-hide">
        <div className="flex flex-col items-center gap-1 w-full">
          {mainItems.map(renderNavItem)}
        </div>

        <div className="w-8 h-px bg-border my-2" />

        <div className="flex flex-col items-center gap-1 w-full">
          {tradingItems.map(renderNavItem)}
        </div>

        <div className="w-8 h-px bg-border my-2" />

        <div className="flex flex-col items-center gap-1 w-full">
          {toolsItems.map(renderNavItem)}
        </div>
      </nav>

      <button
        onClick={() => navigate('/settings')}
        className="w-12 h-12 rounded-xl flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-accent transition-all group relative"
      >
        <Settings size={20} />
        <span className="absolute left-full ml-3 px-3 py-1.5 rounded-lg bg-popover text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50 border border-border shadow-lg">
          Settings
        </span>
      </button>
    </aside>
  );
};

export default Sidebar;

