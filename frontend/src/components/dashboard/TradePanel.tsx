import React, { useState, useEffect } from 'react';
import { GlassButton } from '@/components/ui/GlassButton';
import { useTrading } from '@/context/TradingContext';
import { cn } from '@/lib/utils';
import { ArrowUpCircle, ArrowDownCircle, Calculator, Loader2, TrendingUp, Briefcase } from 'lucide-react';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';

import {
  submitAdvancedOrder,
  AdvancedOrderRequest
} from '@/lib/api-services';
import { useToast } from '@/hooks/use-toast';

interface TradePanelProps {
  symbol?: string;
  type?: 'CE' | 'PE' | 'FUT' | 'EQ';
  strike?: number;
  expiry?: string;
  prefillSide?: 'BUY' | 'SELL';
  prefillPrice?: number;
}

export const TradePanel: React.FC<TradePanelProps> = ({
  symbol: propSymbol,
  type: propType = 'EQ',
  strike: propStrike = 24900,
  expiry = '26-DEC-24',
  prefillSide,
  prefillPrice,
}) => {
  const { toast } = useToast();
  const { selectedSymbol, selectedOption, quotes, portfolio } = useTrading();

  const symbol = propSymbol || selectedSymbol;

  const [tradingMode, setTradingMode] = useState<'equity' | 'derivatives'>('equity');
  const [type, setType] = useState<'CE' | 'PE' | 'FUT' | 'EQ'>(tradingMode === 'equity' ? 'EQ' : propType);
  const strike = selectedOption?.strike || propStrike;

  const [action, setAction] = useState<'BUY' | 'SELL'>(prefillSide || 'BUY');
  const [qty, setQty] = useState(1);
  const [price, setPrice] = useState(prefillPrice || 0);
  const [orderType, setOrderType] = useState<AdvancedOrderRequest['order_type']>('MARKET');
  const [isExecuting, setIsExecuting] = useState(false);

  // Advanced parameters
  const [targetPrice, setTargetPrice] = useState<number>(0);
  const [stopLossPrice, setStopLossPrice] = useState<number>(0);
  const [trailPercent, setTrailPercent] = useState<number>(1.5);

  // Update type when trading mode changes
  useEffect(() => {
    if (tradingMode === 'equity') {
      setType('EQ');
      setQty(1);
    } else {
      setType(selectedOption?.type || 'CE');
      const lotSize = symbol === 'NIFTY' ? 50 : symbol === 'BANKNIFTY' ? 15 : 250;
      setQty(lotSize);
    }
  }, [tradingMode, symbol, selectedOption]);

  const lotSize = tradingMode === 'derivatives'
    ? (symbol === 'NIFTY' ? 50 : symbol === 'BANKNIFTY' ? 15 : 250)
    : 1;

  // Get live price from quotes
  const quote = quotes.get(symbol);
  const livePrice = quote?.regularMarketPrice || 0;

  // For options, calculate approximate option price
  const optionPrice = type === 'EQ' || type === 'FUT'
    ? livePrice
    : Math.abs(livePrice - strike) + 50; // Simplified formula

  const executionPrice = orderType === 'MARKET' ? optionPrice : price;

  // Calculate margin
  const margin = tradingMode === 'equity'
    ? qty * (executionPrice || livePrice)
    : action === 'BUY' ? qty * (executionPrice || livePrice) : qty * (executionPrice || livePrice) * 0.15;

  const handleExecute = async () => {
    setIsExecuting(true);
    try {
      const orderRequest: AdvancedOrderRequest = {
        symbol,
        side: action,
        order_type: orderType,
        quantity: qty,
        price: orderType === 'LIMIT' ? price : undefined,
        target_price: orderType === 'BRACKET' ? targetPrice : undefined,
        stop_price: (orderType === 'BRACKET' || orderType === 'TRAILING_STOP') ? stopLossPrice : undefined,
        trail_percent: orderType === 'TRAILING_STOP' ? trailPercent : undefined,
      };

      const result = await submitAdvancedOrder(orderRequest);

      toast({
        title: "Order Submitted",
        description: `Professional ${orderType} order for ${symbol} placed successfully. ID: ${result.order_id}`,
      });
    } catch (error: any) {
      toast({
        title: "Order Failed",
        description: error.message || "Failed to submit professional order.",
        variant: "destructive"
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const canAfford = action === 'SELL' || margin <= portfolio.availableMargin;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Place Order</h2>
        <div className="flex items-center gap-2">
          <span className={cn(
            'text-xs px-2 py-1 rounded-full font-medium',
            type === 'CE' && 'bg-emerald-500/20 text-emerald-400',
            type === 'PE' && 'bg-rose-500/20 text-rose-400',
            type === 'FUT' && 'bg-primary/20 text-primary',
            type === 'EQ' && 'bg-blue-500/20 text-blue-400'
          )}>
            {symbol} {type === 'EQ' ? 'Equity' : type} {(type === 'CE' || type === 'PE') && strike}
          </span>
        </div>
      </div>

      <div className="glass-card p-5 space-y-5">
        {/* Trading Mode Tabs */}
        <Tabs value={tradingMode} onValueChange={(v) => setTradingMode(v as 'equity' | 'derivatives')} className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-muted/50">
            <TabsTrigger value="equity" className="gap-2">
              <Briefcase size={14} />
              Stocks
            </TabsTrigger>
            <TabsTrigger value="derivatives" className="gap-2">
              <TrendingUp size={14} />
              F&O
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Live Price Display */}
        {quote && (
          <div className="flex items-center justify-between p-3 rounded-xl bg-muted/30">
            <span className="text-sm text-muted-foreground">
              {tradingMode === 'equity' ? 'Stock Price' : 'Underlying'}
            </span>
            <div className="text-right">
              <span className="font-mono font-semibold">₹{livePrice.toFixed(2)}</span>
              <span className={cn(
                'ml-2 text-xs',
                quote.regularMarketChange >= 0 ? 'text-emerald-400' : 'text-rose-400'
              )}>
                {quote.regularMarketChange >= 0 ? '+' : ''}{quote.regularMarketChange.toFixed(2)}
                ({quote.regularMarketChangePercent.toFixed(2)}%)
              </span>
            </div>
          </div>
        )}

        {/* Derivative Type Selection */}
        {tradingMode === 'derivatives' && (
          <div className="space-y-2">
            <label className="text-sm text-muted-foreground">Instrument Type</label>
            <div className="grid grid-cols-3 gap-2">
              {(['CE', 'PE', 'FUT'] as const).map(t => (
                <button
                  key={t}
                  onClick={() => setType(t)}
                  className={cn(
                    'py-2 rounded-lg text-sm font-medium transition-all border',
                    type === t
                      ? t === 'CE' ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400'
                        : t === 'PE' ? 'border-rose-500 bg-rose-500/10 text-rose-400'
                          : 'border-primary bg-primary/10 text-primary'
                      : 'border-border text-muted-foreground hover:border-primary/50'
                  )}
                >
                  {t === 'CE' ? 'Call' : t === 'PE' ? 'Put' : 'Future'}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Action Toggle */}
        <div className="grid grid-cols-2 gap-2 p-1 rounded-xl bg-muted/50">
          <button
            onClick={() => setAction('BUY')}
            className={cn(
              'py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2',
              action === 'BUY'
                ? 'bg-emerald-500 text-emerald-950 shadow-lg shadow-emerald-500/30'
                : 'text-muted-foreground hover:text-foreground'
            )}
          >
            <ArrowUpCircle size={18} />
            BUY
          </button>
          <button
            onClick={() => setAction('SELL')}
            className={cn(
              'py-3 rounded-lg font-semibold transition-all flex items-center justify-center gap-2',
              action === 'SELL'
                ? 'bg-rose-500 text-rose-950 shadow-lg shadow-rose-500/30'
                : 'text-muted-foreground hover:text-foreground'
            )}
          >
            <ArrowDownCircle size={18} />
            SELL
          </button>
        </div>

        {/* Order Type */}
        <div className="space-y-2">
          <label className="text-sm text-muted-foreground">Order Type</label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {(['MARKET', 'LIMIT', 'BRACKET', 'TRAILING_STOP'] as const).map(t => (
              <button
                key={t}
                onClick={() => setOrderType(t)}
                className={cn(
                  'py-2 rounded-lg text-xs font-medium transition-all border shrink-0',
                  orderType === t
                    ? 'border-primary bg-primary/10 text-primary'
                    : 'border-border text-muted-foreground hover:border-primary/50'
                )}
              >
                {t.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Quantity */}
        <div className="space-y-2">
          <label className="text-sm text-muted-foreground flex items-center justify-between">
            <span>Quantity</span>
            {tradingMode === 'derivatives' && <span className="text-xs">Lot Size: {lotSize}</span>}
          </label>
          <div className="flex gap-2">
            <button
              onClick={() => setQty(Math.max(lotSize, qty - lotSize))}
              className="glass-button px-4 py-2 text-lg font-bold"
            >
              −
            </button>
            <input
              type="number"
              value={qty}
              onChange={(e) => setQty(Math.max(1, parseInt(e.target.value) || 1))}
              step={tradingMode === 'equity' ? 1 : lotSize}
              className="flex-1 bg-muted/50 border border-border rounded-xl px-4 py-2 text-center font-mono text-lg focus:outline-none focus:border-primary transition-colors"
            />
            <button
              onClick={() => setQty(qty + lotSize)}
              className="glass-button px-4 py-2 text-lg font-bold"
            >
              +
            </button>
          </div>
        </div>

        {/* Price */}
        {orderType === 'LIMIT' && (
          <div className="space-y-2">
            <label className="text-sm text-muted-foreground">Limit Price</label>
            <input
              type="number"
              value={price}
              onChange={(e) => setPrice(parseFloat(e.target.value) || 0)}
              step={0.05}
              className="w-full bg-muted/50 border border-border rounded-xl px-4 py-2 font-mono text-lg focus:outline-none focus:border-primary transition-colors"
            />
          </div>
        )}

        {/* Bracket Order Inputs */}
        {orderType === 'BRACKET' && (
          <div className="grid grid-cols-2 gap-4 animate-in fade-in slide-in-from-top-2">
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Target Price (TP)</label>
              <input
                type="number"
                value={targetPrice}
                onChange={(e) => setTargetPrice(parseFloat(e.target.value) || 0)}
                className="w-full bg-emerald-500/10 border border-emerald-500/20 rounded-xl px-4 py-2 font-mono text-lg text-emerald-400 focus:outline-none focus:border-emerald-500"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm text-muted-foreground">Stop Loss (SL)</label>
              <input
                type="number"
                value={stopLossPrice}
                onChange={(e) => setStopLossPrice(parseFloat(e.target.value) || 0)}
                className="w-full bg-rose-500/10 border border-rose-500/20 rounded-xl px-4 py-2 font-mono text-lg text-rose-400 focus:outline-none focus:border-rose-500"
              />
            </div>
          </div>
        )}

        {/* Trailing Stop Input */}
        {orderType === 'TRAILING_STOP' && (
          <div className="space-y-2 animate-in fade-in slide-in-from-top-2">
            <label className="text-sm text-muted-foreground">Trail Gap (%)</label>
            <div className="relative">
              <input
                type="number"
                value={trailPercent}
                onChange={(e) => setTrailPercent(parseFloat(e.target.value) || 0)}
                step={0.1}
                className="w-full bg-primary/10 border border-primary/20 rounded-xl px-4 py-2 font-mono text-lg text-primary focus:outline-none focus:border-primary"
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-primary font-mono">%</span>
            </div>
          </div>
        )}

        {/* Order Summary */}
        <div className="p-4 rounded-xl bg-muted/30 space-y-3">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calculator size={16} />
            Order Summary
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Est. Price</span>
              <span className="font-mono">₹{executionPrice.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Value</span>
              <span className="font-mono">₹{(qty * executionPrice).toLocaleString('en-IN')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">
                {tradingMode === 'equity' ? 'Total Amount' : 'Required Margin'}
              </span>
              <span className={cn(
                'font-mono',
                !canAfford && 'text-rose-400'
              )}>
                ₹{margin.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Available</span>
              <span className="font-mono text-emerald-400">
                ₹{portfolio.availableMargin.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
              </span>
            </div>
            {tradingMode === 'derivatives' && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Lots</span>
                <span className="font-mono">{qty / lotSize}</span>
              </div>
            )}
          </div>
        </div>

        {/* Submit Button */}
        <GlassButton
          variant={action === 'BUY' ? 'success' : 'destructive'}
          size="lg"
          className="w-full"
          onClick={handleExecute}
          disabled={isExecuting || !canAfford}
        >
          {isExecuting ? (
            <>
              <Loader2 size={18} className="animate-spin mr-2" />
              Executing...
            </>
          ) : (
            <>
              {action} {qty} {tradingMode === 'equity' ? 'shares' : 'qty'} @ {orderType === 'MARKET' ? 'Market' : `₹${price.toFixed(2)}`}
            </>
          )}
        </GlassButton>

        {!canAfford && (
          <p className="text-xs text-destructive text-center">
            Insufficient {tradingMode === 'equity' ? 'funds' : 'margin'}. Reduce quantity or close existing positions.
          </p>
        )}

        <p className="text-[10px] text-muted-foreground text-center mt-2 italic">
          Order execution occurs in the Trading Terminal.
        </p>
      </div>
    </div>
  );
};