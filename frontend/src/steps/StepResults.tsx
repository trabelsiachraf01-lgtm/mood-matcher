import type { SuggestionResponse } from '../api/types'
import { HeroIllustration } from '../components/HeroIllustration'
import { SunIcon, WaveformIcon } from '../components/icons'

interface StepResultsProps {
  result: SuggestionResponse
  onBack: () => void
}

export function StepResults({ result, onBack }: StepResultsProps) {
  return (
    <div className="pb-8">
      <p className="font-mono text-xs uppercase tracking-wide text-ink-dim">Step 3 of 3</p>
      <button
        type="button"
        onClick={onBack}
        className="mt-2 font-body text-sm text-ink-dim underline-offset-2 hover:text-ink hover:underline"
      >
        ← Back to search
      </button>

      <div className="mt-6">
        <HeroIllustration label={result.matchedMedia.label} />
      </div>

      <p className="mt-6 font-mono text-xs uppercase tracking-wide text-ink-dim">
        From your search · {result.searchSummary}
      </p>

      <p className="mt-3 font-display text-2xl italic leading-snug text-ink">
        &ldquo;{result.caption}&rdquo;
      </p>

      <p className="mt-4 font-body text-sm text-ink-dim">
        {result.attribution.creator} · {result.attribution.source} · {result.attribution.license}{' '}
        <a
          href={result.attribution.sourceUrl}
          target="_blank"
          rel="noreferrer"
          className="font-medium text-coral hover:text-coral-hover"
        >
          View source →
        </a>
      </p>

      <hr className="mt-8 border-border" />

      <div className="mt-6">
        <h2 className="font-body text-sm font-semibold text-ink">Related matches</h2>
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
          {result.relatedMatches.map((match) => {
            const isImage = match.kind === 'image'
            return (
              <a
                key={match.id}
                href="#"
                className="flex items-center gap-3 rounded-xl border border-border bg-surface p-3 transition-colors hover:border-ink-dim"
              >
                <div
                  className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${
                    isImage ? 'bg-tint-coral' : 'bg-teal-bg'
                  }`}
                >
                  {isImage ? (
                    <SunIcon className="h-5 w-5 text-coral-hover" />
                  ) : (
                    <WaveformIcon className="h-5 w-5 text-teal-fg" />
                  )}
                </div>
                <div className="min-w-0">
                  <p className="truncate font-body text-sm font-medium text-ink">{match.title}</p>
                  <p className="truncate font-body text-xs text-ink-dim">{match.creator}</p>
                </div>
              </a>
            )
          })}
        </div>
      </div>
    </div>
  )
}
