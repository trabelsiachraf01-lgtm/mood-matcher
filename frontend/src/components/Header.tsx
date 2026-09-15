import { CheckIcon } from './icons'

interface HeaderProps {
  /** 1-indexed current step. */
  currentStep: 1 | 2
}

const TOTAL_STEPS = 2

export function Header({ currentStep }: HeaderProps) {
  return (
    <header className="flex items-center justify-between py-6">
      <span className="font-display text-lg font-bold text-ink">Hushtone</span>
      <div className="flex items-center">
        {Array.from({ length: TOTAL_STEPS }, (_, i) => i + 1).map((step, i) => (
          <div key={step} className="flex items-center">
            {i > 0 && (
              <div
                className={`h-0.5 w-8 ${step <= currentStep ? 'bg-ink' : 'bg-border'}`}
                aria-hidden="true"
              />
            )}
            <div
              className={`flex h-7 w-7 items-center justify-center rounded-full border font-mono text-xs ${
                step < currentStep
                  ? 'border-ink bg-ink text-white'
                  : step === currentStep
                    ? 'border-ink bg-ink text-white'
                    : 'border-border bg-transparent text-ink-dim'
              }`}
            >
              {step < currentStep ? <CheckIcon className="h-3.5 w-3.5" /> : step}
            </div>
          </div>
        ))}
      </div>
    </header>
  )
}
