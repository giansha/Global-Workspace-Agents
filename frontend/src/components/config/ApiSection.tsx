'use client'

import { GWAConfig } from '@/lib/types'
import { TextField } from '@/components/ui/TextField'

interface Props {
  config: GWAConfig
  onChange: (patch: Partial<GWAConfig>) => void
}

export function ApiSection({ config, onChange }: Props) {
  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider">API</p>
      <TextField
        label="Base URL"
        value={config.api_base_url}
        onChange={(e) => onChange({ api_base_url: e.target.value })}
        placeholder="https://api.openai.com/v1"
      />
      <TextField
        label="API Key"
        type="password"
        value={config.api_key}
        onChange={(e) => onChange({ api_key: e.target.value })}
        placeholder="sk-..."
      />
      <TextField
        label="Chat Model"
        value={config.chat_model}
        onChange={(e) => onChange({ chat_model: e.target.value })}
        placeholder="gpt-4o"
      />
      <TextField
        label="Embedding Model"
        value={config.embedding_model}
        onChange={(e) => onChange({ embedding_model: e.target.value })}
        placeholder="text-embedding-3-small"
      />
    </div>
  )
}
