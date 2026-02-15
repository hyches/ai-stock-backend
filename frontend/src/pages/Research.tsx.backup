
import React, { useState } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Section from '@/components/ui/section';
import CustomCard from '@/components/ui/custom-card';
import FormGroup from '@/components/ui/form-group';
import { Download, FilePdf, FileText, FileSpreadsheet, Loader, TrendingUp, TrendingDown } from '@/utils/icons';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const Research = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isFullAnalysis, setIsFullAnalysis] = useState(false);
  const { toast } = useToast();

  const handleGenerateAnalysis = () => {
    setIsLoading(true);
    
    // Simulating API call
    setTimeout(() => {
      setIsLoading(false);
      toast({
        title: "Analysis Generated",
        description: isFullAnalysis ? "Full AI analysis complete" : "Quick AI analysis complete",
      });
    }, 2000);
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
    <AppLayout title="AI Research Reports" description="Get AI-generated insights and analysis on stocks">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <CustomCard title="Research Parameters" description="Configure AI analysis settings">
            <div className="space-y-4">
              <FormGroup htmlFor="stock" label="Stock Symbol">
                <Input id="stock" placeholder="e.g. AAPL, MSFT, GOOGL" />
              </FormGroup>
              
              <FormGroup htmlFor="timeframe" label="Analysis Timeframe">
                <Select defaultValue="3months">
                  <SelectTrigger id="timeframe">
                    <SelectValue placeholder="Select timeframe" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1month">1 Month</SelectItem>
                    <SelectItem value="3months">3 Months</SelectItem>
                    <SelectItem value="6months">6 Months</SelectItem>
                    <SelectItem value="1year">1 Year</SelectItem>
                    <SelectItem value="3years">3 Years</SelectItem>
                  </SelectContent>
                </Select>
              </FormGroup>
              
              <FormGroup htmlFor="depth" label="Analysis Depth">
                <div className="flex items-center justify-between">
                  <span>Quick Analysis</span>
                  <Switch 
                    id="depth"
                    checked={isFullAnalysis} 
                    onCheckedChange={setIsFullAnalysis}
                  />
                  <span>Full Analysis</span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {isFullAnalysis 
                    ? "Comprehensive analysis including fundamentals, technicals, and sentiment." 
                    : "Basic overview with key metrics and recommendations."}
                </p>
              </FormGroup>
              
              <FormGroup htmlFor="factors" label="Include Factors">
                <div className="grid grid-cols-2 gap-2">
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="technical" className="rounded text-teal" defaultChecked />
                    <label htmlFor="technical" className="text-sm">Technical</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="fundamental" className="rounded text-teal" defaultChecked />
                    <label htmlFor="fundamental" className="text-sm">Fundamental</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="sentiment" className="rounded text-teal" defaultChecked />
                    <label htmlFor="sentiment" className="text-sm">Sentiment</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" id="news" className="rounded text-teal" defaultChecked />
                    <label htmlFor="news" className="text-sm">News</label>
                  </div>
                </div>
              </FormGroup>
              
              <Button 
                className="w-full" 
                disabled={isLoading}
                onClick={handleGenerateAnalysis}
              >
                {isLoading ? (
                  <>
                    <Loader className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  'Generate Analysis'
                )}
              </Button>
            </div>
          </CustomCard>
          
          <CustomCard title="Download Reports" className="mt-6">
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
              
              <Button 
                variant="outline" 
                className="w-full justify-start"
                disabled={isDownloading}
                onClick={() => handleDownload('Word')}
              >
                <FileText className="mr-2 h-4 w-4 text-blue-500" />
                Export to Word
              </Button>
            </div>
          </CustomCard>
        </div>
        
        <div className="lg:col-span-2">
          <Tabs defaultValue="summary">
            <TabsList className="mb-4">
              <TabsTrigger value="summary">Summary</TabsTrigger>
              <TabsTrigger value="technical">Technical</TabsTrigger>
              <TabsTrigger value="fundamental">Fundamental</TabsTrigger>
              <TabsTrigger value="news">News & Sentiment</TabsTrigger>
            </TabsList>
            
            <TabsContent value="summary" className="space-y-6">
              <CustomCard 
                title="AI-Generated Stock Summary" 
                description="Key insights and recommendations generated by AI"
              >
                <div className="p-4 bg-teal/5 border border-teal/20 rounded-md">
                  <div className="flex justify-between items-center mb-4">
                    <div>
                      <h3 className="text-xl font-bold">AAPL</h3>
                      <p className="text-sm text-muted-foreground">Apple Inc.</p>
                    </div>
                    <Badge variant={Math.random() > 0.5 ? "success" : "destructive"}>
                      {Math.random() > 0.5 ? (
                        <><TrendingUp className="mr-1 h-3 w-3" /> Buy</>
                      ) : (
                        <><TrendingDown className="mr-1 h-3 w-3" /> Sell</>
                      )}
                    </Badge>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-sm text-muted-foreground mb-1">Key Insights</h4>
                      <p className="text-sm">
                        Apple shows strong technical momentum with an uptrend above the 50-day moving average. 
                        Recent product launches have been well-received, contributing to positive sentiment. 
                        The company's revenue growth remains steady at 8% YoY, though slightly below analyst expectations of 10%.
                      </p>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-sm text-muted-foreground mb-1">Risk Assessment</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Volatility</p>
                          <div className="h-2 w-full bg-gray-200 rounded-full">
                            <div className="h-2 bg-amber-500 rounded-full" style={{ width: '40%' }}></div>
                          </div>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground mb-1">Market Risk</p>
                          <div className="h-2 w-full bg-gray-200 rounded-full">
                            <div className="h-2 bg-red-500 rounded-full" style={{ width: '65%' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-sm text-muted-foreground mb-1">AI Recommendation</h4>
                      <p className="text-sm">
                        Based on technical analysis, fundamental factors, and market sentiment, 
                        our AI model suggests a <span className="font-bold text-green-500">MODERATE BUY</span> with 
                        a 12-month price target of $220-$245. Consider dollar-cost averaging into the position 
                        and set a stop-loss at $175 to manage downside risk.
                      </p>
                    </div>
                  </div>
                </div>
              </CustomCard>
              
              <CustomCard title="Key Performance Indicators">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">Price to Earnings</p>
                    <p className="text-xl font-semibold">28.5</p>
                    <div className="flex items-center text-xs text-green-500 mt-1">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      <span>4.2% vs Industry</span>
                    </div>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">Revenue Growth</p>
                    <p className="text-xl font-semibold">8.3%</p>
                    <div className="flex items-center text-xs text-red-500 mt-1">
                      <TrendingDown className="h-3 w-3 mr-1" />
                      <span>1.7% below forecast</span>
                    </div>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <p className="text-xs text-muted-foreground">Profit Margin</p>
                    <p className="text-xl font-semibold">21.7%</p>
                    <div className="flex items-center text-xs text-green-500 mt-1">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      <span>2.3% vs Previous Quarter</span>
                    </div>
                  </div>
                </div>
              </CustomCard>
            </TabsContent>
            
            <TabsContent value="technical">
              <CustomCard title="Technical Analysis">
                <p className="text-muted-foreground mb-4">Technical indicators and chart patterns</p>
                <div className="h-64 bg-gray-100 dark:bg-gray-800 rounded-md flex items-center justify-center">
                  <p className="text-muted-foreground">Technical chart placeholder</p>
                </div>
              </CustomCard>
            </TabsContent>
            
            <TabsContent value="fundamental">
              <CustomCard title="Fundamental Analysis">
                <p className="text-muted-foreground mb-4">Financial metrics and company fundamentals</p>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Metric</TableHead>
                      <TableHead>Value</TableHead>
                      <TableHead>vs Industry</TableHead>
                      <TableHead>Signal</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell>EPS</TableCell>
                      <TableCell>$6.42</TableCell>
                      <TableCell>+15%</TableCell>
                      <TableCell>
                        <Badge variant="success">Strong</Badge>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>P/E Ratio</TableCell>
                      <TableCell>28.5</TableCell>
                      <TableCell>+5%</TableCell>
                      <TableCell>
                        <Badge variant="warning">Fair</Badge>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Debt/Equity</TableCell>
                      <TableCell>1.2</TableCell>
                      <TableCell>-10%</TableCell>
                      <TableCell>
                        <Badge variant="success">Strong</Badge>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>ROE</TableCell>
                      <TableCell>32.1%</TableCell>
                      <TableCell>+25%</TableCell>
                      <TableCell>
                        <Badge variant="success">Strong</Badge>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </CustomCard>
            </TabsContent>
            
            <TabsContent value="news">
              <CustomCard title="News & Sentiment Analysis">
                <p className="text-muted-foreground mb-4">Market sentiment and recent news impact</p>
                <div className="space-y-4">
                  <div className="p-3 border rounded-md">
                    <div className="flex justify-between">
                      <h4 className="font-medium">Quarterly Earnings Report</h4>
                      <Badge>Positive</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      Apple reported earnings above analyst expectations, with services revenue showing strong growth.
                    </p>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <div className="flex justify-between">
                      <h4 className="font-medium">Product Launch Event</h4>
                      <Badge>Neutral</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      The latest iPhone iteration received mixed reviews with analysts concerned about incremental upgrades.
                    </p>
                  </div>
                  
                  <div className="p-3 border rounded-md">
                    <div className="flex justify-between">
                      <h4 className="font-medium">Supply Chain Report</h4>
                      <Badge variant="destructive">Negative</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      Reports indicate potential supply constraints for key components in Q3, potentially impacting production.
                    </p>
                  </div>
                </div>
              </CustomCard>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </AppLayout>
  );
};

export default Research;
