'use client'

import { InputHTMLAttributes } from 'react'

interface SliderFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string
  value: number
  unit?: string
}

export function SliderField({ label, value, unit = '', className = '', ...props }: SliderFieldProps) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between items-center">
        <label className="text-xs text-[var(--text-secondary)] font-medium">{label}</label>
        <span className="text-xs font-mono text-[var(--accent-cyan)]">
          {value}{unit}
        </span>
      </div>
      <input
        type="range"
        value={value}
        className={`
          w-full h-1 rounded-full appearance-none cursor-pointer
          bg-[var(--border-muted)]
          accent-[var(--accent-primary)]
          ${className}
        `}
        {...props}
      />
    </div>
  )
}
