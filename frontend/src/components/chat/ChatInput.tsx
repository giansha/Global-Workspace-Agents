'use client'

import { useState, KeyboardEvent } from 'react'
import { useGWAStore } from '@/store/useGWAStore'
import { useSSEChat } from '@/hooks/useSSEChat'
import { Button } from '@/components/ui/Button'

export function ChatInput() {
  const [text, setText] = useState('')
  const { streaming, engineInitialized } = useGWAStore()
  const { sendMessage } = useSSEChat()

  const disabled = streaming || !engineInitialized

  const submit = () => {
    const msg = text.trim()
    if (!msg || disabled) return
    setText('')
    sendMessage(msg)
  }

  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="px-4 py-3 bg-[var(--bg-surface)] border-t border-[var(--border-subtle)]">
      {!engineInitialized && (
        <p className="text-xs text-[var(--accent-warning)] mb-2 font-mono">
          ↑ Configure API settings and click Save &amp; Initialize to start
        </p>
      )}
      <div className="flex gap-2 items-end">
        <textarea
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={onKey}
          disabled={disabled}
          placeholder={disabled && !streaming ? 'Initialize engine first…' : 'Message GWA…'}
          className="
            flex-1 px-3 py-2 rounded-md text-sm bg-[var(--bg-elevated)]
            border border-[var(--border-muted)] text-[var(--text-primary)]
            placeholder:text-[var(--text-muted)]
            focus:outline-none focus:border-[var(--accent-primary)]
            resize-none transition-colors duration-150
            disabled:opacity-40 disabled:cursor-not-allowed
            max-h-40 overflow-y-auto
          "
          style={{ lineHeight: '1.5' }}
        />
        <Button onClick={submit} disabled={disabled || !text.trim()} className="shrink-0 h-9">
          Send
        </Button>
      </div>
    </div>
  )
}
