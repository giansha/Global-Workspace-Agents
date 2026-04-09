'use client'

import { useGWAStore } from '@/store/useGWAStore'
import { enableIdle, disableIdle } from '@/lib/api'

export function DebugToggleBar() {
  const { debugMode, setDebugMode, engineInitialized, idleEnabled, setIdleEnabled } = useGWAStore()

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
