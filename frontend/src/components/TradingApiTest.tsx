import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
// Trading API functions (placeholder for future implementation)
const tradingApi = {
  getOrders: () => Promise.resolve({ data: [] }),
  placeOrder: () => Promise.resolve({ data: { id: 1, status: 'pending' } }),
  cancelOrder: () => Promise.resolve({ data: { success: true } }),
};

const TradingApiTest = () => {
  const [testResults, setTestResults] = useState<{
    strategies: { status: string; message: string; data?: any };
    trades: { status: string; message: string; data?: any };
    positions: { status: string; message: string; data?: any };
  }>({
    strategies: { status: 'idle', message: '' },
    trades: { status: 'idle', message: '' },
    positions: { status: 'idle', message: '' }
  });

  const testStrategies = async () => {
    setTestResults(prev => ({
      ...prev,
      strategies: { status: 'testing', message: 'Testing strategies API...' }
    }));

    try {
      const response = await tradingApi.getStrategies();
      setTestResults(prev => ({
        ...prev,
        strategies: { 
          status: 'success', 
          message: `Found ${response.data.length} strategies`, 
          data: response.data 
        }
      }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        strategies: { 
          status: 'error', 
          message: `Failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
        }
      }));
    }
  };

  const testTrades = async () => {
    setTestResults(prev => ({
      ...prev,
      trades: { status: 'testing', message: 'Testing trades API...' }
    }));

    try {
      const response = await tradingApi.getTrades();
      setTestResults(prev => ({
        ...prev,
        trades: { 
          status: 'success', 
          message: `Found ${response.data.length} trades`, 
          data: response.data 
        }
      }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        trades: { 
          status: 'error', 
          message: `Failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
        }
      }));
    }
  };

  const testPositions = async () => {
    setTestResults(prev => ({
      ...prev,
      positions: { status: 'testing', message: 'Testing positions API...' }
    }));

    try {
      const response = await tradingApi.getPositions();
      setTestResults(prev => ({
        ...prev,
        positions: { 
          status: 'success', 
          message: `Found ${response.data.length} positions`, 
          data: response.data 
        }
      }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        positions: { 
          status: 'error', 
          message: `Failed: ${error instanceof Error ? error.message : 'Unknown error'}` 
        }
      }));
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-500';
      case 'error': return 'bg-red-500';
      case 'testing': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>Trading API Test</CardTitle>
        <CardDescription>Test backend connectivity for trading endpoints</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Button onClick={testStrategies} className="w-full">
              Test Strategies
            </Button>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(testResults.strategies.status)}`}></div>
              <span className="text-sm">{testResults.strategies.message}</span>
            </div>
          </div>

          <div className="space-y-2">
            <Button onClick={testTrades} className="w-full">
              Test Trades
            </Button>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(testResults.trades.status)}`}></div>
              <span className="text-sm">{testResults.trades.message}</span>
            </div>
          </div>

          <div className="space-y-2">
            <Button onClick={testPositions} className="w-full">
              Test Positions
            </Button>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(testResults.positions.status)}`}></div>
              <span className="text-sm">{testResults.positions.message}</span>
            </div>
          </div>
        </div>

        {testResults.strategies.data && (
          <div className="mt-4">
            <h4 className="font-semibold mb-2">Strategies Data:</h4>
            <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto">
              {JSON.stringify(testResults.strategies.data, null, 2)}
            </pre>
          </div>
        )}

        {testResults.trades.data && (
          <div className="mt-4">
            <h4 className="font-semibold mb-2">Trades Data:</h4>
            <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto">
              {JSON.stringify(testResults.trades.data, null, 2)}
            </pre>
          </div>
        )}

        {testResults.positions.data && (
          <div className="mt-4">
            <h4 className="font-semibold mb-2">Positions Data:</h4>
            <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto">
              {JSON.stringify(testResults.positions.data, null, 2)}
            </pre>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default TradingApiTest;
