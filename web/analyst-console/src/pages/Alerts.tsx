import React from 'react'
import { cn } from '../utils'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { Badge } from './ui/Badge'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/Select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/Table'
import { AlertTriangle, Search, Filter, ChevronDown, ChevronUp } from 'lucide-react'

const mockAlerts = [
  { id: '1', rule: 'DET-001', title: 'Repeated Failed Authentication', severity: 'high', status: 'open', source: 'auth-simulator', time: '2 min ago' },
  { id: '2', rule: 'DET-003', title: 'DNS Tunneling Detected', severity: 'critical', status: 'investigating', source: 'dns-simulator', time: '15 min ago' },
  { id: '3', rule: 'DET-004', title: 'Cryptocurrency Mining Process', severity: 'high', status: 'open', source: 'workload-simulator', time: '1 hour ago' },
  { id: '4', rule: 'DET-005', title: 'Large Data Transfer', severity: 'high', status: 'acknowledged', source: 'traffic-simulator', time: '3 hours ago' },
  { id: '5', rule: 'DET-001', title: 'Repeated Failed Authentication', severity: 'medium', status: 'closed', source: 'auth-simulator', time: '5 hours ago' },
]

export function Alerts() {
  const [search, setSearch] = React.useState('')
  const [severityFilter, setSeverityFilter] = React.useState('all')
  const [statusFilter, setStatusFilter] = React.useState('all')
  const [sortConfig, setSortConfig] = React.useState<{ key: string; direction: 'asc' | 'desc' }>({ key: 'time', direction: 'desc' })

  const filteredAlerts = mockAlerts.filter(alert => {
    const matchesSearch = alert.title.toLowerCase().includes(search.toLowerCase()) || alert.source.toLowerCase().includes(search.toLowerCase())
    const matchesSeverity = severityFilter === 'all' || alert.severity === severityFilter
    const matchesStatus = statusFilter === 'all' || alert.status === statusFilter
    return matchesSearch && matchesSeverity && matchesStatus
  })

  const sortedAlerts = [...filteredAlerts].sort((a, b) => {
    if (sortConfig.direction === 'asc') return a[sortConfig.key] > b[sortConfig.key] ? 1 : -1
    return a[sortConfig.key] < b[sortConfig.key] ? 1 : -1
  })

  const handleSort = (key: string) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Alerts</h1>
          <p className="text-muted-foreground">Monitor and triage security alerts</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" className="hidden sm:flex">
            <span className="mr-2">↻</span> Refresh
          </button>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search alerts..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex gap-2">
          <Select value={severityFilter} onValueChange={setSeverityFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Severity" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Severities</SelectItem>
              <SelectItem value="critical">Critical</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
              <SelectItem value="info">Info</SelectItem>
            </SelectContent>
          </Select>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="open">Open</SelectItem>
              <SelectItem value="investigating">Investigating</SelectItem>
              <SelectItem value="acknowledged">Acknowledged</SelectItem>
              <SelectItem value="closed">Closed</SelectItem>
              <SelectItem value="false_positive">False Positive</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Alerts
            <span className="text-sm text-muted-foreground">Showing {mockAlerts.length} alerts</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  {[
                    { key: 'title', label: 'Title' },
                    { key: 'severity', label: 'Severity' },
                    { key: 'status', label: 'Status' },
                    { key: 'source', label: 'Source' },
                    { key: 'time', label: 'Time' },
                  ].map((col) => (
                    <TableHead key={col.key}>
                      <TableRow>
                        <TableHead
                          className="cursor-pointer select-none hover:bg-accent"
                          onClick={() => handleSort(col.key)}
                        >
                          <div className="flex items-center gap-1">
                            {col.label}
                            {sortConfig.key === col.key && (
                              sortConfig.direction === 'asc' ? (
                                <ChevronUp className="h-4 w-4" />
                              ) : (
                                <ChevronDown className="h-4 w-4" />
                              )
                            )}
                          </div>
                        </TableHead>
                      </TableRow>
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockAlerts.map((alert) => (
                  <TableRow key={alert.id}>
                    <TableCell className="font-medium">{alert.title}</TableCell>
                    <TableCell>
                      <Badge variant={alert.severity === 'critical' ? 'destructive' : alert.severity === 'high' ? 'default' : alert.severity === 'medium' ? 'secondary' : 'outline'}>
                        {alert.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={alert.status === 'open' ? 'default' : alert.status === 'investigating' ? 'secondary' : alert.status === 'acknowledged' ? 'outline' : 'destructive'}>
                        {alert.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{alert.source}</TableCell>
                    <TableCell className="text-muted-foreground">{alert.time}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
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
    'inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
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
const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(({ className, ...props }, ref) => (
  <input ref={ref} className={cn('flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50', className)} {...props} />
))
Input.displayName = 'Input'

const Select = ({ children, ...props }: React.SelectHTMLAttributes<HTMLSelectElement>) => <select {...props}>{children}</select>
const SelectTrigger = ({ children, className, ...props }: { children: React.ReactNode; className?: string } & React.ButtonHTMLAttributes<HTMLButtonElement>) => (
  <button className={cn('flex h-10 w-full items-center justify-between rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50', className)} {...props}>{children}</button>
)
const SelectContent = ({ children, className, ...props }: { children: React.ReactNode; className?: string } & React.HTMLAttributes<HTMLDivElement>) => <div className={cn('relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-md border border-input bg-popover text-popover-foreground shadow-md', className)} {...props}>{children}</div>
const SelectItem = ({ value, children, ...props }: { value: string; children: React.ReactNode } & React.HTMLAttributes<HTMLOptionElement>) => <option value={value} {...props}>{children}</option>
const SelectValue = ({ children, ...props }: { children: React.ReactNode } & React.HTMLAttributes<HTMLSpanElement>) => <span {...props}>{children}</span>

const Table = ({ children, className }: { children: React.ReactNode; className?: string }) => <div className={cn('w-full caption-bottom text-sm', className)}>{children}</div>
const TableHeader = ({ children, className }: { children: React.ReactNode; className?: string }) => <thead className={cn('[&_tr]:border-b', className)}>{children}</thead>
const TableBody = ({ children, className }: { children: React.ReactNode; className?: string }) => <tbody className={cn('[&_tr:last-child]:border-0', className)}>{children}</tbody>
const TableRow = ({ children, className }: { children: React.ReactNode; className?: string }) => <tr className={cn('border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted', className)}>{children}</tr>
const TableHead = ({ children, className, ...props }: { children: React.ReactNode; className?: string } & React.ThHTMLAttributes<HTMLTableCellElement>) => <th className={cn('h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0', className)} {...props}>{children}</th>
const TableCell = ({ children, className, ...props }: { children: React.ReactNode; className?: string } & React.TdHTMLAttributes<HTMLTableCellElement>) => <td className={cn('p-4 align-middle [&:has([role=checkbox])]:pr-0', className)} {...props}>{children}</td>

import { ChevronUp, ChevronDown } from 'lucide-react'