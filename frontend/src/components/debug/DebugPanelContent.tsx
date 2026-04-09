'use client'

import { useGWAStore } from '@/store/useGWAStore'
import { LiveStatePanel } from './LiveStatePanel'
import { AgentStream } from './AgentStream'
import { DebugEvent } from '@/lib/types'

const AGENTS = ['attention', 'generator', 'critic', 'meta'] as const

function groupByTickAndAgent(events: DebugEvent[]) {
  const ticks: Map<number, Map<string, DebugEvent[]>> = new Map()
  for (const e of events) {
    if (!ticks.has(e.tick)) ticks.set(e.tick, new Map())
    const agentMap = ticks.get(e.tick)!
    if (!agentMap.has(e.agent)) agentMap.set(e.agent, [])
    agentMap.get(e.agent)!.push(e)
  }
  return ticks
}

export function DebugPanelContent() {
  const { debugEvents, streaming, currentTicks } = useGWAStore()

  const grouped = groupByTickAndAgent(debugEvents)
  const tickNums = Array.from(grouped.keys()).sort((a, b) => a - b)

  // Determine current streaming tick (latest in currentTicks or debugEvents)
  const latestTick = currentTicks[currentTicks.length - 1]?.tick
  const latestDebugTick = debugEvents[debugEvents.length - 1]?.tick

  return (
    <div className="flex flex-col gap-0 p-4">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <span
          className={`w-2 h-2 rounded-full shrink-0 ${streaming ? 'animate-pulse-dot' : ''}`}
          style={{ backgroundColor: streaming ? 'var(--accent-danger)' : 'var(--border-accent)' }}
        />
        <span className="text-[10px] font-mono tracking-widest uppercase text-[var(--text-secondary)]">
          Debug Console
        </span>
      </div>

      {/* Live State */}
      <div className="mb-4">
        <p className="text-[9px] font-mono tracking-widest uppercase text-[var(--text-muted)] mb-2">
          live state
        </p>
        <LiveStatePanel />
      </div>

      <div className="border-t border-[var(--border-subtle)] mb-4" />

      {/* Agent Streams by Tick */}
      <p className="text-[9px] font-mono tracking-widest uppercase text-[var(--text-muted)] mb-3">
        agent streams
      </p>

      {tickNums.length === 0 && (
        <p className="text-[10px] text-[var(--text-muted)] font-mono text-center py-4">
          {streaming ? 'waiting for agents…' : 'no debug data yet'}
        </p>
      )}

      {tickNums.map((tick) => {
        const agentMap = grouped.get(tick)!
        const isCurrentTick = tick === latestDebugTick
        return (
          <div key={tick} className="mb-4">
            {/* Tick divider */}
            <div className="flex items-center gap-2 mb-2">
              <span
                className="text-[9px] font-mono tracking-widest uppercase"
                style={{ color: isCurrentTick ? 'var(--accent-primary)' : 'var(--text-muted)' }}
              >
                TICK {tick}
              </span>
              <div className="flex-1 h-px bg-[var(--border-subtle)]" />
            </div>

            <div className="flex flex-col gap-3">
              {AGENTS.map((agent) => (
                <AgentStream
                  key={agent}
                  agent={agent}
                  events={agentMap.get(agent) ?? []}
                  streaming={streaming && isCurrentTick}
                />
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}
