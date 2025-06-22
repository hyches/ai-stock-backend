
import React, { useState } from 'react';
import AppLayout from '@/components/layout/AppLayout';
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

  const handleOptimize = () => {
    setIsLoading(true);
    
    // Simulating API call
    setTimeout(() => {
      setIsLoading(false);
      toast({
        title: "Portfolio Optimized",
        description: isDeepOptimize ? "Deep optimization complete" : "Quick optimization complete",
      });
    }, 2500);
  };

  const handleDownload = (type: string) => {
    setIsDownloading(true);
    
    // Simulating download
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
              <div className="p-4 border rounded-md">
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <h4 className="font-medium">AAPL (Apple Inc.)</h4>
                    <p className="text-xs text-muted-foreground">Technology</p>
                  </div>
                  <Badge variant="success"><TrendingUp className="mr-1 h-3 w-3" /> Increase</Badge>
                </div>
                <div className="flex items-center mb-2">
                  <span className="text-sm text-muted-foreground w-24">Current:</span>
                  <div className="flex-1 h-2 bg-gray-200 rounded-full">
                    <div className="h-2 bg-blue-500 rounded-full" style={{ width: '15%' }}></div>
                  </div>
                  <span className="text-sm ml-2">15%</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-muted-foreground w-24">Recommended:</span>
                  <div className="flex-1 h-2 bg-gray-200 rounded-full">
                    <div className="h-2 bg-green-500 rounded-full" style={{ width: '20%' }}></div>
                  </div>
                  <span className="text-sm ml-2">20%</span>
                </div>
              </div>
              
              <div className="p-4 border rounded-md">
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <h4 className="font-medium">MSFT (Microsoft Corp.)</h4>
                    <p className="text-xs text-muted-foreground">Technology</p>
                  </div>
                  <Badge variant="destructive"><TrendingUp className="mr-1 h-3 w-3 rotate-180" /> Decrease</Badge>
                </div>
                <div className="flex items-center mb-2">
                  <span className="text-sm text-muted-foreground w-24">Current:</span>
                  <div className="flex-1 h-2 bg-gray-200 rounded-full">
                    <div className="h-2 bg-blue-500 rounded-full" style={{ width: '25%' }}></div>
                  </div>
                  <span className="text-sm ml-2">25%</span>
                </div>
                <div className="flex items-center">
                  <span className="text-sm text-muted-foreground w-24">Recommended:</span>
                  <div className="flex-1 h-2 bg-gray-200 rounded-full">
                    <div className="h-2 bg-red-500 rounded-full" style={{ width: '20%' }}></div>
                  </div>
                  <span className="text-sm ml-2">20%</span>
                </div>
              </div>
              
              <div className="p-4 border rounded-md">
                <div className="flex justify-between items-center mb-2">
                  <div>
                    <h4 className="font-medium">New Recommendation</h4>
                    <p className="text-xs text-muted-foreground">Add to Portfolio</p>
                  </div>
                  <Badge variant="warning">New Addition</Badge>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-3">
                  <div className="p-3 border rounded-md">
                    <h5 className="text-sm font-medium">NVDA</h5>
                    <p className="text-xs text-muted-foreground">Nvidia Corp.</p>
                    <p className="text-sm font-medium mt-1">Allocation: 5%</p>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <h5 className="text-sm font-medium">GOOGL</h5>
                    <p className="text-xs text-muted-foreground">Alphabet Inc.</p>
                    <p className="text-sm font-medium mt-1">Allocation: 7%</p>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <h5 className="text-sm font-medium">AMZN</h5>
                    <p className="text-xs text-muted-foreground">Amazon.com Inc.</p>
                    <p className="text-sm font-medium mt-1">Allocation: 8%</p>
                  </div>
                </div>
              </div>
            </div>
          </Section>
        </div>
      </div>
    </AppLayout>
  );
};

export default Optimizer;
