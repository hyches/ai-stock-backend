
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
import { useTrades, usePositions } from '@/lib/queries';

// Mock data for strategies
const mockStrategies = [
  {
    id: 1,
    name: 'Bull Call Spread',
    type: 'Options',
    is_active: true,
    performance: { total_return: 15.5, sharpe_ratio: 1.2, max_drawdown: 5.2 },
    created_at: '2023-10-26T10:00:00Z',
    description: 'A bullish strategy involving two call options.'
  },
  {
    id: 2,
    name: 'Iron Condor',
    type: 'Options',
    is_active: false,
    performance: { total_return: 8.2, sharpe_ratio: 0.9, max_drawdown: 3.1 },
    created_at: '2023-10-25T12:30:00Z',
    description: 'A neutral strategy with limited risk and profit.'
  }
];

const Trading = () => {
  const [selectedStrategy, setSelectedStrategy] = useState('bullish');
  const [isRunningBacktest, setIsRunningBacktest] = useState(false);
  const [tabValue, setTabValue] = useState('signals');
  const { toast } = useToast();

  // Fetch data from APIs
  const { data: trades, isLoading: tradesLoading } = useTrades();
  const { data: positions, isLoading: positionsLoading } = usePositions();

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
      title="F&O Trading" 
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
                    <div className="text-2xl font-bold">{mockStrategies.length}</div>
                    <p className="text-xs text-muted-foreground">
                      Active strategies
                    </p>
                  </CardContent>
                </CustomCard>
                
                <CustomCard variant="glass">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Active Strategies</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-stockup flex items-center">
                      {mockStrategies.filter(s => s.is_active).length}
                      <TrendingUp className="ml-2 h-4 w-4" />
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {`${Math.round((mockStrategies.filter(s => s.is_active).length / mockStrategies.length) * 100)}% of total`}
                    </p>
                  </CardContent>
                </CustomCard>
                
                <CustomCard variant="glass">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Inactive Strategies</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold text-stockdown flex items-center">
                      {mockStrategies.filter(s => !s.is_active).length}
                      <TrendingDown className="ml-2 h-4 w-4" />
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {`${Math.round((mockStrategies.filter(s => !s.is_active).length / mockStrategies.length) * 100)}% of total`}
                    </p>
                  </CardContent>
                </CustomCard>
                
                <CustomCard variant="glass">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground">Avg Return</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {`${Math.round(mockStrategies.reduce((sum, s) => sum + (s.performance?.total_return || 0), 0) / mockStrategies.length)}%`}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Average performance
                    </p>
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
                        <TableHead>Strategy</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Return</TableHead>
                        <TableHead>Sharpe</TableHead>
                        <TableHead>Drawdown</TableHead>
                        <TableHead>Created</TableHead>
                        <TableHead>Action</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {mockStrategies.map(strategy => (
                        <TableRow key={strategy.id}>
                          <TableCell className="font-medium">{strategy.name}</TableCell>
                          <TableCell>{strategy.type}</TableCell>
                          <TableCell>
                            <Badge variant={strategy.is_active ? 'success' : 'secondary'}>
                              {strategy.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </TableCell>
                          <TableCell>{strategy.performance?.total_return || 0}%</TableCell>
                          <TableCell>{strategy.performance?.sharpe_ratio || 0}</TableCell>
                          <TableCell>{strategy.performance?.max_drawdown || 0}%</TableCell>
                          <TableCell>{new Date(strategy.created_at || Date.now()).toLocaleDateString()}</TableCell>
                          <TableCell>
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => handleTradeAction(strategy.id)}
                            >
                              {strategy.is_active ? 'Deactivate' : 'Activate'}
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
                      <CardTitle className="text-xl font-semibold">Existing Strategies</CardTitle>
                      <BarChart2 className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                          {mockStrategies.map(strategy => (
                            <div key={strategy.id} className="border rounded-lg p-4">
                              <div className="flex justify-between items-start">
                                <div>
                                  <h3 className="font-semibold">{strategy.name}</h3>
                                  <p className="text-sm text-muted-foreground">{strategy.description}</p>
                                  <div className="flex gap-4 mt-2 text-sm">
                                    <span>Type: {strategy.type}</span>
                                    <span>Return: {strategy.performance?.total_return || 0}%</span>
                                    <span>Sharpe: {strategy.performance?.sharpe_ratio || 0}</span>
                                  </div>
                                </div>
                                <Badge variant={strategy.is_active ? 'success' : 'secondary'}>
                                  {strategy.is_active ? 'Active' : 'Inactive'}
                                </Badge>
                              </div>
                            </div>
                          ))}
                        </div>
                    </CardContent>
                  </CustomCard>
                </div>
                
                <div className="lg:col-span-2">
                  <CustomCard>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-xl font-semibold">Strategy Details</CardTitle>
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
                          {tradesLoading ? (
                            <TableRow>
                              <TableCell colSpan={7} className="text-center">Loading trades...</TableCell>
                            </TableRow>
                          ) : trades?.map(trade => (
                            <TableRow key={trade.id}>
                              <TableCell className="font-medium">{trade.strategy || 'N/A'}</TableCell>
                              <TableCell>{trade.symbol}</TableCell>
                              <TableCell>{new Date(trade.created_at).toLocaleDateString()}</TableCell>
                              <TableCell>
                                <Badge variant={trade.status === 'executed' ? 'info' : 'secondary'}>
                                  {trade.status}
                                </Badge>
                              </TableCell>
                              <TableCell className={trade.pnl > 0 ? 'text-stockup' : 'text-stockdown'}>
                                {trade.pnl > 0 ? '+' : ''}₹{trade.pnl?.toLocaleString() || '0'}
                              </TableCell>
                              <TableCell className={trade.pnl > 0 ? 'text-stockup' : 'text-stockdown'}>
                                {trade.pnl > 0 ? '+' : ''}{((trade.pnl / (trade.price * trade.quantity)) * 100).toFixed(1)}%
                              </TableCell>
                              <TableCell>
                                {trade.status === 'executed' ? (
                                  <Button variant="outline" size="sm">Details</Button>
                                ) : (
                                  <Button variant="outline" size="sm">Cancel</Button>
                                )}
                              </TableCell>
                            </TableRow>
                          )) || []}
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
