import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useTrading } from '@/context/TradingContext';
import { useToast } from '@/hooks/use-toast';
import { Loader } from 'lucide-react';

interface TradeDialogProps {
    isOpen: boolean;
    onClose: () => void;
    symbol: string;
    currentPrice: number;
    initialSide?: 'buy' | 'sell';
}

const TradeDialog: React.FC<TradeDialogProps> = ({
    isOpen,
    onClose,
    symbol,
    currentPrice,
    initialSide = 'buy'
}) => {
    const { buyStock, sellStock, virtualCash, positions } = useTrading();
    const [side, setSide] = useState<'buy' | 'sell'>(initialSide);
    const [quantity, setQuantity] = useState<number>(1);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const { toast } = useToast();

    const holding = positions.find(p => p.symbol === symbol);
    const totalCost = quantity * currentPrice;

    useEffect(() => {
        if (isOpen) {
            setSide(initialSide);
            setQuantity(1);
        }
    }, [isOpen, initialSide]);

    const handleSubmit = async () => {
        setIsSubmitting(true);
        let success = false;

        if (side === 'buy') {
            success = await buyStock(symbol, quantity, 'MARKET');
        } else {
            success = await sellStock(symbol, quantity, 'MARKET');
        }

        setIsSubmitting(false);
        if (success) {
            toast({
                title: `${side.toUpperCase()} Order Executed`,
                description: `Successfully ${side === 'buy' ? 'bought' : 'sold'} ${quantity} shares of ${symbol}`,
                variant: "default" // success equivalent
            });
            onClose();
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>{side === 'buy' ? 'Buy' : 'Sell'} {symbol}</DialogTitle>
                    <DialogDescription>
                        Current Market Price: ₹{currentPrice?.toFixed(2) || '0.00'}
                    </DialogDescription>
                </DialogHeader>

                <Tabs defaultValue={side} onValueChange={(v) => setSide(v as 'buy' | 'sell')} className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="buy" className="data-[state=active]:bg-green-600 data-[state=active]:text-white">Buy</TabsTrigger>
                        <TabsTrigger value="sell" className="data-[state=active]:bg-red-600 data-[state=active]:text-white">Sell</TabsTrigger>
                    </TabsList>

                    <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="qty" className="text-right">Quantity</Label>
                            <Input
                                id="qty"
                                type="number"
                                value={quantity}
                                onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 0))}
                                className="col-span-3 font-mono"
                            />
                        </div>

                        <div className="space-y-1 bg-muted p-3 rounded">
                            <div className="flex justify-between text-sm">
                                <span>Estimated Total:</span>
                                <span className="font-bold">₹{(totalCost || 0).toFixed(2)}</span>
                            </div>
                        </div>

                        {side === 'buy' ? (
                            <div className="text-xs text-muted-foreground">
                                Available Margin: ₹{(virtualCash || 0).toFixed(2)}
                            </div>
                        ) : (
                            <div className="text-xs text-muted-foreground">
                                Available Qty: {holding?.quantity || 0}
                            </div>
                        )}
                    </div>

                    <DialogFooter>
                        <Button variant="outline" onClick={onClose} disabled={isSubmitting}>Cancel</Button>
                        <Button
                            className={side === 'buy' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}
                            onClick={handleSubmit}
                            disabled={isSubmitting}
                        >
                            {isSubmitting ? <Loader className="w-4 h-4 animate-spin mr-2" /> : null}
                            Confirm {side.toUpperCase()}
                        </Button>
                    </DialogFooter>
                </Tabs>
            </DialogContent>
        </Dialog>
    );
};

export default TradeDialog;
