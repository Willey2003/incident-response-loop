import React from 'react'
import { useAuth } from '../contexts/AuthContext'
import { cn } from '../utils'
import { Menu, Bell, User, LogOut, Search, Shield, Brain, AlertTriangle } from 'lucide-react'

interface HeaderProps {
  onMenuClick: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const { user, logout } = useAuth()

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4 lg:px-6">
      <button
        onClick={onMenuClick}
        className="lg:hidden p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="flex-1 flex items-center justify-between gap-4">
        <div className="flex-1 max-w-md hidden sm:block">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="search"
              placeholder="Search alerts, incidents, runbooks..."
              className="w-full h-9 pl-10 pr-4 rounded-lg bg-muted/50 border border-border/50 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:bg-background"
              placeholder="Search alerts, incidents, runbooks..."
            />
          </div>
        </div>

        <div className="flex items-center gap-2 lg:gap-4">
          <button
            className="p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
            aria-label="Search"
          >
            <Search className="h-5 w-5" />
          </button>

          <button
            className="p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors relative"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-destructive text-[10px] font-medium text-white">
              3
            </span>
          </button>

          <div className="hidden lg:flex items-center gap-3 pl-4 border-l border-border">
            <div className="text-right">
              <p className="text-sm font-medium text-foreground">{'user?.username || 'User'}</p>
              <p className="text-xs text-muted-foreground">
                {'user?.roles?.[0] || 'User'}
              </p>
            </div>
            <div className="relative">
              <button className="flex items-center gap-2 p-1 rounded-lg hover:bg-accent transition-colors">
                <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                  <Shield className="h-4 w-4 text-primary" />
                </div>
              </button>
            </div>
          </div>

          <div className="lg:hidden flex items-center gap-2">
            <button
              onClick={onMenuClick}
              className="p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}