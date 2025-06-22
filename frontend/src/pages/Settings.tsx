import React from 'react';
import AppLayout from '@/components/layout/AppLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { 
  Bell, 
  CreditCard, 
  Download, 
  Lock, 
  Mail, 
  MessageSquare, 
  Phone, 
  Shield, 
  User 
} from 'lucide-react';

const Settings = () => {
  return (
    <AppLayout>
      <div className="card-glass p-6 rounded-lg">
        <h1 className="text-2xl font-bold mb-2">Settings</h1>
        <p className="text-muted-foreground mb-6">Manage your account preferences and platform settings</p>
        
        <Tabs defaultValue="profile" className="w-full">
          <TabsList className="grid grid-cols-5 mb-6">
            <TabsTrigger value="profile">Profile</TabsTrigger>
            <TabsTrigger value="notifications">Notifications</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="billing">Billing</TabsTrigger>
            <TabsTrigger value="api">API</TabsTrigger>
          </TabsList>
          
          <TabsContent value="profile">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Personal Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    <Input id="name" placeholder="John Doe" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input id="email" type="email" placeholder="john@example.com" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input id="phone" placeholder="+1 (555) 123-4567" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="dob">Date of Birth</Label>
                    <Input id="dob" type="date" />
                  </div>
                </div>
              </div>
              
              <Separator />
              
              <div>
                <h3 className="text-lg font-semibold mb-4">Trading Preferences</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="risk-profile">Risk Profile</Label>
                    <Select defaultValue="moderate">
                      <SelectTrigger id="risk-profile">
                        <SelectValue placeholder="Select your risk profile" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="conservative">Conservative</SelectItem>
                        <SelectItem value="moderate">Moderate</SelectItem>
                        <SelectItem value="aggressive">Aggressive</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="investment-horizon">Investment Horizon</Label>
                    <Select defaultValue="medium">
                      <SelectTrigger id="investment-horizon">
                        <SelectValue placeholder="Select your investment horizon" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="short">Short Term (&lt; 1 year)</SelectItem>
                        <SelectItem value="medium">Medium Term (1-5 years)</SelectItem>
                        <SelectItem value="long">Long Term (&gt; 5 years)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="preferred-sectors">Preferred Sectors</Label>
                    <Select>
                      <SelectTrigger id="preferred-sectors">
                        <SelectValue placeholder="Select preferred sectors" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="technology">Technology</SelectItem>
                        <SelectItem value="finance">Finance</SelectItem>
                        <SelectItem value="healthcare">Healthcare</SelectItem>
                        <SelectItem value="energy">Energy</SelectItem>
                        <SelectItem value="consumer">Consumer</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="investment-amount">Typical Investment Amount</Label>
                    <Input id="investment-amount" placeholder="e.g., 100000" />
                  </div>
                </div>
              </div>
              
              <Separator />
              
              <div className="flex justify-end">
                <Button>Save Changes</Button>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="notifications">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Notification Preferences</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Bell className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">Price Alerts</p>
                        <p className="text-xs text-muted-foreground">Receive notifications when stocks reach your price targets</p>
                      </div>
                    </div>
                    <Switch />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <MessageSquare className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">AI Research Reports</p>
                        <p className="text-xs text-muted-foreground">Get notified when new research reports are available</p>
                      </div>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Mail className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">Email Digests</p>
                        <p className="text-xs text-muted-foreground">Weekly summary of market moves and portfolio performance</p>
                      </div>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Phone className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">SMS Alerts</p>
                        <p className="text-xs text-muted-foreground">Critical alerts via SMS for high-priority notifications</p>
                      </div>
                    </div>
                    <Switch />
                  </div>
                </div>
              </div>
              
              <Separator />
              
              <div>
                <h3 className="text-lg font-semibold mb-4">Telegram Integration</h3>
                <p className="text-sm text-muted-foreground mb-4">Connect your Telegram account to receive real-time alerts and signals</p>
                <Button variant="outline">
                  Connect Telegram
                </Button>
              </div>
              
              <Separator />
              
              <div className="flex justify-end">
                <Button>Save Preferences</Button>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="security">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Account Security</h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="current-password">Current Password</Label>
                      <Input id="current-password" type="password" />
                    </div>
                    <div></div>
                    <div className="space-y-2">
                      <Label htmlFor="new-password">New Password</Label>
                      <Input id="new-password" type="password" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="confirm-password">Confirm New Password</Label>
                      <Input id="confirm-password" type="password" />
                    </div>
                  </div>
                  
                  <Button className="mt-2">
                    <Lock className="mr-2 h-4 w-4" />
                    Update Password
                  </Button>
                </div>
              </div>
              
              <Separator />
              
              <div>
                <h3 className="text-lg font-semibold mb-4">Two-Factor Authentication</h3>
                <p className="text-sm text-muted-foreground mb-4">Add an extra layer of security to your account</p>
                <div className="flex items-center space-x-2 mb-4">
                  <Switch id="2fa" />
                  <Label htmlFor="2fa">Enable Two-Factor Authentication</Label>
                </div>
                <Button variant="outline" disabled>
                  <Shield className="mr-2 h-4 w-4" />
                  Set Up 2FA
                </Button>
              </div>
              
              <Separator />
              
              <div>
                <h3 className="text-lg font-semibold mb-4">Sessions</h3>
                <div className="space-y-4">
                  <div className="bg-navy-700 p-4 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium">Current Session</p>
                        <p className="text-xs text-muted-foreground">Windows 11 • Chrome • Mumbai, India</p>
                      </div>
                      <span className="px-2 py-1 bg-teal/20 text-teal text-xs rounded-full">Active</span>
                    </div>
                  </div>
                  
                  <div className="bg-navy-700 p-4 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium">Mobile App</p>
                        <p className="text-xs text-muted-foreground">iPhone 15 • iOS 18 • Mumbai, India</p>
                      </div>
                      <Button variant="ghost" size="sm">Sign Out</Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="billing">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Subscription</h3>
                <div className="bg-navy-700 p-6 rounded-lg mb-6">
                  <div className="flex justify-between items-center mb-4">
                    <div>
                      <p className="text-lg font-bold">Pro Plan</p>
                      <p className="text-sm text-muted-foreground">Billed annually</p>
                    </div>
                    <div className="bg-teal/20 text-teal px-3 py-1 rounded-full text-xs font-medium">
                      Active
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Next billing date</p>
                      <p className="font-medium">June 15, 2025</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Amount</p>
                      <p className="font-medium">₹12,999/year</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline">Change Plan</Button>
                    <Button variant="outline" className="text-stockdown">Cancel</Button>
                  </div>
                </div>
                
                <h3 className="text-lg font-semibold mb-4">Payment Method</h3>
                <div className="bg-navy-700 p-4 rounded-lg flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <CreditCard className="h-5 w-5 text-muted-foreground mr-2" />
                    <div>
                      <p className="text-sm font-medium">VISA ending in 4242</p>
                      <p className="text-xs text-muted-foreground">Expires 04/27</p>
                    </div>
                  </div>
                  <div className="bg-secondary px-2 py-1 rounded text-xs">Default</div>
                </div>
                <Button variant="outline">
                  Add Payment Method
                </Button>
              </div>
              
              <Separator />
              
              <div>
                <h3 className="text-lg font-semibold mb-4">Billing History</h3>
                <div className="bg-navy-700 rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead>
                      <tr>
                        <th className="text-left p-4 text-sm font-medium">Date</th>
                        <th className="text-left p-4 text-sm font-medium">Description</th>
                        <th className="text-left p-4 text-sm font-medium">Amount</th>
                        <th className="text-left p-4 text-sm font-medium">Invoice</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-t border-white/10">
                        <td className="p-4 text-sm">Jun 15, 2024</td>
                        <td className="p-4 text-sm">Pro Plan - Annual</td>
                        <td className="p-4 text-sm">₹12,999</td>
                        <td className="p-4 text-sm">
                          <Button variant="ghost" size="sm">
                            <Download className="h-4 w-4 mr-1" />
                            PDF
                          </Button>
                        </td>
                      </tr>
                      <tr className="border-t border-white/10">
                        <td className="p-4 text-sm">Jun 15, 2023</td>
                        <td className="p-4 text-sm">Pro Plan - Annual</td>
                        <td className="p-4 text-sm">₹11,999</td>
                        <td className="p-4 text-sm">
                          <Button variant="ghost" size="sm">
                            <Download className="h-4 w-4 mr-1" />
                            PDF
                          </Button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="api">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">API Keys</h3>
                <p className="text-sm text-muted-foreground mb-4">Manage your API keys to integrate with our platform</p>
                
                <div className="bg-navy-700 p-4 rounded-lg flex items-center justify-between mb-4">
                  <div>
                    <p className="text-sm font-medium">Production API Key</p>
                    <p className="text-xs text-muted-foreground">Created on April 10, 2025</p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">Reveal</Button>
                    <Button variant="outline" size="sm" className="text-stockdown">Revoke</Button>
                  </div>
                </div>
                
                <div className="bg-navy-700 p-4 rounded-lg flex items-center justify-between mb-4">
                  <div>
                    <p className="text-sm font-medium">Test API Key</p>
                    <p className="text-xs text-muted-foreground">Created on May 5, 2025</p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">Reveal</Button>
                    <Button variant="outline" size="sm" className="text-stockdown">Revoke</Button>
                  </div>
                </div>
                
                <Button variant="outline">
                  Generate New API Key
                </Button>
              </div>
              
              <Separator />
              
              <div>
                <h3 className="text-lg font-semibold mb-4">Webhooks</h3>
                <p className="text-sm text-muted-foreground mb-4">Set up webhooks to receive real-time updates</p>
                
                <div className="bg-navy-700 p-4 rounded-lg mb-4">
                  <Label htmlFor="webhook-url" className="mb-2 block">Webhook URL</Label>
                  <div className="flex gap-2">
                    <Input id="webhook-url" placeholder="https://your-app.com/webhook" className="flex-1" />
                    <Button>Save</Button>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div>
                        <p className="text-sm font-medium">Trading Signals</p>
                        <p className="text-xs text-muted-foreground">Receive webhook notifications for new trading signals</p>
                      </div>
                    </div>
                    <Switch />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div>
                        <p className="text-sm font-medium">Portfolio Updates</p>
                        <p className="text-xs text-muted-foreground">Receive webhook notifications for portfolio changes</p>
                      </div>
                    </div>
                    <Switch />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div>
                        <p className="text-sm font-medium">Price Alerts</p>
                        <p className="text-xs text-muted-foreground">Receive webhook notifications for price alerts</p>
                      </div>
                    </div>
                    <Switch defaultChecked />
                  </div>
                </div>
              </div>
              
              <Separator />
              
              <div>
                <h3 className="text-lg font-semibold mb-4">API Documentation</h3>
                <p className="text-sm text-muted-foreground mb-4">Access our comprehensive API documentation to integrate with our platform</p>
                <Button variant="outline">
                  View Documentation
                </Button>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </AppLayout>
  );
};

export default Settings;
