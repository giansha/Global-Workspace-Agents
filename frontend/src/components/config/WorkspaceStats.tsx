'use client'

import { useGWAStore } from '@/store/useGWAStore'
import { useWorkspaceStats } from '@/hooks/useWorkspaceStats'
import { MetricBar } from '@/components/ui/MetricBar'

export function WorkspaceStats() {
  useWorkspaceStats()
  const stats = useGWAStore((s) => s.stats)
  const config = useGWAStore((s) => s.config)

  if (!stats?.initialized) {
    return (
      <div className="text-xs text-[var(--text-muted)] italic px-1">
        Engine not initialized
      </div>
    )
  }

  const maxEntropy = Math.log(config.K || 5)
  const maxTgen = config.T_base + config.alpha

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider">Workspace</p>
      <div className="grid grid-cols-3 gap-2 text-center">
        <Stat label="STM" value={stats.stm_tokens.toLocaleString()} unit="tok" />
        <Stat label="LTM" value={String(stats.ltm_documents)} unit="docs" />
        <Stat label="Ticks" value={String(stats.total_ticks)} unit="" />
      </div>
      <MetricBar label="H(W)" value={stats.last_entropy} max={maxEntropy} color="var(--accent-cyan)" />
      <MetricBar label="T_gen" value={stats.last_T_gen} max={maxTgen} color="var(--accent-warning)" />
    </div>
  )
}

function Stat({ label, value, unit }: { label: string; value: string; unit: string }) {
  return (
    <div className="flex flex-col items-center py-2 rounded-md bg-[var(--bg-elevated)] border border-[var(--border-subtle)]">
      <span className="text-xs text-[var(--text-muted)]">{label}</span>
      <span className="text-sm font-mono text-[var(--text-primary)] font-semibold">{value}</span>
      {unit && <span className="text-[10px] text-[var(--text-muted)]">{unit}</span>}
    </div>
  )
}
