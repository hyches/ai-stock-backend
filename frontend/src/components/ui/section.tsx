
import React from 'react';
import { cn } from "@/lib/utils";
import { Button } from '@/components/ui/button';

interface SectionProps {
  className?: string;
  title?: React.ReactNode;
  description?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
  columns?: 1 | 2 | 3 | 4;
  gap?: 'xs' | 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  collapsible?: boolean;
}

const Section = ({ 
  className, 
  title, 
  description, 
  children,
  action,
  columns = 3,
  gap = 'md',
  isLoading = false,
  collapsible = false
}: SectionProps) => {
  const [collapsed, setCollapsed] = React.useState(false);

  const gapClasses = {
    xs: 'gap-2',
    sm: 'gap-3',
    md: 'gap-4',
    lg: 'gap-6'
  };

  const columnClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'
  };

  return (
    <div className={cn("mb-8", className)}>
      {(title || description || action) && (
        <div className="flex items-center justify-between mb-4">
          <div>
            {title && (
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-semibold text-foreground">
                  {title}
                </h2>
                {isLoading && (
                  <div className="h-4 w-4 rounded-full border-2 border-teal border-r-transparent animate-spin" />
                )}
                {collapsible && (
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setCollapsed(!collapsed)}
                    className="ml-2 p-0 h-7 w-7"
                  >
                    {collapsed ? '+' : '-'}
                  </Button>
                )}
              </div>
            )}
            {description && <p className="text-sm text-muted-foreground mt-1">{description}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {!collapsed && (
        <div className={cn(`grid ${columnClasses[columns]} ${gapClasses[gap]}`)}>
          {children}
        </div>
      )}
    </div>
  );
};

export default Section;
