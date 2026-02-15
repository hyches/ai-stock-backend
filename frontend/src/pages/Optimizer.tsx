
import React, { useState } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import apiClient, { api } from '@/lib/api-client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import Section from '@/components/ui/section';
import CustomCard from '@/components/ui/custom-card';
import FormGroup from '@/components/ui/form-group';
import { Download, FilePdf, FileSpreadsheet, Loader, TrendingUp, PieChart } from '@/utils/icons';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';

const Optimizer = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isDeepOptimize, setIsDeepOptimize] = useState(false);
  const { toast } = useToast();

  const [recommendations, setRecommendations] = useState<any[]>([]);

  const handleOptimize = async () => {
    setIsLoading(true);
    try {
      // Fetch real rebalancing plan from backend
      // Assuming portfolio ID 1 for now as per previous mocks
      const response = await api.trading.rebalance(1, {
        "AAPL": 0.2,
        "GOOGL": 0.2,
        "MSFT": 0.2,
        "NVDA": 0.2,
        "AMZN": 0.2
        // In a real app, these weights would come from the UI inputs
      });
      setRecommendations(response.data.suggested_actions);

      toast({
        title: "Portfolio Optimized",
        description: `Generated ${response.data.suggested_actions.length} rebalancing actions.`,
      });
    } catch (error) {
      console.error("Optimization failed:", error);
      toast({
        title: "Optimization Failed",
        description: "Could not fetch rebalancing plan from server.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = (type: string) => {
    setIsDownloading(true);

    // Simulating download (backend export not implemented yet)
    setTimeout(() => {
      setIsDownloading(false);
      toast({
        title: `${type} Download Started`,
        description: `Your ${type} file will be ready shortly.`,
      });
    }, 1500);
  };

  return (
    <AppLayout title="Portfolio Optimizer" description="Optimize your portfolio for maximum returns with minimal risk">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <CustomCard title="Optimization Parameters" description="Configure your optimization preferences">
            <div className="space-y-4">
              <FormGroup htmlFor="strategy" label="Optimization Strategy">
                <Select defaultValue="maxSharpe">
                  <SelectTrigger id="strategy">
                    <SelectValue placeholder="Select strategy" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="maxSharpe">Maximize Sharpe Ratio</SelectItem>
                    <SelectItem value="minRisk">Minimize Risk</SelectItem>
                    <SelectItem value="maxReturn">Maximize Return</SelectItem>
                    <SelectItem value="efficient">Efficient Frontier</SelectItem>
                  </SelectContent>
                </Select>
              </FormGroup>

              <FormGroup htmlFor="riskTolerance" label="Risk Tolerance">
                <Slider
                  id="riskTolerance"
                  defaultValue={[50]}
                  max={100}
                  step={1}
                  className="py-4"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>Conservative</span>
                  <span>Balanced</span>
                  <span>Aggressive</span>
                </div>
              </FormGroup>

              <FormGroup htmlFor="optimizationType" label="Optimization Type">
                <div className="flex items-center justify-between">
                  <span>Quick Optimize</span>
                  <Switch
                    id="optimizationType"
                    checked={isDeepOptimize}
                    onCheckedChange={setIsDeepOptimize}
                  />
                  <span>Deep Optimize</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {isDeepOptimize
                    ? "Deep optimization uses advanced algorithms and Monte Carlo simulations (slower but more accurate)"
                    : "Quick optimization provides rapid results using simplified models"}
                </p>
              </FormGroup>

              <FormGroup htmlFor="constraints" label="Additional Constraints">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label htmlFor="maxWeight" className="text-sm">Max Weight per Asset</label>
                    <Input id="maxWeight" type="number" defaultValue={20} className="w-20 h-8" min={1} max={100} />
                  </div>
                  <div className="flex items-center justify-between">
                    <label htmlFor="minWeight" className="text-sm">Min Weight per Asset</label>
                    <Input id="minWeight" type="number" defaultValue={5} className="w-20 h-8" min={0} max={50} />
                  </div>
                </div>
              </FormGroup>

              <Button
                className="w-full"
                disabled={isLoading}
                onClick={handleOptimize}
              >
                {isLoading ? (
                  <>
                    <Loader className="mr-2 h-4 w-4 animate-spin" />
                    Optimizing...
                  </>
                ) : (
                  <>
                    <PieChart className="mr-2 h-4 w-4" />
                    Optimize Portfolio
                  </>
                )}
              </Button>
            </div>
          </CustomCard>

          <CustomCard title="Download Results">
            <div className="space-y-3">
              <Button
                variant="outline"
                className="w-full justify-start"
                disabled={isDownloading}
                onClick={() => handleDownload('PDF')}
              >
                <FilePdf className="mr-2 h-4 w-4 text-red-500" />
                Download as PDF
              </Button>

              <Button
                variant="outline"
                className="w-full justify-start"
                disabled={isDownloading}
                onClick={() => handleDownload('Excel')}
              >
                <FileSpreadsheet className="mr-2 h-4 w-4 text-green-500" />
                Export to Excel
              </Button>
            </div>
          </CustomCard>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <CustomCard title="AI Portfolio Suggestions" description="Optimization results based on your preferences">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <h4 className="text-sm font-medium mb-2">Current Portfolio</h4>
                <div className="h-40 bg-gray-100 dark:bg-gray-800 rounded-md flex items-center justify-center">
                  <p className="text-muted-foreground">Current allocation chart</p>
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium mb-2">Optimized Portfolio</h4>
                <div className="h-40 bg-gray-100 dark:bg-gray-800 rounded-md flex items-center justify-center">
                  <p className="text-muted-foreground">Optimized allocation chart</p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Expected Return</span>
                <div className="flex items-center">
                  <Badge variant="success" className="mr-2">+12.5%</Badge>
                  <span className="text-green-500 text-xs">↑ 2.8%</span>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Portfolio Risk</span>
                <div className="flex items-center">
                  <Badge variant="success" className="mr-2">-15.2%</Badge>
                  <span className="text-green-500 text-xs">↓ 3.4%</span>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Sharpe Ratio</span>
                <div className="flex items-center">
                  <Badge className="mr-2">1.8</Badge>
                  <span className="text-green-500 text-xs">↑ 0.3</span>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Diversification Score</span>
                <div className="flex items-center">
                  <Badge variant="info" className="mr-2">85/100</Badge>
                  <span className="text-green-500 text-xs">↑ 12</span>
                </div>
              </div>
            </div>
          </CustomCard>

          <Section
            title="Recommended Portfolio Changes"
            description="Suggested actions to optimize your portfolio"
            columns={1}
          >
            <div className="space-y-4">
              {recommendations.length > 0 ? (
                recommendations.map((rec, index) => (
                  <div key={index} className="p-4 border rounded-md">
                    <div className="flex justify-between items-center mb-2">
                      <div>
                        <h4 className="font-medium">{rec.symbol}</h4>
                        <p className="text-xs text-muted-foreground">{rec.action === 'buy' ? 'Increase Position' : 'Reduce Position'}</p>
                      </div>
                      <Badge variant={rec.action === 'buy' ? 'success' : 'destructive'}>
                        {rec.action === 'buy' ? <TrendingUp className="mr-1 h-3 w-3" /> : <TrendingUp className="mr-1 h-3 w-3 rotate-180" />}
                        {rec.action.toUpperCase()}
                      </Badge>
                    </div>
                    <div className="flex items-center mb-2">
                      <span className="text-sm text-muted-foreground w-24">Quantity:</span>
                      <span className="text-sm ml-2 font-mono">{rec.quantity} shares</span>
                    </div>
                    <div className="flex items-center">
                      <span className="text-sm text-muted-foreground w-24">Est. Price:</span>
                      <span className="text-sm ml-2">₹{rec.current_price || rec.price}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center text-muted-foreground border border-dashed rounded-md">
                  Click "Optimize Portfolio" to see real-time AI recommendations.
                </div>
              )}
            </div>
          </Section>
        </div>
      </div>
    </AppLayout>
  );
};

export default Optimizer;
