'use client'

import { useEffect } from 'react'
import { useGWAStore } from '@/store/useGWAStore'
import { useIdleStream } from '@/hooks/useIdleStream'
import { Sidebar } from './Sidebar'
import { DebugSidebar } from './DebugSidebar'
import { DebugToggleBar } from './DebugToggleBar'
import { WorkspacePanel } from './WorkspacePanel'
import { ConversationPanel } from '@/components/chat/ConversationPanel'

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export function AppShell() {
  const { debugMode, engineInitialized } = useGWAStore()
  useIdleStream(engineInitialized)

  useEffect(() => {
    const handleUnload = () => {
      const sid = sessionStorage.getItem('gwa_session_id')
      if (!sid) return
      navigator.sendBeacon(`${BASE}/api/session?session_id=${encodeURIComponent(sid)}`)
    }
    window.addEventListener('beforeunload', handleUnload)
    return () => window.removeEventListener('beforeunload', handleUnload)
  }, [])

  return (
    <div className="flex h-full bg-[var(--bg-base)]">
      <Sidebar />
      <main className="flex-1 min-w-0 h-full flex flex-col relative">
        <DebugToggleBar />
        <WorkspacePanel />
        <div className="flex-1 min-h-0">
          <ConversationPanel />
        </div>
      </main>
      {debugMode && <DebugSidebar />}
    </div>
  )
}
