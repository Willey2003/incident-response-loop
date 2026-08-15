import React from 'react'
import { cn } from '../utils'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { Badge } from './ui/Badge'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/Select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/Table'
import { Play, Stop, RotateCcw, AlertTriangle, Shield, Brain, Activity, ChevronDown, ChevronUp } from 'lucide-react'

const mockScenarios = [
  { id: 'auth-brute-force', name: 'Authentication Brute Force', severity: 'high', mitre: ['T1110.001'], duration: 300, enabled: true },
  { id: 'dns-tunneling', name: 'DNS Tunneling Exfiltration', severity: 'high', mitre: ['T1048.003'], duration: 300, enabled: true },
  { id: 'traffic-beaconing', name: 'C2 Beaconing Pattern', severity: 'high', mitre: ['T1071.001'], duration: 300, enabled: true },
  { id: 'traffic-port-scan', name: 'Internal Port Scan', severity: 'medium', mitre: ['T1046'], duration: 300, enabled: true },
  { id: 'workload-privilege-escalation', name: 'Container Privilege Escalation', severity: 'critical', mitre: ['T1611'], duration: 300, enabled: true },
  { id: 'crypto-mining', name: 'Cryptocurrency Mining', severity: 'high', mitre: ['T1496'], duration: 300, enabled: true },
  { id: 'data-exfiltration', name: 'Data Exfiltration Simulation', severity: 'critical', mitre: ['T1041'], duration: 300, enabled: true },
]

const mockRuns = [
  { id: 'run-1', scenario: 'auth-brute-force', status: 'completed', events: 245, started: '10 min ago' },
  { id: 'run-2', scenario: 'dns-tunneling', status: 'running', events: 120, started: '5 min ago' },
  { id: 'run-3', scenario: 'traffic-beaconing', status: 'pending', events: 0, started: 'pending' },
]

export function EmulationLab() {
  const [activeTab, setActiveTab] = React.useState('scenarios')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Emulation Lab</h1>
          <p className="text-muted-foreground">Safe threat emulation and validation scenarios</p>
        </div>
      </div>

      <div className="flex gap-4 mb-6">
        <Button
          variant={activeTab === 'scenarios' ? 'default' : 'outline'}
          onClick={() => setActiveTab('scenarios')}
        >
          Scenarios
        </Button>
        <Button
          variant={activeTab === 'runs' ? 'default' : 'outline'}
          onClick={() => setActiveTab('runs')}
        >
          Active Runs
        </Button>
        <Button
          variant={activeTab === 'templates' ? 'default' : 'outline'}
          onClick={() => setActiveTab('templates')}
        >
          Templates
        </Button>
      </div>

      {activeTab === 'scenarios' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Scenarios
              <Badge variant="outline" className="ml-2">CPU Only</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    {['Name', 'Category', 'Severity', 'MITRE', 'Duration', 'Status', 'Actions'].map((col) => (
                      <TableHead key={col}>{col}</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockScenarios.map((scenario) => (
                    <TableRow key={scenario.id}>
                      <TableCell className="font-medium">{scenario.name}</TableCell>
                      <TableCell>{scenario.id.split('-')[0]}</TableCell>
                      <TableCell>
                        <Badge variant={
                          scenario.severity === 'critical' ? 'destructive' :
                          scenario.severity === 'high' ? 'default' :
                          scenario.severity === 'medium' ? 'secondary' : 'outline'
                        }>
                          {scenario.severity}
                        </Badge>
                      </TableCell>
                      <TableCell>{scenario.mitre.join(', ')}</TableCell>
                      <TableCell>{scenario.duration}s</TableCell>
                      <TableCell>
                        <Badge variant={scenario.enabled ? 'default' : 'outline'}>
                          {scenario.enabled ? 'Enabled' : 'Disabled'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Button variant="outline" size="sm">
                            <Play className="mr-1 h-4 w-4" />
                            Run
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

      {activeTab === 'runs' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Active Runs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    {['Run ID', 'Scenario', 'Status', 'Events', 'Started', 'Actions'].map((col) => (
                      <TableHead key={col}>{col}</TableHead>
                    ))}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockRuns.map((run) => (
                    <TableRow key={run.id}>
                      <TableCell className="font-mono text-sm">{run.id}</TableCell>
                      <TableCell>{run.scenario}</TableCell>
                      <TableCell>
                        <Badge variant={
                          run.status === 'running' ? 'default' :
                          run.status === 'completed' ? 'secondary' :
                          run.status === 'pending' ? 'outline' : 'destructive'
                        }>
                          {run.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{run.events}</TableCell>
                      <TableCell className="text-muted-foreground">{run.started}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {run.status === 'running' && (
                            <Button variant="ghost" size="sm" onClick={() => {}}>
                              <Stop className="mr-1 h-4 w-4" />
                              Stop
                            </Button>
                          )}
                          {run.status === 'pending' && (
                            <Button variant="ghost" size="sm" onClick={() => {}}>
                              <RotateCcw className="mr-1 h-4 w-4" />
                              Cancel
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

      {activeTab === 'templates' && (
        <Card>
          <CardHeader>
            <CardTitle>Scenario Templates</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[
                { id: 'auth-brute-force', name: 'Auth Brute Force', category: 'authentication', severity: 'high', mitre: ['T1110.001'] },
                { id: 'dns-tunneling', name: 'DNS Tunneling', category: 'dns', severity: 'high', mitre: ['T1048.003'] },
                { id: 'traffic-beaconing', name: 'C2 Beaconing', category: 'traffic', severity: 'high', mitre: ['T1071.001'] },
                { id: 'traffic-port-scan', name: 'Port Scan', category: 'traffic', severity: 'medium', mitre: ['T1046'] },
                { id: 'workload-privilege-escalation', name: 'Privilege Escalation', category: 'workload', severity: 'critical', mitre: ['T1611'] },
                { id: 'crypto-mining', name: 'Crypto Mining', category: 'workload', severity: 'high', mitre: ['T1496'] },
              ].map((template) => (
                <Card key={template.id} className="p-4 hover:border-primary/50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-medium">{template.name}</h4>
                      <p className="text-sm text-muted-foreground">{template.category}</p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant={template.severity === 'critical' ? 'destructive' : template.severity === 'high' ? 'default' : template.severity === 'medium' ? 'secondary' : 'outline'}>
                          {template.severity}
                        </Badge>
                        <span className="text-xs text-muted-foreground">{template.mitre.join(', ')}</span>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => {}}>
                      Use Template
                    </Button>
                  </div>
                ))}
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

// Placeholder UI components
const Card = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={cn('rounded-xl border border-border bg-card text-card-foreground shadow-sm', className)}>{children}</div>
)
const CardHeader = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={cn('flex flex-col space-y-1.5 p-6', className)}>{children}</div>
)
const CardTitle = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <h3 className={cn('text-xl font-semibold leading-none tracking-tight', className)}>{children}</h3>
)
const CardContent = ({ children, className }: { children: React.ReactNode; className?: string }) => (
  <div className={cn('p-6 pt-0', className)}>{children}</div>
)
const Badge = ({ children, variant = 'default', className }: { children: React.ReactNode; variant?: 'default' | 'secondary' | 'destructive' | 'outline'; className?: string }) => (
  <span className={cn(
    'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
    {
      'bg-primary text-primary-foreground hover:bg-primary/80': variant === 'default',
      'bg-secondary text-secondary-foreground hover:bg-secondary/80': variant === 'secondary',
      'bg-destructive text-destructive-foreground hover:bg-destructive/80': variant === 'destructive',
      'border border-input bg-background hover:bg-accent hover:text-accent-foreground': variant === 'outline',
    },
    className
  )}>{children}</span>
)
const Button = ({ children, variant = 'default', className, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link' }) => (
  <button className={cn(
    'inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-ring disabled:opacity-50 disabled:pointer-events-none',
    {
      'bg-primary text-primary-foreground hover:bg-primary/90': variant === 'default',
      'bg-destructive text-destructive-foreground hover:bg-destructive/90': variant === 'destructive',
      'bg-secondary text-secondary-foreground hover:bg-secondary/80': variant === 'secondary',
      'border border-input bg-background hover:bg-accent hover:text-accent-foreground': variant === 'outline',
      'hover:bg-accent hover:text-accent-foreground': variant === 'ghost',
      'text-primary underline-offset-4 hover:underline': variant === 'link',
    },
    className
  )} {...props}>{children}</button>
)
const Table = ({ children, className }: { children: React.ReactNode; className?: string }) => <div className={cn('w-full caption-bottom text-sm', className)}>{children}</div>
const TableHeader = ({ children, className }: { children: React.ReactNode; className?: string }) => <thead className={cn('[&_tr]:border-b', className)}>{children}</thead>
const TableBody = ({ children, className }: { children: React.ReactNode; className?: string }) => <tbody className={cn('[&_tr:last-child]:border-0', className)}>{children}</tbody>
const TableRow = ({ children, className }: { children: React.ReactNode; className?: string }) => <tr className={cn('border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted', className)}>{children}</tr>
const TableHead = ({ children, className, ...props }: { children: React.ReactNode; className?: string } & React.ThHTMLAttributes<HTMLTableCellElement>) => <th className={cn('h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0', className)} {...props}>{children}</th>
const TableCell = ({ children, className, ...props }: { children: React.ReactNode; className?: string } & React.TdHTMLAttributes<HTMLTableCellElement>) => <td className={cn('p-4 align-middle [&:has([role=checkbox])]:pr-0', className)} {...props}>{children}</td>
const TableHeader = ({ children, className }: { children: React.ReactNode; className?: string }) => <thead className={cn('[&_tr]:border-b', className)}>{children}</thead>
const TableBody = ({ children, className }: { children: React.ReactNode; className?: string }) => <tbody className={cn('[&_tr:last-child]:border-0', className)}>{children}</tbody>
const TableRow = ({ children, className }: { children: React.ReactNode; className?: string }) => <tr className={cn('border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted', className)}>{children}</tr>
const Play = ({ className }: { className?: string }) => <svg className={cn('h-4 w-4', className)} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
const Stop = ({ className }: { className?: string }) => <svg className={cn('h-4 w-4', className)} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
const RotateCcw = ({ className }: { className?: string }) => <svg className={cn('h-4 w-4', className)} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0 0-18 9 9 0 0 0 0 18"/></svg>