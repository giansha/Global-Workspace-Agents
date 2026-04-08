'use client'

import { useCallback } from 'react'
import { useGWAStore } from '@/store/useGWAStore'
import { ConversationTurn, TickSnapshot } from '@/lib/types'
import { v4 as uuidv4 } from 'uuid'

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export function useSSEChat() {
  const {
    appendTick,
    setStreaming,
    clearCurrentTicks,
    addTurn,
    setError,
  } = useGWAStore()

  const sendMessage = useCallback(
    async (message: string) => {
      // Add user turn immediately
      addTurn({ id: uuidv4(), role: 'user', content: message, ticks: [] })
      clearCurrentTicks()
      setStreaming(true)
      setError(null)

      const collectedTicks: TickSnapshot[] = []
      let finalResponse = ''

      try {
        const response = await fetch(`${BASE}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message }),
        })

        if (!response.ok || !response.body) {
          throw new Error(`HTTP ${response.status}`)
        }

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        let currentEvent = 'message'

        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })

          const lines = buffer.split('\n')
          buffer = lines.pop() ?? ''

          for (const line of lines) {
            if (line.startsWith('event:')) {
              currentEvent = line.slice(6).trim()
            } else if (line.startsWith('data:')) {
              const raw = line.slice(5).trim()
              if (!raw) continue
              try {
                const payload = JSON.parse(raw)
                if (currentEvent === 'tick') {
                  const tick = payload as TickSnapshot
                  collectedTicks.push(tick)
                  appendTick(tick)
                  if (tick.final_response) {
                    finalResponse = tick.final_response
                  }
                } else if (currentEvent === 'done') {
                  if (payload.final_response) {
                    finalResponse = payload.final_response
                  }
                } else if (currentEvent === 'error') {
                  setError(payload.message ?? 'Unknown error')
                }
              } catch {
                // ignore malformed SSE data lines
              }
            }
          }
        }
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err)
        setError(msg)
      } finally {
        // Commit assistant turn with all collected ticks
        addTurn({
          id: uuidv4(),
          role: 'assistant',
          content: finalResponse,
          ticks: [...collectedTicks],
        })
        clearCurrentTicks()
        setStreaming(false)
      }
    },
    [addTurn, appendTick, clearCurrentTicks, setError, setStreaming]
    // eslint-disable-next-line react-hooks/exhaustive-deps
  )

  return { sendMessage }
}
