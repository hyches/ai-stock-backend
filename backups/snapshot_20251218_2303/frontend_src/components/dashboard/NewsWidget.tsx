
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Newspaper, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

interface NewsItemProps {
  title: string;
  source: string;
  time: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  link: string;
}

const newsItems: NewsItemProps[] = [
  {
    title: "Fed signals potential rate cuts coming later this year",
    source: "Financial Times",
    time: "2h ago",
    sentiment: "positive",
    link: "#"
  },
  {
    title: "Tech stocks rally as inflation data comes in lower than expected",
    source: "Wall Street Journal",
    time: "4h ago",
    sentiment: "positive",
    link: "#"
  },
  {
    title: "Oil prices drop amid concerns over global demand",
    source: "Reuters",
    time: "6h ago",
    sentiment: "negative",
    link: "#"
  },
  {
    title: "Retail sales flat in April, missing economist expectations",
    source: "CNBC",
    time: "8h ago",
    sentiment: "negative",
    link: "#"
  },
  {
    title: "New startup funding rounds reach quarterly high",
    source: "Bloomberg",
    time: "10h ago",
    sentiment: "positive",
    link: "#"
  }
];

const NewsItem = ({ title, source, time, sentiment, link }: NewsItemProps) => {
  return (
    <div className="border-b border-white/5 py-3 last:border-0 last:pb-0">
      <div className="flex justify-between gap-2">
        <h4 className="font-medium text-sm hover:text-teal cursor-pointer transition-colors">
          {title}
        </h4>
        <a href={link} className="shrink-0 text-muted-foreground hover:text-foreground">
          <ExternalLink className="h-4 w-4" />
        </a>
      </div>
      <div className="flex items-center mt-1 justify-between">
        <div className="text-xs text-muted-foreground">
          {source} • {time}
        </div>
        <div className={cn(
          "text-xs font-medium px-1.5 py-0.5 rounded",
          sentiment === 'positive' && "bg-stockup/20 text-stockup",
          sentiment === 'negative' && "bg-stockdown/20 text-stockdown",
          sentiment === 'neutral' && "bg-gray-500/20 text-gray-400"
        )}>
          {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}
        </div>
      </div>
    </div>
  );
};

const NewsWidget = () => {
  return (
    <Card className="card-glass">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center">
          <Newspaper className="h-5 w-5 mr-2 text-teal" />
          Market News
        </CardTitle>
      </CardHeader>
      <CardContent className="max-h-[400px] overflow-y-auto">
        <div className="space-y-1">
          {newsItems.map((item, index) => (
            <NewsItem key={index} {...item} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default NewsWidget;
