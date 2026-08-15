import React from 'react'
import { cn } from '../utils'
import {
  AlertTriangle,
  FileText,
  Shield,
  Brain,
  FlaskConical,
  Activity,
  AlertTriangle as AlertTriangleIcon,
  TrendingUp,
  TrendingDown,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { Badge } from './ui/Badge'

const stats = [
  {
    title: 'Active Alerts',
    value: '24',
    change: '+12%',
    trend: 'up',
    icon: AlertTriangleIcon,
    color: 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30',
  },
  {
    title: 'Open Incidents',
    value: '7',
    change: '-2',
    trend: 'down',
    icon: FileText,
    color: 'text-orange-600 bg-orange-100 dark:text-orange-400 dark:bg-orange-900/30',
  },
  {
    title: 'Active Responses',
    value: '3',
    change: '+1',
    trend: 'up',
    icon: Shield,
    color: 'text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30',
  },
  {
    title: 'AI Analyses Today',
    value: '42',
    change: '+15%',
    trend: 'up',
    icon: Brain,
    color: 'text-purple-600 bg-purple-100 dark:text-purple-400 dark:bg-purple-900/30',
  },
]

const recentAlerts = [
  {
    id: '1',
    title: 'Repeated Failed Authentication',
    severity: 'high',
    source: 'auth-simulator',
    time: '2 min ago',
    mitre: ['T1110.001'],
  },
  {
    id: '2',
    title: 'DNS Tunneling Detected',
    severity: 'critical',
    source: 'dns-simulator',
    time: '15 min ago',
    mitre: ['T1048.003'],
  },
  {
    id: '3',
    title: 'Suspicious Process Execution',
    severity: 'high',
    source: 'workload-simulator',
    time: '1 hour ago',
    mitre: ['T1059.004'],
  },
  {
    id: '4',
    title: 'C2 Beaconing Detected',
    severity: 'critical',
    source: 'traffic-simulator',
    time: '3 hours ago',
    mitre: ['T1071.001'],
  },
  {
    id: '5',
    title: 'Port Scan Detected',
    severity: 'medium',
    source: 'traffic-simulator',
    time: '4 hours ago',
    mitre: ['T1046'],
  },
]

export function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Overview of security posture and active threats
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="btn btn-secondary btn-sm">
            <span className="mr-2">↻</span>
            Refresh
          </button>
          <button className="btn btn-primary btn-sm">
            + New Incident
          </button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <div className={cn('h-4 w-4', stat.color)}>
                <stat.icon className="h-4 w-4" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline justify-between">
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className={cn('text-sm font-medium', stat.trend === 'up' ? 'text-green-600' : 'text-red-600')}>
                  {stat.trend === 'up' ? (
                    <TrendingUp className="h-4 w-4 mr-1" />
                  ) : (
                    <TrendingDown className="h-4 w-4 mr-1" />
                  )}
                  {stat.change}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Recent Alerts
              <span className="text-sm text-muted-foreground">Last 24 hours</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-start gap-4 p-4 rounded-lg border border-border/50 hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                    <AlertTriangleIcon className="h-5 w-5 text-red-600 dark:text-red-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-foreground truncate">{alert.title}</div>
                      <span className="text-xs text-muted-foreground">{alert.time}</span>
                    </div>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`badge px-2 py-0.5 text-xs ${
                          alert.severity === 'critical'
                            ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                          : alert.severity === 'high'
                            ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400'
                            : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
                        }`}
                      >
                        {alert.severity}
                      </span>
                      <span className="text-xs text-muted-foreground">{alert.source}</span>
                      <span className="text-xs text-muted-foreground">{alert.mitre.join(', ')}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Active Incidents
                <span className="text-sm text-muted-foreground">Requiring attention</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { id: 'INC-001', title: 'Suspicious lateral movement detected', severity: 'critical', status: 'investigating', commander: 'analyst-1' },
                  { id: 'INC-002', title: 'Potential data exfiltration via DNS', severity: 'high', status: 'contained', commander: 'analyst-2' },
                  { id: 'INC-003', title: 'Cryptominer detected on worker node', severity: 'high', status: 'open', commander: 'analyst-1' },
                ].map((incident) => (
                  <div
                    key={incident.id}
                    className="flex items-center justify-between p-4 rounded-lg border border-border/50 hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium text-foreground truncate">{incident.title}</div>
                        <span className={`badge px-2 py-0.5 text-xs ${incident.severity === 'critical' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' : 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400'}`}>
                          {incident.severity}
                        </span>
                        <span className="badge bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400">
                          {incident.status}
                        </span>
                      </div>
                      <p className="text-sm text-muted-foreground truncate max-w-xs">Commander: {incident.commander}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="btn btn-ghost btn-sm">View</button>
                      <button className="btn btn-ghost btn-sm">Timeline</button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                AI Copilot Activity
                <span className="text-sm text-muted-foreground">Last 24 hours</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { type: 'Incident Summary', count: 12, icon: Brain },
                  { type: 'Alert Triage', count: 28, icon: AlertTriangle },
                  { type: 'Runbook Recommendations', count: 7, icon: Shield },
                  { type: 'Report Generation', count: 3, icon: FileText },
                ].map((item) => (
                  <div key={item.type} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <item.icon className="h-5 w-5 text-primary" />
                      </div>
                      <span className="font-medium">{item.type}</span>
                    </div>
                    <span className="text-2xl font-bold text-foreground">{item.count}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Emulation Lab Status
                <span className="text-sm text-muted-foreground">Active scenarios</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: 'Auth Brute Force', status: 'running', events: 245 },
                  { name: 'DNS Tunneling', status: 'completed', events: 120 },
                  { name: 'C2 Beaconing', status: 'pending', events: 0 },
                  { name: 'Port Scan', status: 'running', events: 89 },
                ].map((item) => (
                  <div key={item.name} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${item.status === 'running' ? 'bg-green-500' : item.status === 'completed' ? 'bg-blue-500' : 'bg-gray-400'}`} />
                      <span className="font-medium">{item.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">{item.events} events</span>
                      <span className={`badge px-2 py-0.5 text-xs ${
                        item.status === 'running' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' :
                        item.status === 'completed' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' :
                        'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400'
                      }`}>
                        {item.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                System Health
                <span className="text-sm text-muted-foreground">All systems operational</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: 'API Gateway', status: 'healthy', latency: '45ms' },
                  { name: 'Detection Engine', status: 'healthy', latency: '120ms' },
                  { name: 'AI Copilot', status: 'healthy', latency: '2.1s' },
                  { name: 'Response Orchestrator', status: 'healthy', latency: '85ms' },
                  { name: 'Emulation Controller', status: 'healthy', latency: '32ms' },
                  { name: 'PostgreSQL', status: 'healthy', latency: '8ms' },
                  { name: 'Redpanda', status: 'healthy', latency: '3ms' },
                  { name: 'Qdrant', status: 'healthy', latency: '12ms' },
                  { name: 'MinIO', status: 'healthy', latency: '15ms' },
                  { name: 'Ollama', status: 'healthy', latency: '1.2s' },
                ].map((item) => (
                  <div key={item.name} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${item.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
                      <span className="font-medium">{item.name}</span>
                    </div>
                    <span className="text-sm text-muted-foreground">{item.latency}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}