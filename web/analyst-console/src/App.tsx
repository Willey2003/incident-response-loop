import React, { useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './pages/Dashboard'
import { Alerts } from './pages/Alerts'
import { Incidents } from './pages/Incidents'
import { Response } from './pages/Response'
import { AIInvestigation } from './pages/AIInvestigation'
import { EmulationLab } from './pages/EmulationLab'
import { Settings } from './pages/Settings'
import { Login } from './pages/Login'
import { useAuth } from './contexts/AuthContext'
import { Toaster } from 'react-hot-toast'

function App() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-muted-foreground">Loading AegisForge...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Login />
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/*"
        element={
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="/incidents" element={<Incidents />} />
              <Route path="/response" element={<Response />} />
              <Route path="/ai-investigation" element={<AIInvestigation />} />
              <Route path="/emulation-lab" element={<EmulationLab />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </Layout>
        }
      />
    </Routes>
  )
}

export default App