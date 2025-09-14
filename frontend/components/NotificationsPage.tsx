import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { 
  Bell, 
  Search, 
  Check,
  Trash2,
  AlertTriangle,
  Info,
  CheckCircle,
  Plus
} from 'lucide-react';

const notificationsData = [
  {
    id: 1,
    title: 'Low Stock Alert',
    message: '23 products are running low on stock and need reordering',
    type: 'warning',
    read: false,
    timestamp: '2 minutes ago',
    icon: AlertTriangle
  },
  {
    id: 2,
    title: 'Payment Received',
    message: 'Payment of $12,500 received from Tech Solutions Inc',
    type: 'success',
    read: false,
    timestamp: '15 minutes ago',
    icon: CheckCircle
  },
  {
    id: 3,
    title: 'System Backup Complete',
    message: 'Daily backup completed successfully at 2:00 AM',
    type: 'info',
    read: true,
    timestamp: '8 hours ago',
    icon: Info
  },
  {
    id: 4,
    title: 'New User Registration',
    message: 'New user Sarah Johnson registered and pending approval',
    type: 'info',
    read: true,
    timestamp: '1 day ago',
    icon: Info
  },
  {
    id: 5,
    title: 'Overdue Payment Alert',
    message: '5 customers have overdue payments totaling $12,450',
    type: 'warning',
    read: false,
    timestamp: '2 days ago',
    icon: AlertTriangle
  },
];

export function NotificationsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [readFilter, setReadFilter] = useState('all');

  const filteredNotifications = notificationsData.filter(notification => {
    const matchesSearch = notification.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         notification.message.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = typeFilter === 'all' || notification.type === typeFilter;
    const matchesRead = readFilter === 'all' || 
                       (readFilter === 'unread' && !notification.read) ||
                       (readFilter === 'read' && notification.read);
    return matchesSearch && matchesType && matchesRead;
  });

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'success': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'warning': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'error': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'info': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'success': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      case 'info': return 'text-blue-400';
      default: return 'text-gray-400';
    }
  };

  const unreadCount = notificationsData.filter(n => !n.read).length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white text-2xl flex items-center">
            <Bell className="w-6 h-6 mr-3" />
            Notifications
            {unreadCount > 0 && (
              <Badge className="ml-2 bg-red-500/20 text-red-400 border-red-500/30">
                {unreadCount} new
              </Badge>
            )}
          </h1>
          <p className="text-white/70">Stay updated with system alerts and messages</p>
        </div>
        <div className="flex space-x-2">
          <Button className="bg-white/20 hover:bg-white/30 text-white border border-white/30">
            <Plus className="w-4 h-4 mr-2" />
            Send Notification
          </Button>
          <Button variant="outline" className="border-white/30 text-white hover:bg-white/10">
            <Check className="w-4 h-4 mr-2" />
            Mark All Read
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="bg-white/10 backdrop-blur-md border-white/20">
        <CardContent className="p-4">
          <div className="flex items-center space-x-4">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/50 w-4 h-4" />
              <Input
                placeholder="Search notifications..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 bg-white/10 border-white/20 text-white placeholder:text-white/50"
              />
            </div>
            <div className="flex space-x-2">
              {['all', 'info', 'success', 'warning', 'error'].map(type => (
                <Button
                  key={type}
                  variant={typeFilter === type ? "default" : "outline"}
                  size="sm"
                  className={typeFilter === type 
                    ? "bg-white/20 text-white border-white/30" 
                    : "border-white/30 text-white hover:bg-white/10"
                  }
                  onClick={() => setTypeFilter(type)}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </Button>
              ))}
            </div>
            <div className="flex space-x-2">
              {['all', 'unread', 'read'].map(status => (
                <Button
                  key={status}
                  variant={readFilter === status ? "default" : "outline"}
                  size="sm"
                  className={readFilter === status 
                    ? "bg-white/20 text-white border-white/30" 
                    : "border-white/30 text-white hover:bg-white/10"
                  }
                  onClick={() => setReadFilter(status)}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </Button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notifications List */}
      <div className="space-y-4">
        {filteredNotifications.map((notification) => {
          const IconComponent = notification.icon;
          return (
            <Card 
              key={notification.id} 
              className={`bg-white/10 backdrop-blur-md border-white/20 transition-colors hover:bg-white/15 ${
                !notification.read ? 'border-l-4 border-l-blue-400' : ''
              }`}
            >
              <CardContent className="p-4">
                <div className="flex items-start space-x-4">
                  <div className={`p-2 rounded-lg bg-white/10 ${getTypeIcon(notification.type)}`}>
                    <IconComponent className="w-5 h-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className={`text-white ${!notification.read ? 'font-medium' : ''}`}>
                          {notification.title}
                        </h3>
                        <p className="text-white/70 text-sm mt-1">{notification.message}</p>
                        <div className="flex items-center space-x-2 mt-2">
                          <Badge className={getTypeColor(notification.type)}>
                            {notification.type}
                          </Badge>
                          <span className="text-white/50 text-xs">{notification.timestamp}</span>
                          {!notification.read && (
                            <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 text-xs">
                              New
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div className="flex space-x-2 ml-4">
                        {!notification.read && (
                          <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                            <Check className="w-4 h-4" />
                          </Button>
                        )}
                        <Button size="sm" variant="ghost" className="text-white/70 hover:text-white hover:bg-white/10">
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
        
        {filteredNotifications.length === 0 && (
          <Card className="bg-white/10 backdrop-blur-md border-white/20">
            <CardContent className="p-8 text-center">
              <Bell className="w-12 h-12 text-white/50 mx-auto mb-4" />
              <h3 className="text-white text-lg mb-2">No notifications found</h3>
              <p className="text-white/70">Try adjusting your filters or search terms</p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4 text-center">
            <Bell className="w-8 h-8 text-blue-400 mx-auto mb-2" />
            <p className="text-white/70 text-sm">Total</p>
            <p className="text-white text-xl">{notificationsData.length}</p>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4 text-center">
            <AlertTriangle className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
            <p className="text-white/70 text-sm">Unread</p>
            <p className="text-white text-xl">{unreadCount}</p>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4 text-center">
            <CheckCircle className="w-8 h-8 text-green-400 mx-auto mb-2" />
            <p className="text-white/70 text-sm">Alerts</p>
            <p className="text-white text-xl">{notificationsData.filter(n => n.type === 'warning' || n.type === 'error').length}</p>
          </CardContent>
        </Card>
        
        <Card className="bg-white/10 backdrop-blur-md border-white/20">
          <CardContent className="p-4 text-center">
            <Info className="w-8 h-8 text-purple-400 mx-auto mb-2" />
            <p className="text-white/70 text-sm">System</p>
            <p className="text-white text-xl">{notificationsData.filter(n => n.type === 'info').length}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}