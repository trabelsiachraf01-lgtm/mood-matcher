import { useRef } from 'react'
import type { InputMode } from '../api/types'
import { Button } from '../components/Button'
import { ImageIcon, TextLinesIcon, WaveformIcon } from '../components/icons'
import type { WizardState } from '../wizardState'

interface StepInputProps {
  state: WizardState
  onChange: (patch: Partial<WizardState>) => void
  onContinue: () => void
  isLoading: boolean
  error: string | null
}

const MODES: { mode: InputMode; label: string; Icon: typeof ImageIcon; accept: string }[] = [
  { mode: 'image', label: 'Image', Icon: ImageIcon, accept: 'image/*' },
  { mode: 'song', label: 'Song', Icon: WaveformIcon, accept: 'audio/*' },
  { mode: 'text', label: 'Mood', Icon: TextLinesIcon, accept: '' },
]

export function StepInput({ state, onChange, onContinue, isLoading, error }: StepInputProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const activeMode = MODES.find((m) => m.mode === state.inputMode) ?? MODES[2]
  const canContinue = state.inputMode === 'text' ? state.text.trim().length > 0 : state.file !== null

  function selectMode(mode: InputMode) {
    onChange({ inputMode: mode, file: null })
  }

  function handleFilePick(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] ?? null
    onChange({ file })
  }

  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-wide text-ink-dim">Step 1 of 2</p>
      <h1 className="mt-2 font-display text-3xl font-bold text-ink">
        What&apos;s your starting point?
      </h1>

      <div className="mt-8 flex items-center gap-2">
        {MODES.map(({ mode, label, Icon }) => {
          const selected = state.inputMode === mode
          return (
            <button
              key={mode}
              type="button"
              onClick={() => selectMode(mode)}
              aria-pressed={selected}
              title={label}
              className={`flex h-11 w-11 items-center justify-center rounded-full border-2 transition-colors ${
                selected
                  ? 'border-coral bg-tint-coral text-coral'
                  : 'border-border text-ink-dim hover:border-ink-dim'
              }`}
            >
              <Icon className="h-5 w-5" />
              <span className="sr-only">{label}</span>
            </button>
          )
        })}
      </div>

      {state.inputMode === 'text' ? (
        <input
          id="mood-text-input"
          type="text"
          value={state.text}
          onChange={(e) => onChange({ text: e.target.value })}
          placeholder="Describe a mood — a sentence is enough"
          className="mt-6 w-full rounded-xl border border-border bg-surface px-4 py-3 font-body text-sm text-ink outline-none focus:border-ink-dim"
        />
      ) : (
        <div className="mt-6">
          <input
            ref={fileInputRef}
            id="mood-file-input"
            type="file"
            accept={activeMode.accept}
            onChange={handleFilePick}
            className="sr-only"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex w-full items-center gap-3 rounded-xl border border-dashed border-border bg-surface px-4 py-3 text-left font-body text-sm text-ink-dim hover:border-ink-dim"
          >
            <activeMode.Icon className="h-5 w-5 flex-shrink-0 text-ink-dim" />
            {state.file ? (
              <span className="truncate text-ink">{state.file.name}</span>
            ) : (
              <span>
                {state.inputMode === 'image' ? 'Choose an image to upload' : 'Choose a song to upload'}
              </span>
            )}
          </button>
        </div>
      )}

      {error && <p className="mt-4 font-body text-sm text-coral">{error}</p>}

      <div className="mt-8 flex justify-end">
        <Button onClick={onContinue} disabled={!canContinue || isLoading}>
          {isLoading ? 'Finding your match…' : 'Continue'}
        </Button>
      </div>
    </div>
  )
}
