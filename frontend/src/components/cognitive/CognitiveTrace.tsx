'use client'

import { useState } from 'react'
import { TickSnapshot } from '@/lib/types'
import { TickCard } from './TickCard'

export function CognitiveTrace({ ticks }: { ticks: TickSnapshot[] }) {
  const [open, setOpen] = useState(false)

  if (ticks.length === 0) return null

  return (
    <div className="mt-2">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 text-[10px] font-mono text-[var(--text-muted)] hover:text-[var(--accent-primary)] transition-colors cursor-pointer"
      >
        <span className="font-bold">{open ? '▼' : '▶'}</span>
        cognitive trace ({ticks.length} tick{ticks.length !== 1 ? 's' : ''})
      </button>
      {open && (
        <div className="mt-2 flex flex-col gap-2">
          {ticks.map((snap) => (
            <TickCard key={snap.tick} snap={snap} />
          ))}
        </div>
      )}
    </div>
  )
}
