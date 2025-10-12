import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { useTrading } from '@/context/TradingContext';
import { 
  TrendingUp, 
  TrendingDown, 
  Star, 
  StarOff, 
  DollarSign,
  Wallet
} from 'lucide-react';

interface TradingActionsProps {
  symbol: string;
  name: string;
  currentPrice: number;
  change: number;
  changePercent: number;
}

const TradingActions: React.FC<TradingActionsProps> = ({
  symbol,
  name,
  currentPrice,
  change,
  changePercent
}) => {
  const [quantity, setQuantity] = useState<number>(1);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const {
    virtualCash,
    buyStock,
    sellStock,
    addToWatchlist,
    removeFromWatchlist,
    isInWatchlist,
    getPortfolioItem
  } = useTrading();

  const portfolioItem = getPortfolioItem(symbol);
  const inWatchlist = isInWatchlist(symbol);
  const totalCost = quantity * currentPrice;
  const canBuy = totalCost <= virtualCash;
  const canSell = portfolioItem && portfolioItem.quantity >= quantity;

  const handleBuy = async () => {
    if (!canBuy) {
      toast({
        title: "Insufficient Funds",
        description: `You need ₹${totalCost.toLocaleString()} but only have ₹${virtualCash.toLocaleString()}`,
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    try {
      const success = buyStock(symbol, name, quantity, currentPrice);
      if (success) {
        toast({
          title: "Purchase Successful",
          description: `Bought ${quantity} shares of ${symbol} for ₹${totalCost.toLocaleString()}`,
        });
        setQuantity(1);
      }
    } catch (error) {
      toast({
        title: "Purchase Failed",
        description: "Something went wrong. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSell = async () => {
    if (!canSell) {
      toast({
        title: "Insufficient Shares",
        description: `You only have ${portfolioItem?.quantity || 0} shares of ${symbol}`,
        variant: "destructive"
      });
      return;
    }

    setIsLoading(true);
    try {
      const success = sellStock(symbol, quantity, currentPrice);
      if (success) {
        toast({
          title: "Sale Successful",
          description: `Sold ${quantity} shares of ${symbol} for ₹${totalCost.toLocaleString()}`,
        });
        setQuantity(1);
      }
    } catch (error) {
      toast({
        title: "Sale Failed",
        description: "Something went wrong. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleWatchlistToggle = () => {
    if (inWatchlist) {
      removeFromWatchlist(symbol);
      toast({
        title: "Removed from Watchlist",
        description: `${symbol} has been removed from your watchlist`,
      });
    } else {
      addToWatchlist(symbol, name, currentPrice, change, changePercent);
      toast({
        title: "Added to Watchlist",
        description: `${symbol} has been added to your watchlist`,
      });
    }
  };

  return (
    <div className="space-y-4">
      {/* Virtual Cash Display */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center text-sm font-medium">
            <Wallet className="h-4 w-4 mr-2" />
            Virtual Cash
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-600">
            ₹{virtualCash.toLocaleString()}
          </div>
        </CardContent>
      </Card>

      {/* Portfolio Position */}
      {portfolioItem && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Your Position</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Shares Owned:</span>
                <span className="font-medium">{portfolioItem.quantity}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Avg. Price:</span>
                <span className="font-medium">₹{portfolioItem.averagePrice.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Total Value:</span>
                <span className="font-medium">₹{portfolioItem.totalValue.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">P&L:</span>
                <span className={`font-medium ${portfolioItem.profitLoss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  ₹{portfolioItem.profitLoss.toLocaleString()} ({portfolioItem.profitLossPercent.toFixed(2)}%)
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Trading Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Trading Actions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Quantity Input */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Quantity</label>
            <Input
              type="number"
              min="1"
              max={portfolioItem?.quantity || 1000}
              value={quantity}
              onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
              className="w-full"
            />
          </div>

          {/* Cost Display */}
          <div className="p-3 bg-muted rounded-lg">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Total Cost:</span>
              <span className="text-lg font-bold">₹{totalCost.toLocaleString()}</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <Button
              onClick={handleBuy}
              disabled={!canBuy || isLoading}
              className="w-full"
              variant="default"
            >
              <TrendingUp className="h-4 w-4 mr-2" />
              {isLoading ? 'Buying...' : 'Buy'}
            </Button>
            
            <Button
              onClick={handleSell}
              disabled={!canSell || isLoading}
              className="w-full"
              variant="destructive"
            >
              <TrendingDown className="h-4 w-4 mr-2" />
              {isLoading ? 'Selling...' : 'Sell'}
            </Button>
          </div>

          {/* Watchlist Button */}
          <Button
            onClick={handleWatchlistToggle}
            variant="outline"
            className="w-full"
          >
            {inWatchlist ? (
              <>
                <StarOff className="h-4 w-4 mr-2" />
                Remove from Watchlist
              </>
            ) : (
              <>
                <Star className="h-4 w-4 mr-2" />
                Add to Watchlist
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default TradingActions;
