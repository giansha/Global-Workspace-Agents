import { ButtonHTMLAttributes, ReactNode } from 'react'

type Variant = 'primary' | 'secondary' | 'danger'

const styles: Record<Variant, string> = {
  primary:
    'bg-[var(--accent-primary)] hover:bg-violet-400 text-white border-transparent',
  secondary:
    'bg-[var(--bg-elevated)] hover:bg-[var(--bg-overlay)] text-[var(--text-primary)] border border-[var(--border-muted)]',
  danger:
    'bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30',
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  children: ReactNode
}

export function Button({ variant = 'primary', className = '', children, ...props }: ButtonProps) {
  return (
    <button
      className={`
        inline-flex items-center justify-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium
        transition-colors duration-150 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed
        ${styles[variant]} ${className}
      `}
      {...props}
    >
      {children}
    </button>
  )
}
