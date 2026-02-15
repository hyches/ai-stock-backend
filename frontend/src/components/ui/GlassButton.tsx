import React from 'react';
import { cn } from '@/lib/utils';

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'primary' | 'success' | 'destructive';
  size?: 'sm' | 'md' | 'lg';
  withTilt?: boolean;
}

const variantClasses = {
  default: 'glass-button',
  primary: 'glass-button border-primary/30 hover:border-primary/50 hover:shadow-[0_0_30px_hsl(var(--primary)/0.3)]',
  success: 'glass-button border-success/30 hover:border-success/50 hover:shadow-[0_0_30px_hsl(var(--success)/0.3)] bg-success/10',
  destructive: 'glass-button border-destructive/30 hover:border-destructive/50 hover:shadow-[0_0_30px_hsl(var(--destructive)/0.3)] bg-destructive/10',
};

const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
};

export const GlassButton: React.FC<GlassButtonProps> = ({
  children,
  className,
  variant = 'default',
  size = 'md',
  withTilt = false,
  ...props
}) => {
  return (
    <button
      className={cn(
        variantClasses[variant],
        sizeClasses[size],
        'font-medium transition-all duration-300',
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
};
