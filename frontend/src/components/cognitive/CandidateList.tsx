import { TickSnapshot } from '@/lib/types'
import { CandidateItem } from './CandidateItem'

export function CandidateList({ snap }: { snap: TickSnapshot }) {
  return (
    <div className="flex flex-col gap-2 p-3">
      <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-wider">
        Candidates ({snap.candidates.length})
      </p>
      {snap.candidates.length === 0 ? (
        <p className="text-xs text-[var(--text-muted)] italic">none</p>
      ) : (
        snap.candidates.map((c, i) => (
          <CandidateItem
            key={i}
            index={i}
            candidate={c}
            evaluation={snap.evaluations[i]}
          />
        ))
      )}
    </div>
  )
}
