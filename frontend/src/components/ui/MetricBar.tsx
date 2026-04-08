interface MetricBarProps {
  label: string
  value: number
  max: number
  color?: string
}

export function MetricBar({ label, value, max, color = 'var(--accent-cyan)' }: MetricBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-[var(--text-secondary)] font-mono w-14 shrink-0">{label}</span>
      <div className="flex-1 h-1.5 bg-[var(--border-muted)] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-xs font-mono w-12 text-right shrink-0" style={{ color }}>
        {value.toFixed(3)}
      </span>
    </div>
  )
}
