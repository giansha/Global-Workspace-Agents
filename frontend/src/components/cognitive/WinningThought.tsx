export function WinningThought({ thought }: { thought: string }) {
  return (
    <div className="px-3 pb-3">
      <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-1.5">
        W_t — Winning Thought
      </p>
      <div className="border-l-2 border-[var(--accent-primary)] bg-[var(--bg-elevated)] rounded-r-md px-3 py-2.5">
        <p className="text-xs text-[var(--text-primary)] leading-relaxed whitespace-pre-wrap">
          {thought}
        </p>
      </div>
    </div>
  )
}
