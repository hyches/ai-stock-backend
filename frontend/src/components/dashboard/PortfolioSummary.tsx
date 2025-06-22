
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PieChart, ChartBar, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

const PortfolioSummary = () => {
  // Mock portfolio data
  const portfolioValue = 158742.63;
  const totalReturn = 12845.79;
  const percentReturn = 8.76;
  const dayChange = 1254.32;
  const dayChangePercent = 0.92;
  
  const isPositive = totalReturn > 0;
  const isDayPositive = dayChange > 0;

  // Asset allocation data
  const allocation = [
    { name: "Technology", percentage: 35, color: "bg-teal-500" },
    { name: "Healthcare", percentage: 25, color: "bg-coral-500" },
    { name: "Financial", percentage: 20, color: "bg-blue-500" },
    { name: "Consumer", percentage: 15, color: "bg-purple-500" },
    { name: "Energy", percentage: 5, color: "bg-amber-500" },
  ];

  return (
    <Card className="card-glass">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center">
          <PieChart className="h-5 w-5 mr-2 text-teal" />
          Portfolio Summary
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col md:flex-row gap-8">
          <div className="flex-1 space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">Portfolio Value</p>
              <h2 className="text-2xl font-bold">${portfolioValue.toLocaleString()}</h2>
              
              <div className="mt-2 grid grid-cols-2 gap-2">
                <div>
                  <p className="text-xs text-muted-foreground">Total Return</p>
                  <div className={cn(
                    "flex items-center",
                    isPositive ? "text-stockup" : "text-stockdown"
                  )}>
                    <span className="font-semibold">${Math.abs(totalReturn).toLocaleString()}</span>
                    <span className="text-xs ml-1">({isPositive ? "+" : "-"}{Math.abs(percentReturn).toFixed(2)}%)</span>
                  </div>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Today</p>
                  <div className={cn(
                    "flex items-center",
                    isDayPositive ? "text-stockup" : "text-stockdown"
                  )}>
                    {isDayPositive ? 
                      <ArrowUpRight className="h-3 w-3 mr-1" /> : 
                      <ArrowDownRight className="h-3 w-3 mr-1" />
                    }
                    <span className="font-semibold">${Math.abs(dayChange).toLocaleString()}</span>
                    <span className="text-xs ml-1">({isDayPositive ? "+" : "-"}{Math.abs(dayChangePercent).toFixed(2)}%)</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-1">
                <p className="text-sm font-medium">Top Performers</p>
                <span className="text-xs text-muted-foreground">% Change</span>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span>AAPL</span>
                  <span className="text-stockup">+2.4%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>MSFT</span>
                  <span className="text-stockup">+1.8%</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>GOOGL</span>
                  <span className="text-stockup">+1.2%</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="flex-1">
            <div className="mb-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium flex items-center">
                  <ChartBar className="h-4 w-4 mr-1 text-muted-foreground" />
                  Asset Allocation
                </h3>
              </div>
              
              <div className="mt-4 space-y-3">
                {allocation.map((asset) => (
                  <div key={asset.name}>
                    <div className="flex justify-between text-sm mb-1">
                      <span>{asset.name}</span>
                      <span>{asset.percentage}%</span>
                    </div>
                    <Progress value={asset.percentage} className={cn("h-2", asset.color)} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PortfolioSummary;
