import { ScoreBadge } from '@/components/ui/Badge'

interface Props {
  index: number
  candidate: string
  evaluation?: [number, string]
}

export function CandidateItem({ index, candidate, evaluation }: Props) {
  const score = evaluation?.[0] ?? 0
  const critique = evaluation?.[1] ?? ''

  return (
    <div className="flex flex-col gap-1 p-2 rounded bg-[var(--bg-base)] border border-[var(--border-subtle)]">
      <div className="flex items-start gap-2">
        <span className="text-[10px] font-mono text-[var(--text-muted)] shrink-0 mt-0.5">{index + 1}.</span>
        <ScoreBadge score={score} />
        <p className="text-xs text-[var(--text-primary)] leading-relaxed line-clamp-3 flex-1">
          {candidate}
        </p>
      </div>
      {critique && (
        <p className="text-[10px] text-[var(--text-muted)] italic ml-6 leading-relaxed">
          &ldquo;{critique}&rdquo;
        </p>
      )}
    </div>
  )
}
