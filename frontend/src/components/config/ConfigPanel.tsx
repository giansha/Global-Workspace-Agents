'use client'

import { useEffect, useState } from 'react'
import { useGWAStore } from '@/store/useGWAStore'
import { GWAConfig } from '@/lib/types'
import { getConfig, postConfig, deleteSession } from '@/lib/api'
import { ApiSection } from './ApiSection'
import { HyperSection } from './HyperSection'
import { WorkspaceStats } from './WorkspaceStats'
import { Button } from '@/components/ui/Button'

export function ConfigPanel() {
  const { config, setConfig, setEngineInitialized, setError, clearConversation } = useGWAStore()
  const [localConfig, setLocalConfig] = useState<GWAConfig>(config)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [resetting, setResetting] = useState(false)

  useEffect(() => {
    getConfig().then(setLocalConfig).catch(() => {/* backend not up yet, keep defaults */})
  }, [])

  const handleChange = (patch: Partial<GWAConfig>) => {
    setLocalConfig((c) => ({ ...c, ...patch }))
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    try {
      await postConfig(localConfig)
      setConfig(localConfig)
      setEngineInitialized(true)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="flex flex-col gap-5 p-4">
      <div className="flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-[var(--accent-primary)] shadow-[0_0_6px_var(--accent-primary)]" />
        <span className="text-sm font-semibold text-[var(--text-primary)] font-mono tracking-wide">
          GWA ENGINE
        </span>
      </div>

      <ApiSection config={localConfig} onChange={handleChange} />
      <div className="border-t border-[var(--border-subtle)]" />
      <HyperSection config={localConfig} onChange={handleChange} />
      <div className="border-t border-[var(--border-subtle)]" />

      <Button onClick={handleSave} disabled={saving || resetting} className="w-full">
        {saving ? 'Initializing...' : saved ? '✓ Initialized' : 'Save & Initialize'}
      </Button>

      <Button
        onClick={async () => {
          setResetting(true)
          setError(null)
          try {
            await deleteSession()
            setEngineInitialized(false)
            clearConversation()
          } catch (err) {
            setError(err instanceof Error ? err.message : String(err))
          } finally {
            setResetting(false)
          }
        }}
        disabled={saving || resetting}
        className="w-full opacity-60 hover:opacity-100"
      >
        {resetting ? 'Resetting...' : 'Reset Session'}
      </Button>

      <div className="border-t border-[var(--border-subtle)]" />
      <WorkspaceStats />
    </div>
  )
}
