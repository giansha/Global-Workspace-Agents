'use client'

import { useEffect, useRef } from 'react'
import { useGWAStore } from '@/store/useGWAStore'
import { TickSnapshot } from '@/lib/types'
import { v4 as uuidv4 } from 'uuid'

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

/**
 * Opens a persistent SSE connection to /api/idle-stream.
 * Feeds tick events into conversation and debug events into the debug panel.
 * Reconnects automatically on disconnect.
 */
export function useIdleStream(engineInitialized: boolean) {
  const { addTurn, appendDebugEvent } = useGWAStore()
  const esRef = useRef<EventSource | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (!engineInitialized) return

    let delay = 1000

    function connect() {
      if (esRef.current) {
        esRef.current.close()
      }

      const es = new EventSource(`${BASE}/api/idle-stream`)
      esRef.current = es

      const collectedTicks: TickSnapshot[] = []
      let finalResponse = ''

      es.addEventListener('tick', (e) => {
        try {
          const snap = JSON.parse(e.data) as TickSnapshot
          collectedTicks.push(snap)
          if (snap.final_response) {
            finalResponse = snap.final_response
          }
        } catch { /* ignore */ }
      })

      es.addEventListener('done', () => {
        if (finalResponse) {
          addTurn({
            id: uuidv4(),
            role: 'assistant',
            content: finalResponse,
            ticks: [...collectedTicks],
          })
        }
        // Reset for next idle cycle
        collectedTicks.length = 0
        finalResponse = ''
        delay = 1000  // reset backoff on successful cycle
      })

      es.addEventListener('debug', (e) => {
        try {
          appendDebugEvent(JSON.parse(e.data))
        } catch { /* ignore */ }
      })

      es.onerror = () => {
        es.close()
        esRef.current = null
        // Exponential backoff, max 30s
        reconnectTimer.current = setTimeout(() => {
          delay = Math.min(delay * 2, 30000)
          connect()
        }, delay)
      }
    }

    connect()

    return () => {
      esRef.current?.close()
      esRef.current = null
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
    }
  }, [engineInitialized, addTurn, appendDebugEvent])
}
