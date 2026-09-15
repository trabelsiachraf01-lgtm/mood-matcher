interface HeroIllustrationProps {
  /** The matched piece's own title — not the AI-generated mood caption shown elsewhere. */
  label: string
  creator: string
  source: string
  /** The real matched photo. When absent (a song match), falls back to a mood illustration. */
  imageUrl?: string
}

/**
 * Presents the match like a single piece hung on a gallery wall: a dark wall panel,
 * a lit frame with matting around the full (uncropped) image, and a museum-style
 * plaque underneath — rather than a cropped, edge-to-edge photo.
 */
export function HeroIllustration({ label, creator, source, imageUrl }: HeroIllustrationProps) {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-ink px-4 py-10 sm:px-10 sm:py-14">
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-40"
        style={{ background: 'radial-gradient(60% 100% at 50% 0%, rgba(255,255,255,0.14), transparent)' }}
        aria-hidden="true"
      />

      <div className="relative mx-auto aspect-[21/9] w-full max-w-3xl">
        <div className="absolute inset-0 flex items-center justify-center rounded-sm bg-[#f4f1e9] p-2.5 shadow-[0_12px_40px_rgba(0,0,0,0.45)] sm:p-3.5">
          {imageUrl ? (
            <img src={imageUrl} alt={label} className="h-full w-full object-contain" />
          ) : (
            <div
              className="h-full w-full"
              style={{ background: 'linear-gradient(180deg, #ffd7b0 0%, #ff9d8a 58%, #ff6f80 100%)' }}
            />
          )}
        </div>
      </div>

      <div className="relative mx-auto mt-6 w-full max-w-3xl border-t border-white/15 pt-3 text-center">
        <p className="font-display text-sm italic text-white">{label}</p>
        <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.15em] text-white/50">
          {creator} — {source}
        </p>
      </div>
    </div>
  )
}
