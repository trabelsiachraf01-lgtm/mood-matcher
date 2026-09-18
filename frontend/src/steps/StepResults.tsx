import type { SongSource, SuggestionResponse } from '../api/types'
import { HeroIllustration } from '../components/HeroIllustration'

interface StepResultsProps {
  result: SuggestionResponse
  onBack: () => void
  songSource: SongSource
  onGenerateMusic: () => void
  isGeneratingMusic: boolean
  generateError: string | null
}

export function StepResults({
  result,
  onBack,
  songSource,
  onGenerateMusic,
  isGeneratingMusic,
  generateError,
}: StepResultsProps) {
  return (
    <div className="pb-8">
      <p className="font-mono text-xs uppercase tracking-wide text-ink-dim">Step 2 of 2</p>
      <button
        type="button"
        onClick={onBack}
        className="mt-2 font-body text-sm text-ink-dim underline-offset-2 hover:text-ink hover:underline"
      >
        ← Back to search
      </button>

      <div className="mt-6">
        <HeroIllustration
          label={result.matchedMedia.label}
          creator={result.attribution.creator}
          source={result.attribution.source}
          imageUrl={result.matchedMedia.kind === 'image' ? result.matchedMedia.assetUrl : undefined}
        />
      </div>

      <p className="mt-6 font-display text-2xl italic leading-snug text-ink">
        &ldquo;{result.caption}&rdquo;
      </p>

      <p className="mt-4 font-body text-sm text-ink-dim">
        {result.attribution.license}{' '}
        <a
          href={result.attribution.sourceUrl}
          target="_blank"
          rel="noreferrer"
          className="font-medium text-coral hover:text-coral-hover"
        >
          View source →
        </a>
      </p>

      {songSource === 'catalog' && (
        <div className="mt-6 border-t border-ink/10 pt-6">
          <button
            type="button"
            onClick={onGenerateMusic}
            disabled={isGeneratingMusic}
            className="rounded-lg bg-ink px-4 py-2 font-body text-sm font-medium text-white hover:bg-ink/90 disabled:opacity-50"
          >
            {isGeneratingMusic ? 'Generating…' : 'Generate a track with ElevenLabs'}
          </button>
          <p className="mt-2 font-mono text-[11px] uppercase tracking-wide text-ink-dim">
            Replaces the matched song below with an original, AI-generated one
          </p>
          {generateError && <p className="mt-2 font-body text-sm text-coral">{generateError}</p>}
        </div>
      )}
    </div>
  )
}
