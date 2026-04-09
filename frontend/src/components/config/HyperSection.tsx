'use client'

import { GWAConfig } from '@/lib/types'
import { SliderField } from '@/components/ui/SliderField'
import { TextField } from '@/components/ui/TextField'

interface Props {
  config: GWAConfig
  onChange: (patch: Partial<GWAConfig>) => void
}

export function HyperSection({ config, onChange }: Props) {
  return (
    <div className="flex flex-col gap-4">
      <p className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider">Hyperparameters</p>

      <SliderField
        label="N (candidates)"
        value={config.N}
        min={1} max={6} step={1}
        onChange={(e) => onChange({ N: Number(e.target.value) })}
      />
      <SliderField
        label="T_base"
        value={config.T_base}
        min={0.1} max={1.5} step={0.05}
        onChange={(e) => onChange({ T_base: Number(e.target.value) })}
      />
      <SliderField
        label="α (alpha)"
        value={config.alpha}
        min={0} max={2.0} step={0.1}
        onChange={(e) => onChange({ alpha: Number(e.target.value) })}
      />
      <SliderField
        label="β (beta)"
        value={config.beta}
        min={0.5} max={5.0} step={0.1}
        onChange={(e) => onChange({ beta: Number(e.target.value) })}
      />
      <SliderField
        label="τ (tau)"
        value={config.tau}
        min={0.1} max={2.0} step={0.1}
        onChange={(e) => onChange({ tau: Number(e.target.value) })}
      />
      <SliderField
        label="θ (STM tokens)"
        value={config.theta}
        min={500} max={8000} step={500}
        onChange={(e) => onChange({ theta: Number(e.target.value) })}
      />
      <SliderField
        label="max_ticks"
        value={config.max_ticks}
        min={1} max={16} step={1}
        onChange={(e) => onChange({ max_ticks: Number(e.target.value) })}
      />
      <SliderField
        label="Idle interval (s)"
        value={config.idle_interval}
        min={5} max={300} step={5}
        onChange={(e) => onChange({ idle_interval: Number(e.target.value) })}
      />

      <p className="text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider pt-1">Max Tokens per Agent</p>
      <div className="grid grid-cols-2 gap-2">
        <TextField
          label="Attention"
          type="number"
          min={1}
          value={config.attention_max_tokens}
          onChange={(e) => onChange({ attention_max_tokens: Number(e.target.value) })}
        />
        <TextField
          label="Generator"
          type="number"
          min={1}
          value={config.generator_max_tokens}
          onChange={(e) => onChange({ generator_max_tokens: Number(e.target.value) })}
        />
        <TextField
          label="Critic"
          type="number"
          min={1}
          value={config.critic_max_tokens}
          onChange={(e) => onChange({ critic_max_tokens: Number(e.target.value) })}
        />
        <TextField
          label="Meta"
          type="number"
          min={1}
          value={config.meta_max_tokens}
          onChange={(e) => onChange({ meta_max_tokens: Number(e.target.value) })}
        />
        <TextField
          label="Response"
          type="number"
          min={1}
          value={config.response_max_tokens}
          onChange={(e) => onChange({ response_max_tokens: Number(e.target.value) })}
        />
      </div>
    </div>
  )
}
