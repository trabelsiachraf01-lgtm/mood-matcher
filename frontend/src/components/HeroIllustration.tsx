interface HeroIllustrationProps {
  label: string
  /** The real matched photo. When absent (a song match), falls back to a mood illustration. */
  imageUrl?: string
}

/**
 * When the match is an image, shows the real matched photo — never AI-generated, this is the
 * actual attributed source image. When the match is a song, there's no photo to show, so a
 * deliberate gradient-sky illustration stands in as a mood visual instead.
 */
export function HeroIllustration({ label, imageUrl }: HeroIllustrationProps) {
  if (imageUrl) {
    return (
      <div className="relative h-[340px] w-full overflow-hidden rounded-2xl bg-tint-coral">
        <img src={imageUrl} alt={label} className="h-full w-full object-cover" />
        <span className="absolute bottom-4 left-4 rounded-full bg-ink/80 px-3 py-1 font-mono text-xs text-white">
          {label}
        </span>
      </div>
    )
  }

  return (
    <div
      className="relative h-[340px] w-full overflow-hidden rounded-2xl"
      style={{
        background: 'linear-gradient(180deg, #ffd7b0 0%, #ff9d8a 58%, #ff6f80 100%)',
      }}
    >
      <div
        className="absolute inset-x-0"
        style={{ top: '58%', height: '1px', background: 'rgba(255,255,255,0.45)' }}
        aria-hidden="true"
      />
      <svg
        className="absolute left-1/2 top-[42%] h-24 w-24 -translate-x-1/2 -translate-y-1/2"
        viewBox="0 0 100 100"
        aria-hidden="true"
      >
        <circle cx="50" cy="50" r="34" fill="rgba(255,255,255,0.75)" />
      </svg>
      <span className="absolute bottom-4 left-4 rounded-full bg-ink/80 px-3 py-1 font-mono text-xs text-white">
        {label}
      </span>
    </div>
  )
}
