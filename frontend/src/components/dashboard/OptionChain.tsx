import React, { useState, useMemo } from 'react';
import { generateOptionChain, OptionData } from '@/lib/mockData';
import { useTrading } from '@/context/TradingContext';
import { cn } from '@/lib/utils';
import { ChevronDown } from 'lucide-react';

const formatNumber = (value: number, decimals: number = 2) => {
  if (value >= 100000) {
    return `${(value / 100000).toFixed(2)}L`;
  }
  return value.toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

interface OptionRowProps {
  data: OptionData;
  spotPrice: number;
  onSelectCall?: () => void;
  onSelectPut?: () => void;
}

const OptionRow: React.FC<OptionRowProps> = ({ data, spotPrice, onSelectCall, onSelectPut }) => {
  const isITM = {
    call: data.strikePrice < spotPrice,
    put: data.strikePrice > spotPrice,
  };
  const isATM = Math.abs(data.strikePrice - spotPrice) < 25;

  return (
    <div className={cn(
      'grid grid-cols-9 gap-2 py-2.5 px-3 text-xs font-mono hover:bg-accent/30 transition-colors rounded-lg group',
      isATM && 'bg-primary/5 border border-primary/20'
    )}>
      <div className={cn('cursor-pointer hover:text-emerald-400', isITM.call && 'text-emerald-400/80')} onClick={onSelectCall}>
        {formatNumber(data.callOI, 0)}
      </div>
      <div className={cn(data.callOIChange >= 0 ? 'text-emerald-400' : 'text-rose-400')}>
        {data.callOIChange >= 0 ? '+' : ''}{formatNumber(data.callOIChange, 0)}
      </div>
      <div>{data.callIV.toFixed(1)}%</div>
      <div className={cn('font-semibold cursor-pointer hover:text-primary', isITM.call && 'text-emerald-400')} onClick={onSelectCall}>
        ₹{formatNumber(data.callLTP)}
      </div>
      <div className={cn('text-center font-semibold', isATM && 'text-primary')}>
        {data.strikePrice}
        {isATM && <span className="text-[10px] ml-1 text-primary">ATM</span>}
      </div>
      <div className={cn('font-semibold cursor-pointer hover:text-primary', isITM.put && 'text-rose-400')} onClick={onSelectPut}>
        ₹{formatNumber(data.putLTP)}
      </div>
      <div>{data.putIV.toFixed(1)}%</div>
      <div className={cn(data.putOIChange >= 0 ? 'text-emerald-400' : 'text-rose-400')}>
        {data.putOIChange >= 0 ? '+' : ''}{formatNumber(data.putOIChange, 0)}
      </div>
      <div className={cn('cursor-pointer hover:text-rose-400', isITM.put && 'text-rose-400/80')} onClick={onSelectPut}>
        {formatNumber(data.putOI, 0)}
      </div>
    </div>
  );
};

interface OptionChainProps {
  symbol?: string;
  onSelectOption?: (type: 'CE' | 'PE', strike: number) => void;
}

export const OptionChain: React.FC<OptionChainProps> = ({ symbol = 'NIFTY', onSelectOption }) => {
  const { quotes } = useTrading();
  const [selectedExpiry, setSelectedExpiry] = useState('26-DEC-24');

  const quote = quotes.get(symbol);
  const spotPrice = quote?.regularMarketPrice || 24850.50;

  const optionChainData = useMemo(() => generateOptionChain(spotPrice), [spotPrice]);
  const expiries = ['26-DEC-24', '02-JAN-25', '09-JAN-25', '30-JAN-25'];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">{symbol} Option Chain</h2>
          <p className="text-sm text-muted-foreground">
            Spot: <span className="text-foreground font-mono">₹{formatNumber(spotPrice)}</span>
          </p>
        </div>
        <div className="relative">
          <select value={selectedExpiry} onChange={(e) => setSelectedExpiry(e.target.value)} className="glass-button appearance-none pr-8 cursor-pointer text-sm">
            {expiries.map(exp => (<option key={exp} value={exp} className="bg-card">{exp}</option>))}
          </select>
          <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-muted-foreground" />
        </div>
      </div>
      <div className="glass-card p-0 overflow-hidden">
        <div className="grid grid-cols-9 gap-2 py-3 px-3 text-xs font-medium text-muted-foreground border-b border-border/50 bg-muted/30">
          <div>OI</div><div>Chng</div><div>IV</div><div className="text-emerald-400">CALL</div>
          <div className="text-center">STRIKE</div><div className="text-rose-400">PUT</div><div>IV</div><div>Chng</div><div>OI</div>
        </div>
        <div className="max-h-[400px] overflow-y-auto">
          {optionChainData.map((row) => (
            <OptionRow key={row.strikePrice} data={row} spotPrice={spotPrice}
              onSelectCall={() => onSelectOption?.('CE', row.strikePrice)}
              onSelectPut={() => onSelectOption?.('PE', row.strikePrice)} />
          ))}
        </div>
        <div className="grid grid-cols-2 gap-4 p-4 border-t border-border/50 bg-muted/20">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">Total Call OI</p>
            <p className="font-mono font-semibold text-emerald-400">{formatNumber(optionChainData.reduce((acc, row) => acc + row.callOI, 0), 0)}</p>
          </div>
          <div className="space-y-1 text-right">
            <p className="text-xs text-muted-foreground">Total Put OI</p>
            <p className="font-mono font-semibold text-rose-400">{formatNumber(optionChainData.reduce((acc, row) => acc + row.putOI, 0), 0)}</p>
          </div>
        </div>
      </div>
    </div>
  );
};