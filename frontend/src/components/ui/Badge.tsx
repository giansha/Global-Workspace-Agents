import { ReactNode } from 'react'

type Variant = 'default' | 'response' | 'think' | 'cyan' | 'compressed'

const styles: Record<Variant, string> = {
  default: 'bg-[var(--bg-overlay)] text-[var(--text-secondary)] border border-[var(--border-muted)]',
  response: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
  think: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
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

export function TagBadge({ tag }: { tag: 'THINK_MORE' | 'RESPONSE' | 'WEB_SEARCH' }) {
  const variant = tag === 'RESPONSE' ? 'response' : tag === 'WEB_SEARCH' ? 'cyan' : 'think'
  return (
    <Badge variant={variant}>
      {tag}
    </Badge>
  )
}
