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
    // Use a flag to prevent double-sending when both beforeunload and pagehide
    // fire for the same navigation event (they do on desktop Chrome/Firefox).
    let beaconSent = false
    const sendClose = () => {
      if (beaconSent) return
      beaconSent = true
      const sid = sessionStorage.getItem('gwa_session_id')
      if (!sid) return
      navigator.sendBeacon(`${BASE}/api/session/close?session_id=${encodeURIComponent(sid)}`)
    }
    // beforeunload: fires reliably on desktop browsers for tab close / refresh.
    // pagehide: fires on mobile browsers where beforeunload is suppressed,
    //           and also covers bfcache navigations on Safari.
    window.addEventListener('beforeunload', sendClose)
    window.addEventListener('pagehide', sendClose)
    return () => {
      window.removeEventListener('beforeunload', sendClose)
      window.removeEventListener('pagehide', sendClose)
    }
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
