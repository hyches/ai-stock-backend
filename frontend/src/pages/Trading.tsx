
import React, { useState } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import CustomCard from '@/components/ui/custom-card';
import FormGroup from '@/components/ui/form-group';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle
} from '@/components/ui/card';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  BarChart2, 
  Download, 
  TrendingDown, 
  TrendingUp, 
  PlayCircle, 
  Loader 
} from '@/utils/icons';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';

const mockSignals = [
  { id: 1, stock: 'NIFTY', strike: '21500 CE', signal: 'Buy', price: '145.2', target: '180.5', sl: '125.0', date: '2025-05-19' },
  { id: 2, stock: 'BANKNIFTY', strike: '48000 PE', signal: 'Sell', price: '320.8', target: '250.0', sl: '350.0', date: '2025-05-19' },
  { id: 3, stock: 'RELIANCE', strike: '3200 CE', signal: 'Buy', price: '89.5', target: '120.0', sl: '75.0', date: '2025-05-18' },
  { id: 4, stock: 'INFY', strike: '1600 PE', signal: 'Buy', price: '45.3', target: '65.0', sl: '35.0', date: '2025-05-18' },
  { id: 5, stock: 'HDFCBANK', strike: '1750 CE', signal: 'Sell', price: '52.1', target: '30.0', sl: '65.0', date: '2025-05-17' },
];

const mockPaperTrades = [
  { id: 1, strategy: 'Bull Call Spread', underlying: 'NIFTY', entryDate: '2025-05-15', status: 'Open', pnl: '+₹8,500', roi: '+15.2%' },
  { id: 2, strategy: 'Iron Condor', underlying: 'BANKNIFTY', entryDate: '2025-05-10', status: 'Closed', pnl: '+₹3,200', roi: '+4.8%' },
  { id: 3, strategy: 'Protective Put', underlying: 'RELIANCE', entryDate: '2025-05-05', status: 'Closed', pnl: '-₹1,200', roi: '-2.6%' },
  { id: 4, strategy: 'Covered Call', underlying: 'INFY', entryDate: '2025-04-25', status: 'Closed', pnl: '+₹4,100', roi: '+8.5%' },
];

const Trading = () => {
  const [selectedStrategy, setSelectedStrategy] = useState('bullish');
  const [isRunningBacktest, setIsRunningBacktest] = useState(false);
  const [tabValue, setTabValue] = useState('signals');
  const { toast } = useToast();

  const handleRunBacktest = () => {
    setIsRunningBacktest(true);
    // Simulate backtest
    setTimeout(() => {
      setIsRunningBacktest(false);
      toast({
        title: "Backtest Completed",
        description: "Your strategy has been backtested successfully.",
      });
    }, 3000);
  };

  const handleTradeAction = (id: number) => {
    toast({
      title: "Trade Executed",
      description: `Signal #${id} has been added to your paper trading account.`,
    });
  };

  return (
    <AppLayout 
      title="F&O Trading Terminal" 
      description="Get AI-powered options trading signals and execute paper trades"
    >
      <div className="flex flex-col gap-6">
        <CustomCard className="animate-fade-in">
          <Tabs defaultValue={tabValue} onValueChange={setTabValue} className="w-full">
            <TabsList className="grid grid-cols-4 mb-6">
              <TabsTrigger value="signals">Signals</TabsTrigger>
              <TabsTrigger value="strategy">Strategy Builder</TabsTrigger>
              <TabsTrigger value="paperTrading">Paper Trading</TabsTrigger>
              <TabsTrigger value="backtest">Backtest</TabsTrigger>
            </TabsList>
            
            <TabsContent value="signals">
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
                <CustomCard variant="glass">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Total Signals</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">23</div>
                    <p className="text-xs text-muted-foreground">+5 from yesterday</p>
                  </CardContent>
                </CustomCard>
                
                <CustomCard variant="glass">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Buy Signals</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-stockup flex items-center">
                      15
                      <TrendingUp className="ml-2 h-4 w-4" />
                    </div>
                    <p className="text-xs text-muted-foreground">65% of total</p>
                  </CardContent>
                </CustomCard>
                
                <CustomCard variant="glass">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Sell Signals</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-stockdown flex items-center">
                      8
                      <TrendingDown className="ml-2 h-4 w-4" />
                    </div>
                    <p className="text-xs text-muted-foreground">35% of total</p>
                  </CardContent>
                </CustomCard>
                
                <CustomCard variant="glass">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Success Rate</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">78%</div>
                    <p className="text-xs text-muted-foreground">Last 30 days</p>
                  </CardContent>
                </CustomCard>
              </div>
              
              <CustomCard variant="default">
                <div className="overflow-x-auto">
                  <div className="flex justify-between mb-4">
                    <h2 className="text-lg font-semibold">Latest F&O Signals</h2>
                    <Button variant="outline" size="sm">
                      <Download className="mr-2 h-4 w-4" />
                      Export
                    </Button>
                  </div>
                  
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Stock/Index</TableHead>
                        <TableHead>Strike</TableHead>
                        <TableHead>Signal</TableHead>
                        <TableHead>Price</TableHead>
                        <TableHead>Target</TableHead>
                        <TableHead>SL</TableHead>
                        <TableHead>Date</TableHead>
                        <TableHead>Action</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {mockSignals.map(signal => (
                        <TableRow key={signal.id}>
                          <TableCell className="font-medium">{signal.stock}</TableCell>
                          <TableCell>{signal.strike}</TableCell>
                          <TableCell>
                            <Badge variant={signal.signal === 'Buy' ? 'success' : 'destructive'}>
                              {signal.signal}
                            </Badge>
                          </TableCell>
                          <TableCell>{signal.price}</TableCell>
                          <TableCell>{signal.target}</TableCell>
                          <TableCell>{signal.sl}</TableCell>
                          <TableCell>{signal.date}</TableCell>
                          <TableCell>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => handleTradeAction(signal.id)}
                            >
                              Trade
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CustomCard>
            </TabsContent>
            
            <TabsContent value="strategy">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1">
                  <CustomCard>
                    <CardHeader>
                      <CardTitle>Strategy Builder</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <FormGroup htmlFor="strategy" label="Strategy Type">
                        <Select value={selectedStrategy} onValueChange={setSelectedStrategy}>
                          <SelectTrigger id="strategy">
                            <SelectValue placeholder="Select strategy" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="bullish">Bullish</SelectItem>
                            <SelectItem value="bearish">Bearish</SelectItem>
                            <SelectItem value="neutral">Neutral</SelectItem>
                            <SelectItem value="volatile">Volatile</SelectItem>
                            <SelectItem value="custom">Custom</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormGroup>
                      
                      <FormGroup htmlFor="stock" label="Underlying">
                        <Select>
                          <SelectTrigger id="stock">
                            <SelectValue placeholder="Select stock/index" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="nifty">NIFTY</SelectItem>
                            <SelectItem value="banknifty">BANKNIFTY</SelectItem>
                            <SelectItem value="reliance">RELIANCE</SelectItem>
                            <SelectItem value="infy">INFOSYS</SelectItem>
                            <SelectItem value="tcs">TCS</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormGroup>
                      
                      <FormGroup htmlFor="expiry" label="Expiry">
                        <Select>
                          <SelectTrigger id="expiry">
                            <SelectValue placeholder="Select expiry" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="weekly">Weekly (23-May-2025)</SelectItem>
                            <SelectItem value="monthly">Monthly (29-May-2025)</SelectItem>
                            <SelectItem value="quarterly">Quarterly (26-Jun-2025)</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormGroup>
                      
                      <FormGroup htmlFor="capital" label="Capital">
                        <Input id="capital" type="number" placeholder="e.g., 100000" />
                      </FormGroup>
                      
                      <Button className="w-full">
                        Generate Strategy
                      </Button>
                    </CardContent>
                  </CustomCard>
                </div>
                
                <div className="lg:col-span-2">
                  <CustomCard>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-xl font-semibold">Bull Call Spread</CardTitle>
                      <BarChart2 className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                      <div className="h-64 flex items-center justify-center text-muted-foreground">
                        Payoff diagram will appear here
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 mt-4">
                        <div className="bg-navy-700 p-3 rounded-lg">
                          <div className="text-sm text-muted-foreground">Max Profit</div>
                          <div className="text-xl font-semibold text-stockup">₹12,500</div>
                        </div>
                        <div className="bg-navy-700 p-3 rounded-lg">
                          <div className="text-sm text-muted-foreground">Max Loss</div>
                          <div className="text-xl font-semibold text-stockdown">₹7,500</div>
                        </div>
                        <div className="bg-navy-700 p-3 rounded-lg">
                          <div className="text-sm text-muted-foreground">Break-even</div>
                          <div className="text-xl font-semibold">21,375</div>
                        </div>
                        <div className="bg-navy-700 p-3 rounded-lg">
                          <div className="text-sm text-muted-foreground">Probability</div>
                          <div className="text-xl font-semibold">68%</div>
                        </div>
                      </div>
                      
                      <div className="mt-6">
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Leg</TableHead>
                              <TableHead>Strike</TableHead>
                              <TableHead>Type</TableHead>
                              <TableHead>Action</TableHead>
                              <TableHead>Price</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            <TableRow>
                              <TableCell>1</TableCell>
                              <TableCell>21300</TableCell>
                              <TableCell>CE</TableCell>
                              <TableCell>Buy</TableCell>
                              <TableCell>150</TableCell>
                            </TableRow>
                            <TableRow>
                              <TableCell>2</TableCell>
                              <TableCell>21500</TableCell>
                              <TableCell>CE</TableCell>
                              <TableCell>Sell</TableCell>
                              <TableCell>75</TableCell>
                            </TableRow>
                          </TableBody>
                        </Table>
                      </div>
                      
                      <div className="mt-6 flex justify-end space-x-2">
                        <Button variant="outline">Modify</Button>
                        <Button>Execute Strategy</Button>
                      </div>
                    </CardContent>
                  </CustomCard>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="paperTrading">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1">
                  <CustomCard title="New Paper Trade">
                    <div className="space-y-4">
                      <FormGroup htmlFor="paperStrategy" label="Strategy">
                        <Select defaultValue="bullCallSpread">
                          <SelectTrigger id="paperStrategy">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="bullCallSpread">Bull Call Spread</SelectItem>
                            <SelectItem value="bearPutSpread">Bear Put Spread</SelectItem>
                            <SelectItem value="ironCondor">Iron Condor</SelectItem>
                            <SelectItem value="coveredCall">Covered Call</SelectItem>
                            <SelectItem value="protectivePut">Protective Put</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormGroup>
                      
                      <FormGroup htmlFor="paperUnderlying" label="Underlying">
                        <Select defaultValue="nifty">
                          <SelectTrigger id="paperUnderlying">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="nifty">NIFTY</SelectItem>
                            <SelectItem value="banknifty">BANKNIFTY</SelectItem>
                            <SelectItem value="reliance">RELIANCE</SelectItem>
                            <SelectItem value="infy">INFOSYS</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormGroup>
                      
                      <FormGroup htmlFor="paperStrikes" label="Strike Selection">
                        <div className="grid grid-cols-2 gap-3">
                          <Input placeholder="Lower Strike" />
                          <Input placeholder="Upper Strike" />
                        </div>
                      </FormGroup>
                      
                      <FormGroup htmlFor="paperExpiry" label="Expiry">
                        <Select defaultValue="weekly">
                          <SelectTrigger id="paperExpiry">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="weekly">Weekly (23-May-2025)</SelectItem>
                            <SelectItem value="monthly">Monthly (29-May-2025)</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormGroup>
                      
                      <FormGroup htmlFor="paperLots" label="Number of Lots">
                        <Input id="paperLots" type="number" defaultValue="1" />
                      </FormGroup>
                      
                      <FormGroup htmlFor="paperSL" label="Stop Loss" optional>
                        <Input id="paperSL" placeholder="e.g., 5000" />
                      </FormGroup>
                      
                      <FormGroup htmlFor="paperTarget" label="Target" optional>
                        <Input id="paperTarget" placeholder="e.g., 10000" />
                      </FormGroup>
                      
                      <Button className="w-full">
                        Add Paper Trade
                      </Button>
                    </div>
                  </CustomCard>
                </div>
                
                <div className="lg:col-span-2">
                  <CustomCard title="Paper Trading Portfolio">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                      <div className="bg-navy-700 p-3 rounded-lg">
                        <div className="text-sm text-muted-foreground">Total Paper Trades</div>
                        <div className="text-xl font-semibold">4</div>
                      </div>
                      <div className="bg-navy-700 p-3 rounded-lg">
                        <div className="text-sm text-muted-foreground">Open P&L</div>
                        <div className="text-xl font-semibold text-stockup">+₹8,500</div>
                      </div>
                      <div className="bg-navy-700 p-3 rounded-lg">
                        <div className="text-sm text-muted-foreground">Win Rate</div>
                        <div className="text-xl font-semibold">75%</div>
                      </div>
                    </div>
                    
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Strategy</TableHead>
                            <TableHead>Underlying</TableHead>
                            <TableHead>Entry Date</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>P&L</TableHead>
                            <TableHead>ROI</TableHead>
                            <TableHead>Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {mockPaperTrades.map(trade => (
                            <TableRow key={trade.id}>
                              <TableCell className="font-medium">{trade.strategy}</TableCell>
                              <TableCell>{trade.underlying}</TableCell>
                              <TableCell>{trade.entryDate}</TableCell>
                              <TableCell>
                                <Badge variant={trade.status === 'Open' ? 'info' : 'secondary'}>
                                  {trade.status}
                                </Badge>
                              </TableCell>
                              <TableCell className={trade.pnl.startsWith('+') ? 'text-stockup' : 'text-stockdown'}>
                                {trade.pnl}
                              </TableCell>
                              <TableCell className={trade.roi.startsWith('+') ? 'text-stockup' : 'text-stockdown'}>
                                {trade.roi}
                              </TableCell>
                              <TableCell>
                                {trade.status === 'Open' ? (
                                  <Button variant="outline" size="sm">Close</Button>
                                ) : (
                                  <Button variant="outline" size="sm">Details</Button>
                                )}
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </CustomCard>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="backtest">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1">
                  <CustomCard title="Backtest Settings">
                    <div className="space-y-4">
                      <FormGroup htmlFor="backtestStrategy" label="Strategy">
                        <Select defaultValue="bullCallSpread">
                          <SelectTrigger id="backtestStrategy">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="bullCallSpread">Bull Call Spread</SelectItem>
                            <SelectItem value="bearPutSpread">Bear Put Spread</SelectItem>
                            <SelectItem value="ironCondor">Iron Condor</SelectItem>
                            <SelectItem value="strangle">Strangle</SelectItem>
                            <SelectItem value="straddle">Straddle</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormGroup>
                      
                      <FormGroup htmlFor="backtestUnderlying" label="Underlying">
                        <Select defaultValue="nifty">
                          <SelectTrigger id="backtestUnderlying">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="nifty">NIFTY</SelectItem>
                            <SelectItem value="banknifty">BANKNIFTY</SelectItem>
                            <SelectItem value="reliance">RELIANCE</SelectItem>
                            <SelectItem value="infy">INFOSYS</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormGroup>
                      
                      <FormGroup htmlFor="backtestPeriod" label="Period">
                        <Select defaultValue="1y">
                          <SelectTrigger id="backtestPeriod">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="3m">3 months</SelectItem>
                            <SelectItem value="6m">6 months</SelectItem>
                            <SelectItem value="1y">1 year</SelectItem>
                            <SelectItem value="2y">2 years</SelectItem>
                            <SelectItem value="custom">Custom</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormGroup>
                      
                      <FormGroup htmlFor="backtestEntry" label="Entry Condition">
                        <Select defaultValue="everyMonday">
                          <SelectTrigger id="backtestEntry">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="everyMonday">Every Monday</SelectItem>
                            <SelectItem value="firstDayMonth">First day of month</SelectItem>
                            <SelectItem value="afterEarnings">After earnings</SelectItem>
                            <SelectItem value="custom">Custom condition</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormGroup>
                      
                      <FormGroup htmlFor="backtestExit" label="Exit Condition">
                        <Select defaultValue="expiry">
                          <SelectTrigger id="backtestExit">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="expiry">At expiry</SelectItem>
                            <SelectItem value="50profit">50% profit</SelectItem>
                            <SelectItem value="100profit">100% profit</SelectItem>
                            <SelectItem value="50loss">50% loss</SelectItem>
                            <SelectItem value="custom">Custom condition</SelectItem>
                          </SelectContent>
                        </Select>
                      </FormGroup>
                      
                      <Button 
                        className="w-full" 
                        onClick={handleRunBacktest}
                        disabled={isRunningBacktest}
                      >
                        {isRunningBacktest ? (
                          <>
                            <Loader className="mr-2 h-4 w-4 animate-spin" />
                            Running...
                          </>
                        ) : (
                          <>
                            <PlayCircle className="mr-2 h-4 w-4" />
                            Run Backtest
                          </>
                        )}
                      </Button>
                    </div>
                  </CustomCard>
                </div>
                
                <div className="lg:col-span-2">
                  <CustomCard title="Backtest Results">
                    <div className="h-96 flex items-center justify-center text-muted-foreground flex-col">
                      <BarChart2 className="h-12 w-12 mb-4 text-muted-foreground/50" />
                      <p>Run a backtest to see detailed performance metrics</p>
                    </div>
                  </CustomCard>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CustomCard>
      </div>
    </AppLayout>
  );
};

export default Trading;
