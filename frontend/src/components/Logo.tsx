import React from 'react';

interface LogoProps {
  className?: string;
  showText?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const Logo: React.FC<LogoProps> = ({ 
  className = '', 
  showText = true, 
  size = 'md' 
}) => {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  const textSizes = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl'
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      {/* Logo Icon - AS Monogram Design */}
      <div className={`${sizeClasses[size]} flex items-center justify-center bg-gradient-to-br from-primary to-primary/80 rounded-lg`}>
        <div className="text-white font-bold text-sm">
          AS
        </div>
      </div>
      
      {showText && (
        <span className={`font-bold text-primary ${textSizes[size]}`}>
          AlgoSentia
        </span>
      )}
    </div>
  );
};

export default Logo;
