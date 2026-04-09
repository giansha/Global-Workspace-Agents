'use client'

import { useGWAStore } from '@/store/useGWAStore'

export function DebugToggleBar() {
  const { debugMode, setDebugMode } = useGWAStore()

  return (
    <div className="h-8 px-4 flex items-center justify-end border-b border-[var(--border-subtle)] bg-[var(--bg-surface)] shrink-0">
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
