'use client'

import { create } from 'zustand'
import { ConversationTurn, DebugEvent, GWAConfig, TickSnapshot, WorkspaceStats, DEFAULT_CONFIG } from '@/lib/types'

interface GWAStore {
  // Config & engine
  config: GWAConfig
  setConfig: (c: GWAConfig) => void
  engineInitialized: boolean
  setEngineInitialized: (v: boolean) => void

  // Conversation history
  conversation: ConversationTurn[]
  addTurn: (turn: ConversationTurn) => void
  clearConversation: () => void

  // In-flight streaming state
  streaming: boolean
  setStreaming: (v: boolean) => void
  currentTicks: TickSnapshot[]
  appendTick: (tick: TickSnapshot) => void
  clearCurrentTicks: () => void

  // Workspace stats (polled)
  stats: WorkspaceStats | null
  setStats: (s: WorkspaceStats) => void

  // Error banner
  error: string | null
  setError: (e: string | null) => void

  // Debug mode
  debugMode: boolean
  setDebugMode: (v: boolean) => void
  debugEvents: DebugEvent[]
  appendDebugEvent: (e: DebugEvent) => void
  clearDebugEvents: () => void
}

export const useGWAStore = create<GWAStore>((set) => ({
  config: DEFAULT_CONFIG,
  setConfig: (c) => set({ config: c }),
  engineInitialized: false,
  setEngineInitialized: (v) => set({ engineInitialized: v }),

  conversation: [],
  addTurn: (turn) => set((s) => ({ conversation: [...s.conversation, turn] })),
  clearConversation: () => set({ conversation: [] }),

  streaming: false,
  setStreaming: (v) => set({ streaming: v }),
  currentTicks: [],
  appendTick: (tick) => set((s) => ({ currentTicks: [...s.currentTicks, tick] })),
  clearCurrentTicks: () => set({ currentTicks: [] }),

  stats: null,
  setStats: (s) => set({ stats: s }),

  error: null,
  setError: (e) => set({ error: e }),

  debugMode: false,
  setDebugMode: (v) => set({ debugMode: v }),
  debugEvents: [],
  appendDebugEvent: (e) => set((s) => ({ debugEvents: [...s.debugEvents, e] })),
  clearDebugEvents: () => set({ debugEvents: [] }),
}))
