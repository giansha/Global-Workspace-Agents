import type { ConversationTurn, WorkspaceData } from './types'

const SEP_HEAVY = '═'.repeat(60)
const SEP_LIGHT = '─'.repeat(60)

function pad2(n: number): string {
  return String(n).padStart(2, '0')
}

function formatDate(separator: { date: string; time: string; between: string }): string {
  const d = new Date()
  const date = `${d.getFullYear()}${separator.date}${pad2(d.getMonth() + 1)}${separator.date}${pad2(d.getDate())}`
  const time = `${pad2(d.getHours())}${separator.time}${pad2(d.getMinutes())}${separator.time}${pad2(d.getSeconds())}`
  return `${date}${separator.between}${time}`
}

function timestamp(): string {
  return formatDate({ date: '-', time: ':', between: ' ' })
}

function filenameTimestamp(): string {
  return formatDate({ date: '-', time: '-', between: '_' })
}

function formatTick(snap: ConversationTurn['ticks'][number]): string {
  const lines: string[] = []

  lines.push(SEP_LIGHT)
  lines.push(
    `TICK ${snap.tick} | entropy=${snap.entropy.toFixed(4)} | T_gen=${snap.T_gen.toFixed(4)} | ` +
    `STM tokens=${snap.stm_token_count} | compressed=${snap.compressed} | tag=${snap.transition_tag}`
  )
  lines.push('')

  lines.push('RAG Queries:')
  if (snap.rag_queries.length === 0) {
    lines.push('  (none)')
  } else {
    snap.rag_queries.forEach((q, i) => lines.push(`  ${i + 1}. ${q}`))
  }
  lines.push('')

  lines.push('RAG Context:')
  lines.push(snap.rag_context || '(empty)')
  lines.push('')

  lines.push('Candidates:')
  snap.candidates.forEach((candidate, i) => {
    const critique = snap.evaluations[i] ?? '(missing)'
    lines.push(`  [${i + 1}] ${candidate}`)
    lines.push(`      Critique: ${critique}`)
    lines.push('')
  })

  if (snap.critic_raw) {
    lines.push('Critic Output (full):')
    lines.push(snap.critic_raw)
    lines.push('')
  }

  lines.push('Winning Thought:')
  lines.push(snap.winning_thought)
  lines.push('')

  if (snap.meta_raw) {
    lines.push('Meta Output (full):')
    lines.push(snap.meta_raw)
    lines.push('')
  }

  if (snap.transition_tag === 'RESPONSE' && snap.final_response !== null) {
    lines.push('Final Response:')
    lines.push(snap.final_response)
    lines.push('')
  }

  return lines.join('\n')
}

function formatTurn(turn: ConversationTurn, turnIndex: number): string {
  const lines: string[] = []

  lines.push(SEP_HEAVY)
  lines.push(`[TURN ${turnIndex + 1}]`)
  lines.push('')

  if (turn.role === 'user') {
    lines.push('USER:')
    lines.push(turn.content)
    lines.push('')
  } else {
    lines.push(`ASSISTANT — ${turn.ticks.length} tick(s)`)
    turn.ticks.forEach((snap) => lines.push(formatTick(snap)))
  }

  return lines.join('\n')
}

function formatWorkspaceState(data: WorkspaceData): string {
  const lines: string[] = []

  lines.push('')
  lines.push(SEP_HEAVY)
  lines.push(SEP_HEAVY)
  lines.push('')
  lines.push('WORKSPACE STATE (at time of export)')
  lines.push('')

  lines.push(`STM ENTRIES (${data.stm_entries.length} entries):`)
  if (data.stm_entries.length === 0) {
    lines.push('  (empty)')
  } else {
    data.stm_entries.forEach((entry, i) => {
      lines.push(`  [entry ${i + 1}] role=${entry.role} tick=${entry.tick}`)
      lines.push(`  ${entry.content}`)
      lines.push('')
    })
  }

  lines.push('LTM:')
  lines.push(`  Total documents: ${data.ltm_count}`)
  lines.push('  Last stored knowledge:')
  lines.push(`  ${data.ltm_last_knowledge || '(none)'}`)
  lines.push('')

  lines.push(SEP_HEAVY)

  return lines.join('\n')
}

export function formatLog(
  conversation: ConversationTurn[],
  workspaceData: WorkspaceData | null,
): string {
  const lines: string[] = []

  lines.push('GWA SESSION LOG')
  lines.push(`Generated: ${timestamp()}`)
  lines.push(SEP_HEAVY)

  conversation.forEach((turn, i) => lines.push(formatTurn(turn, i)))

  if (conversation.length > 0) {
    lines.push(SEP_HEAVY)
  }

  if (workspaceData !== null) {
    lines.push(formatWorkspaceState(workspaceData))
  }

  return lines.join('\n')
}

export function downloadLog(
  conversation: ConversationTurn[],
  workspaceData: WorkspaceData | null,
): void {
  const text = formatLog(conversation, workspaceData)
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `gwa-log-${filenameTimestamp()}.txt`
  a.click()
  setTimeout(() => URL.revokeObjectURL(url), 60_000)
}
