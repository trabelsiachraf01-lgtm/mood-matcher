import { PauseIcon, WaveformIcon } from './icons'
import type { NowPlaying } from '../api/types'

interface NowPlayingBarProps {
  nowPlaying: NowPlaying
}

export function NowPlayingBar({ nowPlaying }: NowPlayingBarProps) {
  return (
    <div className="flex w-full items-center gap-4 bg-ink px-6 py-4">
      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-teal-bg">
        <WaveformIcon className="h-5 w-5 text-teal-fg" />
      </div>

      <div className="min-w-0">
        <p className="font-mono text-[11px] uppercase tracking-wide text-teal-fg">Now playing</p>
        <p className="truncate font-body text-sm text-white/90">
          {nowPlaying.title} · {nowPlaying.album}
        </p>
      </div>

      <button
        type="button"
        aria-label="Pause"
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-teal-fg text-teal-bg"
      >
        <PauseIcon className="h-4 w-4" />
      </button>

      <div className="hidden flex-1 items-center gap-2 sm:flex">
        <span className="font-mono text-xs text-white/60">{nowPlaying.currentTimeLabel}</span>
        <div className="h-1 flex-1 rounded-full bg-white/15">
          <div
            className="h-1 rounded-full bg-teal-fg"
            style={{ width: `${nowPlaying.progressPercent}%` }}
          />
        </div>
        <span className="font-mono text-xs text-white/60">{nowPlaying.durationLabel}</span>
      </div>

      <span className="hidden shrink-0 font-mono text-xs text-white/60 sm:inline">
        {nowPlaying.attribution.source} · {nowPlaying.attribution.license}
      </span>
    </div>
  )
}
