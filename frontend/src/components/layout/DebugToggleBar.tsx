'use client'

import { useGWAStore } from '@/store/useGWAStore'
import { enableIdle, disableIdle } from '@/lib/api'
import { downloadLog } from '@/lib/exportLog'

export function DebugToggleBar() {
  const {
    debugMode, setDebugMode,
    engineInitialized,
    idleEnabled, setIdleEnabled,
    memoryPanelOpen, setMemoryPanelOpen,
    conversation, workspaceData,
  } = useGWAStore()

  const handleExportLog = () => {
    downloadLog(conversation, workspaceData)
  }

  const handleIdleToggle = async () => {
    if (idleEnabled) {
      await disableIdle()
      setIdleEnabled(false)
    } else {
      await enableIdle()
      setIdleEnabled(true)
    }
  }

  return (
    <div className="h-8 px-4 flex items-center justify-end border-b border-[var(--border-subtle)] bg-[var(--bg-surface)] shrink-0 gap-4">
      <button
        onClick={handleExportLog}
        className="flex items-center gap-1.5 text-[10px] font-mono tracking-widest uppercase transition-colors cursor-pointer mr-auto"
        style={{ color: 'var(--text-muted)' }}
      >
        <span>↓</span>
        <span>EXPORT LOG</span>
      </button>
      <button
        onClick={() => setMemoryPanelOpen(!memoryPanelOpen)}
        disabled={!engineInitialized}
        className="flex items-center gap-1.5 text-[10px] font-mono tracking-widest uppercase transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
        style={{ color: memoryPanelOpen ? 'var(--accent-secondary, #8b5cf6)' : 'var(--text-muted)' }}
      >
        <span>{memoryPanelOpen ? '●' : '○'}</span>
        <span>MEMORY</span>
      </button>
      <button
        onClick={handleIdleToggle}
        disabled={!engineInitialized}
        className="flex items-center gap-1.5 text-[10px] font-mono tracking-widest uppercase transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
        style={{ color: idleEnabled ? 'var(--accent-primary)' : 'var(--text-muted)' }}
      >
        <span>{idleEnabled ? '●' : '○'}</span>
        <span>IDLE</span>
      </button>
      <button
        onClick={() => setDebugMode(!debugMode)}
        className="flex items-center gap-1.5 text-[10px] font-mono tracking-widest uppercase transition-colors cursor-pointer"
        style={{ color: debugMode ? 'var(--accent-danger)' : 'var(--text-muted)' }}
      >
        <span>{debugMode ? '●' : '○'}</span>
        <span>DEBUG</span>
      </button>
    </div>
  )
}
