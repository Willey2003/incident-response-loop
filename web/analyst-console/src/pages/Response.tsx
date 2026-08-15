import React from 'react'
import { cn } from '../utils'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { Badge } from './ui/Badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/Table'

const mockActions = [
  { id: '1', type: 'quarantine_workload', status: 'completed', target: 'webapp-pod-1', requestedBy: 'analyst-1', time: '10 min ago', dryRun: false },
  { id: '2', type: 'scale_deployment', status: 'pending_approval', target: 'malicious-deployment', requestedBy: 'analyst-2', time: '5 min ago', dryRun: true },
  { id: '3', type: 'revoke_service_account', status: 'approved', target: 'compromised-sa', requestedBy: 'analyst-1', time: '1 hour ago', dryRun: false },
  { id: '4', type: 'quarantine_workload', status: 'rolled_back', target: 'webapp-pod-2', requestedBy: 'analyst-3', time: '2 hours ago', dryRun: false },
]

export function Response() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Response Actions</h1>
          <p className="text-muted-foreground">Manage and track containment actions</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Response Actions
            <span className="text-sm text-muted-foreground">{mockActions.length} actions</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  {['Action', 'Target', 'Status', 'Requested By', 'Time', 'Dry Run', 'Actions'].map((col) => (
                    <TableHead key={col}>{col}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockActions.map((action) => (
                  <TableRow key={action.id}>
                    <TableCell>
                      <Badge variant={action.type === 'quarantine_workload' ? 'default' : action.type === 'scale_deployment' ? 'secondary' : 'outline'}>
                        {action.type.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-mono">{action.target}</TableCell>
                    <TableCell>
                      <Badge variant={
                        action.status === 'completed' ? 'default' :
                        action.status === 'pending_approval' ? 'secondary' :
                        action.status === 'approved' ? 'outline' :
                        action.status === 'rolled_back' ? 'destructive' : 'secondary'
                      }>
                        {action.status.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>{action.requestedBy}</TableCell>
                    <TableCell className="text-muted-foreground">{action.time}</TableCell>
                    <TableCell>
                      <Badge variant={action.dryRun ? 'outline' : 'default'}>
                        {action.dryRun ? 'Dry Run' : 'Live'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                      </div>
                    </TableCell>
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
const Table = ({ children, className }: { children: React.ReactNode; className?: string }) => <div className={cn('w-full caption-bottom text-sm', className)}>{children}</div>
const TableHeader = ({ children, className }: { children: React.ReactNode; className?: string }) => <thead className={cn('[&_tr]:border-b', className)}>{children}</thead>
const TableBody = ({ children, className }: { children: React.ReactNode; className?: string }) => <tbody className={cn('[&_tr:last-child]:border-0', className)}>{children}</tbody>
const TableRow = ({ children, className }: { children: React.ReactNode; className?: string }) => <tr className={cn('border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted', className)}>{children}</tr>
const TableHead = ({ children, className, ...props }: { children: React.ReactNode; className?: string } & React.ThHTMLAttributes<HTMLTableCellElement>) => <th className={cn('h-12 px-4 text-left align-middle font-medium text-muted-foreground [&:has([role=checkbox])]:pr-0', className)} {...props}>{children}</th>
const TableCell = ({ children, className, ...props }: { children: React.ReactNode; className?: string } & React.TdHTMLAttributes<HTMLTableCellElement>) => <td className={cn('p-4 align-middle [&:has([role=checkbox])]:pr-0', className)} {...props}>{children}</td>
const TableHeader = ({ children, className }: { children: React.ReactNode; className?: string }) => <thead className={cn('[&_tr]:border-b', className)}>{children}</thead>
const TableBody = ({ children, className }: { children: React.ReactNode; className?: string }) => <tbody className={cn('[&_tr:last-child]:border-0', className)}>{children}</tbody>
const TableRow = ({ children, className }: { children: React.ReactNode; className?: string }) => <tr className={cn('border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted', className)}>{children}</tr>