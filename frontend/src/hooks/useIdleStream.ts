'use client'

import { useEffect, useRef } from 'react'
import { useGWAStore } from '@/store/useGWAStore'
import { TickSnapshot } from '@/lib/types'
import { v4 as uuidv4 } from 'uuid'

const BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

function getSessionId(): string {
  const KEY = 'gwa_session_id'
  let id = sessionStorage.getItem(KEY)
  if (!id) {
    id = crypto.randomUUID()
    sessionStorage.setItem(KEY, id)
  }
  return id
}

export function useIdleStream(engineInitialized: boolean) {
  const { addTurn, appendDebugEvent } = useGWAStore()
  const abortRef = useRef<AbortController | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (!engineInitialized) return

    let delay = 1000
    let cancelled = false

    async function connect() {
      abortRef.current?.abort()
      const controller = new AbortController()
      abortRef.current = controller

      const collectedTicks: TickSnapshot[] = []
      let finalResponse = ''
      let currentEvent = 'message'
      let buffer = ''

      try {
        const response = await fetch(`${BASE}/api/idle-stream`, {
          headers: { 'X-Session-ID': getSessionId() },
          signal: controller.signal,
        })

        if (!response.ok || !response.body) throw new Error(`HTTP ${response.status}`)

        const reader = response.body.getReader()
        const decoder = new TextDecoder()

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
                  const snap = payload as TickSnapshot
                  collectedTicks.push(snap)
                  if (snap.final_response) finalResponse = snap.final_response
                } else if (currentEvent === 'done') {
                  if (finalResponse) {
                    addTurn({
                      id: uuidv4(),
                      role: 'assistant',
                      content: finalResponse,
                      ticks: [...collectedTicks],
                    })
                  }
                  collectedTicks.length = 0
                  finalResponse = ''
                  delay = 1000
                } else if (currentEvent === 'debug') {
                  appendDebugEvent(payload)
                }
              } catch { /* ignore */ }
            }
          }
        }
      } catch (err: unknown) {
        if (err instanceof Error && err.name === 'AbortError') return
      }

      if (!cancelled) {
        reconnectTimer.current = setTimeout(() => {
          delay = Math.min(delay * 2, 30000)
          connect()
        }, delay)
      }
    }

    connect()

    return () => {
      cancelled = true
      abortRef.current?.abort()
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
    }
  }, [engineInitialized, addTurn, appendDebugEvent])
}
