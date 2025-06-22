
import React, { useState, useEffect } from 'react';
import AppHeader from './AppHeader';
import Sidebar from './Sidebar';
import { useToast } from '@/hooks/use-toast';

interface AppLayoutProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
}

const AppLayout = ({ children, title, description }: AppLayoutProps) => {
  const [isMobileView, setIsMobileView] = useState(false);
  const { toast } = useToast();
  
  useEffect(() => {
    const handleResize = () => {
      setIsMobileView(window.innerWidth < 768);
    };
    
    handleResize(); // Check on initial load
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  useEffect(() => {
    // Example toast that could be shown when route changes
    if (title && !isMobileView) {
      toast({
        title: `Viewing ${title}`,
        description: description,
        duration: 2000,
      });
    }
  }, [title, isMobileView, toast, description]);

  return (
    <div className="flex h-screen overflow-hidden bg-navy-900">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <AppHeader />
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          {title && (
            <div className="mb-6">
              <h1 className="text-2xl md:text-3xl font-bold text-foreground">{title}</h1>
              {description && (
                <p className="text-muted-foreground mt-1">{description}</p>
              )}
              <div className="mt-1 h-1 w-16 bg-teal rounded-full"></div>
            </div>
          )}
          {children}
        </main>
      </div>
    </div>
  );
};

export default AppLayout;
