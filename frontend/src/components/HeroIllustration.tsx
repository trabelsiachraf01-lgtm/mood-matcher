interface HeroIllustrationProps {
  label: string
}

/**
 * Deliberate hero illustration for the results screen: a CSS gradient sky
 * with a thin horizon line and an SVG sun, standing in for the real matched
 * photo (never AI-generated — this is a placeholder frame around the
 * attributed source image).
 */
export function HeroIllustration({ label }: HeroIllustrationProps) {
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
