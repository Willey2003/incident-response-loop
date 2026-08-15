import React from 'react'
import { cn } from '../utils'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { Badge } from './ui/Badge'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Switch } from './ui/Switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/Tabs'
import { Shield, Key, Database, Cpu, Network, Bell, User, Save, Loader2 } from 'lucide-react'

export function Settings() {
  const [activeTab, setActiveTab] = React.useState('general')
  const [saving, setSaving] = React.useState(false)

  const handleSave = async () => {
    setSaving(true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    setSaving(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">Configure AegisForge platform settings</p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="ai">AI Copilot</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Platform Settings
                <Badge variant="outline">General</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="label">Platform Name</label>
                  <Input placeholder="AegisForge" defaultValue="AegisForge" />
                </div>
                <div className="space-y-2">
                  <label className="label">Environment</label>
                  <select className="select">
                    <option value="development">Development</option>
                    <option value="staging">Staging</option>
                    <option value="production" selected>Production</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="label">Log Level</label>
                  <select className="select">
                    <option value="debug">Debug</option>
                    <option value="info" selected>Info</option>
                    <option value="warn">Warn</option>
                    <option value="error">Error</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="label">Timezone</label>
                  <select className="select">
                    <option value="UTC" selected>UTC</option>
                    <option value="America/New_York">America/New_York</option>
                    <option value="Europe/London">Europe/London</option>
                    <option value="Asia/Tokyo">Asia/Tokyo</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end">
                <Button onClick={handleSave} disabled={saving}>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Save Changes
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Security Settings
                <Badge variant="outline">Security</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <label className="label">Require MFA for Admin</label>
                    <p className="text-sm text-muted-foreground">Require MFA for all administrative actions</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <label className="label">Require Approval for Response Actions</label>
                    <p className="text-sm text-muted-foreground">Require explicit approval before executing response actions</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <label className="label">Dry Run Mode by Default</label>
                    <p className="text-sm text-muted-foreground">Run all response actions in dry-run mode by default</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <label className="label">Enable AI Redaction</label>
                    <p className="text-sm text-muted-foreground">Automatically redact secrets, PII, and IPs before AI processing</p>
                  </div>
                  <Switch defaultChecked />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                API Keys & Tokens
                <Badge variant="outline">Authentication</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <h4 className="font-medium">API Keys</h4>
                <p className="text-sm text-muted-foreground">Manage API keys for external integrations</p>
              </div>
              <Button variant="outline">Generate New API Key</Button>
              <div className="space-y-2">
                <div className="flex items-center justify-between p-3 rounded-lg border border-border">
                  <div>
                    <p className="font-mono text-sm">aegisforge_sk_live_abc123...</p>
                    <p className="text-xs text-muted-foreground">Created: 2024-01-15 • Last used: 2 hours ago</p>
                  </div>
                  <Button variant="ghost" size="sm">Revoke</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="integrations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                External Integrations
                <Badge variant="outline">Integrations</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                {[
                  { name: 'Slack', icon: 'MessageSquare', status: 'connected', config: '2 channels' },
                  { name: 'PagerDuty', icon: 'AlertTriangle', status: 'disconnected', config: 'Not configured' },
                  { name: 'Jira', icon: 'Ticket', status: 'connected', config: '1 project' },
                  { name: 'Splunk', icon: 'Database', status: 'disconnected', config: 'Not configured' },
                  { name: 'Elasticsearch', icon: 'Database', status: 'connected', config: '3 indices' },
                  { name: 'Microsoft Teams', icon: 'Users', status: 'disconnected', config: 'Not configured' },
                ].map((integration) => (
                  <div key={integration.name} className="flex items-center justify-between p-4 rounded-lg border border-border/50">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <integration.icon className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-medium">{integration.name}</p>
                        <p className="text-sm text-muted-foreground">{integration.config}</p>
                      </div>
                    </div>
                    <span className={cn('badge px-2 py-1 text-xs', integration.status === 'connected' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600')}>
                      {integration.status}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ai" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                AI Copilot Configuration
                <Badge variant="outline">AI</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="label">LLM Model</label>
                  <select className="select">
                    <option value="llama3.2:1b" selected>Llama 3.2 1B (Recommended)</option>
                    <option value="phi3:mini">Phi-3 Mini</option>
                    <option value="qwen2:0.5b">Qwen2 0.5B</option>
                    <option value="gemma2:2b">Gemma 2 2B</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="label">Embedding Model</label>
                  <select className="select">
                    <option value="all-MiniLM-L6-v2" selected>all-MiniLM-L6-v2 (384-dim)</option>
                    <option value="all-mpnet-base-v2">all-mpnet-base-v2 (768-dim)</option>
                    <option value="bge-small-en-v1.5">BGE Small EN v1.5</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="label">Max Tokens</label>
                  <Input type="number" defaultValue="2048" min="256" max="8192" />
                </div>
                <div className="space-y-2">
                  <label className="label">Temperature</label>
                  <Input type="number" step="0.1" defaultValue="0.1" min="0" max="1" />
                </div>
              </div>
              <div className="space-y-4">
                <h4 className="font-medium">Redaction Settings</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <label className="label">Redact Secrets/API Keys</label>
                      <p className="text-sm text-muted-foreground">Automatically redact API keys, tokens, passwords before AI processing</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <label className="label">Redact PII</label>
                      <p className="text-sm text-muted-foreground">Redact emails, names, phone numbers</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <label className="label">Redact IP Addresses</label>
                      <p className="text-sm text-muted-foreground">Redact IPv4 and IPv6 addresses</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <label className="label">Redact Tokens/JWTs</label>
                      <p className="text-sm text-muted-foreground">Redact JWT tokens and bearer tokens</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Notification Preferences
                <Badge variant="outline">Notifications</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                {[
                  { title: 'Critical Alerts', desc: 'Immediate notification for critical severity alerts', default: true },
                  { title: 'High Severity Alerts', desc: 'Notification for high severity alerts', default: true },
                  { title: 'New Incidents', desc: 'Notify when new incidents are created', default: true },
                  { title: 'Response Action Required', desc: 'Notify when approval is needed for response actions', default: true },
                  { title: 'Incident Status Changes', desc: 'Notify on incident status changes', default: false },
                  { title: 'AI Analysis Complete', desc: 'Notify when AI analysis is complete', default: true },
                  { title: 'Emulation Run Complete', desc: 'Notify when emulation runs complete', default: false },
                  { title: 'System Health Alerts', desc: 'System health and performance alerts', default: true },
                ].map((notif) => (
                  <div key={notif.title} className="flex items-center justify-between">
                    <div className="space-y-1">
                      <label className="label">{notif.title}</label>
                      <p className="text-sm text-muted-foreground">{notif.desc}</p>
                    </div>
                    <Switch defaultChecked={notif.default} />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Advanced Settings
                <Badge variant="outline">Advanced</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <label className="label">Enable Debug Logging</label>
                    <p className="text-sm text-muted-foreground">Enable verbose debug logging for all services</p>
                  </div>
                  <Switch />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <label className="label">Enable Profiling Endpoints</label>
                    <p className="text-sm text-muted-foreground">Enable pprof/debug endpoints for performance analysis</p>
                  </div>
                  <Switch />
                </div>
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <label className="label">Enable Experimental Features</label>
                    <p className="text-sm text-muted-foreground">Enable experimental features that may be unstable</p>
                  </div>
                  <Switch />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Data Retention
                <Badge variant="outline">Data</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div className="space-y-2">
                  <label className="label">Alert Retention (days)</label>
                  <Input type="number" defaultValue="90" min="1" max="3650" />
                </div>
                <div className="space-y-2">
                  <label className="label">Incident Retention (days)</label>
                  <Input type="number" defaultValue="365" min="1" max="3650" />
                </div>
                <div className="space-y-2">
                  <label className="label">Evidence Retention (days)</label>
                  <Input type="number" defaultValue="2555" min="1" max="3650" />
                </div>
                <div className="space-y-2">
                  <label className="label">Audit Log Retention (days)</label>
                  <Input type="number" defaultValue="2555" min="1" max="3650" />
                </div>
                <div className="space-y-2">
                  <label className="label">Metrics Retention (days)</label>
                  <Input type="number" defaultValue="30" min="1" max="365" />
                </div>
                <div className="space-y-2">
                  <label className="label">Log Retention (days)</label>
                  <Input type="number" defaultValue="90" min="1" max="365" />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
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
const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(({ className, ...props }, ref) => (
  <input ref={ref} className={cn('flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50', className)} {...props} ref={ref} />
)
Input.displayName = 'Input'

const Switch = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement>>(({ className, checked, onChange, ...props }, ref) => (
  <button
    ref={ref}
    role="switch"
    aria-checked={checked}
    onChange={onChange}
    className={cn(
      'peer inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary data-[state=unchecked]:bg-input',
      className
    )}
    {...props}
    ref={ref}
  >
    <span className="pointer-events-none block h-5 w-5 shrink-0 rounded-full bg-background shadow-lg ring-0 transition-transform data-[state=checked]:translate-x-5 data-[state=unchecked]:translate-x-0" />
  </button>
)
Switch.displayName = 'Switch'

const Tabs = ({ children, value, onValueChange, ...props }: { children: React.ReactNode; value: string; onValueChange: (value: string) => void } & React.HTMLAttributes<HTMLDivElement>) => <div {...props}>{children}</div>
const TabsList = ({ children, className, ...props }: { children: React.ReactNode; className?: string } & React.HTMLAttributes<HTMLDivElement>) => <div className={cn('inline-flex h-10 items-center justify-center rounded-lg bg-muted p-1 text-muted-foreground', className)} {...props}>{children}</div>
const TabsTrigger = ({ children, value, ...props }: { children: React.ReactNode; value: string } & React.ButtonHTMLAttributes<HTMLButtonElement>) => <button className={cn('flex items-center justify-center rounded-lg px-3 py-1.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 data-[state=active]:bg-background data-[state=active]:text-foreground data-[state=active]:shadow-sm', value)} {...props}>{children}</button>
const TabsContent = ({ children, value, ...props }: { children: React.ReactNode; value: string } & React.HTMLAttributes<HTMLDivElement>) => <div {...props}>{children}</div>