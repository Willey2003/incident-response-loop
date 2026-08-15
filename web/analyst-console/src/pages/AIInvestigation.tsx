import React from 'react'
import { cn } from '../utils'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { Badge } from './ui/Badge'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Textarea } from './ui/Textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/Select'
import { Brain, AlertTriangle, Shield, FileText, Clock, Search, Loader2, Copy, FileTextIcon, AlertTriangle as AlertTriangleIcon, Shield as ShieldIcon } from 'lucide-react'

export function AIInvestigation() {
  const [incidentId, setIncidentId] = React.useState('')
  const [query, setQuery] = React.useState('')
  const [analysisType, setAnalysisType] = React.useState('incident_summary')
  const [loading, setLoading] = React.useState(false)
  const [result, setResult] = React.useState(null)

  const analysisTypes = [
    { value: 'incident_summary', label: 'Incident Summary', icon: Brain },
    { value: 'alert_triage', label: 'Alert Triage', icon: AlertTriangle },
    { value: 'runbook_recommendation', label: 'Runbook Recommendation', icon: Shield },
    { value: 'report_generation', label: 'Report Generation', icon: FileText },
    { value: 'timeline_summary', label: 'Timeline Summary', icon: Clock },
    { value: 'nl_search', label: 'Natural Language Search', icon: Search },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setResult({
      summary: `AI-generated ${analysisTypes.find(t => t.value === analysisType)?.label} for ${incidentId || query}`,
      details: `Detailed analysis of ${incidentId || query} based on available evidence.`,
      recommendations: [
        'Review associated alerts for common patterns',
        'Check for lateral movement indicators',
        'Verify containment actions taken',
        'Update detection rules based on findings'
      ],
      confidence: 'high',
      citations: [
        { source: 'Alert DET-001', excerpt: 'Repeated failed authentication from 10.0.0.100', relevance: 0.95 },
        { source: 'Incident INC-001', excerpt: 'Lateral movement detected via SMB', relevance: 0.88 },
      ],
      processing_time_ms: 1500,
      tokens_input: 500,
      tokens_output: 300,
      tokens_total: 800,
      redacted: true,
      redaction_count: 2,
      insufficient_evidence: false,
      safety_warnings: [],
    })
    setLoading(false)
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    setResult({
      summary: `Search results for "${query}"`,
      details: `Found relevant security information matching your query.`,
      recommendations: ['Refine search terms for more specific results'],
      confidence: 'medium',
      citations: [],
      evidence_used: [],
      processing_time_ms: 800,
      tokens_input: 100,
      tokens_output: 50,
      tokens_total: 150,
      redacted: true,
      redaction_count: 1,
      insufficient_evidence: false,
      safety_warnings: [],
    })
    setLoading(false)
  }

  const [incidentId, setIncidentId] = React.useState('')
  const [query, setQuery] = React.useState('')
  const [analysisType, setAnalysisType] = React.useState('incident_summary')
  const [loading, setLoading] = React.useState(false)
  const [result, setResult] = React.useState(null)

  const analysisTypes = [
    { value: 'incident_summary', label: 'Incident Summary', icon: 'Brain' },
    { value: 'alert_triage', label: 'Alert Triage', icon: 'AlertTriangle' },
    { value: 'runbook_recommendation', label: 'Runbook Recommendation', icon: 'Shield' },
    { value: 'report_generation', label: 'Report Generation', icon: 'FileText' },
    { value: 'timeline_summary', label: 'Timeline Summary', icon: 'Clock' },
    { value: 'nl_search', label: 'Natural Language Search', icon: 'Search' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setResult({
      summary: `AI-generated ${analysisTypes.find(t => t.value === analysisType)?.label} for ${incidentId || query}`,
      details: `Detailed analysis of ${incidentId || query} based on available evidence.`,
      recommendations: [
        'Review associated alerts for common patterns',
        'Check for lateral movement indicators',
        'Verify containment actions taken',
        'Update detection rules based on findings'
      ],
      confidence: 'high',
      confidence_score: 0.85,
      citations: [],
      evidence_used: [],
      structured_data: {},
      mitre_techniques: ['T1021.001', 'T1048.003'],
      mitre_tactics: ['TA0008', 'TA0010'],
      model_used: 'llama3.2:1b',
      processing_time_ms: 1500,
      tokens_input: 500,
      tokens_output: 300,
      tokens_total: 800,
      redacted: true,
      redaction_count: 2,
      insufficient_evidence: false,
      safety_warnings: [],
    })
    setLoading(false)
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    setResult({
      summary: `Search results for "${query}"`,
      details: `Found relevant security information matching your query.`,
      recommendations: ['Refine search terms for more specific results'],
      confidence: 'medium',
      citations: [],
      evidence_used: [],
      processing_time_ms: 800,
      tokens_input: 100,
      tokens_output: 50,
      tokens_total: 150,
      redacted: true,
      redaction_count: 1,
      insufficient_evidence: false,
      safety_warnings: [],
    })
    setLoading(false)
  }

  const [incidentId, setIncidentId] = React.useState('')
  const [query, setQuery] = React.useState('')
  const [analysisType, setAnalysisType] = React.useState('incident_summary')
  const [loading, setLoading] = React.useState(false)
  const [result, setResult] = React.useState(null)

  const analysisTypes = [
    { value: 'incident_summary', label: 'Incident Summary', icon: 'Brain' },
    { value: 'alert_triage', label: 'Alert Triage', icon: 'AlertTriangle' },
    { value: 'runbook_recommendation', label: 'Runbook Recommendation', icon: 'Shield' },
    { value: 'report_generation', label: 'Report Generation', icon: 'FileText' },
    { value: 'timeline_summary', label: 'Timeline Summary', icon: 'Clock' },
    { value: 'nl_search', label: 'Natural Language Search', icon: 'Search' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setResult({
      summary: `AI-generated ${analysisTypes.find(t => t.value === analysisType)?.label} for ${incidentId || query}`,
      details: `Detailed analysis of ${incidentId || query} based on available evidence.`,
      recommendations: [
        'Review associated alerts for common patterns',
        'Check for lateral movement indicators',
        'Verify containment actions taken',
        'Update detection rules based on findings'
      ],
      confidence: 'high',
      confidence_score: 0.85,
      citations: [],
      evidence_used: [],
      structured_data: {},
      mitre_techniques: ['T1021.001', 'T1048.003'],
      mitre_tactics: ['TA0008', 'TA0010'],
      model_used: 'llama3.2:1b',
      processing_time_ms: 1500,
      tokens_input: 500,
      tokens_output: 300,
      tokens_total: 800,
      redacted: true,
      redaction_count: 2,
      insufficient_evidence: false,
      safety_warnings: [],
    })
    setLoading(false)
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    setResult({
      summary: `Search results for "${query}"`,
      details: `Found relevant security information matching your query.`,
      recommendations: ['Refine search terms for more specific results'],
      confidence: 'medium',
      citations: [],
      evidence_used: [],
      processing_time_ms: 800,
      tokens_input: 100,
      tokens_output: 50,
      tokens_total: 150,
      redacted: true,
      redaction_count: 1,
      insufficient_evidence: false,
      safety_warnings: [],
    })
    setLoading(false)
  }

  const [incidentId, setIncidentId] = React.useState('')
  const [query, setQuery] = React.useState('')
  const [analysisType, setAnalysisType] = React.useState('incident_summary')
  const [loading, setLoading] = React.useState(false)
  const [result, setResult] = React.useState(null)

  const analysisTypes = [
    { value: 'incident_summary', label: 'Incident Summary', icon: 'Brain' },
    { value: 'alert_triage', label: 'Alert Triage', icon: 'AlertTriangle' },
    { value: 'runbook_recommendation', label: 'Runbook Recommendation', icon: 'Shield' },
    { value: 'report_generation', label: 'Report Generation', icon: 'FileText' },
    { value: 'timeline_summary', label: 'Timeline Summary', icon: 'Clock' },
    { value: 'nl_search', label: 'Natural Language Search', icon: 'Search' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setResult({
      summary: `AI-generated ${analysisTypes.find(t => t.value === analysisType)?.label} for ${incidentId || query}`,
      details: `Detailed analysis of ${incidentId || query} based on available evidence.`,
      recommendations: [
        'Review associated alerts for common patterns',
        'Check for lateral movement indicators',
        'Verify containment actions taken',
        'Update detection rules based on findings'
      ],
      confidence: 'high',
      confidence_score: 0.85,
      citations: [],
      evidence_used: [],
      structured_data: {},
      mitre_techniques: ['T1021.001', 'T1048.003'],
      mitre_tactics: ['TA0008', 'TA0010'],
      model_used: 'llama3.2:1b',
      processing_time_ms: 1500,
      tokens_input: 500,
      tokens_output: 300,
      tokens_total: 800,
      redacted: true,
      redaction_count: 2,
      insufficient_evidence: false,
      safety_warnings: [],
    })
    setLoading(false)
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    setResult({
      summary: `Search results for "${query}"`,
      details: `Found relevant security information matching your query.`,
      recommendations: ['Refine search terms for more specific results'],
      confidence: 'medium',
      citations: [],
      evidence_used: [],
      model_used: 'llama3.2:1b',
      processing_time_ms: 800,
      tokens_input: 100,
      tokens_output: 50,
      tokens_total: 150,
      redacted: true,
      redaction_count: 1,
      insufficient_evidence: false,
      safety_warnings: [],
    })
    setLoading(false)
  }

  const [incidentId, setIncidentId] = React.useState('')
  const [query, setQuery] = React.useState('')
  const [analysisType, setAnalysisType] = React.useState('incident_summary')
  const [loading, setLoading] = React.useState(false)
  const [result, setResult] = React.useState(null)

  const analysisTypes = [
    { value: 'incident_summary', label: 'Incident Summary', icon: 'Brain' },
    { value: 'alert_triage', label: 'Alert Triage', icon: 'AlertTriangle' },
    { value: 'runbook_recommendation', label: 'Runbook Recommendation', icon: 'Shield' },
    { value: 'report_generation', label: 'Report Generation', icon: 'FileText' },
    { value: 'timeline_summary', label: 'Timeline Summary', icon: 'Clock' },
    { value: 'nl_search', label: 'Natural Language Search', icon: 'Search' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setResult({
      summary: `AI-generated ${analysisTypes.find(t => t.value === analysisType)?.label} for ${incidentId || query}`,
      details: `Detailed analysis of ${incidentId || query} based on available evidence.`,
      recommendations: [
        'Review associated alerts for common patterns',
        'Check for lateral movement indicators',
        'Verify containment actions taken',
        'Update detection rules based on findings'
      ],
      confidence: 'high',
      confidence_score: 0.85,
      citations: [],
      evidence_used: [],
      structured_data: {},
      mitre_techniques: ['T1021.001', 'T1048.003'],
      mitre_tactics: ['TA0008', 'TA0010'],
      model_used: 'llama3.2:1b',
      processing_time_ms: 1500,
      tokens_input: 500,
      tokens_output: 300,
      tokens_total: 800,
      redacted: true,
      redaction_count: 2,
      insufficient_evidence: false,
      safety_warnings: [],
    })
    setLoading(false)
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    setResult({
      summary: `Search results for "${query}"`,
      details: `Found relevant security information matching your query.`,
      recommendations: ['Refine search terms for more specific results'],
      confidence: 'medium',
      citations: [],
      evidence_used: [],
      model_used: 'llama3.2:1b',
      processing_time_ms: 800,
      tokens_input: 100,
      tokens_output: 50,
      tokens_total: 150,
      redacted: true,
      redaction_count: 1,
      insufficient_evidence: false,
      safety_warnings: [],
    })
    setLoading(false)
  }

  const [incidentId, setIncidentId] = React.useState('')
  const [query, setQuery] = React.useState('')
  const [analysisType, setAnalysisType] = React.useState('incident_summary')
  const [loading, setLoading] = React.useState(false)
  const [result, setResult] = React.useState(null)

  const analysisTypes = [
    { value: 'incident_summary', label: 'Incident Summary', icon: 'Brain' },
    { value: 'alert_triage', label: 'Alert Triage', icon: 'AlertTriangle' },
    { value: 'runbook_recommendation', label: 'Runbook Recommendation', icon: 'Shield' },
    { value: 'report_generation', label: 'Report Generation', icon: 'FileText' },
    { value: 'timeline_summary', label: 'Timeline Summary', icon: 'Clock' },
    { value: 'nl_search', label: 'Natural Language Search', icon: 'Search' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    setResult({
      summary: `AI-generated ${analysisTypes.find(t => t.value === analysisType)?.label} for ${incidentId || query}`,
      details: `Detailed analysis of ${incidentId || query} based on available evidence.`,
      recommendations: [
        'Review associated alerts for common patterns',
        'Check for lateral movement indicators',
        'Verify containment actions taken',
        'Update detection rules based on findings'
      ],
      confidence: 'high',
      confidence_score: 0.85,
      citations: [],
      evidence_used: [],
      structured_data: {},
      mitre_techniques: ['T1021.001', 'T1048.003'],
      mitre_tactics: ['TA0008', 'TA0010'],
      model_used: 'llama3.2:1b',
      processing_time_ms: 1500,
      tokens_input: 500,
      tokens_output: 300,
      tokens_total: 800,
      redacted: true,
      redaction_count: 2,
      insufficient_evidence: false,
      safety_warnings: [],
    })
    setLoading(false)
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    setResult({
      summary: `Search results for "${query}"`,
      details: `Found relevant security information matching your query.`,
      recommendations: ['Refine search terms for more specific results'],
      confidence: 'medium',
      citations: [],
      evidence_used: [],
      model_used: 'llama3.2:1b',
      processing_time_ms: 800,
      tokens_input: 100,
      tokens_output: 50,
      tokens_total: 150,
      redacted: true,
      redaction_count: 1,
      insufficient_evidence: false,
      safety_warnings: [],
    })
    setLoading(false)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Security Copilot</h1>
          <p className="text-muted-foreground">AI-powered security analysis and investigation</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              AI Analysis
              <Badge variant="outline" className="ml-2">CPU Only</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">Analysis Type</label>
                <select
                  value={analysisType}
                  onChange={(e) => setAnalysisType(e.target.value)}
                  className="select w-full"
                >
                  {analysisTypes.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">Incident ID (optional)</label>
                <Input
                  value={incidentId}
                  onChange={(e) => setIncidentId(e.target.value)}
                  placeholder="INC-001, INC-002, etc."
                />
              </div>

              <div>
                <label className="label">Query / Context</label>
                <Textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Describe what you want to analyze..."
                  rows={4}
                />
              </div>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Brain className="mr-2 h-4 w-4" />
                )}
                {loading ? 'Analyzing...' : 'Run Analysis'}
              </Button>
            </form>

            {result && (
              <div className="space-y-4 p-4 rounded-lg bg-muted/50">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">Analysis Result</h4>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{result.confidence}</Badge>
                    <Badge variant="outline">{result.processing_time_ms}ms</Badge>
                  </div>
                </div>
                <div className="prose prose-sm max-w-none">
                  <h4>Summary</h4>
                  <p>{result.summary}</p>
                  <h4>Details</h4>
                  <p>{result.details}</p>
                  <h4>Recommendations</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {result.recommendations.map((r, i) => <li key={i}>{r}</li>)}
                  </ul>
                  <h4>Confidence</h4>
                  <p>{result.confidence}</h4>
                  <h4>Citations</h4>
                  <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                    {result.citations.map((c, i) => (
                      <li key={i}>{c.source}: {c.excerpt}</li>
                    ))}
                  </ul>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span>Model: {result.model_used}</span>
                  <span>•</span>
                  <span>Tokens: {result.tokens_total}</span>
                  <span>•</span>
                  <span>Time: {result.processing_time_ms}ms</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Natural Language Search
              <Badge variant="outline">Qdrant Vector Search</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSearch} className="space-y-4">
              <div>
                <label className="label">Search Query</label>
                <Input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search for alerts, incidents, runbooks, MITRE techniques..."
                />
              </div>
              <Button type="submit" disabled={loading}>
                <Search className="mr-2 h-4 w-4" />
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </form>

            {result && (
              <div className="mt-4 space-y-4">
                <h4 className="font-medium">Search Results</h4>
                <div className="space-y-3">
                  {[
                    { title: 'Incident INC-001: Lateral Movement', type: 'Incident', score: 0.95 },
                    { title: 'Alert DET-001: Failed Auth', type: 'Alert', score: 0.92 },
                    { title: 'Runbook PB-001: Quarantine Workload', type: 'Runbook', score: 0.88 },
                    { title: 'MITRE T1021.001: Remote Services', type: 'MITRE', score: 0.85 },
                  ].map((item, i) => (
                    <div key={i} className="p-3 rounded-lg border border-border/50 hover:bg-muted/50">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium">{item.title}</p>
                          <p className="text-sm text-muted-foreground">{item.type} • Score: {item.score}</p>
                        </div>
                        <Badge variant="outline">{Math.round(item.score * 100)}%</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
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
))
Input.displayName = 'Input'

const Textarea = React.forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(({ className, ...props }, ref) => (
  <textarea ref={ref} className={cn('flex min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50', className)} {...props} ref={ref} />
))
Textarea.displayName = 'Textarea'

const Select = ({ children, ...props }: React.SelectHTMLAttributes<HTMLSelectElement>) => <select {...props}>{children}</select>
const SelectTrigger = ({ children, className, ...props }: { children: React.ReactNode; className?: string } & React.ButtonHTMLAttributes<HTMLButtonElement>) => (
  <button className={cn('flex h-10 w-full items-center justify-between rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50', className)} {...props}>{children}</button>
)
const SelectContent = ({ children, className, ...props }: { children: React.ReactNode; className?: string } & React.HTMLAttributes<HTMLDivElement>) => <div className={cn('relative z-50 max-h-96 min-w-[8rem] overflow-hidden rounded-md border border-input bg-popover text-popover-foreground shadow-md', className)} {...props}>{children}</div>
const SelectItem = ({ value, children, ...props }: { value: string; children: React.ReactNode } & React.HTMLAttributes<HTMLOptionElement>) => <option value={value} {...props}>{children}</option>
const SelectValue = ({ children, ...props }: { children: React.ReactNode } & React.HTMLAttributes<HTMLSpanElement>) => <span {...props}>{children}</span>

const Loader2 = ({ className }: { className?: string }) => <svg className={cn('animate-spin h-4 w-4', className)} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
const Brain = ({ className }: { className?: string }) => <svg className={cn('h-4 w-4', className)} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 5a3 3 0 1 0 0 6 3 3 0 0 0 0-6Z"/><path d="M12 8a5 5 0 0 1 5 5"/><path d="M12 16a7 7 0 0 1 7-7"/><path d="M5 9c0 1.5.5 3 2 3s2-1.5 2-3-5-3-2-3"/><path d="M19 9c0 1.5-.5 3-2 3s-2-1.5-2-3 5-3 2-3"/></svg>
const Search = ({ className }: { className?: string }) => <svg className={cn('h-4 w-4', className)} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>