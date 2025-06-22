
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrendingUp } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StockRecommendationProps {
  symbol: string;
  name: string;
  price: number;
  change: number;
  recommendation: string;
  confidence: number;
  aiReason: string;
}

const stockRecommendations: StockRecommendationProps[] = [
  {
    symbol: "AAPL",
    name: "Apple Inc.",
    price: 187.42,
    change: 1.8,
    recommendation: "Buy",
    confidence: 87,
    aiReason: "Strong earnings forecast, new product cycle, and expanding services revenue."
  },
  {
    symbol: "MSFT",
    name: "Microsoft Corp.",
    price: 402.95,
    change: 2.1,
    recommendation: "Strong Buy",
    confidence: 93,
    aiReason: "Cloud growth acceleration, AI integration boosting future outlook."
  },
  {
    symbol: "AMZN",
    name: "Amazon.com Inc.",
    price: 178.35,
    change: -0.7,
    recommendation: "Hold",
    confidence: 65,
    aiReason: "Retail slowing but AWS growth remains strong. Wait for better entry point."
  },
  {
    symbol: "NVDA",
    name: "NVIDIA Corp.",
    price: 820.18,
    change: 3.5,
    recommendation: "Buy",
    confidence: 89,
    aiReason: "AI chip demand continuing to exceed supply, datacenter growth accelerating."
  }
];

const StockRecommendationCard = ({
  symbol,
  name,
  price,
  change,
  recommendation,
  confidence,
  aiReason
}: StockRecommendationProps) => {
  const isPositive = change >= 0;
  
  const getRecommendationColor = () => {
    switch (recommendation) {
      case "Strong Buy": return "bg-stockup text-white";
      case "Buy": return "bg-stockup/20 text-stockup";
      case "Hold": return "bg-amber-500/20 text-amber-500";
      case "Sell": return "bg-stockdown/20 text-stockdown";
      default: return "bg-muted text-muted-foreground";
    }
  };
  
  return (
    <Card className="overflow-hidden bg-navy-800 h-full border-white/5 hover:border-teal/30 transition-all">
      <CardContent className="p-4">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-bold text-lg">{symbol}</h3>
            <p className="text-sm text-muted-foreground">{name}</p>
          </div>
          <div className={cn(
            "px-2 py-1 rounded-md text-xs font-medium",
            getRecommendationColor()
          )}>
            {recommendation}
          </div>
        </div>
        
        <div className="flex justify-between mt-3">
          <div>
            <p className="text-2xl font-bold">${price.toLocaleString()}</p>
            <p className={cn(
              "text-sm flex items-center",
              isPositive ? "text-stockup" : "text-stockdown"
            )}>
              {isPositive ? "+" : ""}{change.toFixed(2)}%
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-muted-foreground">AI Confidence</p>
            <p className="text-lg font-medium">{confidence}%</p>
          </div>
        </div>
        
        <div className="mt-4 border-t border-white/5 pt-3">
          <p className="text-xs text-muted-foreground mb-1">AI Analysis</p>
          <p className="text-sm">{aiReason}</p>
        </div>
        
        <div className="mt-3 flex gap-2">
          <Button size="sm" className="w-full">View Details</Button>
        </div>
      </CardContent>
    </Card>
  );
};

const StockRecommendations = () => {
  return (
    <Card className="card-glass">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center">
          <TrendingUp className="h-5 w-5 mr-2 text-teal" />
          AI Stock Recommendations
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {stockRecommendations.map((stock) => (
            <StockRecommendationCard key={stock.symbol} {...stock} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default StockRecommendations;
