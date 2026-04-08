'use client'

import { useEffect, useRef } from 'react'
import { useGWAStore } from '@/store/useGWAStore'
import { MessageBubble } from './MessageBubble'
import { StreamingStatus } from './StreamingStatus'
import { ChatInput } from './ChatInput'
import { TickCard } from '@/components/cognitive/TickCard'

export function ConversationPanel() {
  const { conversation, streaming, currentTicks, error, setError } = useGWAStore()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [conversation, currentTicks])

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 flex flex-col gap-4">
        {conversation.length === 0 && (
          <div className="flex-1 flex items-center justify-center">
            <p className="text-sm text-[var(--text-muted)] font-mono text-center">
              Global Workspace is ready.<br />
              <span className="text-[var(--text-secondary)]">Configure the engine and send a message to begin.</span>
            </p>
          </div>
        )}
        {conversation.map((turn) => (
          <MessageBubble key={turn.id} turn={turn} />
        ))}
        {/* Live tick preview while streaming */}
        {streaming && currentTicks.length > 0 && (
          <div className="flex justify-start animate-fade-in">
            <div className="max-w-[80%] bg-[var(--bg-surface)] border border-[var(--border-muted)] rounded-xl rounded-bl-sm px-3 py-2">
              <p className="text-[10px] font-mono text-[var(--text-muted)] mb-1">
                Thinking… ({currentTicks.length} tick{currentTicks.length !== 1 ? 's' : ''})
              </p>
              {currentTicks.map((snap) => (
                <TickCard key={snap.tick} snap={snap} />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Error banner */}
      {error && (
        <div className="mx-4 mb-2 px-3 py-2 rounded-md bg-red-500/15 border border-red-500/30 flex items-center justify-between gap-2">
          <span className="text-xs text-red-400 font-mono">{error}</span>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300 text-xs cursor-pointer">✕</button>
        </div>
      )}

      <StreamingStatus />
      <ChatInput />
    </div>
  )
}
