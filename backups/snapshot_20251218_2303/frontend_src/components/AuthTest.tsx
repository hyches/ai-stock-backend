import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';

const AuthTest = () => {
  const [testResults, setTestResults] = useState<{
    token: { status: string; message: string };
    api: { status: string; message: string };
  }>({
    token: { status: 'idle', message: '' },
    api: { status: 'idle', message: '' }
  });

  const { user, isAuthenticated } = useAuth();

  const testToken = () => {
    const token = localStorage.getItem('access_token');
    const isAuth = localStorage.getItem('isAuthenticated');
    
    setTestResults(prev => ({
      ...prev,
      token: { 
        status: token ? 'success' : 'error', 
        message: token ? `Token found: ${token.substring(0, 20)}...` : 'No token found' 
      }
    }));
  };

  const testApiCall = async () => {
    setTestResults(prev => ({
      ...prev,
      api: { status: 'testing', message: 'Testing API call...' }
    }));

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/v1/trading/strategies/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTestResults(prev => ({
          ...prev,
          api: { 
            status: 'success', 
            message: `API call successful: ${data.length} strategies found` 
          }
        }));
      } else {
        setTestResults(prev => ({
          ...prev,
          api: { 
            status: 'error', 
            message: `API call failed: ${response.status} ${response.statusText}` 
          }
        }));
      }
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        api: { 
          status: 'error', 
          message: `Network error: ${error instanceof Error ? error.message : 'Unknown error'}` 
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
        <CardTitle>Authentication Test</CardTitle>
        <CardDescription>Test authentication token and API connectivity</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <p><strong>Auth Status:</strong> {isAuthenticated ? 'Authenticated' : 'Not Authenticated'}</p>
          <p><strong>User:</strong> {user ? JSON.stringify(user) : 'No user data'}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Button onClick={testToken} className="w-full">
              Test Token Storage
            </Button>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(testResults.token.status)}`}></div>
              <span className="text-sm">{testResults.token.message}</span>
            </div>
          </div>

          <div className="space-y-2">
            <Button onClick={testApiCall} className="w-full">
              Test API Call
            </Button>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor(testResults.api.status)}`}></div>
              <span className="text-sm">{testResults.api.message}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AuthTest;
