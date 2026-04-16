import { describe, it, expect } from 'vitest'
import { formatLog } from './exportLog'
import type { ConversationTurn, WorkspaceData } from './types'

const mockTurn: ConversationTurn = {
  id: 'turn-1',
  role: 'assistant',
  content: 'final response text',
  ticks: [
    {
      tick: 1,
      rag_queries: ['what is consciousness?', 'global workspace'],
      rag_context: 'Consciousness is a state of awareness...',
      entropy: 0.8234,
      T_gen: 1.23,
      candidates: ['thought A full text', 'thought B full text', 'thought C full text'],
      evaluations: ['Strong reasoning', 'Acceptable but vague', 'Off-topic'],
      winning_thought: 'thought A full text',
      transition_tag: 'THINK_MORE',
      stm_token_count: 412,
      compressed: false,
      final_response: null,
    },
    {
      tick: 2,
      rag_queries: ['entropy in cognitive systems'],
      rag_context: 'Entropy measures disorder...',
      entropy: 0.5100,
      T_gen: 0.97,
      candidates: ['response thought full text'],
      evaluations: ['Clear and complete'],
      winning_thought: 'response thought full text',
      transition_tag: 'RESPONSE',
      stm_token_count: 598,
      compressed: false,
      final_response: 'final response text',
    },
  ],
}

const mockUserTurn: ConversationTurn = {
  id: 'turn-0',
  role: 'user',
  content: 'What is consciousness?',
  ticks: [],
}

const mockWorkspaceData: WorkspaceData = {
  stm_entries: [
    { role: 'user', content: 'What is consciousness?', tick: 0 },
    { role: 'assistant', content: 'final response text', tick: 2 },
  ],
  ltm_count: 5,
  ltm_last_knowledge: 'Global Workspace Theory posits...',
  rag_context: 'Consciousness is a state of awareness...',
  rag_queries: ['what is consciousness?'],
}

describe('formatLog', () => {
  it('includes session header with Generated timestamp', () => {
    const log = formatLog([mockUserTurn, mockTurn], null)
    expect(log).toMatch(/GWA SESSION LOG/)
    expect(log).toMatch(/Generated:/)
  })

  it('includes full user message without truncation', () => {
    const log = formatLog([mockUserTurn, mockTurn], null)
    expect(log).toContain('What is consciousness?')
  })

  it('includes tick metadata', () => {
    const log = formatLog([mockUserTurn, mockTurn], null)
    expect(log).toContain('TICK 1')
    expect(log).toContain('entropy=0.8234')
    expect(log).toContain('T_gen=1.2300')
    expect(log).toContain('STM tokens=412')
    expect(log).toContain('compressed=false')
    expect(log).toContain('tag=THINK_MORE')
  })

  it('includes all RAG queries', () => {
    const log = formatLog([mockUserTurn, mockTurn], null)
    expect(log).toContain('what is consciousness?')
    expect(log).toContain('global workspace')
  })

  it('includes full RAG context without truncation', () => {
    const log = formatLog([mockUserTurn, mockTurn], null)
    expect(log).toContain('Consciousness is a state of awareness...')
  })

  it('includes all candidates with critiques', () => {
    const log = formatLog([mockUserTurn, mockTurn], null)
    expect(log).toContain('thought A full text')
    expect(log).toContain('thought B full text')
    expect(log).toContain('thought C full text')
    expect(log).toContain('Strong reasoning')
    expect(log).toContain('Acceptable but vague')
    expect(log).toContain('Off-topic')
  })

  it('includes winning thought', () => {
    const log = formatLog([mockUserTurn, mockTurn], null)
    expect(log).toContain('Winning Thought:')
    expect(log).toContain('thought A full text')
  })

  it('includes final response on RESPONSE tick', () => {
    const log = formatLog([mockUserTurn, mockTurn], null)
    expect(log).toContain('Final Response:')
    expect(log).toContain('final response text')
  })

  it('includes workspace state section when workspaceData provided', () => {
    const log = formatLog([mockUserTurn, mockTurn], mockWorkspaceData)
    expect(log).toContain('WORKSPACE STATE (at time of export)')
    expect(log).toContain('STM ENTRIES')
    expect(log).toContain('What is consciousness?')
    expect(log).toContain('LTM:')
    expect(log).toContain('Total documents: 5')
    expect(log).toContain('Global Workspace Theory posits...')
  })

  it('omits workspace state section when workspaceData is null', () => {
    const log = formatLog([mockUserTurn, mockTurn], null)
    expect(log).not.toContain('WORKSPACE STATE')
  })

  it('handles empty conversation', () => {
    const log = formatLog([], null)
    expect(log).toMatch(/GWA SESSION LOG/)
  })
})
