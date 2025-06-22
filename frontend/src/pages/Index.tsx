
import React from 'react';
import AppLayout from '@/components/layout/AppLayout';
import MarketOverview from '@/components/dashboard/MarketOverview';
import PortfolioSummary from '@/components/dashboard/PortfolioSummary';
import StockRecommendations from '@/components/dashboard/StockRecommendations';
import StockChart from '@/components/dashboard/StockChart';
import NewsWidget from '@/components/dashboard/NewsWidget';
import AISentimentAnalysis from '@/components/dashboard/AISentimentAnalysis';

const Index = () => {
  return (
    <AppLayout>
      <div className="grid gap-6">
        <MarketOverview />
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PortfolioSummary />
          <StockChart />
        </div>
        
        <StockRecommendations />
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <NewsWidget />
          <AISentimentAnalysis />
        </div>
      </div>
    </AppLayout>
  );
};

export default Index;
