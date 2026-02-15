
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Button } from '@/components/ui/button';
import { Loader } from 'lucide-react';

interface CustomCardProps {
  className?: string;
  title?: React.ReactNode;
  description?: React.ReactNode;
  children: React.ReactNode;
  headerAction?: React.ReactNode;
  footer?: React.ReactNode;
  isLoading?: boolean;
  isActive?: boolean;
  onClick?: () => void;
  variant?: 'default' | 'outline' | 'glass';
}

const CustomCard = ({ 
  className, 
  title, 
  description, 
  children,
  headerAction,
  footer,
  isLoading = false,
  isActive = false,
  onClick,
  variant = 'default'
}: CustomCardProps) => {
  const variantClasses = {
    default: "bg-card/90 backdrop-blur-sm border border-white/10",
    outline: "bg-transparent border border-white/20",
    glass: "bg-white/5 backdrop-blur-xl border border-white/10"
  };

  const cardContent = (
    <>
      {(title || description) && (
        <CardHeader className={cn(
          "flex flex-row items-center justify-between",
          !headerAction && "pb-2"
        )}>
          <div>
            {title && (
              <CardTitle className="flex items-center gap-2">
                {title}
                {isLoading && <Loader className="h-4 w-4 animate-spin text-muted-foreground" />}
              </CardTitle>
            )}
            {description && <CardDescription>{description}</CardDescription>}
          </div>
          {headerAction && (
            <div className="flex items-center">
              {headerAction}
            </div>
          )}
        </CardHeader>
      )}
      <CardContent>
        {children}
      </CardContent>
      {footer && (
        <CardFooter className="border-t border-white/10 pt-4">
          {footer}
        </CardFooter>
      )}
    </>
  );

  return onClick ? (
    <Card 
      className={cn(
        "overflow-hidden animate-fade-in shadow-md transition-all duration-200", 
        variantClasses[variant],
        isActive && "ring-1 ring-teal",
        "hover:shadow-lg cursor-pointer",
        className
      )}
      onClick={onClick}
    >
      {cardContent}
    </Card>
  ) : (
    <Card 
      className={cn(
        "overflow-hidden animate-fade-in shadow-md", 
        variantClasses[variant],
        isActive && "ring-1 ring-teal",
        className
      )}
    >
      {cardContent}
    </Card>
  );
};

export default CustomCard;
