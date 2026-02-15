import React, { useState } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import CustomCard from '@/components/ui/custom-card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Search, Plus, Trash2, TrendingUp, TrendingDown, MoreHorizontal } from 'lucide-react';
import { useTrading } from '@/context/TradingContext';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from '@/components/ui/badge';
import SearchBar from '@/components/SearchBar';
import { useToast } from '@/hooks/use-toast';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import TradeDialog from '@/components/TradeDialog';

const Watchlist = () => {
    const { watchlist, addToWatchlist, removeFromWatchlist } = useTrading();
    const [isAddMode, setIsAddMode] = useState(false);
    const [tradeConfig, setTradeConfig] = useState<{ isOpen: boolean, symbol: string, price: number, side: 'buy' | 'sell' }>({
        isOpen: false, symbol: '', price: 0, side: 'buy'
    });
    const { toast } = useToast();

    const handleStockSelect = (stock: any) => {
        if (stock) {
            addToWatchlist(
                stock.symbol,
                stock.name || stock.symbol,
                stock.price || 0,
                stock.change || 0,
                stock.changePercent || 0
            );
            setIsAddMode(false);
            toast({ title: "Added to Watchlist", description: `${stock.symbol} has been added.` });
        }
    };

    const openTrade = (symbol: string, price: number, side: 'buy' | 'sell') => {
        setTradeConfig({ isOpen: true, symbol, price, side });
    };

    return (
        <AppLayout title="My Watchlist" description="Track your favorite stocks">
            <div className="max-w-6xl mx-auto space-y-6">

                <div className="flex justify-between items-center bg-card p-4 rounded-lg border">
                    <div>
                        <h3 className="font-bold text-lg">Your Lists</h3>
                        <p className="text-sm text-muted-foreground">{watchlist.length} symbols</p>
                    </div>
                    <Button onClick={() => setIsAddMode(!isAddMode)}>
                        {isAddMode ? "Cancel" : <><Plus className="mr-2 h-4 w-4" /> Add Symbol</>}
                    </Button>
                </div>

                {isAddMode && (
                    <div className="bg-muted/30 p-4 rounded-lg border animate-in slide-in-from-top-2">
                        <p className="mb-2 text-sm font-medium">Search to add:</p>
                        <SearchBar
                            placeholder="Search stock (e.g. TATASTEEL)..."
                            onStockSelect={handleStockSelect}
                            className="max-w-md bg-background"
                        />
                    </div>
                )}

                <CustomCard>
                    {watchlist.length > 0 ? (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Symbol</TableHead>
                                    <TableHead>Company</TableHead>
                                    <TableHead className="text-right">Price</TableHead>
                                    <TableHead className="text-right">Change</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {watchlist.map((item) => (
                                    <TableRow key={item.symbol} className="group">
                                        <TableCell className="font-medium">{item.symbol}</TableCell>
                                        <TableCell className="text-muted-foreground text-sm">{item.name}</TableCell>
                                        <TableCell className="text-right font-mono">₹{item.price.toFixed(2)}</TableCell>
                                        <TableCell className={`text-right font-mono ${item.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                            {item.change > 0 ? '+' : ''}{item.change.toFixed(2)} ({item.changePercent.toFixed(2)}%)
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                <Button size="sm" className="bg-green-600 hover:bg-green-700 h-8" onClick={() => openTrade(item.symbol, item.price, 'buy')}>Buy</Button>
                                                <Button size="sm" variant="destructive" className="h-8" onClick={() => openTrade(item.symbol, item.price, 'sell')}>Sell</Button>
                                                <Button size="icon" variant="ghost" className="h-8 w-8 text-muted-foreground hover:text-red-500" onClick={() => removeFromWatchlist(item.symbol)}>
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    ) : (
                        <div className="text-center py-12 text-muted-foreground">
                            <p>Your watchlist is empty.</p>
                            <Button variant="link" onClick={() => setIsAddMode(true)}>Add your first stock</Button>
                        </div>
                    )}
                </CustomCard>

                <TradeDialog
                    isOpen={tradeConfig.isOpen}
                    onClose={() => setTradeConfig(prev => ({ ...prev, isOpen: false }))}
                    symbol={tradeConfig.symbol}
                    currentPrice={tradeConfig.price}
                    initialSide={tradeConfig.side}
                />
            </div>
        </AppLayout>
    );
};

export default Watchlist;
