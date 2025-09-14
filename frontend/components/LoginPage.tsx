import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { toast } from 'sonner';
import { Eye, EyeOff, Building2, Shield, Zap } from 'lucide-react';

interface LoginUserData {
  id: string;
  email: string;
  name: string;
  role: string;
  branch: string;
  permissions: string[];
}

interface LoginPageProps {
  onLogin?: (user: LoginUserData) => void; // kept for backward compatibility (unused)
}

export function LoginPage({ onLogin: _onLogin }: LoginPageProps) {
  const { login, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false); // local spinner for transition

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please fill in all fields');
      return;
    }

    setIsLoading(true);
    try {
      await login(email, password);
      toast.success('Login successful');
    } catch (e: any) {
      toast.error(e?.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      {/* Glassmorphism background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-indigo-500/10 rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10 w-full max-w-md">
        {/* Logo/Brand Section */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 mb-4">
            <Building2 className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl text-white mb-2">FinanceOS</h1>
          <p className="text-white/70">Enterprise Financial Management</p>
        </div>

        {/* Login Card */}
        <Card className="bg-white/10 backdrop-blur-md border-white/20 shadow-2xl">
          <CardHeader className="text-center">
            <CardTitle className="text-white">Welcome Back</CardTitle>
            <CardDescription className="text-white/70">
              Sign in to your account to continue
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-white">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="admin@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password" className="text-white">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-white/10 border-white/20 text-white placeholder:text-white/50 focus:border-white/40 pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/70 hover:text-white"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
              <Button
                type="submit"
                className="w-full bg-white/20 hover:bg-white/30 text-white border border-white/30"
                disabled={isLoading}
              >
                {isLoading || loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            {/* Demo credentials hint */}
            <div className="mt-6 p-3 bg-white/5 rounded-lg border border-white/10">
              <p className="text-white/70 text-sm mb-2">Demo Account:</p>
              <div className="space-y-1 text-xs">
                <p className="text-white/60">Email: demo@sofinance.com</p>
                <p className="text-white/60">Password: any password</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Features */}
        <div className="mt-8 grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-8 h-8 bg-white/10 backdrop-blur-md rounded-lg border border-white/20 mb-2">
              <Shield className="w-4 h-4 text-white" />
            </div>
            <p className="text-white/70 text-xs">Secure</p>
          </div>
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-8 h-8 bg-white/10 backdrop-blur-md rounded-lg border border-white/20 mb-2">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <p className="text-white/70 text-xs">Fast</p>
          </div>
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-8 h-8 bg-white/10 backdrop-blur-md rounded-lg border border-white/20 mb-2">
              <Building2 className="w-4 h-4 text-white" />
            </div>
            <p className="text-white/70 text-xs">Enterprise</p>
          </div>
        </div>
      </div>
    </div>
  );
}