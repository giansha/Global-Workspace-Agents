import { ConversationTurn } from '@/lib/types'
import { CognitiveTrace } from '@/components/cognitive/CognitiveTrace'

export function MessageBubble({ turn }: { turn: ConversationTurn }) {
  const isUser = turn.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
      <div className={`max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
        <div
          className={`
            px-3 py-2.5 rounded-xl text-sm leading-relaxed whitespace-pre-wrap
            ${isUser
              ? 'bg-[var(--accent-primary)] text-white rounded-br-sm'
              : 'bg-[var(--bg-surface)] text-[var(--text-primary)] border border-[var(--border-muted)] rounded-bl-sm'
            }
          `}
        >
          {turn.content || (
            <span className="italic text-[var(--text-muted)]">No response generated.</span>
          )}
        </div>
        {!isUser && <CognitiveTrace ticks={turn.ticks} />}
      </div>
    </div>
  )
}
