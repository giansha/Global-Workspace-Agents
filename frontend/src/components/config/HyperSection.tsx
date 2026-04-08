'use client'

import { GWAConfig } from '@/lib/types'
import { SliderField } from '@/components/ui/SliderField'

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
    </div>
  )
}
