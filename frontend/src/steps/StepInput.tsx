import type { InputMode } from '../api/types'
import { Button } from '../components/Button'
import { ImageIcon, MusicIcon, TextLinesIcon } from '../components/icons'
import type { WizardState } from '../wizardState'

interface StepInputProps {
  state: WizardState
  onChange: (patch: Partial<WizardState>) => void
  onContinue: () => void
}

const OPTIONS: {
  mode: InputMode
  title: string
  subtext: string
  Icon: typeof ImageIcon
}[] = [
  {
    mode: 'image',
    title: 'Upload an image',
    subtext: 'Drop a photo whose mood you want to match',
    Icon: ImageIcon,
  },
  {
    mode: 'song',
    title: 'Paste a song link',
    subtext: 'A track that captures the vibe you’re after',
    Icon: MusicIcon,
  },
  {
    mode: 'text',
    title: 'Describe a mood',
    subtext: 'A sentence is enough',
    Icon: TextLinesIcon,
  },
]

export function StepInput({ state, onChange, onContinue }: StepInputProps) {
  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-wide text-ink-dim">Step 1 of 3</p>
      <h1 className="mt-2 font-display text-3xl font-bold text-ink">
        What&apos;s your starting point?
      </h1>

      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        {OPTIONS.map(({ mode, title, subtext, Icon }) => {
          const selected = state.inputMode === mode
          return (
            <button
              key={mode}
              type="button"
              onClick={() => onChange({ inputMode: mode })}
              className={`relative rounded-2xl border-2 bg-surface p-5 text-left transition-colors ${
                selected ? 'border-coral' : 'border-border hover:border-ink-dim'
              }`}
            >
              {selected && (
                <span className="absolute right-4 top-4 rounded-full bg-tint-coral px-2 py-0.5 font-mono text-[10px] font-medium uppercase tracking-wide text-coral-hover">
                  Selected
                </span>
              )}
              <Icon className={`h-6 w-6 ${selected ? 'text-coral' : 'text-ink-dim'}`} />
              <p className={`mt-4 font-body text-sm font-semibold ${selected ? 'text-coral' : 'text-ink'}`}>
                {title}
              </p>
              <p className="mt-1 font-body text-sm text-ink-dim">{subtext}</p>
            </button>
          )
        })}
      </div>

      <input
        type="text"
        value={state.inputValue}
        onChange={(e) => onChange({ inputValue: e.target.value })}
        className="mt-6 w-full rounded-xl border border-border bg-surface px-4 py-3 font-body text-sm text-ink outline-none focus:border-ink-dim"
      />

      <div className="mt-8 flex justify-end">
        <Button onClick={onContinue}>Continue</Button>
      </div>
    </div>
  )
}
