import { Button } from '../components/Button'
import { INITIAL_MOOD_TAGS, type WizardState } from '../wizardState'

interface StepPreferencesProps {
  state: WizardState
  onChange: (patch: Partial<WizardState>) => void
  onBack: () => void
  onContinue: () => void
}

export function StepPreferences({ state, onChange, onBack, onContinue }: StepPreferencesProps) {
  function toggleTag(tag: string) {
    const isSelected = state.moodTags.includes(tag)
    onChange({
      moodTags: isSelected
        ? state.moodTags.filter((t) => t !== tag)
        : [...state.moodTags, tag],
    })
  }

  return (
    <div>
      <p className="font-mono text-xs uppercase tracking-wide text-ink-dim">Step 2 of 3</p>
      <h1 className="mt-2 font-display text-3xl font-bold text-ink">Fine-tune the mood</h1>
      <p className="mt-2 font-body text-sm text-ink-dim">
        These help us pick the right matches from what&apos;s out there.
      </p>

      <div className="mt-8 rounded-2xl border border-border bg-surface p-6">
        <section>
          <h2 className="font-body text-sm font-semibold text-ink">Mood &amp; style</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {INITIAL_MOOD_TAGS.map((tag) => {
              const selected = state.moodTags.includes(tag)
              return (
                <button
                  key={tag}
                  type="button"
                  onClick={() => toggleTag(tag)}
                  className={`rounded-full border px-3.5 py-1.5 font-body text-sm transition-colors ${
                    selected
                      ? 'border-coral bg-coral text-white'
                      : 'border-border text-ink hover:border-ink-dim'
                  }`}
                >
                  {tag}
                </button>
              )
            })}
          </div>
        </section>

        <section className="mt-8">
          <div className="flex items-center justify-between">
            <h2 className="font-body text-sm font-semibold text-ink">Energy</h2>
          </div>
          <div className="mt-4 flex items-center gap-3">
            <span className="font-mono text-xs uppercase tracking-wide text-ink-dim">Calm</span>
            <input
              type="range"
              min={0}
              max={100}
              value={state.energy}
              onChange={(e) => onChange({ energy: Number(e.target.value) })}
              className="range-coral h-1.5 w-full flex-1 cursor-pointer appearance-none rounded-full bg-border"
              style={{
                background: `linear-gradient(to right, var(--color-coral) ${state.energy}%, var(--color-border) ${state.energy}%)`,
              }}
            />
            <span className="font-mono text-xs uppercase tracking-wide text-ink-dim">
              Energetic
            </span>
          </div>
        </section>
      </div>

      <div className="mt-8 flex justify-end gap-3">
        <Button variant="outline" onClick={onBack}>
          Back
        </Button>
        <Button onClick={onContinue}>Continue</Button>
      </div>
    </div>
  )
}
