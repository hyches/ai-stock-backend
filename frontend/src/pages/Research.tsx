import React from 'react';
import { useNavigate } from 'react-router-dom';
import AppLayout from '@/components/layout/AppLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  AlertTriangle,
  Search,
} from 'lucide-react';
import SearchBar from '@/components/SearchBar';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';
import { useStockData } from '@/context/StockDataContext';

const Research = (): JSX.Element => {
    const navigate = useNavigate();
    const { 
        symbol, 
        stockDetails: stockData, 
        isLoading, 
        error,
        historicalData,
        news,
        analysis,
        financials,
        peers
    } = useStockData();

    // Helper to format large numbers
    const formatNumber = (value: number | undefined | null) => {
        if (value === null || value === undefined) return 'N/A';
        if (value >= 1e12) return `₹${(value / 1e12).toFixed(2)}T`;
        if (value >= 1e9) return `₹${(value / 1e9).toFixed(2)}B`;
        if (value >= 1e6) return `₹${(value / 1e6).toFixed(2)}M`;
        return value.toLocaleString();
    };

    return (
        <AppLayout title="Stock Research" description="Get comprehensive data and analysis on Indian stocks">
            <div className="space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Search className="h-5 w-5" />
                            Search Indian Stocks
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <SearchBar
                            placeholder="e.g., RELIANCE, TCS, HDFCBANK"
                            onSymbolSelect={(selectedSymbol) => navigate(`/research?symbol=${selectedSymbol}`)}
                        />
                    </CardContent>
                </Card>

                {!symbol && (
                    <Card className="text-center py-12">
                        <CardContent>
                            <Search className="h-12 w-12 mx-auto text-muted-foreground opacity-50 mb-4" />
                            <p className="text-lg font-semibold">Search for a stock to begin</p>
                            <p className="text-sm text-muted-foreground mt-1">
                                Enter a stock symbol above to load its detailed report.
                            </p>
                        </CardContent>
                    </Card>
                )}

                {error && (
                    <Card className="border-destructive">
                        <CardContent className="pt-6">
                            <div className="flex items-center gap-2 text-destructive">
                                <AlertTriangle className="h-5 w-5" />
                                <div>
                                    <p className="font-semibold">Error fetching data</p>
                                    <p className="text-sm text-muted-foreground">{error.message}</p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                )}

                {isLoading && <p>Loading data for {symbol}...</p>}

                {stockData && (
                    <Tabs defaultValue="summary" className="space-y-4">
                        <TabsList className="grid w-full grid-cols-4">
                            <TabsTrigger value="summary">Summary</TabsTrigger>
                            <TabsTrigger value="charts">Charts & Technicals</TabsTrigger>
                            <TabsTrigger value="financials">Financials</TabsTrigger>
                            <TabsTrigger value="news">News & Peers</TabsTrigger>
                        </TabsList>

                        {/* Summary Tab */}
                        <TabsContent value="summary" className="space-y-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle>{stockData.name} ({stockData.symbol})</CardTitle>
                                    <p className="text-sm text-muted-foreground">{stockData.sector} / {stockData.industry}</p>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-sm">{stockData.description}</p>
                                </CardContent>
                            </Card>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <Card><CardHeader><CardTitle>Market Cap</CardTitle></CardHeader><CardContent><p>{formatNumber(stockData.marketCap)}</p></CardContent></Card>
                                <Card><CardHeader><CardTitle>Volume</CardTitle></CardHeader><CardContent><p>{formatNumber(stockData.volume)}</p></CardContent></Card>
                                <Card><CardHeader><CardTitle>P/E Ratio</CardTitle></CardHeader><CardContent><p>{stockData.pe?.toFixed(2)}</p></CardContent></Card>
                                <Card><CardHeader><CardTitle>Div. Yield</CardTitle></CardHeader><CardContent><p>{stockData.dividendYield ? `${(stockData.dividendYield * 100).toFixed(2)}%` : 'N/A'}</p></CardContent></Card>
                            </div>
                        </TabsContent>

                        {/* Charts & Technicals Tab */}
                        <TabsContent value="charts" className="space-y-6">
                            <Card>
                                <CardHeader><CardTitle>Price Chart (1 Year)</CardTitle></CardHeader>
                                <CardContent>
                                    <ResponsiveContainer width="100%" height={400}>
                                        <LineChart data={historicalData}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis dataKey="date" tickFormatter={(tick) => format(new Date(tick), 'MMM yy')} />
                                            <YAxis />
                                            <Tooltip />
                                            <Legend />
                                            <Line type="monotone" dataKey="close" name="Close Price" stroke="#8884d8" dot={false} />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </CardContent>
                            </Card>
                        </TabsContent>
                        
                        {/* Financials Tab */}
                        <TabsContent value="financials" className="space-y-6">
                             <Card>
                                <CardHeader><CardTitle>Key Financial Metrics</CardTitle></CardHeader>
                                <CardContent>
                                    <Table>
                                        <TableBody>
                                            <TableRow><TableCell>Market Cap</TableCell><TableCell>{formatNumber(stockData.marketCap)}</TableCell></TableRow>
                                            <TableRow><TableCell>P/E Ratio</TableCell><TableCell>{stockData.pe?.toFixed(2)}</TableCell></TableRow>
                                            <TableRow><TableCell>EPS</TableCell><TableCell>{stockData.eps?.toFixed(2)}</TableCell></TableRow>
                                            <TableRow><TableCell>Dividend Yield</TableCell><TableCell>{stockData.dividendYield ? `${(stockData.dividendYield * 100).toFixed(2)}%` : 'N/A'}</TableCell></TableRow>
                                            <TableRow><TableCell>Beta</TableCell><TableCell>{stockData.beta?.toFixed(2)}</TableCell></TableRow>
                                            <TableRow><TableCell>52 Week High</TableCell><TableCell>{formatNumber(stockData.high52Week)}</TableCell></TableRow>
                                            <TableRow><TableCell>52 Week Low</TableCell><TableCell>{formatNumber(stockData.low52Week)}</TableCell></TableRow>
                                        </TableBody>
                                    </Table>
                                </CardContent>
                            </Card>
                        </TabsContent>

                        {/* News & Peers Tab */}
                        <TabsContent value="news" className="space-y-6">
                            <Card>
                                <CardHeader><CardTitle>Recent News</CardTitle></CardHeader>
                                <CardContent>
                                    {news?.slice(0, 5).map((item: any, index: number) => (
                                        <div key={index} className="mb-4 border-b pb-2">
                                            <a href={item.url} target="_blank" rel="noopener noreferrer" className="font-semibold hover:underline">{item.title}</a>
                                            <p className="text-xs text-muted-foreground mt-1">{item.source} - {format(new Date(item.publishedAt), 'PPP')}</p>
                                        </div>
                                    ))}
                                </CardContent>
                            </Card>
                            <Card>
                                <CardHeader><CardTitle>Peer Companies</CardTitle></CardHeader>
                                <CardContent>
                                    <Table>
                                        <TableHeader><TableRow><TableHead>Symbol</TableHead><TableHead>Name</TableHead><TableHead>Price</TableHead><TableHead>Change</TableHead></TableRow></TableHeader>
                                        <TableBody>
                                            {peers?.map((peer: any, index: number) => (
                                                <TableRow key={index} onClick={() => navigate(`/research?symbol=${peer.symbol}`)} className="cursor-pointer">
                                                    <TableCell>{peer.symbol}</TableCell>
                                                    <TableCell>{peer.name}</TableCell>
                                                    <TableCell>{peer.price.toFixed(2)}</TableCell>
                                                    <TableCell className={peer.change >= 0 ? 'text-green-500' : 'text-red-500'}>
                                                        {peer.change.toFixed(2)} ({peer.changePercent.toFixed(2)}%)
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </CardContent>
                            </Card>
                        </TabsContent>
                    </Tabs>
                )}
            </div>
        </AppLayout>
    );
};

export default Research;
