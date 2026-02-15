
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MarketIndexProps {
  name: string;
  value: number;
  change: number;
  percentChange: number;
}

const MarketIndex = ({ name, value, change, percentChange }: MarketIndexProps) => {
  const isPositive = change >= 0;
  
  return (
    <div className="flex items-center justify-between">
      <div>
        <h4 className="font-medium">{name}</h4>
        <p className="text-lg font-semibold">{value.toLocaleString()}</p>
      </div>
      <div className={cn(
        "flex flex-col items-end",
        isPositive ? "text-stockup" : "text-stockdown"
      )}>
        <div className="flex items-center">
          {isPositive ? <TrendingUp className="h-4 w-4 mr-1" /> : <TrendingDown className="h-4 w-4 mr-1" />}
          <span>{change.toFixed(2)}</span>
        </div>
        <p className="text-sm">{isPositive ? "+" : ""}{percentChange.toFixed(2)}%</p>
      </div>
    </div>
  );
};

const marketData = [
  { name: "S&P 500", value: 4782.82, change: 35.42, percentChange: 0.74 },
  { name: "Nasdaq", value: 16330.61, change: 183.02, percentChange: 1.13 },
  { name: "Dow Jones", value: 38239.97, change: -68.12, percentChange: -0.18 },
  { name: "Russell 2000", value: 2107.35, change: 16.87, percentChange: 0.81 },
];

const MarketOverview = () => {
  return (
    <Card className="card-glass">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center">
          <DollarSign className="h-5 w-5 mr-2 text-teal" />
          Market Overview
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {marketData.map((index) => (
            <MarketIndex key={index.name} {...index} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default MarketOverview;
