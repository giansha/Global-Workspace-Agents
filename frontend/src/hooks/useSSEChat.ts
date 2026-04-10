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
    appendDebugEvent,
  } = useGWAStore()

  const sendMessage = useCallback(
    async (message: string) => {
      // Do NOT add user turn yet — wait until the engine actually starts
      // processing this message (first tick event). If an idle tick is running,
      // the producer thread blocks on the lock; the user bubble should only
      // appear after the idle response (if any) has been committed.
      clearCurrentTicks()
      setStreaming(true)
      setError(null)

      const pendingUserTurn: ConversationTurn = {
        id: uuidv4(),
        role: 'user',
        content: message,
        ticks: [],
      }
      let userTurnAdded = false

      const collectedTicks: TickSnapshot[] = []
      let finalResponse = ''

      try {
        const sessionId = sessionStorage.getItem('gwa_session_id') ?? ''
        const response = await fetch(`${BASE}/api/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Session-ID': sessionId,
          },
          body: JSON.stringify({ message, debug: true }),
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
                if (currentEvent === 'debug') {
                  appendDebugEvent(payload)
                } else if (currentEvent === 'tick') {
                  // Engine has acquired the lock and started — now show user bubble
                  if (!userTurnAdded) {
                    addTurn(pendingUserTurn)
                    userTurnAdded = true
                  }
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
        // If we never got a tick (e.g. network error before lock), still show
        // the user bubble so the conversation isn't silently lost.
        if (!userTurnAdded) addTurn(pendingUserTurn)
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
    [addTurn, appendDebugEvent, appendTick, clearCurrentTicks, setError, setStreaming]
  )

  return { sendMessage }
}
