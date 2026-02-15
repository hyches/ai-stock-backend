
import React, { useState } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import CustomCard from '@/components/ui/custom-card';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Download, FilePdf, FileSpreadsheet, FileText, Calendar, Loader } from '@/utils/icons';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import Section from '@/components/ui/section';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import FormGroup from '@/components/ui/form-group';

const mockReports = [
  {
    id: 1,
    name: 'Portfolio Performance Q2 2025',
    date: '2025-05-15',
    type: 'Performance',
    format: 'PDF',
  },
  {
    id: 2,
    name: 'Risk Analysis May 2025',
    date: '2025-05-10',
    type: 'Risk',
    format: 'EXCEL',
  },
  {
    id: 3,
    name: 'Stock Recommendations',
    date: '2025-05-01',
    type: 'Advisory',
    format: 'PDF',
  },
  {
    id: 4,
    name: 'Technical Analysis Report',
    date: '2025-04-28',
    type: 'Technical',
    format: 'WORD',
  },
  {
    id: 5,
    name: 'Sector Rotation Strategy',
    date: '2025-04-15',
    type: 'Strategy',
    format: 'PDF',
  }
];

const Reports = () => {
  const [selectedReportType, setSelectedReportType] = useState('all');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isExporting, setIsExporting] = useState<string | null>(null);
  const { toast } = useToast();

  const handleDownload = (reportId: number, format: string) => {
    setIsExporting(reportId.toString());
    // Simulate download
    setTimeout(() => {
      toast({
        title: "Download started",
        description: `Your ${format.toLowerCase()} file will be ready soon.`,
      });
      setIsExporting(null);
    }, 1500);
  };

  const handleGenerateReport = () => {
    setIsGenerating(true);
    // Simulate report generation
    setTimeout(() => {
      toast({
        title: "Report generated successfully",
        description: "Your custom report is ready to download.",
      });
      setIsGenerating(false);
    }, 2000);
  };

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'PDF':
        return <FilePdf className="h-4 w-4 text-red-500" />;
      case 'EXCEL':
        return <FileSpreadsheet className="h-4 w-4 text-green-500" />;
      case 'WORD':
        return <FileText className="h-4 w-4 text-blue-500" />;
      default:
        return <FileText className="h-4 w-4" />;
    }
  };

  return (
    <AppLayout title="Reports & Downloads" description="Access and generate reports on your portfolio and trading activities">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <CustomCard 
          title="Generate Custom Report" 
          description="Create a report with your preferred settings"
          className="lg:col-span-1"
        >
          <div className="space-y-4">
            <FormGroup htmlFor="reportType" label="Report Type">
              <Select value={selectedReportType} onValueChange={setSelectedReportType}>
                <SelectTrigger id="reportType">
                  <SelectValue placeholder="Select report type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Reports</SelectItem>
                  <SelectItem value="performance">Performance</SelectItem>
                  <SelectItem value="risk">Risk Analysis</SelectItem>
                  <SelectItem value="advisory">Stock Advisory</SelectItem>
                  <SelectItem value="technical">Technical Analysis</SelectItem>
                </SelectContent>
              </Select>
            </FormGroup>
            
            <FormGroup 
              htmlFor="dateRange" 
              label="Date Range" 
              tooltip="Select the period for your report data"
            >
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Input
                    id="startDate"
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                <div>
                  <Input
                    id="endDate"
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
              </div>
            </FormGroup>
            
            <FormGroup 
              htmlFor="format" 
              label="Format" 
              optional={true}
              hint="Default format is PDF"
            >
              <Select defaultValue="pdf">
                <SelectTrigger id="format">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pdf">PDF</SelectItem>
                  <SelectItem value="excel">Excel</SelectItem>
                  <SelectItem value="word">Word</SelectItem>
                </SelectContent>
              </Select>
            </FormGroup>
            
            <Button 
              className="w-full mt-4" 
              onClick={handleGenerateReport}
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <Loader className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <FileText className="mr-2 h-4 w-4" />
                  Generate Report
                </>
              )}
            </Button>
          </div>
        </CustomCard>
        
        <CustomCard 
          title="Available Downloads" 
          description="Documents and files ready for download"
          className="lg:col-span-2"
        >
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Report Name</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Format</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockReports.map((report) => (
                  <TableRow key={report.id}>
                    <TableCell className="font-medium">{report.name}</TableCell>
                    <TableCell>{report.date}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{report.type}</Badge>
                    </TableCell>
                    <TableCell className="flex items-center gap-1">
                      {getFormatIcon(report.format)}
                      <span>{report.format}</span>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownload(report.id, report.format)}
                        disabled={isExporting === report.id.toString()}
                      >
                        {isExporting === report.id.toString() ? (
                          <Loader className="h-4 w-4 animate-spin" />
                        ) : (
                          <Download className="h-4 w-4" />
                        )}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CustomCard>
      </div>
      
      <Section 
        title="Scheduled Reports" 
        description="Reports that are generated automatically"
        columns={3}
        action={
          <Button variant="outline" size="sm">
            <Calendar className="mr-2 h-4 w-4" />
            Add Schedule
          </Button>
        }
      >
        <CustomCard title="Weekly Performance" description="Generated every Monday at 8:00 AM">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Format:</span>
              <span className="text-sm flex items-center">
                <FilePdf className="h-4 w-4 text-red-500 mr-1" /> PDF
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Last Generated:</span>
              <span className="text-sm">May 20, 2025</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Recipients:</span>
              <span className="text-sm">3 users</span>
            </div>
            <div className="mt-4">
              <Button variant="outline" size="sm" className="w-full">
                <Download className="mr-2 h-4 w-4" />
                Download Latest
              </Button>
            </div>
          </div>
        </CustomCard>
        
        <CustomCard title="Monthly Portfolio Summary" description="Generated on the 1st of each month">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Format:</span>
              <span className="text-sm flex items-center">
                <FileSpreadsheet className="h-4 w-4 text-green-500 mr-1" /> Excel
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Last Generated:</span>
              <span className="text-sm">May 1, 2025</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Recipients:</span>
              <span className="text-sm">5 users</span>
            </div>
            <div className="mt-4">
              <Button variant="outline" size="sm" className="w-full">
                <Download className="mr-2 h-4 w-4" />
                Download Latest
              </Button>
            </div>
          </div>
        </CustomCard>
        
        <CustomCard title="Quarterly Tax Report" description="Generated at the end of each quarter">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Format:</span>
              <span className="text-sm flex items-center">
                <FileText className="h-4 w-4 text-blue-500 mr-1" /> Word
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Last Generated:</span>
              <span className="text-sm">Mar 31, 2025</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Recipients:</span>
              <span className="text-sm">2 users</span>
            </div>
            <div className="mt-4">
              <Button variant="outline" size="sm" className="w-full">
                <Download className="mr-2 h-4 w-4" />
                Download Latest
              </Button>
            </div>
          </div>
        </CustomCard>
      </Section>
    </AppLayout>
  );
};

export default Reports;
