'use client'

import { useEffect } from 'react'
import { useGWAStore } from '@/store/useGWAStore'
import { getStats } from '@/lib/api'

export function useWorkspaceStats() {
  const { setStats, streaming } = useGWAStore()

  useEffect(() => {
    // Fetch once immediately
    getStats().then(setStats).catch(() => {})

    // Poll every 3s when not streaming
    if (streaming) return
    const interval = setInterval(() => {
      getStats().then(setStats).catch(() => {})
    }, 3000)
    return () => clearInterval(interval)
  }, [streaming, setStats])
}
