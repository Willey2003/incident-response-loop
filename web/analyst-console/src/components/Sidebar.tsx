import React from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { cn } from '../utils'
import {
  LayoutDashboard,
  AlertTriangle,
  FileText,
  Shield,
  Brain,
  FlaskConical,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  FlaskRound,
} from 'lucide-react'

interface SidebarProps {
  open: boolean
  onClose: () => void
}

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/alerts', label: 'Alerts', icon: AlertTriangle, badge: 3 },
  { path: '/incidents', label: 'Incidents', icon: FileText },
  { path: '/response', label: 'Response', icon: Shield },
  { path: '/ai-investigation', label: 'AI Investigation', icon: Brain },
  { path: '/emulation-lab', label: 'Emulation Lab', icon: FlaskConical },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const location = useLocation()

  return (
    <>
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 bg-card border-r border-border transition-all duration-200 ease-in-out',
          'flex flex-col',
          'lg:translate-x-0',
          open ? 'w-64' : 'w-16'
        )}
        aria-label="Main navigation"
      >
        <div className="flex h-16 items-center justify-between px-4 border-b border-border">
          {open && (
            <NavLink to="/dashboard" className="flex items-center gap-2 font-semibold text-lg text-foreground">
              <ShieldAlert className="h-6 w-6 text-primary" />
              <span>AegisForge</span>
            </NavLink>
          }
          {!open && (
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
              aria-label="Expand sidebar"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          )}
        </div>

        <nav className="flex-1 overflow-y-auto p-4 space-y-1" aria-label="Main navigation">
          {open ? (
            <ul className="space-y-1" role="list">
              {navItems.map((item) => (
                <li key={item.path}>
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-primary text-primary-foreground'
                          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                      )
                    }
                  >
                    <item.icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                    <span>{item.label}</span>
                    {item.badge && (
                      <span className="ml-auto px-2 py-0.5 text-xs font-medium bg-primary/10 text-primary rounded-full">
                        {item.badge}
                      </span>
                    )}
                  </NavLink>
                ))}
            </ul>
          ) : (
            <ul className="space-y-1" role="list">
              {navItems.map((item) => (
                <li key={item.path}>
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center justify-center p-2 rounded-lg transition-colors',
                        isActive
                          ? 'bg-primary text-primary-foreground'
                          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                      )
                    }
                    title={item.label}
                    aria-label={item.label}
                  >
                    <item.icon className="h-5 w-5" aria-hidden="true" />
                    {item.badge && (
                      <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center px-1 text-[10px] font-medium bg-primary/10 text-primary rounded-full">
                        {item.badge}
                      </span>
                    )}
                  </NavLink>
                </li>
              ))}
            </ul>
          )}
        </nav>

        <div className="p-4 border-t border-border">
          <div className="rounded-lg bg-muted/50 p-3">
            <p className="text-xs text-muted-foreground text-center">
              AegisForge v1.0.0
            </p>
          </div>
        </div>
      </aside>

      {!open && (
        <button
          onClick={() => onClose(false)}
          className="fixed left-16 top-16 z-40 p-2 rounded-lg bg-card border border-border shadow-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors lg:hidden"
          aria-label="Open sidebar"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
      )}
    </>
  )
}