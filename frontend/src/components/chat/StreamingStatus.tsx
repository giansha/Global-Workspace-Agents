'use client'

import { useGWAStore } from '@/store/useGWAStore'

export function StreamingStatus() {
  const { streaming, currentTicks } = useGWAStore()

  if (!streaming) return null

  const tickCount = currentTicks.length
  const lastTick = currentTicks[tickCount - 1]

  return (
    <div className="flex items-center gap-3 px-4 py-2 bg-[var(--bg-surface)] border-t border-[var(--border-subtle)]">
      <span className="w-2 h-2 rounded-full bg-[var(--accent-warning)] animate-pulse-dot shrink-0" />
      <span className="text-xs font-mono text-[var(--text-secondary)]">
        {tickCount === 0
          ? 'Initializing cognitive tick…'
          : lastTick?.transition_tag === 'RESPONSE'
          ? 'Formulating response…'
          : `Tick ${tickCount} — H(W) ${lastTick?.entropy?.toFixed(3)} · T_gen ${lastTick?.T_gen?.toFixed(3)}`}
      </span>
    </div>
  )
}
