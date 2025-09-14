import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Plus, 
  Search, 
  BookOpen, 
  DollarSign,
  TrendingUp,
  TrendingDown,
  Eye,
  Edit,
  Download
} from 'lucide-react';

const journalEntries = [
  { 
    id: 'JE-001', 
    date: '2024-12-15',
    description: 'Sale to Tech Solutions Inc',
    reference: 'SAL-001',
    debit: 12500,
    credit: 0,
    account: 'Accounts Receivable',
    category: 'Revenue'
  },
  { 
    id: 'JE-002', 
    date: '2024-12-15',
    description: 'Sale to Tech Solutions Inc',
    reference: 'SAL-001',
    debit: 0,
    credit: 12500,
    account: 'Sales Revenue',
    category: 'Revenue'
  },
  { 
    id: 'JE-003', 
    date: '2024-12-14',
    description: 'Payment from Digital Agency',
    reference: 'PAY-002',
    debit: 8900,
    credit: 0,
    account: 'Cash',
    category: 'Asset'
  },
  { 
    id: 'JE-004', 
    date: '2024-12-14',
    description: 'Payment from Digital Agency',
    reference: 'PAY-002',
    debit: 0,
    credit: 8900,
    account: 'Accounts Receivable',
    category: 'Asset'
  },
  { 
    id: 'JE-005', 
    date: '2024-12-13',
    description: 'Inventory Purchase',
    reference: 'PO-045',
    debit: 15000,
    credit: 0,
    account: 'Inventory',
    category: 'Asset'
  },
  { 
    id: 'JE-006', 
    date: '2024-12-13',
    description: 'Inventory Purchase',
    reference: 'PO-045',
    debit: 0,
    credit: 15000,
    account: 'Accounts Payable',
    category: 'Liability'
  },
];

const accountSummary = [
  { account: 'Cash', balance: 45600, type: 'Asset' },
  { account: 'Accounts Receivable', balance: 23400, type: 'Asset' },
  { account: 'Inventory', balance: 87500, type: 'Asset' },
  { account: 'Accounts Payable', balance: 12300, type: 'Liability' },
  { account: 'Sales Revenue', balance: 156700, type: 'Revenue' },
  { account: 'Cost of Goods Sold', balance: 89400, type: 'Expense' },
];

export function JournalPage() {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredEntries = journalEntries.filter(entry => {
    const matchesSearch = entry.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         entry.reference.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         entry.account.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'Asset': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'Liability': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'Revenue': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'Expense': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const totalDebits = filteredEntries.reduce((sum, entry) => sum + entry.debit, 0);
  const totalCredits = filteredEntries.reduce((sum, entry) => sum + entry.credit, 0);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl">Journal & Accounting</h1>
          <p className="text-white/70">Track financial transactions and account balances</p>
        </div>
        <div className="flex space-x-2">
          <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30">
            <Plus className="w-4 h-4 mr-2" />
            New Entry
          </Button>
          <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <BookOpen className="w-8 h-8 text-blue-400" />
              <div>
                <p className="text-white/70 text-sm">Total Entries</p>
                <p className="text-white text-xl">{journalEntries.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-8 h-8 text-green-400" />
              <div>
                <p className="text-white/70 text-sm">Total Debits</p>
                <p className="text-white text-xl">${totalDebits.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <TrendingDown className="w-8 h-8 text-red-400" />
              <div>
                <p className="text-white/70 text-sm">Total Credits</p>
                <p className="text-white text-xl">${totalCredits.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <DollarSign className="w-8 h-8 text-purple-400" />
              <div>
                <p className="text-white/70 text-sm">Balance</p>
                <p className={`text-xl ${totalDebits === totalCredits ? 'text-green-400' : 'text-red-400'}`}>
                  ${Math.abs(totalDebits - totalCredits).toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="journal" className="space-y-4">
        <TabsList className="bg-white/10 border border-white/20">
          <TabsTrigger value="journal" className="data-[state=active]:bg-white/20 text-white">
            Journal Entries
          </TabsTrigger>
          <TabsTrigger value="accounts" className="data-[state=active]:bg-white/20 text-white">
            Chart of Accounts
          </TabsTrigger>
          <TabsTrigger value="trial-balance" className="data-[state=active]:bg-white/20 text-white">
            Trial Balance
          </TabsTrigger>
        </TabsList>

        <TabsContent value="journal" className="space-y-4">
          {/* Filters */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-4">
              <div className="flex items-center space-x-4">
                <div className="relative flex-1 max-w-md">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50 w-4 h-4" />
                  <Input
                    placeholder="Search entries..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50"
                  />
                </div>
                <Input
                  type="date"
                  className="bg-white/10 border-white/20 text-white"
                />
                <Input
                  type="date"
                  className="bg-white/10 border-white/20 text-white"
                />
              </div>
            </CardContent>
          </Card>

          {/* Journal Entries Table */}
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Journal Entries</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">Entry ID</TableHead>
                    <TableHead className="text-white/70">Date</TableHead>
                    <TableHead className="text-white/70">Description</TableHead>
                    <TableHead className="text-white/70">Account</TableHead>
                    <TableHead className="text-white/70">Debit</TableHead>
                    <TableHead className="text-white/70">Credit</TableHead>
                    <TableHead className="text-white/70">Reference</TableHead>
                    <TableHead className="text-white/70">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredEntries.map((entry) => (
                    <TableRow key={`${entry.id}-${entry.account}`} className="border-white/20">
                      <TableCell className="text-white">{entry.id}</TableCell>
                      <TableCell className="text-white/70">{entry.date}</TableCell>
                      <TableCell className="text-white">{entry.description}</TableCell>
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          <span className="text-white">{entry.account}</span>
                          <Badge className={getCategoryColor(entry.category)}>
                            {entry.category}
                          </Badge>
                        </div>
                      </TableCell>
                      <TableCell className={entry.debit > 0 ? "text-green-400" : "text-white/50"}>
                        {entry.debit > 0 ? `$${entry.debit.toLocaleString()}` : '-'}
                      </TableCell>
                      <TableCell className={entry.credit > 0 ? "text-red-400" : "text-white/50"}>
                        {entry.credit > 0 ? `$${entry.credit.toLocaleString()}` : '-'}
                      </TableCell>
                      <TableCell className="text-white/70">{entry.reference}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                            <Edit className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="accounts" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Chart of Accounts</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow className="border-white/20">
                    <TableHead className="text-white/70">Account Name</TableHead>
                    <TableHead className="text-white/70">Type</TableHead>
                    <TableHead className="text-white/70">Balance</TableHead>
                    <TableHead className="text-white/70">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {accountSummary.map((account, index) => (
                    <TableRow key={index} className="border-white/20">
                      <TableCell className="text-white">{account.account}</TableCell>
                      <TableCell>
                        <Badge className={getCategoryColor(account.type)}>
                          {account.type}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-white">${account.balance.toLocaleString()}</TableCell>
                      <TableCell>
                        <div className="flex space-x-2">
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                            <Edit className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trial-balance" className="space-y-4">
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white">Trial Balance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-white mb-4">Assets & Expenses</h3>
                  <div className="space-y-2">
                    {accountSummary.filter(acc => acc.type === 'Asset' || acc.type === 'Expense').map((account, index) => (
                      <div key={index} className="flex justify-between p-2 bg-white/5 rounded">
                        <span className="text-white/70">{account.account}</span>
                        <span className="text-white">${account.balance.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="text-white mb-4">Liabilities & Revenue</h3>
                  <div className="space-y-2">
                    {accountSummary.filter(acc => acc.type === 'Liability' || acc.type === 'Revenue').map((account, index) => (
                      <div key={index} className="flex justify-between p-2 bg-white/5 rounded">
                        <span className="text-white/70">{account.account}</span>
                        <span className="text-white">${account.balance.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}