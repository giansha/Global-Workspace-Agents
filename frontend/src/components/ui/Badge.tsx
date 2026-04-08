import { ReactNode } from 'react'

type Variant = 'default' | 'response' | 'think' | 'positive' | 'neutral' | 'negative' | 'cyan' | 'compressed'

const styles: Record<Variant, string> = {
  default: 'bg-[var(--bg-overlay)] text-[var(--text-secondary)] border border-[var(--border-muted)]',
  response: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
  think: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
  positive: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
  neutral: 'bg-[var(--bg-overlay)] text-[var(--text-secondary)] border border-[var(--border-muted)]',
  negative: 'bg-red-500/15 text-red-400 border border-red-500/30',
  cyan: 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30',
  compressed: 'bg-violet-500/15 text-violet-400 border border-violet-500/30',
}

export function Badge({ variant = 'default', children }: { variant?: Variant; children: ReactNode }) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium ${styles[variant]}`}
    >
      {children}
    </span>
  )
}

export function ScoreBadge({ score }: { score: number }) {
  const variant = score > 0 ? 'positive' : score < 0 ? 'negative' : 'neutral'
  const label = score > 0 ? `+${score}` : String(score)
  return <Badge variant={variant}>{label}</Badge>
}

export function TagBadge({ tag }: { tag: 'THINK_MORE' | 'RESPONSE' }) {
  return (
    <Badge variant={tag === 'RESPONSE' ? 'response' : 'think'}>
      {tag === 'RESPONSE' ? 'RESPONSE' : 'THINK_MORE'}
    </Badge>
  )
}
