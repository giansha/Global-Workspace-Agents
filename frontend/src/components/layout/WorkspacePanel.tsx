'use client'

import { useEffect } from 'react'
import { useGWAStore } from '@/store/useGWAStore'
import { getWorkspace } from '@/lib/api'

export function WorkspacePanel() {
  const { memoryPanelOpen, workspaceData, setWorkspaceData, currentTicks, conversation } = useGWAStore()

  useEffect(() => {
    if (!memoryPanelOpen) return
    // Fetch immediately on open
    getWorkspace().then(setWorkspaceData).catch(() => {})
    // Poll every 1s while open
    const id = setInterval(() => {
      getWorkspace().then(setWorkspaceData).catch(() => {})
    }, 1000)
    return () => clearInterval(id)
  }, [memoryPanelOpen, setWorkspaceData])

  if (!memoryPanelOpen) return null

  const allTicks = [
    ...currentTicks,
    ...conversation.flatMap((turn) => turn.ticks),
  ]
  const lastWebSearchTick = [...allTicks].reverse().find(
    (t) => t.transition_tag === 'WEB_SEARCH' && t.web_search_raw && t.web_search_raw.length > 0
  )
  const webSearchResults = lastWebSearchTick?.web_search_raw ?? []
  const webSearchQuery = lastWebSearchTick?.web_search_query ?? ''

  const stm = workspaceData?.stm_entries ?? []
  const ltmCount = workspaceData?.ltm_count ?? 0
  const ltmKnowledge = workspaceData?.ltm_last_knowledge ?? ''
  const ragQueries = workspaceData?.rag_queries ?? []
  const ragContext = workspaceData?.rag_context ?? ''

  return (
    <div
      className="absolute left-0 right-0 z-20 flex border-b border-[var(--border-subtle)] bg-[var(--bg-surface)]"
      style={{ top: '2rem', maxHeight: '18rem' }}
    >
      {/* STM Column */}
      <div className="flex-1 min-w-0 border-r border-[var(--border-subtle)] flex flex-col">
        <div className="px-3 py-1.5 border-b border-[var(--border-subtle)] shrink-0">
          <span className="text-[10px] font-mono font-semibold tracking-widest uppercase text-[var(--text-muted)]">
            STM ({stm.length} entries)
          </span>
        </div>
        <div className="overflow-y-auto flex-1 p-2 flex flex-col gap-1.5">
          {stm.length === 0 ? (
            <span className="text-[10px] text-[var(--text-muted)] italic">—</span>
          ) : (
            stm.map((entry, i) => (
              <div key={i} className="flex gap-1.5 items-start">
                <span
                  className="text-[9px] font-mono font-bold shrink-0 px-1 rounded"
                  style={{
                    background: 'var(--bg-base)',
                    color: entry.role === 'user'
                      ? 'var(--accent-primary)'
                      : entry.role === 'system' || entry.role === 'memory'
                      ? 'var(--accent-warning, #f59e0b)'
                      : 'var(--text-secondary)',
                  }}
                >
                  {entry.role.toUpperCase()}
                </span>
                <span className="text-[10px] text-[var(--text-secondary)] font-mono whitespace-pre-wrap break-all leading-relaxed">
                  {entry.content.slice(0, 400)}{entry.content.length > 400 ? '…' : ''}
                </span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* LTM Column */}
      <div className="w-56 shrink-0 border-r border-[var(--border-subtle)] flex flex-col">
        <div className="px-3 py-1.5 border-b border-[var(--border-subtle)] shrink-0">
          <span className="text-[10px] font-mono font-semibold tracking-widest uppercase text-[var(--text-muted)]">
            LTM ({ltmCount} docs)
          </span>
        </div>
        <div className="overflow-y-auto flex-1 p-2">
          {ltmKnowledge ? (
            <p className="text-[10px] text-[var(--text-secondary)] font-mono whitespace-pre-wrap break-all leading-relaxed">
              {ltmKnowledge}
            </p>
          ) : (
            <span className="text-[10px] text-[var(--text-muted)] italic">—</span>
          )}
        </div>
      </div>

      {/* RAG Column */}
      <div className="flex-1 min-w-0 flex flex-col border-r border-[var(--border-subtle)]">
        <div className="px-3 py-1.5 border-b border-[var(--border-subtle)] shrink-0">
          <span className="text-[10px] font-mono font-semibold tracking-widest uppercase text-[var(--text-muted)]">
            RAG
          </span>
        </div>
        <div className="overflow-y-auto flex-1 p-2 flex flex-col gap-2">
          {ragQueries.length > 0 && (
            <div className="flex flex-col gap-0.5">
              <span className="text-[9px] font-mono text-[var(--text-muted)] uppercase tracking-wider">Queries</span>
              {ragQueries.map((q, i) => (
                <div key={i} className="flex gap-1 text-[10px] text-[var(--text-secondary)] font-mono">
                  <span className="text-[var(--text-muted)] shrink-0">{i + 1}.</span>
                  <span className="break-all">{q}</span>
                </div>
              ))}
            </div>
          )}
          {ragContext ? (
            <div className="flex flex-col gap-0.5">
              <span className="text-[9px] font-mono text-[var(--text-muted)] uppercase tracking-wider">Context</span>
              <pre className="text-[10px] font-mono text-[var(--text-secondary)] whitespace-pre-wrap break-all leading-relaxed">
                {ragContext.slice(0, 800)}{ragContext.length > 800 ? '…' : ''}
              </pre>
            </div>
          ) : (
            <span className="text-[10px] text-[var(--text-muted)] italic">—</span>
          )}
        </div>
      </div>

      {/* WEB SEARCH Column */}
      <div className="w-64 shrink-0 flex flex-col">
        <div className="px-3 py-1.5 border-b border-[var(--border-subtle)] shrink-0">
          <span className="text-[10px] font-mono font-semibold tracking-widest uppercase text-[var(--text-muted)]">
            Web Search
          </span>
        </div>
        <div className="overflow-y-auto flex-1 p-2 flex flex-col gap-2">
          {webSearchQuery && (
            <div className="flex flex-col gap-0.5">
              <span className="text-[9px] font-mono text-[var(--text-muted)] uppercase tracking-wider">Query</span>
              <span className="text-[10px] font-mono text-[var(--accent-cyan)] break-all">{webSearchQuery}</span>
            </div>
          )}
          {webSearchResults.length === 0 ? (
            <span className="text-[10px] text-[var(--text-muted)] italic">—</span>
          ) : (
            webSearchResults.map((r, i) => (
              <div key={i} className="flex flex-col gap-0.5 border-b border-[var(--border-subtle)] pb-1.5 last:border-0">
                <span className="text-[10px] font-mono text-[var(--text-primary)] leading-tight">{r.title}</span>
                <a
                  href={r.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[9px] font-mono text-[var(--accent-primary)] hover:underline truncate block"
                >
                  {r.url.length > 50 ? r.url.slice(0, 50) + '…' : r.url}
                </a>
                <span className="text-[10px] text-[var(--text-muted)] font-mono whitespace-pre-wrap break-all leading-relaxed">
                  {r.content.slice(0, 200)}{r.content.length > 200 ? '…' : ''}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
