'use client'

import { useGWAStore } from '@/store/useGWAStore'
import { MetricBar } from '@/components/ui/MetricBar'

export function LiveStatePanel() {
  const { currentTicks, stats, streaming } = useGWAStore()

  const latest = currentTicks[currentTicks.length - 1]

  const entropy = latest?.entropy ?? stats?.last_entropy ?? 0
  const tGen = latest?.T_gen ?? stats?.last_T_gen ?? 0
  const stmTokens = latest?.stm_token_count ?? stats?.stm_tokens ?? 0
  const tickNum = latest?.tick ?? stats?.total_ticks ?? 0
  const compressed = latest?.compressed ?? false
  const tag = latest?.transition_tag

  return (
    <div className="flex flex-col gap-3">
      {/* Tick + STM row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-[var(--text-muted)] uppercase tracking-wider">Tick</span>
          <span className="text-sm font-mono text-[var(--text-primary)]">{tickNum}</span>
          {compressed && (
            <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-[var(--accent-warning)]/15 text-[var(--accent-warning)] border border-[var(--accent-warning)]/30">
              COMPRESSED
            </span>
          )}
        </div>
        {tag && (
          <span
            className={`text-[9px] font-mono px-1.5 py-0.5 rounded border ${
              tag === 'RESPONSE'
                ? 'bg-[var(--accent-secondary)]/15 text-[var(--accent-secondary)] border-[var(--accent-secondary)]/30'
                : tag === 'WEB_SEARCH'
                ? 'bg-[var(--accent-cyan)]/15 text-[var(--accent-cyan)] border-[var(--accent-cyan)]/30'
                : 'bg-[var(--accent-warning)]/15 text-[var(--accent-warning)] border-[var(--accent-warning)]/30'
            }`}
          >
            {tag}
          </span>
        )}
      </div>

      {/* STM tokens */}
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-mono text-[var(--text-muted)] uppercase tracking-wider">STM tokens</span>
        <span className="text-xs font-mono text-[var(--accent-cyan)]">{stmTokens}</span>
      </div>

      {/* Metric bars */}
      <MetricBar label="H(W)" value={entropy} max={1.609} color="var(--accent-cyan)" />
      <MetricBar label="T_gen" value={tGen} max={2.0} color="var(--accent-warning)" />

      {!streaming && !latest && (
        <p className="text-[10px] text-[var(--text-muted)] font-mono text-center pt-1">
          waiting for next tick…
        </p>
      )}
    </div>
  )
}
