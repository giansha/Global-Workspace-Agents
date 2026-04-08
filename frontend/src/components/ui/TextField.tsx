import { InputHTMLAttributes } from 'react'

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
}

export function TextField({ label, className = '', ...props }: TextFieldProps) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-xs text-[var(--text-secondary)] font-medium">{label}</label>
      )}
      <input
        className={`
          w-full px-3 py-1.5 rounded-md text-sm bg-[var(--bg-elevated)]
          border border-[var(--border-muted)] text-[var(--text-primary)]
          placeholder:text-[var(--text-muted)]
          focus:outline-none focus:border-[var(--accent-primary)]
          transition-colors duration-150
          ${className}
        `}
        {...props}
      />
    </div>
  )
}
