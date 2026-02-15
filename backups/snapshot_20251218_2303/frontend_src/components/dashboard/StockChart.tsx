
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChartLine, Info } from 'lucide-react';
import { Tooltip } from '@/components/ui/tooltip';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip
} from 'recharts';

// Mock data for the chart
const generateChartData = (days: number, startPrice: number) => {
  const data = [];
  let price = startPrice;
  
  for (let i = 0; i < days; i++) {
    const change = (Math.random() - 0.48) * 5; // Slightly biased to positive
    price = Math.max(price + change, price * 0.9); // Prevent huge drops
    
    data.push({
      date: new Date(Date.now() - (days - i) * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      }),
      price: price.toFixed(2),
      volume: Math.floor(Math.random() * 10000000) + 5000000
    });
  }
  
  return data;
};

const chartData = generateChartData(30, 150);

const timeRanges = [
  { label: "1D", days: 1 },
  { label: "1W", days: 7 },
  { label: "1M", days: 30 },
  { label: "3M", days: 90 },
  { label: "1Y", days: 365 },
  { label: "5Y", days: 1825 },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-navy-800 p-3 border border-white/10 rounded-md shadow-lg">
        <p className="text-sm font-medium">{label}</p>
        <p className="text-sm text-teal">${parseFloat(payload[0].value).toFixed(2)}</p>
      </div>
    );
  }
  return null;
};

const StockChart = () => {
  const [selectedRange, setSelectedRange] = useState("1M");
  
  // Will hold different ranges of data 
  // For now just show the same data, but in a real app, this would be different data for each range
  
  return (
    <Card className="card-glass">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-center">
          <CardTitle className="flex items-center">
            <ChartLine className="h-5 w-5 mr-2 text-teal" />
            Portfolio Performance
          </CardTitle>
          <div className="flex gap-1">
            {timeRanges.map((range) => (
              <Button 
                key={range.label}
                variant={selectedRange === range.label ? "default" : "ghost"}
                size="sm"
                onClick={() => setSelectedRange(range.label)}
                className={selectedRange === range.label ? "bg-teal text-navy" : ""}
              >
                {range.label}
              </Button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={chartData}
              margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
            >
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4ECDC4" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#4ECDC4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis 
                dataKey="date" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: '#888888', fontSize: 12 }}
              />
              <YAxis 
                domain={['dataMin - 10', 'dataMax + 10']} 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: '#888888', fontSize: 12 }}
                tickFormatter={(value) => `$${value}`}
              />
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#333333" />
              <RechartsTooltip content={<CustomTooltip />} />
              <Area 
                type="monotone" 
                dataKey="price" 
                stroke="#4ECDC4" 
                fillOpacity={1}
                fill="url(#colorPrice)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        
        <div className="mt-4 flex justify-between items-center">
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Info className="h-4 w-4" />
            <span>AI Analysis:</span>
            <span className="text-foreground">Your portfolio is outperforming the S&P 500 by 2.3% this month.</span>
          </div>
          <Button size="sm">Detailed Analysis</Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default StockChart;
