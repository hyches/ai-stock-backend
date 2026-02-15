import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { PortfolioOverview } from '@/components/dashboard/PortfolioOverview';
import { Watchlist } from '@/components/dashboard/Watchlist';
import { OptionChain } from '@/components/dashboard/OptionChain';
import { Positions } from '@/components/dashboard/Positions';
import { TradePanel } from '@/components/dashboard/TradePanel';
import { MLSignals } from '@/components/dashboard/MLSignals';
import { BacktestingPanel } from '@/components/dashboard/BacktestingPanel';
import { MLTrainingPanel } from '@/components/dashboard/MLTrainingPanel';
import { TradingViewChart } from '@/components/dashboard/TradingViewChart';
import { TradeHistory } from '@/components/dashboard/TradeHistory';
import { AnalyticsPanel } from '@/components/dashboard/AnalyticsPanel';
import { MarketScanner } from '@/components/dashboard/MarketScanner';
import { TradeJournal } from '@/components/dashboard/TradeJournal';
import { OptionsAnalytics } from '@/components/dashboard/OptionsAnalytics';
import { useTrading } from '@/context/TradingContext';
import Research from './Research'; // Import our existing "Brain" page

const Trading: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'dashboard';

  const setActiveTab = (tab: string) => {
    setSearchParams({ tab });
  };

  // Mock selected option state
  const [selectedOption, setSelectedOption] = useState<any>(null);
  const { watchlist, setSelectedSymbol } = useTrading();
  const symbolParam = searchParams.get('symbol');
  const prefillSide = searchParams.get('side');
  const prefillPrice = searchParams.get('price');

  // Sync state with research intent
  useEffect(() => {
    if (symbolParam) {
      setSelectedSymbol(symbolParam);
    }
  }, [symbolParam, setSelectedSymbol]);

  const selectedSymbol = symbolParam || (watchlist.length > 0 ? watchlist[0].symbol : "NIFTY");

  const handleSelectOption = (type: 'CE' | 'PE', strike: number) => {
    setSelectedOption({ type, strike, expiry: '26-DEC-24' });
  };

  return (
    <div className="min-h-screen bg-background text-foreground font-sans">
      {/* Background effects */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-primary/5 rounded-full blur-3xl opacity-50" />
        <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-primary/3 rounded-full blur-3xl opacity-50" />
      </div>

      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

      <main className="ml-20 transition-all duration-300">
        <Header />

        <div className="p-6 space-y-6">
          {activeTab === 'dashboard' && (
            <div className="animate-in slide-in-from-bottom-4 duration-500">
              <PortfolioOverview />

              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mt-6">
                <div className="xl:col-span-2 space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Watchlist />
                    <MLSignals />
                  </div>
                  <OptionChain
                    symbol={selectedSymbol}
                    onSelectOption={handleSelectOption}
                  />
                </div>
                <div className="space-y-6">
                  <TradePanel
                    symbol={selectedSymbol}
                    type={selectedOption?.type || 'CE'}
                    strike={selectedOption?.strike || 24900}
                    prefillSide={prefillSide as any}
                    prefillPrice={prefillPrice ? parseFloat(prefillPrice) : undefined}
                  />
                  <Positions />
                </div>
              </div>
            </div>
          )}

          {activeTab === 'charts' && (
            <div className="space-y-6 animate-in fade-in duration-500">
              <TradingViewChart
                symbol={`NSE:${selectedSymbol}`}
                height={600}
              />
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="glass-card p-4">
                  <h3 className="font-bold mb-4">Technical Analysis</h3>
                  <p className="text-muted-foreground">Chart analysis features coming soon.</p>
                </div>
                <Watchlist />
              </div>
            </div>
          )}

          {activeTab === 'scanner' && <MarketScanner />}

          {/* Integration of our powerful Research Page */}
          {activeTab === 'research' && (
            <div className="animate-in zoom-in-95 duration-300">
              {/* Wrapper to fit Research page style into Dashboard */}
              <div className="rounded-xl overflow-hidden border border-border/50">
                <Research standalone={false} />
              </div>
            </div>
          )}

          {activeTab === 'options' && (
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 animate-in slide-in-from-right-4">
              <div className="xl:col-span-2">
                <OptionChain
                  symbol={selectedSymbol}
                  onSelectOption={handleSelectOption}
                />
              </div>
              <div>
                <TradePanel
                  symbol={selectedSymbol}
                  type={selectedOption?.type || 'CE'}
                  strike={selectedOption?.strike || 24900}
                  prefillSide={prefillSide as any}
                  prefillPrice={prefillPrice ? parseFloat(prefillPrice) : undefined}
                />
              </div>
            </div>
          )}

          {activeTab === 'greeks' && <OptionsAnalytics />}

          {activeTab === 'positions' && (
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
              <Positions />
              <PortfolioOverview />
            </div>
          )}

          {activeTab === 'journal' && <TradeJournal />}

          {activeTab === 'backtest' && <BacktestingPanel />}

          {activeTab === 'ml' && <MLTrainingPanel />}

          {activeTab === 'analytics' && <AnalyticsPanel />}

          {activeTab === 'history' && <TradeHistory />}
        </div>
      </main>
    </div>
  );
};

export default Trading;
