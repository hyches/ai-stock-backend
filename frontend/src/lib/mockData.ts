// Minimal mock data for testing - Live data comes from Yahoo Finance service

export interface OptionData {
  strikePrice: number;
  callOI: number;
  callOIChange: number;
  callLTP: number;
  callIV: number;
  putOI: number;
  putOIChange: number;
  putLTP: number;
  putIV: number;
}

// Generate option chain data for any symbol
export const generateOptionChain = (spotPrice: number): OptionData[] => {
  const strikes: OptionData[] = [];
  const baseStrike = Math.round(spotPrice / 50) * 50;
  
  for (let i = -10; i <= 10; i++) {
    const strike = baseStrike + i * 50;
    const distance = Math.abs(spotPrice - strike);
    const moneyness = distance / spotPrice;
    
    strikes.push({
      strikePrice: strike,
      callOI: Math.round(Math.random() * 500000 + 100000),
      callOIChange: Math.round((Math.random() - 0.5) * 50000),
      callLTP: Math.max(5, strike < spotPrice ? spotPrice - strike + Math.random() * 50 : Math.random() * 100 * Math.exp(-moneyness * 10)),
      callIV: 12 + Math.random() * 8 + moneyness * 20,
      putOI: Math.round(Math.random() * 500000 + 100000),
      putOIChange: Math.round((Math.random() - 0.5) * 50000),
      putLTP: Math.max(5, strike > spotPrice ? strike - spotPrice + Math.random() * 50 : Math.random() * 100 * Math.exp(-moneyness * 10)),
      putIV: 12 + Math.random() * 8 + moneyness * 20,
    });
  }
  
  return strikes;
};