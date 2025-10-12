
import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Filter, 
  BookOpen, 
  PieChart, 
  TrendingUp, 
  FileSearch, 
  FileText, 
  Settings,
  ChevronLeft, 
  ChevronRight,
  DollarSign,
  Download,
  Search,
  History
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';

interface NavItemProps {
  icon: React.ElementType;
  label: string;
  path: string;
  active?: boolean;
  collapsed?: boolean;
}

const NavItem = ({ 
  icon: Icon, 
  label, 
  path,
  active = false, 
  collapsed = false
}: NavItemProps) => {
  return (
    <Button
      variant="ghost"
      asChild
      className={cn(
        "flex items-center w-full justify-start gap-3 px-3 py-2 my-1 rounded-md transition-all duration-200",
        active 
          ? "bg-sidebar-primary/20 text-sidebar-primary hover:bg-sidebar-primary/30" 
          : "hover:bg-sidebar-accent text-sidebar-foreground hover:text-sidebar-foreground",
        "group"
      )}
    >
      <Link to={path} className="flex items-center w-full">
        <Icon className={cn("h-5 w-5 shrink-0", active ? "text-sidebar-primary" : "text-sidebar-foreground group-hover:text-sidebar-foreground")} />
        {!collapsed && <span className="ml-3 transition-opacity duration-200">{label}</span>}
      </Link>
    </Button>
  );
};

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", path: "/dashboard" },
  { icon: Search, label: "Stock Search", path: "/search" },
  { icon: Filter, label: "Stock Screener", path: "/screener" },
  { icon: BookOpen, label: "AI Research Reports", path: "/research" },
  { icon: PieChart, label: "Portfolio Optimizer", path: "/optimizer" },
  { icon: TrendingUp, label: "F&O Trading Terminal", path: "/trading" },
  { icon: History, label: "Transactions", path: "/transactions" },
  { icon: FileSearch, label: "Policy Opportunity", path: "/policy" },
  { icon: FileText, label: "Reports & Downloads", path: "/reports" },
  { icon: Settings, label: "Settings", path: "/settings" },
];

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const location = useLocation();
  const { toast } = useToast();
  
  // Handle responsive sidebar
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) {
        setCollapsed(true);
      }
    };

    handleResize(); // Check on initial render
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);
  
  const toggleSidebar = () => {
    setCollapsed(!collapsed);
    
    if (isMobile) {
      toast({
        title: collapsed ? "Navigation expanded" : "Navigation collapsed",
        duration: 1500,
      });
    }
  };

  return (
            <aside className={cn(
              "h-screen flex flex-col bg-sidebar-background border-r border-sidebar-border transition-all duration-300 relative",
              collapsed ? "w-16" : "w-64"
            )}>
      <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
        {!collapsed && (
          <div className="font-bold text-xl flex items-center">
            <DollarSign className="h-6 w-6 text-sidebar-primary mr-2" />
            <span className="text-sidebar-foreground">StockAI</span>
          </div>
        )}
        <Button 
          variant="ghost" 
          size="icon" 
          onClick={toggleSidebar} 
          className={cn(
            "text-sidebar-foreground hover:text-sidebar-foreground hover:bg-sidebar-accent transition-all duration-200",
            collapsed ? "mx-auto" : ""
          )}
        >
          {collapsed ? 
            <ChevronRight className="h-5 w-5" /> : 
            <ChevronLeft className="h-5 w-5" />
          }
        </Button>
      </div>
      
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto scrollbar-hidden">
        {navItems.map((item) => (
          <NavItem
            key={item.label}
            icon={item.icon}
            label={item.label}
            path={item.path}
            active={location.pathname === item.path}
            collapsed={collapsed}
          />
        ))}
      </nav>
      
      <div className="p-4 border-t border-sidebar-border">
        <div className={cn(
          "flex items-center",
          collapsed ? "justify-center" : "gap-3"
        )}>
          <div className="h-8 w-8 rounded-full bg-sidebar-primary/20 flex items-center justify-center text-sidebar-primary">
            U
          </div>
          {!collapsed && <div className="text-sm font-medium text-sidebar-foreground">User</div>}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
