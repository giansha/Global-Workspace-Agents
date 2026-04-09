import { DebugPanelContent } from '@/components/debug/DebugPanelContent'

export function DebugSidebar() {
  return (
    <aside className="w-80 shrink-0 h-full overflow-y-auto border-l border-[var(--border-muted)] bg-[var(--bg-surface)]">
      <DebugPanelContent />
    </aside>
  )
}
