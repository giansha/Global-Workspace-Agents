'use client'

import { useState } from 'react'
import { TickSnapshot } from '@/lib/types'

export function RagPanel({ snap }: { snap: TickSnapshot }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="flex flex-col gap-2 p-3">
      <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-wider">
        RAG Queries
      </p>
      {snap.rag_queries.length === 0 ? (
        <p className="text-xs text-[var(--text-muted)] italic">none</p>
      ) : (
        <ol className="flex flex-col gap-1">
          {snap.rag_queries.map((q, i) => (
            <li key={i} className="text-xs text-[var(--text-secondary)] flex gap-1.5">
              <span className="font-mono text-[var(--text-muted)] shrink-0">{i + 1}.</span>
              <span>{q}</span>
            </li>
          ))}
        </ol>
      )}

      {snap.rag_context && (
        <div className="mt-1">
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-[10px] font-mono text-[var(--accent-primary)] hover:underline cursor-pointer"
          >
            {expanded ? '▲ hide context' : '▼ show context'}
          </button>
          {expanded && (
            <pre className="mt-2 text-[10px] font-mono text-[var(--text-muted)] bg-[var(--bg-base)] border border-[var(--border-subtle)] rounded p-2 whitespace-pre-wrap break-all max-h-40 overflow-y-auto">
              {snap.rag_context.slice(0, 1200)}{snap.rag_context.length > 1200 ? '…' : ''}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}
