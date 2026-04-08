import { TickSnapshot } from '@/lib/types'
import { TagBadge, Badge } from '@/components/ui/Badge'

const MAX_ENTROPY = Math.log(5) // ln(K=5) ≈ 1.609

interface Props {
  snap: TickSnapshot
}

export function TickHeader({ snap }: Props) {
  const entropyPct = Math.min(100, (snap.entropy / MAX_ENTROPY) * 100)
  const tgenMax = 2.0
  const tgenPct = Math.min(100, (snap.T_gen / tgenMax) * 100)

  return (
    <div className="flex items-center gap-3 px-3 py-2 bg-[var(--bg-overlay)] flex-wrap">
      <span className="text-xs font-mono font-bold text-[var(--accent-primary)] shrink-0">
        TICK {snap.tick + 1}
      </span>

      <div className="flex items-center gap-1.5 shrink-0">
        <span className="text-[10px] font-mono text-[var(--text-muted)]">H(W)</span>
        <div className="w-16 h-1.5 bg-[var(--border-muted)] rounded-full overflow-hidden">
          <div
            className="h-full rounded-full"
            style={{ width: `${entropyPct}%`, backgroundColor: 'var(--accent-cyan)' }}
          />
        </div>
        <span className="text-[10px] font-mono text-[var(--accent-cyan)]">
          {snap.entropy.toFixed(3)}
        </span>
      </div>

      <div className="flex items-center gap-1.5 shrink-0">
        <span className="text-[10px] font-mono text-[var(--text-muted)]">T_gen</span>
        <div className="w-12 h-1.5 bg-[var(--border-muted)] rounded-full overflow-hidden">
          <div
            className="h-full rounded-full"
            style={{ width: `${tgenPct}%`, backgroundColor: 'var(--accent-warning)' }}
          />
        </div>
        <span className="text-[10px] font-mono text-[var(--accent-warning)]">
          {snap.T_gen.toFixed(3)}
        </span>
      </div>

      <div className="ml-auto flex items-center gap-1.5 shrink-0">
        {snap.compressed && <Badge variant="compressed">COMPRESSED</Badge>}
        <TagBadge tag={snap.transition_tag} />
      </div>
    </div>
  )
}
