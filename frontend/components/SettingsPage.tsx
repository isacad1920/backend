import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Textarea } from './ui/textarea';
import { toast } from 'sonner';
import { 
  Settings, 
  Building2, 
  Palette, 
  Monitor, 
  Link, 
  Shield,
  Save
} from 'lucide-react';

export function SettingsPage() {
  const [settings, setSettings] = useState({
    companyName: 'FinanceOS Corp',
    companyEmail: 'admin@financeos.com',
    companyPhone: '+1 (555) 123-4567',
    companyAddress: '123 Business Avenue, Downtown',
    currency: 'USD',
    timezone: 'America/New_York',
    language: 'en',
    taxRate: '8.25',
    
    // Branding
    primaryColor: '#3b82f6',
    darkMode: true,
    compactMode: false,
    
    // System
    autoBackup: true,
    backupTime: '02:00',
    sessionTimeout: '30',
    debugMode: false,
    
    // Integrations
    apiKeyStripe: '',
    apiKeyPayPal: '',
    webhookUrl: '',
    
    // Security
    twoFactorAuth: false,
    passwordExpiry: '90',
    maxLoginAttempts: '5'
  });

  const handleSave = () => {
    toast.success('Settings saved successfully!');
  };

  const handleInputChange = (key: keyof typeof settings, value: string | boolean) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl flex items-center">
            <Settings className="w-6 h-6 mr-3" />
            System Settings
          </h1>
          <p className="text-white/70">Configure your system preferences and integrations</p>
        </div>
        <Button onClick={handleSave} className="bg-white/20 hover:bg-white/30 text-white border border-white/30">
          <Save className="w-4 h-4 mr-2" />
          Save Changes
        </Button>
      </div>

      <Tabs defaultValue="general" className="space-y-4">
        <TabsList className="bg-white/10 border border-white/20">
          <TabsTrigger value="general" className="data-[state=active]:bg-white/20 text-white">
            <Building2 className="w-4 h-4 mr-2" />
            General
          </TabsTrigger>
          <TabsTrigger value="branding" className="data-[state=active]:bg-white/20 text-white">
            <Palette className="w-4 h-4 mr-2" />
            Branding
          </TabsTrigger>
          <TabsTrigger value="system" className="data-[state=active]:bg-white/20 text-white">
            <Monitor className="w-4 h-4 mr-2" />
            System
          </TabsTrigger>
          <TabsTrigger value="integrations" className="data-[state=active]:bg-white/20 text-white">
            <Link className="w-4 h-4 mr-2" />
            Integrations
          </TabsTrigger>
          <TabsTrigger value="security" className="data-[state=active]:bg-white/20 text-white">
            <Shield className="w-4 h-4 mr-2" />
            Security
          </TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Company Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-white">Company Name</Label>
                  <Input
                    value={settings.companyName}
                    onChange={(e) => handleInputChange('companyName', e.target.value)}
                    className="bg-white/10 border-white/20 text-white"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-white">Email</Label>
                  <Input
                    type="email"
                    value={settings.companyEmail}
                    onChange={(e) => handleInputChange('companyEmail', e.target.value)}
                    className="bg-white/10 border-white/20 text-white"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-white">Phone</Label>
                  <Input
                    value={settings.companyPhone}
                    onChange={(e) => handleInputChange('companyPhone', e.target.value)}
                    className="bg-white/10 border-white/20 text-white"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-white">Tax Rate (%)</Label>
                  <Input
                    type="number"
                    value={settings.taxRate}
                    onChange={(e) => handleInputChange('taxRate', e.target.value)}
                    className="bg-white/10 border-white/20 text-white"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-white">Address</Label>
                <Textarea
                  value={settings.companyAddress}
                  onChange={(e) => handleInputChange('companyAddress', e.target.value)}
                  className="bg-white/10 border-white/20 text-white"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label className="text-white">Currency</Label>
                  <Select value={settings.currency} onValueChange={(value) => handleInputChange('currency', value)}>
                    <SelectTrigger className="bg-white/10 border-white/20 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="USD">USD - US Dollar</SelectItem>
                      <SelectItem value="EUR">EUR - Euro</SelectItem>
                      <SelectItem value="GBP">GBP - British Pound</SelectItem>
                      <SelectItem value="CAD">CAD - Canadian Dollar</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-white">Timezone</Label>
                  <Select value={settings.timezone} onValueChange={(value) => handleInputChange('timezone', value)}>
                    <SelectTrigger className="bg-white/10 border-white/20 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="America/New_York">Eastern Time</SelectItem>
                      <SelectItem value="America/Chicago">Central Time</SelectItem>
                      <SelectItem value="America/Denver">Mountain Time</SelectItem>
                      <SelectItem value="America/Los_Angeles">Pacific Time</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label className="text-white">Language</Label>
                  <Select value={settings.language} onValueChange={(value) => handleInputChange('language', value)}>
                    <SelectTrigger className="bg-white/10 border-white/20 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Spanish</SelectItem>
                      <SelectItem value="fr">French</SelectItem>
                      <SelectItem value="de">German</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="branding" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Appearance</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Dark Mode</Label>
                    <p className="text-white/70 text-sm">Use dark theme throughout the application</p>
                  </div>
                  <Switch
                    checked={settings.darkMode}
                    onCheckedChange={(checked) => handleInputChange('darkMode', checked)}
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Compact Mode</Label>
                    <p className="text-white/70 text-sm">Reduce spacing for more content on screen</p>
                  </div>
                  <Switch
                    checked={settings.compactMode}
                    onCheckedChange={(checked) => handleInputChange('compactMode', checked)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">System Configuration</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Automatic Backup</Label>
                    <p className="text-white/70 text-sm">Enable automatic daily backups</p>
                  </div>
                  <Switch
                    checked={settings.autoBackup}
                    onCheckedChange={(checked) => handleInputChange('autoBackup', checked)}
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-white">Backup Time</Label>
                    <Input
                      type="time"
                      value={settings.backupTime}
                      onChange={(e) => handleInputChange('backupTime', e.target.value)}
                      className="bg-white/10 border-white/20 text-white"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-white">Session Timeout (minutes)</Label>
                    <Input
                      type="number"
                      value={settings.sessionTimeout}
                      onChange={(e) => handleInputChange('sessionTimeout', e.target.value)}
                      className="bg-white/10 border-white/20 text-white"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label className="text-white">Debug Mode</Label>
                    <p className="text-white/70 text-sm">Enable detailed logging for troubleshooting</p>
                  </div>
                  <Switch
                    checked={settings.debugMode}
                    onCheckedChange={(checked) => handleInputChange('debugMode', checked)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="integrations" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">API Integrations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label className="text-white">Stripe API Key</Label>
                <Input
                  type="password"
                  placeholder="sk_live_..."
                  value={settings.apiKeyStripe}
                  onChange={(e) => handleInputChange('apiKeyStripe', e.target.value)}
                  className="bg-white/10 border-white/20 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-white">PayPal API Key</Label>
                <Input
                  type="password"
                  placeholder="Enter PayPal API key"
                  value={settings.apiKeyPayPal}
                  onChange={(e) => handleInputChange('apiKeyPayPal', e.target.value)}
                  className="bg-white/10 border-white/20 text-white"
                />
              </div>
              <div className="space-y-2">
                <Label className="text-white">Webhook URL</Label>
                <Input
                  placeholder="https://yoursite.com/webhook"
                  value={settings.webhookUrl}
                  onChange={(e) => handleInputChange('webhookUrl', e.target.value)}
                  className="bg-white/10 border-white/20 text-white"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Security Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-white">Two-Factor Authentication</Label>
                  <p className="text-white/70 text-sm">Require 2FA for all user logins</p>
                </div>
                <Switch
                  checked={settings.twoFactorAuth}
                  onCheckedChange={(checked) => handleInputChange('twoFactorAuth', checked)}
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-white">Password Expiry (days)</Label>
                  <Input
                    type="number"
                    value={settings.passwordExpiry}
                    onChange={(e) => handleInputChange('passwordExpiry', e.target.value)}
                    className="bg-white/10 border-white/20 text-white"
                  />
                </div>
                <div className="space-y-2">
                  <Label className="text-white">Max Login Attempts</Label>
                  <Input
                    type="number"
                    value={settings.maxLoginAttempts}
                    onChange={(e) => handleInputChange('maxLoginAttempts', e.target.value)}
                    className="bg-white/10 border-white/20 text-white"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}