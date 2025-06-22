import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const ApiTest = () => {
  const [testResults, setTestResults] = useState<{
    backend: { status: string; message: string; timestamp: string };
    api: { status: string; message: string; timestamp: string };
  }>({
    backend: { status: 'idle', message: '', timestamp: '' },
    api: { status: 'idle', message: '', timestamp: '' }
  });

  const testBackendConnection = async () => {
    setTestResults(prev => ({
      ...prev,
      backend: { status: 'testing', message: 'Testing...', timestamp: new Date().toLocaleTimeString() }
    }));

    try {
      // Test direct backend connection
      const response = await fetch('http://localhost:8000/docs');
      if (response.ok) {
        setTestResults(prev => ({
          ...prev,
          backend: { 
            status: 'success', 
            message: `Backend is running! Status: ${response.status}`, 
            timestamp: new Date().toLocaleTimeString() 
          }
        }));
      } else {
        setTestResults(prev => ({
          ...prev,
          backend: { 
            status: 'error', 
            message: `Backend responded with status: ${response.status}`, 
            timestamp: new Date().toLocaleTimeString() 
          }
        }));
      }
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        backend: { 
          status: 'error', 
          message: `Failed to connect: ${error instanceof Error ? error.message : 'Unknown error'}`, 
          timestamp: new Date().toLocaleTimeString() 
        }
      }));
    }
  };

  const testApiProxy = async () => {
    setTestResults(prev => ({
      ...prev,
      api: { status: 'testing', message: 'Testing...', timestamp: new Date().toLocaleTimeString() }
    }));

    try {
      // Test API proxy (this should go through Vite proxy)
      const response = await fetch('/api/v1/portfolio');
      if (response.ok) {
        setTestResults(prev => ({
          ...prev,
          api: { 
            status: 'success', 
            message: `API proxy working! Status: ${response.status}`, 
            timestamp: new Date().toLocaleTimeString() 
          }
        }));
      } else {
        setTestResults(prev => ({
          ...prev,
          api: { 
            status: 'error', 
            message: `API proxy responded with status: ${response.status}`, 
            timestamp: new Date().toLocaleTimeString() 
          }
        }));
      }
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        api: { 
          status: 'error', 
          message: `API proxy failed: ${error instanceof Error ? error.message : 'Unknown error'}`, 
          timestamp: new Date().toLocaleTimeString() 
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
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Backend Connection Test</CardTitle>
        <CardDescription>
          Test the connection between frontend and backend
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Direct Backend</h3>
              <Badge className={getStatusColor(testResults.backend.status)}>
                {testResults.backend.status}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              {testResults.backend.message || 'Test direct connection to backend'}
            </p>
            {testResults.backend.timestamp && (
              <p className="text-xs text-muted-foreground">
                Tested at: {testResults.backend.timestamp}
              </p>
            )}
            <Button onClick={testBackendConnection} variant="outline" size="sm">
              Test Backend
            </Button>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">API Proxy</h3>
              <Badge className={getStatusColor(testResults.api.status)}>
                {testResults.api.status}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              {testResults.api.message || 'Test API proxy through Vite'}
            </p>
            {testResults.api.timestamp && (
              <p className="text-xs text-muted-foreground">
                Tested at: {testResults.api.timestamp}
              </p>
            )}
            <Button onClick={testApiProxy} variant="outline" size="sm">
              Test API Proxy
            </Button>
          </div>
        </div>

        <div className="mt-6 p-4 bg-muted rounded-lg">
          <h4 className="font-semibold mb-2">Connection Info:</h4>
          <ul className="text-sm space-y-1">
            <li>• <strong>Backend URL:</strong> http://localhost:8000</li>
            <li>• <strong>Frontend URL:</strong> http://localhost:8083</li>
            <li>• <strong>API Proxy:</strong> /api → http://localhost:8000</li>
            <li>• <strong>Status:</strong> {testResults.backend.status === 'success' ? '✅ Connected' : '❌ Not Connected'}</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
};

export default ApiTest; 