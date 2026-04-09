'use client'

import { useEffect, useRef } from 'react'
import { DebugEvent } from '@/lib/types'

const AGENT_COLORS: Record<string, string> = {
  attention: 'var(--accent-cyan)',
  generator: 'var(--accent-primary)',
  critic: 'var(--accent-danger)',
  meta: 'var(--accent-secondary)',
}

const AGENT_LABELS: Record<string, string> = {
  attention: 'ATTENTION',
  generator: 'GENERATOR',
  critic: 'CRITIC',
  meta: 'META',
}

interface AgentStreamProps {
  agent: 'attention' | 'generator' | 'critic' | 'meta'
  events: DebugEvent[]
  streaming: boolean
}

export function AgentStream({ agent, events, streaming }: AgentStreamProps) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const color = AGENT_COLORS[agent]
  const label = AGENT_LABELS[agent]
  const text = events.map((e) => e.token).join('')
  const hasContent = text.length > 0
  const isActive = streaming && events.length > 0

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }, [events.length])

  return (
    <div className="flex flex-col gap-1">
      {/* Agent header */}
      <div className="flex items-center gap-2">
        <span
          className={`w-1.5 h-1.5 rounded-full shrink-0 ${isActive ? 'animate-pulse-dot' : ''}`}
          style={{ backgroundColor: isActive ? color : 'var(--border-accent)' }}
        />
        <span
          className="text-[9px] font-mono tracking-widest uppercase"
          style={{ color: hasContent ? color : 'var(--text-muted)' }}
        >
          {label}
        </span>
      </div>

      {/* Token stream output */}
      <div
        className="rounded overflow-y-auto max-h-28 p-2 bg-[var(--bg-base)] border border-[var(--border-subtle)]"
        style={{ minHeight: '2.5rem' }}
      >
        {hasContent ? (
          <>
            <pre
              className="text-[10px] font-mono whitespace-pre-wrap break-words leading-relaxed"
              style={{ color: 'var(--text-secondary)' }}
            >
              {text}
            </pre>
            <div ref={bottomRef} />
          </>
        ) : (
          <p className="text-[10px] font-mono text-[var(--text-muted)] italic">idle</p>
        )}
      </div>
    </div>
  )
}
