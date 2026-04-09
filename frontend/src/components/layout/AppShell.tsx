'use client'

import { useGWAStore } from '@/store/useGWAStore'
import { useIdleStream } from '@/hooks/useIdleStream'
import { Sidebar } from './Sidebar'
import { DebugSidebar } from './DebugSidebar'
import { DebugToggleBar } from './DebugToggleBar'
import { ConversationPanel } from '@/components/chat/ConversationPanel'

export function AppShell() {
  const { debugMode, engineInitialized } = useGWAStore()
  useIdleStream(engineInitialized)

  return (
    <div className="flex h-full bg-[var(--bg-base)]">
      <Sidebar />
      <main className="flex-1 min-w-0 h-full flex flex-col">
        <DebugToggleBar />
        <div className="flex-1 min-h-0">
          <ConversationPanel />
        </div>
      </main>
      {debugMode && <DebugSidebar />}
    </div>
  )
}
