import { ConfigPanel } from '@/components/config/ConfigPanel'

export function Sidebar() {
  return (
    <aside
      className="w-72 shrink-0 h-full overflow-y-auto border-r border-[var(--border-muted)] bg-[var(--bg-surface)]"
    >
      <ConfigPanel />
    </aside>
  )
}
