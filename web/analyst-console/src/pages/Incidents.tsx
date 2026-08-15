import React from 'react'
import { cn } from '../utils'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { Badge } from './ui/Badge'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/Select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/Table'
import { FileText, Search, Filter, ChevronDown, ChevronUp, Plus } from 'lucide-react'

const mockIncidents = [
  { id: 'INC-001', title: 'Suspicious lateral movement detected', severity: 'critical', status: 'investigating', commander: 'analyst-1', created: '2024-01-15T10:30:00Z' },
  { id: 'INC-002', title: 'Potential data exfiltration via DNS', severity: 'high', status: 'contained', commander: 'analyst-2', created: '2024-01-15T08:15:00Z' },
  { id: 'INC-003', title: 'Cryptominer detected on worker node', severity: 'high', status: 'open', commander: 'analyst-1', created: '2024-01-14T15:20:00Z' },
  { id: 'INC-004', title: 'Suspicious container privilege escalation', severity: 'critical', status: 'contained', commander: 'analyst-3', created: '2024-01-14T09:45:00Z' },
  { id: 'INC-005', title: 'C2 beaconing detected from internal host', severity: 'high', status: 'investigating', commander: 'analyst-2', created: '2024-01-13T14:30:00Z' },
]

export function Incidents() {
  const [search, setSearch] = React.useState('')
  const [severityFilter, setSeverityFilter] = React.useState('all')
  const [statusFilter, setStatusFilter] = React.useState('all')

  const filteredIncidents = mockIncidents.filter(incident => {
    const matchesSearch = incident.title.toLowerCase().includes(search.toLowerCase())
    const matchesSeverity = severityFilter === 'all' || incident.severity === severityFilter
    const matchesStatus = statusFilter === 'all' || incident.status === statusFilter
    return matchesSearch && matchesSeverity && matchesStatus
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Incidents</h1>
          <p className="text-muted-foreground">Manage and track security incidents</p>
        </div>
        <Button className="hidden sm:flex" onClick={() => {}}>
          <Plus className="mr-2 h-4 w-4" />
          New Incident
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search incidents..." value={search} onChange={(e) => setSearch(e.target.value)} className="pl-10" />
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
              <SelectItem value="contained">Contained</SelectItem>
              <SelectItem value="resolved">Resolved</SelectItem>
              <SelectItem value="closed">Closed</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Incidents
            <span className="text-sm text-muted-foreground">Showing {mockIncidents.length} incidents</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  {['Title', 'Severity', 'Status', 'Commander', 'Created'].map((col) => (
                    <TableHead key={col} className="cursor-pointer select-none hover:bg-accent">
                      {col}
                    </TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockIncidents.map((incident) => (
                  <TableRow key={incident.id}>
                    <TableCell className="font-medium">{incident.title}</TableCell>
                    <TableCell>
                      <Badge variant={incident.severity === 'critical' ? 'destructive' : incident.severity === 'high' ? 'default' : incident.severity === 'medium' ? 'secondary' : 'outline'}>
                        {incident.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={incident.status === 'open' ? 'default' : incident.status === 'investigating' ? 'secondary' : incident.status === 'contained' ? 'outline' : 'destructive'}>
                        {incident.status}
                      </Badge>
                    </TableCell>
                    <TableCell>{incident.commander}</TableCell>
                    <TableCell className="text-muted-foreground">{new Date(incident.created).toLocaleString()}</TableCell>
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
    'inline-flex items-center justify-center rounded-lg text-sm font-medium transition-colors focus-ring disabled:opacity-50 disabled:pointer-events-none',
    {
      'bg-primary text-primary-foreground hover:bg-primary/90': 'default',
      'bg-destructive text-destructive-foreground hover:bg-destructive/90': 'destructive',
      'bg-secondary text-secondary-foreground hover:bg-secondary/80': 'secondary',
      'border border-input bg-background hover:bg-accent hover:text-accent-foreground': 'outline',
      'hover:bg-accent hover:text-accent-foreground': 'ghost',
      'text-primary underline-offset-4 hover:underline': 'link',
    },
    variant === 'default' && 'bg-primary text-primary-foreground hover:bg-primary/90',
    variant === 'destructive' && 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
    variant === 'secondary' && 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
    variant === 'outline' && 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
    variant === 'ghost' && 'hover:bg-accent hover:text-accent-foreground',
    variant === 'link' && 'text-primary underline-offset-4 hover:underline',
    className
  )} {...props}>{children}</button>
)
const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(({ className, ...props }, ref) => (
  <input ref={ref} className={cn('flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50', className)} {...props} ref={ref} />
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

import { Search } from 'lucide-react'