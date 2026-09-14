import type { ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outline'
}

export function Button({ variant = 'primary', className = '', ...props }: ButtonProps) {
  const base = 'rounded-xl px-5 py-2.5 font-body text-sm font-medium transition-colors'
  const variants = {
    primary: 'bg-coral text-white hover:bg-coral-hover disabled:opacity-50',
    outline: 'border border-border bg-transparent text-ink hover:border-ink disabled:opacity-50',
  }
  return <button className={`${base} ${variants[variant]} ${className}`} {...props} />
}
