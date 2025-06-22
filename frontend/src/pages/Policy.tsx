
import React, { useState } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Download, FileText, Upload } from 'lucide-react';

const mockSectors = [
  { id: 1, sector: 'Renewable Energy', opportunity: 'High', stocks: ['NTPC', 'TATAPOWER', 'ADANIGREEN'] },
  { id: 2, sector: 'Electric Vehicles', opportunity: 'High', stocks: ['TATAMOTORS', 'M&M', 'HEROMOTOCO'] },
  { id: 3, sector: 'Semiconductor', opportunity: 'Medium', stocks: ['INFY', 'TCS', 'HCLTECH'] },
  { id: 4, sector: 'Healthcare', opportunity: 'Medium', stocks: ['SUNPHARMA', 'DRREDDY', 'CIPLA'] },
  { id: 5, sector: 'Manufacturing', opportunity: 'Low', stocks: ['LARSEN', 'BHEL', 'SIEMENS'] },
];

const Policy = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setFile(files[0]);
    }
  };
  
  const handleUpload = () => {
    if (!file) return;
    
    setUploading(true);
    // Mock API call
    setTimeout(() => {
      setUploading(false);
      // Analysis would come from API
    }, 1500);
  };

  return (
    <AppLayout>
      <div className="flex flex-col gap-6">
        <div className="card-glass p-6 rounded-lg">
          <h1 className="text-2xl font-bold mb-2">Policy Opportunity Detector</h1>
          <p className="text-muted-foreground mb-6">Upload policy documents to discover sector opportunities and relevant stocks</p>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle>Upload Document</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="border-2 border-dashed border-muted rounded-lg p-6 flex flex-col items-center justify-center">
                      <FileText className="h-8 w-8 text-muted-foreground mb-2" />
                      <p className="text-sm text-muted-foreground mb-2">Upload policy document, MoU, or budget paper</p>
                      <Input
                        id="file-upload"
                        type="file"
                        accept=".pdf,.doc,.docx"
                        className="hidden"
                        onChange={handleFileChange}
                      />
                      <Label
                        htmlFor="file-upload"
                        className="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2"
                      >
                        <Upload className="mr-2 h-4 w-4" />
                        Select File
                      </Label>
                    </div>
                    
                    {file && (
                      <div className="bg-navy-700 p-3 rounded-lg">
                        <div className="flex items-center">
                          <FileText className="h-5 w-5 text-teal mr-2" />
                          <div className="text-sm font-medium truncate">{file.name}</div>
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </div>
                      </div>
                    )}
                    
                    <Button
                      className="w-full"
                      disabled={!file || uploading}
                      onClick={handleUpload}
                    >
                      {uploading ? 'Analyzing...' : 'Analyze Document'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
              
              <Card className="mt-6">
                <CardHeader>
                  <CardTitle>Recent Uploads</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="bg-navy-700 p-3 rounded-lg flex items-center justify-between">
                      <div className="flex items-center">
                        <FileText className="h-4 w-4 text-teal mr-2" />
                        <div className="text-sm">Gujarat EV Policy 2025.pdf</div>
                      </div>
                      <div className="text-xs text-muted-foreground">2 days ago</div>
                    </div>
                    <div className="bg-navy-700 p-3 rounded-lg flex items-center justify-between">
                      <div className="flex items-center">
                        <FileText className="h-4 w-4 text-teal mr-2" />
                        <div className="text-sm">Union Budget 2025.pdf</div>
                      </div>
                      <div className="text-xs text-muted-foreground">5 days ago</div>
                    </div>
                    <div className="bg-navy-700 p-3 rounded-lg flex items-center justify-between">
                      <div className="flex items-center">
                        <FileText className="h-4 w-4 text-teal mr-2" />
                        <div className="text-sm">Karnataka Tech Policy.pdf</div>
                      </div>
                      <div className="text-xs text-muted-foreground">1 week ago</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            
            <div className="lg:col-span-2">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0">
                  <CardTitle>Analysis Results</CardTitle>
                  <Button variant="outline" size="sm">
                    <Download className="mr-2 h-4 w-4" />
                    Export Analysis
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-lg font-semibold mb-2">Policy Summary</h3>
                      <p className="text-muted-foreground">
                        This policy focuses on promoting electric vehicles and renewable energy infrastructure in Gujarat.
                        Key initiatives include tax benefits for EV manufacturers, charging infrastructure development,
                        and subsidies for renewable energy projects. The policy aims to attract ₹500 billion in investments
                        over the next five years.
                      </p>
                    </div>
                    
                    <div>
                      <h3 className="text-lg font-semibold mb-2">Sector Opportunities</h3>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Sector</TableHead>
                            <TableHead>Opportunity</TableHead>
                            <TableHead>Relevant Stocks</TableHead>
                            <TableHead>Action</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {mockSectors.map(sector => (
                            <TableRow key={sector.id}>
                              <TableCell className="font-medium">{sector.sector}</TableCell>
                              <TableCell>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  sector.opportunity === 'High' ? 'bg-stockup/20 text-stockup' :
                                  sector.opportunity === 'Medium' ? 'bg-amber-400/20 text-amber-400' :
                                  'bg-stockdown/20 text-stockdown'
                                }`}>
                                  {sector.opportunity}
                                </span>
                              </TableCell>
                              <TableCell>{sector.stocks.join(', ')}</TableCell>
                              <TableCell>
                                <Button variant="outline" size="sm">View Details</Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                    
                    <div className="bg-navy-700 p-4 rounded-lg">
                      <h3 className="text-lg font-semibold mb-2">Key Insights</h3>
                      <ul className="space-y-2 list-disc pl-5">
                        <li>EV adoption expected to grow by 35% annually through 2030</li>
                        <li>Renewable energy capacity to increase by 15 GW in the next 5 years</li>
                        <li>Battery manufacturing and charging infrastructure are high-growth areas</li>
                        <li>Public-private partnerships emphasized for implementation</li>
                        <li>Focus on local manufacturing with 'Make in India' incentives</li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default Policy;
