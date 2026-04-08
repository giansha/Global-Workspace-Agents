import { Sidebar } from './Sidebar'
import { ConversationPanel } from '@/components/chat/ConversationPanel'

export function AppShell() {
  return (
    <div className="flex h-full bg-[var(--bg-base)]">
      <Sidebar />
      <main className="flex-1 min-w-0 h-full">
        <ConversationPanel />
      </main>
    </div>
  )
}
