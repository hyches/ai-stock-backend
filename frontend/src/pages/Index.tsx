import React from 'react';
import algosentiaLogo from "@/assets/algosentia-logo.svg";

const Index = () => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="text-center">
        <img 
          src={algosentiaLogo} 
          alt="AlgoSentia Logo - Interlocking AS monogram with stock chart and neural pathway design" 
          className="w-64 h-64 mx-auto"
        />
        <h1 className="mt-8 text-4xl font-bold text-foreground">AlgoSentia</h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Where Intelligence Meets Algorithms
        </p>
        <div className="mt-8">
          <div className="inline-flex items-center space-x-2 text-sm text-muted-foreground">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
            <span>AI-Powered Trading Platform</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;