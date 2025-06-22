
import React, { useState } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
import { Download, Filter } from 'lucide-react';

const mockStocks = [
  { id: 1, symbol: 'AAPL', name: 'Apple Inc.', sector: 'Technology', marketCap: '2.45T', pe: 28.5, roe: 145.2, score: 92 },
  { id: 2, symbol: 'MSFT', name: 'Microsoft Corp.', sector: 'Technology', marketCap: '2.31T', pe: 32.1, roe: 43.8, score: 88 },
  { id: 3, symbol: 'GOOGL', name: 'Alphabet Inc.', sector: 'Technology', marketCap: '1.72T', pe: 25.4, roe: 28.6, score: 85 },
  { id: 4, symbol: 'AMZN', name: 'Amazon.com Inc.', sector: 'Consumer Cyclical', marketCap: '1.62T', pe: 58.7, roe: 24.3, score: 79 },
  { id: 5, symbol: 'TSLA', name: 'Tesla Inc.', sector: 'Automotive', marketCap: '615.2B', pe: 72.3, roe: 19.8, score: 73 },
];

const sectors = ['All', 'Technology', 'Healthcare', 'Financial', 'Consumer Cyclical', 'Energy', 'Automotive'];
const marketCaps = ['All', 'Mega (>$200B)', 'Large ($10-200B)', 'Mid ($2-10B)', 'Small ($300M-2B)', 'Micro (<$300M)'];

const Screener = () => {
  const [selectedSector, setSelectedSector] = useState('All');
  const [selectedMarketCap, setSelectedMarketCap] = useState('All');

  return (
    <AppLayout>
      <div className="flex flex-col gap-6">
        <div className="card-glass p-6 rounded-lg">
          <h1 className="text-2xl font-bold mb-2">Stock Screener</h1>
          <p className="text-muted-foreground mb-6">Find top-performing stocks based on custom criteria</p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-3">
              <Label htmlFor="sector">Sector</Label>
              <Select value={selectedSector} onValueChange={setSelectedSector}>
                <SelectTrigger>
                  <SelectValue placeholder="Select Sector" />
                </SelectTrigger>
                <SelectContent>
                  {sectors.map(sector => (
                    <SelectItem key={sector} value={sector}>{sector}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-3">
              <Label htmlFor="marketCap">Market Cap</Label>
              <Select value={selectedMarketCap} onValueChange={setSelectedMarketCap}>
                <SelectTrigger>
                  <SelectValue placeholder="Select Market Cap" />
                </SelectTrigger>
                <SelectContent>
                  {marketCaps.map(cap => (
                    <SelectItem key={cap} value={cap}>{cap}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-3">
              <Label htmlFor="minPE">Min P/E Ratio</Label>
              <Input id="minPE" type="number" placeholder="e.g., 10" />
            </div>
            
            <div className="space-y-3">
              <Label htmlFor="maxPE">Max P/E Ratio</Label>
              <Input id="maxPE" type="number" placeholder="e.g., 50" />
            </div>
            
            <div className="space-y-3">
              <Label htmlFor="minROE">Min ROE (%)</Label>
              <Input id="minROE" type="number" placeholder="e.g., 15" />
            </div>
            
            <div className="space-y-3 flex items-end">
              <Button className="w-full">
                <Filter className="mr-2 h-4 w-4" />
                Apply Filters
              </Button>
            </div>
          </div>
        </div>
        
        <div className="card-glass p-6 rounded-lg">
          <div className="flex justify-between mb-6">
            <h2 className="text-xl font-semibold">Results (5 stocks)</h2>
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          </div>
          
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Symbol</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Sector</TableHead>
                  <TableHead>Market Cap</TableHead>
                  <TableHead>P/E</TableHead>
                  <TableHead>ROE (%)</TableHead>
                  <TableHead>Score</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockStocks.map(stock => (
                  <TableRow key={stock.id}>
                    <TableCell className="font-medium">{stock.symbol}</TableCell>
                    <TableCell>{stock.name}</TableCell>
                    <TableCell>{stock.sector}</TableCell>
                    <TableCell>{stock.marketCap}</TableCell>
                    <TableCell>{stock.pe}</TableCell>
                    <TableCell>{stock.roe}</TableCell>
                    <TableCell>
                      <div className="bg-teal/20 text-teal px-2 py-1 rounded-full text-xs font-medium inline-block">
                        {stock.score}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default Screener;
