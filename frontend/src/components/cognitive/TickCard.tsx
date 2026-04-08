import { TickSnapshot } from '@/lib/types'
import { TickHeader } from './TickHeader'
import { RagPanel } from './RagPanel'
import { CandidateList } from './CandidateList'
import { WinningThought } from './WinningThought'

export function TickCard({ snap }: { snap: TickSnapshot }) {
  return (
    <div className="rounded-md border border-[var(--border-muted)] overflow-hidden animate-fade-in bg-[var(--bg-surface)]">
      <TickHeader snap={snap} />
      <div className="grid grid-cols-2 divide-x divide-[var(--border-subtle)] min-h-0">
        <RagPanel snap={snap} />
        <CandidateList snap={snap} />
      </div>
      <div className="border-t border-[var(--border-subtle)]">
        <WinningThought thought={snap.winning_thought} />
      </div>
    </div>
  )
}
