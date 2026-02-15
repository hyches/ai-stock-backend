
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Brain, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface SentimentItemProps {
  ticker: string;
  name: string;
  sentiment: number; // -100 to 100
  change: number;
}

const sentimentData: SentimentItemProps[] = [
  { ticker: "AAPL", name: "Apple Inc.", sentiment: 78, change: 5 },
  { ticker: "TSLA", name: "Tesla Inc.", sentiment: -42, change: -12 },
  { ticker: "MSFT", name: "Microsoft Corp.", sentiment: 65, change: 2 },
  { ticker: "AMZN", name: "Amazon.com Inc.", sentiment: 24, change: -3 },
  { ticker: "GOOGL", name: "Alphabet Inc.", sentiment: 56, change: 8 },
];

const SentimentItem = ({ ticker, name, sentiment, change }: SentimentItemProps) => {
  const getSentimentColor = () => {
    if (sentiment > 50) return "bg-stockup";
    if (sentiment > 0) return "bg-emerald-600";
    if (sentiment > -50) return "bg-amber-500";
    return "bg-stockdown";
  };
  
  const getSentimentText = () => {
    if (sentiment > 50) return "Bullish";
    if (sentiment > 0) return "Somewhat Bullish";
    if (sentiment > -50) return "Somewhat Bearish";
    return "Bearish";
  };
  
  const isPositive = change >= 0;
  const isNeutral = change === 0;
  
  // Normalize sentiment to 0-100 for progress bar
  const normalizedSentiment = 50 + sentiment / 2;
  
  return (
    <div className="py-2">
      <div className="flex justify-between items-center mb-1">
        <div className="flex items-center">
          <div className="font-medium">{ticker}</div>
          <div className="text-xs text-muted-foreground ml-2">{name}</div>
        </div>
        <div className="flex items-center text-xs">
          {isPositive && <TrendingUp className="h-3 w-3 mr-1 text-stockup" />}
          {isNeutral && <Minus className="h-3 w-3 mr-1 text-muted-foreground" />}
          {!isPositive && !isNeutral && <TrendingDown className="h-3 w-3 mr-1 text-stockdown" />}
          <span className={cn(
            isPositive ? "text-stockup" : isNeutral ? "text-muted-foreground" : "text-stockdown"
          )}>
            {isPositive ? "+" : ""}{change}
          </span>
        </div>
      </div>
      <Progress value={normalizedSentiment} className={cn("h-2", getSentimentColor())} />
      <div className="mt-1 flex justify-between text-xs">
        <div className={cn(
          "font-medium",
          sentiment > 0 ? "text-stockup" : "text-stockdown"
        )}>
          {getSentimentText()}
        </div>
        <div className="text-muted-foreground">Score: {sentiment}</div>
      </div>
    </div>
  );
};

const AISentimentAnalysis = () => {
  return (
    <Card className="card-glass">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center">
          <Brain className="h-5 w-5 mr-2 text-teal" />
          AI Market Sentiment
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-1">
          {sentimentData.map((item) => (
            <SentimentItem key={item.ticker} {...item} />
          ))}
        </div>
        <div className="mt-4 pt-3 border-t border-white/10">
          <p className="text-xs text-muted-foreground mb-1">Sentiment Analysis</p>
          <p className="text-sm">AI analysis shows bullish sentiment overall in tech sector, with concerned outlook on EV markets due to supply chain issues.</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default AISentimentAnalysis;
